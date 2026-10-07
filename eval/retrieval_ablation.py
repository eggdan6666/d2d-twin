# -*- coding: utf-8 -*-
"""检索侧离线消融（不调用 LLM）：
1) 会话级 BM25 top-k 对 gold 会话的覆盖率随 k 变化
2) turn 级(±1窗口)检索 vs 会话级检索
3) temporal 类:按日期过滤候选后的覆盖率
输出 eval/results/retrieval_ablation.json + 控制台表。
用法: python eval/retrieval_ablation.py [--n 500]"""
import sys, os, json, re, argparse
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")
from rag.bm25 import BM25

DATA = "data/eval/longmemeval_s.json"
KS = [3, 5, 8, 12, 20]
MONTHS = {m: i for i, m in enumerate(
    ["January","February","March","April","May","June","July",
     "August","September","October","November","December"], 1)}

def parse_date(s):
    m = re.search(r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})", s or "")
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.search(r"(\d{1,2})\s+(\w+),?\s*(\d{4})", s or "")
    if m and m.group(2) in MONTHS:
        return (int(m.group(3)), MONTHS[m.group(2)], int(m.group(1)))
    return None

def session_text(turns):
    return "\n".join(f"{t.get('role','')}: {t.get('content','')}" for t in turns)

def norm(s):
    return re.sub(r"[^a-z0-9 ]", "", str(s).lower()).strip()

def cov(ranked_ids, gold, k):
    top = set(ranked_ids[:k])
    return 1.0 if gold and gold <= top else 0.0

def partial(ranked_ids, gold, k):
    if not gold:
        return None
    return len(set(ranked_ids[:k]) & gold) / len(gold)

def run(n):
    data = json.load(open(DATA, encoding="utf-8"))[:n]
    rows = defaultdict(lambda: defaultdict(list))
    meta = {"n": 0, "gold_string_absent": 0}
    for it in data:
        qtype = it["question_type"]
        gold = set(it.get("answer_session_ids") or [])
        texts = [session_text(s) for s in it["haystack_sessions"]]
        sids = it["haystack_session_ids"]
        meta["n"] += 1
        if gold and not any(norm(it["answer"]) in norm(t) and sid in gold
                            for t, sid in zip(texts, sids)) \
                and qtype in ("single-session-user", "knowledge-update"):
            meta["gold_string_absent"] += 1
        bm = BM25(texts)
        ranked = [sids[i] for i, _ in bm.search(it["question"], top_k=max(KS))]
        for k in KS:
            rows[qtype]["session_cover@%d" % k].append(cov(ranked, gold, k))
            rows[qtype]["session_partial@%d" % k].append(partial(ranked, gold, k) or 0)
        # turn 级:窗口 = 该 turn ±1
        chunks, owner = [], []
        for si, sess in enumerate(it["haystack_sessions"]):
            for ti in range(len(sess)):
                lo, hi = max(0, ti-1), min(len(sess), ti+2)
                chunks.append(session_text(sess[lo:hi])); owner.append(sids[si])
        bmt = BM25(chunks)
        hit_order = []
        for i, _ in bmt.search(it["question"], top_k=40):
            if owner[i] not in hit_order:
                hit_order.append(owner[i])
        for k in (5, 8, 12, 20):
            rows[qtype]["turn_cover@%d" % k].append(cov(hit_order, gold, k))
        # temporal:仅保留日期<=提问日期的会话
        if qtype == "temporal-reasoning":
            qd = parse_date(it.get("question_date"))
            cand = [t for t, d, s in zip(texts, it["haystack_dates"], sids)
                    if qd and parse_date(d) and parse_date(d) <= qd]
            candsid = [s for t, d, s in zip(texts, it["haystack_dates"], sids)
                       if qd and parse_date(d) and parse_date(d) <= qd]
            if cand:
                bmd = BM25(cand)
                rk = [candsid[i] for i, _ in bmd.search(it["question"], top_k=20)]
                for k in (8, 20):
                    rows[qtype]["datefilter_cover@%d" % k].append(cov(rk, gold, k))
                rows[qtype]["datefilter_partial@8"].append(partial(rk, gold, 8) or 0)
    out = {}
    for qtype, m in rows.items():
        out[qtype] = {k: round(sum(v)/len(v), 3) for k, v in sorted(m.items())}
    result = {"meta": meta, "by_type": out}
    os.makedirs("eval/results", exist_ok=True)
    json.dump(result, open("eval/results/retrieval_ablation.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for t in ("multi-session", "temporal-reasoning", "knowledge-update",
              "single-session-user", "single-session-assistant"):
        if t in out:
            print("\n==", t, "==")
            for k, v in out[t].items():
                print(f"  {k:24s} {v}")
    print("\nmeta:", meta)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=500)
    a = ap.parse_args()
    run(a.n)
