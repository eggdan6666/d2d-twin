# -*- coding: utf-8 -*-
"""SCNet API 基线预实验: 从 v3 抽 10 题(7 param + 3 cross), 两种条件(带检索上下文/裸问),
严格判分, 输出 token/延迟/成败, 供全量口径与预算决策。
用法(项目根):
  python eval/qa100/api_pretest.py --model "scnet:<模型广场里的准确ID>"
key 放 .env: SCNET_API_KEY=sk-tp-xxx"""
import sys, os, json, argparse, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.stdout.reconfigure(encoding="utf-8")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_OFFLINE", "1")

from rag import llm
from rag.hierarchical import HierarchicalRetriever
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score2 import correct

SYSTEM = llm_SYSTEM = ("You are an electronics datasheet QA assistant. Give exact values with "
                       "units from the excerpts. Be concise.")

def doc_fallback(retr, part, budget=7000):
    """检索为空时: 直接取该型号的 abs_max/elec_chars/front 切片(参数题的gold行必在其中)."""
    blocks = []
    for did in retr._doc_ids_for_part(part)[:1]:
        for i in retr.docs[did]["chunk_ids"]:
            c = retr.chunks[i]
            if c.section in ("abs_max", "elec_chars", "front", "overview"):
                blocks.append(f"[{c.part} §{c.section}]\n{c.text[:2200]}")
            if sum(len(b) for b in blocks) >= budget:
                break
    return "\n\n---\n\n".join(blocks)


def build_ctx(retr, q, k):
    parts = [s.split(":")[0] for s in q["gold"].split("|")] if q["type"] == "cross" else []
    if not parts:
        m = __import__("re").search(r"of ([\w\-.]+) \(", q["question"])
        parts = [m.group(1)] if m else []
    if parts:
        ctx, hits = retr.context_for_parts(q["question"], parts, k=k)
    else:
        ctx, hits = retr.context_for(q["question"], k=k)
    flag = "none"
    if len(ctx) < 200:
        ctx = "\n\n".join(doc_fallback(retr, p) for p in parts) or ctx
        flag = "doc_fallback"
    return ctx, [h["chunk_id"] for h in hits], flag


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="如 scnet:DeepSeek-V4.1-Flash-Event")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    ds = json.load(open("eval/qa100/datasheet_qa100_v3.json", encoding="utf-8"))
    random.seed(a.seed)
    params = random.sample([q for q in ds if q["type"] == "param"], 7)
    cross = random.sample([q for q in ds if q["type"] == "cross"], min(3, a.n - 7))
    sample = params + cross
    retr = HierarchicalRetriever()
    rows = []
    for i, q in enumerate(sample):
        ctx, srcs, flag = build_ctx(retr, q, a.k)
        for cond, prompt in [
            ("rag", f"Datasheet excerpts:\n{ctx}\n\nQuestion: {q['question']}"),
            ("bare", f"Question: {q['question']}"),
        ]:
            try:
                r = llm.chat(prompt, model=a.model, system=SYSTEM, timeout=600)
                ok = correct(q["gold"], r["text"])
                row = {"i": i, "qid": q["qid"], "cond": cond, "ok": ok, "ctx_flag": flag,
                       "prompt_tokens": r["prompt_tokens"],
                       "completion_tokens": r["completion_tokens"],
                       "latency_s": r["latency_s"],
                       "finish": r.get("finish_reason"), "pred": r["text"][:120]}
            except Exception as e:
                row = {"i": i, "qid": q["qid"], "cond": cond, "ctx_flag": flag,
                       "error": str(e)[:160]}
            rows.append(row)
            print(json.dumps(row, ensure_ascii=False))
    rag_rows = [x for x in rows if x["cond"] == "rag"]
    bare_rows = [x for x in rows if x["cond"] == "bare"]
    ok_r = sum(x.get("ok", False) for x in rag_rows)
    ok_b = sum(x.get("ok", False) for x in bare_rows)
    tok_r = sum(x.get("prompt_tokens", 0) + x.get("completion_tokens", 0) for x in rag_rows)
    print(f"\n== 预实验 {len(sample)}题 model={a.model} ==")
    print(f"rag : acc {ok_r}/{len(rag_rows)} 总tokens {tok_r} 平均 {tok_r//max(1,len(rag_rows))}")
    print(f"bare: acc {ok_b}/{len(bare_rows)}")
    err = [x for x in rows if "error" in x]
    if err:
        print("错误样例:", err[0]["error"])
    out = f"eval/qa100/api_pretest_{a.model.replace(':','_')}.json"
    json.dump({"model": a.model, "rows": rows}, open(out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("明细:", out)

if __name__ == "__main__":
    main()
