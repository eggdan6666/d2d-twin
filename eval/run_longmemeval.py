# -*- coding: utf-8 -*-
"""LongMemEval-S 小样本基线：裸模型 vs 会话检索增强。
用法（项目根）: python eval/run_longmemeval.py --n 10 [--model qwen2.5:3b-instruct] [--k 5]"""
import sys, os, json, time, argparse, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")

from rag.bm25 import BM25
from rag import llm

DATA = "data/eval/longmemeval_s.json"
OUT_DIR = "eval/results"
MAX_CHARS = 9000
SYS = ("You will see dated conversation excerpts retrieved from a user's memory. "
       "Answer the question using ONLY these excerpts. Be concise; if the excerpts "
       "are insufficient, reply INSUFFICIENT_CONTEXT.")
SYS_LOOSE = ("You will see dated conversation excerpts retrieved from a user's memory. "
             "Answer the question as best you can from these excerpts. Even if the "
             "answer is only implied or partial, give your most likely concrete answer. "
             "Never refuse. Be concise.")


def parse_date(s):
    m = re.search(r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})", s or "")
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.search(r"(\d{1,2})\s+(\w+),?\s*(\d{4})", s or "")
    MON = dict(January=1, February=2, March=3, April=4, May=5, June=6, July=7,
               August=8, September=9, October=10, November=11, December=12)
    if m and m.group(2) in MON:
        return (int(m.group(3)), MON[m.group(2)], int(m.group(1)))
    return None


def session_text(turns):
    return "\n".join(f"{t.get('role','')}: {t.get('content','')}" for t in turns)


def build_context(item, k, mode="full", budget=None):
    sessions = item["haystack_sessions"]
    texts = [session_text(s) for s in sessions]
    bm = BM25(texts)
    hits = bm.search(item["question"], top_k=k)
    cap = budget or MAX_CHARS
    blocks, used = [], 0
    if mode in ("windows", "mixed"):
        picks = []
        for rank, (i, score) in enumerate(hits):
            if mode == "mixed" and rank == 0:
                picks.append(((0, 0, 0),
                              f"[{item['haystack_dates'][i]}] (主要会话全文)\n{texts[i][:5500]}"))
                continue
            sess = sessions[i]
            tw = BM25([session_text(sess[max(0, t-1):t+2]) for t in range(len(sess))])
            best = tw.search(item["question"], top_k=1)
            ti = best[0][0] if best else 0
            win = session_text(sess[max(0, ti-1):ti+2])[:450]
            picks.append((parse_date(item["haystack_dates"][i]) or (9999, 1, 1),
                          f"[{item['haystack_dates'][i]}] {win}"))
        picks.sort(key=lambda x: x[0])
        budget_left = cap - len(picks[0][1]) if mode == "mixed" and picks else cap
        if mode == "mixed" and picks:
            blocks.append(picks[0][1]); used += len(picks[0][1])
            rest = picks[1:]
        else:
            rest = picks
        for _d, b in rest:
            if used + len(b) > cap:
                break
            blocks.append(b); used += len(b)
        return "\n\n".join(blocks), [item["haystack_session_ids"][i] for i, _ in hits], \
               set(item.get("answer_session_ids") or [])
    for i, _s in hits:
        b = f"[{item['haystack_dates'][i]}]\n{texts[i][:6000]}"
        if used + len(b) > cap:
            break
        blocks.append(b); used += len(b)
    return "\n\n".join(blocks), [item["haystack_session_ids"][i] for i, _ in hits], \
           set(item.get("answer_session_ids") or [])


def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", str(s).lower()).strip()


def correct(gold, pred):
    g, p = norm(gold), norm(pred)
    if not p:
        return False
    if g in p or p in g:
        return True
    gw = [w for w in g.split() if len(w) > 3]
    return bool(gw) and all(w in p for w in gw[:4])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--model", default=None)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--sysmode", choices=["strict", "loose"], default="strict",
                    help="strict=可拒答(原基线) loose=强制尽力作答(提示词松绑)")
    ap.add_argument("--ctxmode", choices=["full", "windows", "mixed"], default="full",
                    help="full=会话全文(现基线) windows=Tier3命中turn窗口聚合 mixed=top1全文+其余窗口")
    args = ap.parse_args()
    sys_prompt = SYS_LOOSE if args.sysmode == "loose" else SYS

    data = json.load(open(DATA, encoding="utf-8"))[:args.n]
    os.makedirs(OUT_DIR, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    out = open(os.path.join(OUT_DIR, f"smoke_{ts}.jsonl"), "w", encoding="utf-8")
    stat = {c: {"ok": 0, "tok": 0, "lat": 0.0} for c in ("rag", "none")}

    for idx, item in enumerate(data):
        ctx, retrieved, gold_sessions = build_context(item, args.k, args.ctxmode)
        recall = len(set(retrieved) & gold_sessions) / max(1, len(gold_sessions)) \
            if gold_sessions else None
        for cond, prompt in [
            ("rag", f"Conversation excerpts:\n{ctx}\n\n"
                    f"Question ({item['question_date']}): {item['question']}"),
            ("none", f"Question ({item['question_date']}): {item['question']}"),
        ]:
            r = llm.chat(prompt, model=args.model, system=sys_prompt, timeout=600)
            ok = correct(item["answer"], r["text"])
            stat[cond]["ok"] += ok
            stat[cond]["tok"] += r["prompt_tokens"] + r["completion_tokens"]
            stat[cond]["lat"] += r["latency_s"]
            out.write(json.dumps({"idx": idx, "cond": cond, "qid": item["question_id"],
                                  "qtype": item["question_type"], "ok": ok,
                                  "gold": str(item["answer"])[:120],
                                  "pred": r["text"][:120], "gold_recall": recall,
                                  "tokens": r["prompt_tokens"] + r["completion_tokens"],
                                  "latency_s": r["latency_s"]}, ensure_ascii=False) + "\n")
            print(f"[{idx:02d}][{cond:4s}] ok={ok} recall={recall} "
                  f"tok={r['prompt_tokens']}+{r['completion_tokens']} "
                  f"{r['latency_s']}s | {item['question_type']}")
    out.close()
    print("\n== 汇总 (n=%d, model=%s) ==" % (args.n, args.model or llm.DEFAULT_MODEL()))
    for cond, s in stat.items():
        print(f"{cond:5s} acc={s['ok']/args.n:.2f} 平均tokens={s['tok']//args.n} "
              f"平均延迟={s['lat']/args.n:.1f}s")
    print("明细:", out.name)

if __name__ == "__main__":
    main()
