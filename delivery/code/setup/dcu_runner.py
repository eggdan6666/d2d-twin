# -*- coding: utf-8 -*-
"""DCU / transformers 侧评测器：与 eval/qa100/run.py **共用**上下文构造与提示词，
只把推理后端从 Ollama HTTP 换成进程内 transformers 调用。

为什么复用而不复制：跨硬件一致性探针的全部意义在于"除了模型和权重格式，其他都不变"。
build_ctx / SYSTEM / SYSTEM_LOOSE / score2.correct 一律 import，避免两处实现漂移。

必须在项目根布局下运行（依赖 rag/ 与 eval/qa100/）。DCU 上解压 dcubundle 即可。

用法：
  # 跨硬件一致性探针（贪心，20 题）
  python _setup/dcu_runner.py --model-path /root/private_data/models/Qwen2.5-14B \
         --ds eval/qa100/datasheet_qa100_v3.json --tag dcu14b_v3 --loose --limit 20
  # 规模轴 k-trial（一次加载跑完 3 个 seed，省两次模型加载）
  python _setup/dcu_runner.py --model-path ... --tag dcu14b_kt --loose \
         --temperature 0.7 --seeds 1,2,3
  # 只核检索层是否与参照结果一致（不加载模型）
  python _setup/dcu_runner.py --retrieval-check eval/qa100/results_v31_rag7b_loose.json --k 5

已知与本地不可比之处（引用时必须声明）：
- 权重格式不同：本地 GGUF q4_K_M，这里 safetensors bf16 → 差值不能归因给"硬件"或"量化"任一项
- 注意力实现不同：DCU 无 flash 内核，默认 eager；与 Ollama kernel 数值路径不同，
  因此跨硬件比较**只比判分与错误分布，不比 pred 文本逐字**
- max_new_tokens 默认 256，Ollama 侧未显式设上限；答案普遍 <100 token
"""
import sys, os, json, time, argparse, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "eval", "qa100"))
sys.stdout.reconfigure(encoding="utf-8")

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from score2 import correct
from run import build_ctx, SYSTEM, SYSTEM_LOOSE

TVAL = {1: 0.0, 2: 6.314, 3: 4.303}          # 双侧 95% t 值，与 REPORT_ktrial.md 同口径


def summarize(tag, results):
    by, tot = collections.Counter(), collections.Counter()
    for r in results:
        by[r["type"]] += r["ok"]
        tot[r["type"]] += 1
    ok = sum(r["ok"] for r in results)
    line = f"{tag}: {ok}/{len(results)} = {ok/max(1,len(results)):.1%}"
    for t in sorted(tot):
        line += f" | {t} {by[t]}/{tot[t]}"
    print(line, flush=True)
    return ok / max(1, len(results))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-path", default=None)
    ap.add_argument("--ds", default="eval/qa100/datasheet_qa100_v3.json")
    ap.add_argument("--tag", default="dcu")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--only", default=None, help="只跑某题型，如 app/cross")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--loose", action="store_true", help="与 run.py --loose 同义（禁止拒答提示词）")
    ap.add_argument("--max-new", type=int, default=256)
    ap.add_argument("--dtype", default="bfloat16", choices=["bfloat16", "float16", "float32"])
    ap.add_argument("--attn", default="eager", choices=["eager", "sdpa", "flash_attention_2"],
                    help="海光 DCU 的 DTK torch 没有 flash_attn 内核，默认 sdpa 会在 generate 时抛 "
                         "'No matching libraries found for flash_attn_2_cuda*.so'，故默认 eager")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--top-p", type=float, default=0.9, help="对齐 Ollama 默认采样参数")
    ap.add_argument("--top-k", type=int, default=40, help="对齐 Ollama 默认采样参数")
    ap.add_argument("--seeds", default="42", help="逗号分隔；仅在 --temperature>0 时产生不同结果")
    ap.add_argument("--retrieval-check", default=None, metavar="RESULTS.json",
                    help="只比对检索层：对参照结果里的每个 qid 重建上下文，核对 sources/ctx_flag "
                         "是否一致，不加载模型。跨硬件对比的前置门——检索不一致则模型对比无意义")
    ap.add_argument("--dump-ctx", default=None, metavar="OUT.json",
                    help="导出模式：把 --ds 每题的检索上下文写成小 JSON（供 --ctx-file 用）。"
                         "这样 DCU 侧不必上传 54MB 语料，且检索恒等由构造保证，跨硬件差异只剩生成侧")
    ap.add_argument("--ctx-file", default=None, metavar="IN.json",
                    help="输入模式：从 --dump-ctx 导出的文件读上下文，跳过检索层（不需 rag/ 与语料）")
    a = ap.parse_args()
    seeds = [int(s) for s in a.seeds.split(",") if s.strip()]
    if not (a.retrieval_check or a.dump_ctx) and not a.model_path:
        sys.exit("非 --retrieval-check / --dump-ctx 模式必须给 --model-path")
    if len(seeds) > 1 and a.temperature <= 0:
        sys.exit("贪心解码(do_sample=False)与 seed 无关：多 seed 只会产出逐字相同的重复结果并白烧额度。"
                 "要么给 --temperature 0.7，要么只跑单个 seed。")

    qs = json.load(open(a.ds, encoding="utf-8"))
    if a.only:
        qs = [q for q in qs if q["type"] == a.only]
    if a.limit:
        qs = qs[:a.limit]
    sysmsg = SYSTEM_LOOSE if a.loose else SYSTEM
    if a.dump_ctx and a.ctx_file:
        sys.exit("--dump-ctx 与 --ctx-file 互斥（前者产上下文，后者消费）")

    ctxdata = None
    if a.ctx_file:
        ctxdata = json.load(open(a.ctx_file, encoding="utf-8"))
        print(f"上下文来自 {a.ctx_file}（跳过检索层，题数 {len(ctxdata)}）| 提示词="
              f"{'loose' if a.loose else 'strict'}", flush=True)
    else:
        from rag.hierarchical import HierarchicalRetriever   # 延迟 import：--ctx-file 模式不需要 rag/ 与语料
        t0 = time.time()
        retr = HierarchicalRetriever()
        print(f"检索层就绪 {time.time()-t0:.1f}s | 题数 {len(qs)} | 提示词={'loose' if a.loose else 'strict'} "
              f"| k={a.k} | T={a.temperature} seeds={seeds}", flush=True)

    if a.dump_ctx:
        ctxdata = {}
        for q in qs:
            ctx, hits, cflag = build_ctx(retr, q, a.k)
            ctxdata[q["qid"]] = {"ctx": ctx, "sources": [h["chunk_id"] for h in hits],
                                 "ctx_flag": cflag}
        json.dump(ctxdata, open(a.dump_ctx, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"已导出 {len(ctxdata)} 题上下文 → {a.dump_ctx} "
              f"({os.path.getsize(a.dump_ctx)/1e6:.2f} MB，未压缩)")
        return

    if a.retrieval_check:
        ref = {r["qid"]: r for r in json.load(open(a.retrieval_check, encoding="utf-8"))}
        byqid = {q["qid"]: q for q in qs}
        bad_src = bad_flag = miss = 0
        lens = []
        for qid, r in ref.items():
            q = byqid.get(qid)
            if q is None:
                miss += 1
                continue
            ctx, hits, cflag = build_ctx(retr, q, a.k)
            if [h["chunk_id"] for h in hits] != r.get("sources"):
                bad_src += 1
            if cflag != r.get("ctx_flag"):
                bad_flag += 1
            lens.append(len(ctx))
        print(f"检索一致性：sources 不一致 {bad_src}/{len(ref)} | ctx_flag 不一致 {bad_flag} "
              f"| 参照题不在本数据集 {miss}")
        if lens:
            print(f"上下文长度 均值 {sum(lens)/len(lens):.0f} 字符（参照端应同量级）")
        print("判定：", "检索层一致，可以进模型对比" if not (bad_src or bad_flag or miss)
              else "检索层不一致——先查语料/索引版本与 --k，别往下跑模型")
        return

    tok = AutoTokenizer.from_pretrained(a.model_path)
    torch.backends.cuda.enable_flash_sdp(False)
    torch.backends.cuda.enable_math_sdp(True)
    t0 = time.time()
    net = AutoModelForCausalLM.from_pretrained(a.model_path, dtype=getattr(torch, a.dtype),
                                               attn_implementation=a.attn).to("cuda")
    net.eval()
    print(f"模型加载 {time.time()-t0:.1f}s | 显存 {torch.cuda.memory_allocated()/1e9:.1f}GB "
          f"| attn={a.attn} dtype={a.dtype}", flush=True)

    accs = []
    for seed in seeds:
        torch.manual_seed(seed)
        gen = torch.Generator(device="cuda"); gen.manual_seed(seed)
        out = f"eval/qa100/results_{a.tag}.json" if len(seeds) == 1 \
            else f"eval/qa100/results_{a.tag}_s{seed}.json"
        results = []

        def snapshot():
            with open(out, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=1)

        t0 = time.time()
        for i, q in enumerate(qs):
            if ctxdata is not None:
                rec = ctxdata.get(q["qid"])
                if rec is None:
                    print(f"[{i:03d}] {q['qid']} 不在 ctx-file 里，跳过", flush=True)
                    continue
                ctx, srcs, cflag = rec["ctx"], rec["sources"], rec["ctx_flag"]
            else:
                ctx, hits, cflag = build_ctx(retr, q, a.k)
                srcs = [h["chunk_id"] for h in hits]
            prompt = (f"Datasheet excerpts:\n{ctx}\n\nQuestion: {q['question']}" if ctx
                      else f"Question: {q['question']}")
            msgs = [{"role": "system", "content": sysmsg}, {"role": "user", "content": prompt}]
            text_in = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
            # 必须用 encode(text, add_special_tokens=False)：apply_chat_template 已经渲染好
            # system/user 与 special token，若把渲染结果再交给 tokenizer(text, ...) 会二次注入
            # BOS 并把 system 提示词当成待补全文本 → 模型直接复读 "You are an electronics datasheet QA…"
            # （首轮 20 题探针就是这么废掉的：5/20 且多数 pred 以系统提示词开头）
            enc = tok(text_in, return_tensors="pt", add_special_tokens=False).to("cuda")
            n0 = int(enc.input_ids.shape[1])
            kw = dict(max_new_tokens=a.max_new, pad_token_id=tok.eos_token_id)
            if a.temperature > 0:
                kw.update(do_sample=True, temperature=a.temperature, top_p=a.top_p,
                          top_k=a.top_k, generator=gen)
            else:
                kw.update(do_sample=False)
            t1 = time.time()
            with torch.no_grad():
                g = net.generate(**enc, **kw)
            n1 = int(g.shape[1]) - n0
            lat = round(time.time() - t1, 2)
            pred = tok.decode(g[0][n0:], skip_special_tokens=True).strip()
            results.append({"qid": q["qid"], "type": q["type"], "ok": correct(q["gold"], pred),
                            "gold": q["gold"], "pred": pred[:500], "sources": srcs,
                            "ctx_flag": cflag, "verify": None, "tokens": n0 + n1,
                            "latency_s": lat, "seed": seed, "temperature": a.temperature})
            print(f"[{seed}][{i:03d}][{q['type']:5s}] ok={results[-1]['ok']} in={n0} out={n1} {lat}s "
                  f"| {q['question'][:40]} | pred={pred[:36]!r}", flush=True)
            if i % 10 == 9:
                snapshot()
        snapshot()
        accs.append(summarize(f"seed{seed} ({os.path.basename(out)})", results))
        print(f"  本轮 {time.time()-t0:.0f}s | 峰值显存 {torch.cuda.max_memory_allocated()/1e9:.1f}GB", flush=True)
        torch.cuda.empty_cache()

    if len(accs) > 1:
        import statistics as st
        mean = st.mean(accs)
        sd = st.stdev(accs) if len(accs) > 1 else 0.0
        half = TVAL.get(len(accs), 4.303) * sd / len(accs) ** 0.5
        print(f"\n== {a.tag} k-trial: mean {mean:.1%} ± {sd*100:.1f}pp, "
              f"95%CI [{(mean-half)*100:.1f}%, {(mean+half)*100:.1f}%] (n={len(accs)}, t={TVAL.get(len(accs))}) ==")
        print("   逐 seed:", [f"{x:.1%}" for x in accs])


if __name__ == "__main__":
    main()
