# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding="utf-8")
import json, os, glob, datetime

files = ["eval/results/smoke_20261003_191205.jsonl"]
rows = []
for f in files:
    for line in open(f, encoding="utf-8"):
        rows.append(json.loads(line))

# dedup by (cond, qid): keep last occurrence (latest file order)
latest = {}
for i, r in enumerate(rows):
    latest[(r["cond"], r["qid"])] = r
rows = list(latest.values())
print("unique qids:", len({r['qid'] for r in rows}), "rows:", len(rows))

def agg(rs):
    n = len(rs)
    return {
        "n": n,
        "acc": sum(r["ok"] for r in rs) / n,
        "tok": sum(r["tokens"] for r in rs) / n,
        "lat": sum(r["latency_s"] for r in rs) / n,
    }

for cond in ("rag", "none"):
    s = agg([r for r in rows if r["cond"] == cond])
    print(cond, s)

qt = sorted({r["qtype"] for r in rows})
print("\nqtype, n, rag_acc, none_acc")
for q in qt:
    sub = {c: [r for r in rows if r["cond"] == c and r["qtype"] == q] for c in ("rag", "none")}
    print(q, len(sub["rag"]), round(sum(r['ok'] for r in sub['rag'])/max(1,len(sub['rag'])), 3),
          round(sum(r['ok'] for r in sub['none'])/max(1,len(sub['none'])), 3))

rg = [r["gold_recall"] for r in rows if r["cond"] == "rag" and r["gold_recall"] is not None]
print("\nrag gold_recall mean:", round(sum(rg)/len(rg), 4), "n_with_gold:", len(rg))
hit = sum(1 for v in rg if v > 0)
print("recall>0 ratio:", round(hit/len(rg), 4))

fails = [r for r in rows if r["cond"] == "rag" and not r["ok"]]
refused = [r for r in fails if "insufficient" in r["pred"].lower()]
hit_refused = [r for r in fails if r["gold_recall"] and r["gold_recall"] > 0 and "insufficient" in r["pred"].lower()]
hit_wrong = [r for r in fails if r["gold_recall"] and r["gold_recall"] > 0 and "insufficient" not in r["pred"].lower()]
print("\nrag failures:", len(fails))
print("refused:", len(refused), round(len(refused)/len(fails), 4))
print("retrieval-hit but refused:", len(hit_refused), round(len(hit_refused)/len(fails), 4))
print("retrieval-hit wrong-answer (non-refusal):", len(hit_wrong), round(len(hit_wrong)/len(fails), 4))

mt = os.path.getmtime(files[0])
print("\nlast write:", datetime.datetime.fromtimestamp(mt))
