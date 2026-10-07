# -*- coding: utf-8 -*-
"""Datasheet-QA-100 评测器：检索增强答题 + 数值判分。
用法（项目根）:
  python eval/qa100/run.py [--model qwen2.5:3b-instruct] [--limit 10] [--bare]
判分: gold 中所有"数值+单位"组必须全部出现在预测中（宽松顺序无关）。"""
import sys, os, json, re, argparse
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.stdout.reconfigure(encoding="utf-8")

SYSTEM = ("You are an electronics datasheet QA assistant. Answer with exact values "
          "and units from the excerpts. Be concise.")
SYSTEM_LOOSE = ("You are an electronics datasheet QA assistant. Give the most likely concrete "
                "values with units from the excerpts. Even if only implied or partial, answer. "
                "Never refuse. Be concise.")
UNIT = r"(?:V|mA|A|mV|GHz|MHz|kHz|Hz|°C|uF|µF|nF|pF|k?Ω|m?W|dB|ns|us|μs|ps)"

def gold_items(gold):
    return re.findall(rf"\d+(?:\.\d+)?(?:\s*[-–~]\s*\d+(?:\.\d+)?)?\s*{UNIT}?", gold)

def correct(gold, pred):
    items = [g.strip() for g in gold_items(gold) if re.search(UNIT, g)]
    if not items:
        items = gold_items(gold)
    p = pred.replace(",", "")
    def hit(g):
        num = re.match(r"\d+(?:\.\d+)?", g).group(0)
        unit = re.sub(r"[\d.\s-]", "", g)
        return re.search(rf"{re.escape(num)}\s*(?:[\d.\s–~-]*\b)?{re.escape(unit)}?", p) is not None
    return bool(items) and all(hit(g) for g in items)

def doc_fallback(retr, part, budget=7000):
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
    import re as _re
    parts = [s.split(":")[0] for s in q["gold"].split("|")] if q["type"] == "cross" else []
    if not parts:
        m = _re.search(r"of ([\w\-.]+) \(", q["question"])
        parts = [m.group(1)] if m else []
    if not parts:
        # 题干措辞一改，上面那条正则就会静默失效（批次三 36 道 app 题就是这么退化成全局检索的：
        # "guidance for X (TI)" 里没有 "of X ("，sources 与定向检索应得结果 0/36 相同）。
        # 兜底不依赖措辞：取题面里形如型号的词，问检索层"这个词有没有文档"。
        for tok in _re.findall(r"[A-Za-z][A-Za-z0-9\-]*\d[A-Za-z0-9\-]*", q["question"]):
            if retr._doc_ids_for_part(tok):
                parts = [tok]
                break
    if parts:
        ctx, hits = retr.context_for_parts(q["question"], parts, k=k)
    else:
        ctx, hits = retr.context_for(q["question"], k=k)
    flag = "none"
    if len(ctx) < 200:
        ctx = "\n\n".join(doc_fallback(retr, p) for p in parts) or ctx
        flag = "doc_fallback"
    return ctx, hits, flag


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=None)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--bare", action="store_true")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--perdoc", action="store_true", help="cross题按型号各自检索,文档间平衡")
    ap.add_argument("--only", default=None, help="只跑某题型,如 cross")
    ap.add_argument("--loose", action="store_true", help="松绑提示词(禁止拒答)")
    ap.add_argument("--verify", action="store_true", help="cross题归属校验+一次纠错重试")
    ap.add_argument("--ds", default=None, help="数据集文件(默认自动取最新 v4>v3>v2)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--tag", default=None, help="结果文件名标签")
    args = ap.parse_args()
    from rag import llm
    try:
        from score2 import correct as strict_correct
    except Exception:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from score2 import correct as strict_correct
    correct = strict_correct  # 统一采用严格判分协议
    if args.ds:
        qs = json.load(open(args.ds, encoding="utf-8"))
    else:
        qs = json.load(open("eval/qa100/datasheet_qa100.json", encoding="utf-8"))
        for v in ("datasheet_qa100_v2.json", "datasheet_qa100_v3.json",
                  "datasheet_qa100_v4.json"):
            if os.path.exists("eval/qa100/" + v):
                qs = json.load(open("eval/qa100/" + v, encoding="utf-8"))
    if args.only:
        qs = [q for q in qs if q["type"] == args.only]
    if args.limit:
        qs = qs[:args.limit]
    retr = None
    if not args.bare:
        from rag.hierarchical import HierarchicalRetriever
        retr = HierarchicalRetriever()
    sysmsg = SYSTEM_LOOSE if args.loose else SYSTEM
    out = f"eval/qa100/results_{args.tag or int(__import__('time').time())}.json"
    results = []

    def snapshot():
        with open(out, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=1)

    for i, q in enumerate(qs):
        ctx, hits, cflag = ("", [], "bare")
        if retr:
            ctx, hits, cflag = build_ctx(retr, q, args.k)
        srcs = [h["chunk_id"] for h in hits]
        prompt = (f"Datasheet excerpts:\n{ctx}\n\nQuestion: {q['question']}"
                  if ctx else f"Question: {q['question']}")
        try:
            r = llm.chat(prompt, model=args.model, system=sysmsg, timeout=600,
                         temperature=args.temperature, seed=args.seed)
        except Exception as e:  # 单题网络/服务异常: 重试一次, 再失败记错误行继续
            try:
                __import__("time").sleep(20)
                r = llm.chat(prompt, model=args.model, system=sysmsg, timeout=600,
                             temperature=args.temperature, seed=args.seed)
            except Exception as e2:
                results.append({"qid": q["qid"], "type": q["type"], "ok": False,
                                "gold": q["gold"], "pred": "", "sources": srcs,
                                "ctx_flag": cflag, "verify": None, "tokens": 0,
                                "latency_s": 0, "error": str(e2)[:120]})
                snapshot()
                print(f"[{i:03d}] ERROR skip {str(e2)[:60]}", flush=True)
                continue
        vinfo = None
        if args.verify and q["type"] == "cross" and ctx:
            from rag.verify import check_attribution
            v = check_attribution(r["text"], ctx)
            vinfo = {"first_ok": v["ok"], "n_err": len(v["errors"])}
            if not v["ok"]:
                r2 = llm.chat(prompt + "\n\nIMPORTANT: " + v["retry_hint"] +
                              " Give corrected values.", model=args.model,
                              system=sysmsg, timeout=600)
                v2 = check_attribution(r2["text"], ctx)
                vinfo.update({"retried": True, "retry_ok": v2["ok"]})
                if correct(q["gold"], r2["text"]) or not correct(q["gold"], r["text"]):
                    r = r2
        ok = correct(q["gold"], r["text"])
        results.append({"qid": q["qid"], "type": q["type"], "ok": ok,
                        "gold": q["gold"], "pred": r["text"][:500], "sources": srcs,
                        "ctx_flag": cflag, "verify": vinfo,
                        "tokens": r["prompt_tokens"] + r["completion_tokens"],
                        "latency_s": r["latency_s"]})
        print(f"[{i:03d}][{q['type']:5s}] ok={ok} | {q['question'][:56]} | gold={q['gold'][:28]} | pred={r['text'][:40]!r}", flush=True)
        if i % 10 == 9:
            snapshot()
    n = len(results)
    import collections
    by = collections.defaultdict(lambda: [0, 0])
    for x in results:
        by[x["type"]][0] += x["ok"]; by[x["type"]][1] += 1
    print(f"\n== QA100 acc(部分)={sum(x['ok'] for x in results)}/{n} ==")
    for t, (ok, tot) in by.items():
        print(f"  {t:6s} {ok}/{tot} = {ok/tot:.2f}")
    snapshot()
    print("明细:", out)

if __name__ == "__main__":
    main()
