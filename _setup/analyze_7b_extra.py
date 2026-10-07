# -*- coding: utf-8 -*-
"""Supplementary mechanism + cost breakdown for the 3B vs 7B report.
Adds: completion-token verbosity from run logs, answer-precision (given it answered),
per-qtype refusal rates, correct-answers-by-recall-bucket, loose-3B cost of pass,
and the residual gap to MemTier 0.382.  Read-only."""
import sys; sys.stdout.reconfigure(encoding="utf-8")
import json, os, re, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "eval", "results")
LIT = re.compile(r"insufficient", re.I)
RUNS = {"3B-strict": "smoke_20261003_191205.jsonl",
        "7B-strict": "smoke_20261003_225222.jsonl",
        "3B-loose": "smoke_20261004_020225.jsonl"}
LOGS = {"3B-strict": "lme_full.log", "7B-strict": "lme_7b.log", "3B-loose": "lme_loose.log"}
RS_ = 492  # 7B rows appended by resume7b.py (contended latency)


def load(fn):
    rows = [json.loads(l) for l in open(os.path.join(RES, fn), encoding="utf-8") if l.strip()]
    d = {}
    for r in rows:
        d[(r["cond"], r["qid"])] = r
    return list(d.values())


def comp_tokens(logname):
    out = {"rag": [], "none": []}
    p = os.path.join(ROOT, "_setup", logname)
    for line in open(p, encoding="utf-8", errors="replace"):
        m = re.match(r"\[\d+\]\[(rag|none)\s*\].*tok=(\d+)\+(\d+)", line)
        if m:
            out[m.group(1)].append(int(m.group(3)))
    return {k: (sum(v) / len(v), len(v)) for k, v in out.items()}


print("== completion tokens (parsed from run logs, prompt+completion) ==")
for k, lg in LOGS.items():
    c = comp_tokens(lg)
    print("  %-9s rag=%.1f (n=%d)  none=%.1f (n=%d)" % (k, c["rag"][0], c["rag"][1], c["none"][0], c["none"][1]))

print("\n== behaviour given retrieval hit (rag, questions with gold_recall>0) ==")
for k, fn in RUNS.items():
    rag = [r for r in load(fn) if r["cond"] == "rag"]
    hit = [r for r in rag if r["gold_recall"] and r["gold_recall"] > 0]
    ans = [r for r in hit if not LIT.search(r["pred"])]
    ref = [r for r in hit if LIT.search(r["pred"])]
    ok_hit = sum(1 for r in hit if r["ok"])
    ok_miss = sum(1 for r in rag if not (r["gold_recall"] and r["gold_recall"] > 0) and r["ok"])
    print("  %-9s hit=%d refused=%d(%.3f) answered=%d correct_among_answered=%d(%.3f)"
          % (k, len(hit), len(ref), len(ref) / len(hit), len(ans),
             sum(1 for r in ans if r["ok"]), sum(1 for r in ans if r["ok"]) / max(1, len(ans))))
    print("            correct total=%d (from hit=%d, from recall==0/None=%d)"
          % (sum(1 for r in rag if r["ok"]), ok_hit, ok_miss))

print("\n== per-qtype literal-refusal rate among hit questions (rag) ==")
hdr = sorted({r["qtype"] for r in load(RUNS["3B-strict"]) if r["cond"] == "rag"})
print("  %-28s %-16s %-16s %-16s" % ("qtype", "3B refuse/answer-prec", "7B refuse/answer-prec", "loose3B refuse/prec"))
tab = {}
for k, fn in RUNS.items():
    for r in [x for x in load(fn) if x["cond"] == "rag"]:
        if not (r["gold_recall"] and r["gold_recall"] > 0):
            continue
        d = tab.setdefault(k, {}).setdefault(r["qtype"], [0, 0, 0])
        d[0] += 1
        d[1] += 1 if LIT.search(r["pred"]) else 0
        if not LIT.search(r["pred"]):
            d[2] += 1 if r["ok"] else 0
for q in hdr:
    cells = []
    for k in RUNS:
        n, rf, cw = tab[k].get(q, [0, 0, 0])
        ans = n - rf
        cells.append("%3d/%3d=%.2f prec=%.2f" % (rf, n, rf / n if n else 0, cw / ans if ans else 0))
    print("  %-28s %s | %s | %s" % (q, *cells))

print("\n== cost of pass (rag condition) ==")
for k, fn in RUNS.items():
    rag = [r for r in load(fn) if r["cond"] == "rag"]
    acc = sum(r["ok"] for r in rag) / len(rag)
    tok = sum(r["tokens"] for r in rag) / len(rag)
    clean = [r["latency_s"] for r in rag if r["idx"] < RS_]
    lat = sum(clean) / len(clean)
    med = statistics.median(clean)
    print("  %-9s acc=%.4f tok/q=%.1f -> %.0f tok/correct | lat(idx<%d) mean=%.2f med=%.2f -> %.0fs/correct (%.1f min)"
          % (k, acc, tok, tok / acc, RS_, lat, med, lat / acc, lat / acc / 60))

print("\n== residual gap to MemTier 0.382 ==")
MEMTIER = 0.382
for k, fn in RUNS.items():
    rag = [r for r in load(fn) if r["cond"] == "rag"]
    acc = sum(r["ok"] for r in rag) / len(rag)
    print("  %-9s acc=%.4f gap=%.4f (%.1f%% of 0.382 recovered) | recoverable if all hit-refusals turned correct: acc -> %.4f"
          % (k, acc, MEMTIER - acc, 100 * acc / MEMTIER,
             (sum(1 for r in rag if r["ok"]) + sum(1 for r in rag
              if r["gold_recall"] and r["gold_recall"] > 0 and LIT.search(r["pred"]))) / len(rag)))
# ceiling: non-refusal on hit questions already answered + all hit questions
for k, fn in RUNS.items():
    rag = [r for r in load(fn) if r["cond"] == "rag"]
    hit = [r for r in rag if r["gold_recall"] and r["gold_recall"] > 0]
    print("  %-9s upper bound if retrieval fixed to 100%% hit & refusals removed: n_answered_correct + (500-%d hit-refused)"
          % (k, sum(1 for r in hit if LIT.search(r["pred"]))))
