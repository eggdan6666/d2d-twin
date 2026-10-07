# -*- coding: utf-8 -*-
"""3B vs 7B (both strict prompt) comparison on LongMemEval-S.

口径 copied from _setup/analyze_full.py (+ LIT/ANY regexes from
_setup/analyze_loose_extra.py). Read-only: loads result jsonl + run logs only.
"""
import sys; sys.stdout.reconfigure(encoding="utf-8")
import json, os, re, math, statistics
from collections import defaultdict
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "eval", "results")
RUNS = {
    "3B": "smoke_20261003_191205.jsonl",
    "7B": "smoke_20261003_225222.jsonl",
}
LIT = re.compile(r"insufficient", re.I)
ANY = re.compile(r"(insufficient|not contain|don'?t have|do not have|no information|"
                 r"not mention|not specified|not provide|cannot determine|not available|"
                 r"unable to (determin|find|answer)|no mention)", re.I)
RESUME_START = 492          # idx>=492 appended by _setup/resume7b.py (contended window)


def load(fn):
    rows = [json.loads(l) for l in open(os.path.join(RES, fn), encoding="utf-8") if l.strip()]
    latest = {}
    for r in rows:
        latest[(r["cond"], r["qid"])] = r
    return list(latest.values()), len(rows)


def pct(a, b):
    return "%.4f (%d/%d)" % (a / b, a, b) if b else "n/a"


data = {}
for name, fn in RUNS.items():
    rows, raw = load(fn)
    rag = [r for r in rows if r["cond"] == "rag"]
    non = [r for r in rows if r["cond"] == "none"]
    rag.sort(key=lambda r: r["idx"]); non.sort(key=lambda r: r["idx"])
    data[name] = {"rows": rows, "rag": rag, "none": non, "raw": raw}
    print("=" * 78)
    print("%s  file=%s  raw_lines=%d  unique(cond,qid)=%d  rag=%d none=%d"
          % (name, fn, raw, len(rows), len(rag), len(non)))

    # --- overall ---
    for cond, rs in (("rag", rag), ("none", non)):
        okc = sum(r["ok"] for r in rs)
        lat = [r["latency_s"] for r in rs]
        latc = [r["latency_s"] for r in rs if r["idx"] < RESUME_START]
        print("  %-4s acc=%s | tok mean=%.1f | lat mean=%.2fs median=%.2fs"
              % (cond, pct(okc, len(rs)), sum(r["tokens"] for r in rs) / len(rs),
                 sum(lat) / len(lat), statistics.median(lat)), end="")
        print(" | excl.idx>=%d: mean=%.2fs median=%.2fs (n=%d)"
              % (RESUME_START, sum(latc) / len(latc), statistics.median(latc), len(latc)))

    # --- retrieval invariance (single-variable proof) ---
    gr = [r["gold_recall"] for r in rag if r["gold_recall"] is not None]
    print("  retrieval: gold_recall mean=%.4f (n_gold_annotated=%d)  recall>0=%s"
          % (sum(gr) / len(gr), len(gr), pct(sum(1 for v in gr if v > 0), len(gr))))

    # --- failure taxonomy, strict 口径 ---
    fails = [r for r in rag if not r["ok"]]
    lit = [r for r in fails if LIT.search(r["pred"])]
    hit = [r for r in fails if r["gold_recall"] and r["gold_recall"] > 0]
    hit_lit = [r for r in hit if LIT.search(r["pred"])]
    hit_wrong = [r for r in hit if not LIT.search(r["pred"])]
    nohit_lit = [r for r in lit if not (r["gold_recall"] and r["gold_recall"] > 0)]
    nohit = [r for r in fails if not (r["gold_recall"] and r["gold_recall"] > 0)]
    print("  failures=%d (%s of 500)" % (len(fails), pct(len(fails), len(rag))))
    print("    literal-refuse            %s of failures | %.4f of all rag"
          % (pct(len(lit), len(fails)), len(lit) / len(rag)))
    print("    HIT-but-refused           %s of failures | %.4f of all rag"
          % (pct(len(hit_lit), len(fails)), len(hit_lit) / len(rag)))
    print("    HIT-but-wrong(answered)   %s of failures | %.4f of all rag"
          % (pct(len(hit_wrong), len(fails)), len(hit_wrong) / len(rag)))
    print("    MISS(no gold in ctx)      %s of failures | %.4f of all rag"
          % (pct(len(nohit), len(fails)), len(nohit) / len(rag)))
    print("      (miss & refused %d, miss & answered %d)" % (len(nohit_lit), len(nohit) - len(nohit_lit)))
    # wide 口径 for reference
    wide = [r for r in fails if ANY.search(r["pred"])]
    okrows = [r for r in rag if r["ok"]]
    okev = [r for r in okrows if ANY.search(r["pred"])]
    print("    [wide] evasive of failures %s ; judged-correct but evasive=%d -> conservative acc=%.4f"
          % (pct(len(wide), len(fails)), len(okev), (len(okrows) - len(okev)) / len(rag)))
    print("    none-condition literal-refuse=%s evasive=%s"
          % (pct(sum(1 for r in non if LIT.search(r["pred"])), len(non)),
             pct(sum(1 for r in non if ANY.search(r["pred"])), len(non))))

    # --- per qtype --- (recollected in qtsum below)

# recompute qtype cleanly
qtsum = {}
for name in RUNS:
    d = {}
    for cond in ("rag", "none"):
        for r in data[name][cond]:
            d.setdefault(r["qtype"], {"rag": [], "none": []})[cond].append(r)
    qtsum[name] = {k: {c: (sum(r["ok"] for r in v[c]) / len(v[c]), len(v[c])) for c in ("rag", "none")}
                   for k, v in d.items()}
    rc = {}
    for r in data[name]["rag"]:
        if r["gold_recall"] is not None:
            rc.setdefault(r["qtype"], []).append(r["gold_recall"])
    qtsum[name]["__recall__"] = {k: sum(v) / len(v) for k, v in rc.items()}

print("\n" + "=" * 78)
print("PER-QTYPE (rag acc | none acc | gold_recall mean)")
print("%-28s %4s | %-18s | %-18s | delta" % ("qtype", "n", "3B rag/none", "7B rag/none"))
for q in sorted((k for k in qtsum["3B"] if k != "__recall__"),
              key=lambda k: -qtsum["3B"][k]["rag"][1]):
    a, b = qtsum["3B"][q], qtsum["7B"][q]
    print("%-28s %4d | %.3f / %.3f  r=%.3f | %.3f / %.3f  r=%.3f | %+.3f"
          % (q, a["rag"][1], a["rag"][0], a["none"][0], qtsum["3B"]["__recall__"][q],
             b["rag"][0], b["none"][0], qtsum["7B"]["__recall__"][q], b["rag"][0] - a["rag"][0]))

# --- paired per-question flips: 3B -> 7B ---
print("\n" + "=" * 78)
print("PAIRED 3B -> 7B (same qid, same retrieval, strict prompt both sides)")
idx3 = {(r["cond"], r["qid"]): r for r in data["3B"]["rows"]}
idx7 = {(r["cond"], r["qid"]): r for r in data["7B"]["rows"]}
common = sorted(set(idx3) & set(idx7))
print("matched (cond,qid) pairs: %d" % len(common))
for cond in ("rag", "none"):
    keys = [k for k in common if k[0] == cond]
    gain = [idx3[k] for k in keys if not idx3[k]["ok"] and idx7[k]["ok"]]
    loss = [idx3[k] for k in keys if idx3[k]["ok"] and not idx7[k]["ok"]]
    both = sum(1 for k in keys if idx3[k]["ok"] and idx7[k]["ok"])
    neither = sum(1 for k in keys if not idx3[k]["ok"] and not idx7[k]["ok"])
    b, c = len(gain), len(loss)
    p = stats.binomtest(b, b + c, 0.5).pvalue if b + c else 1.0
    print("  %-4s both=%d gain(3B错->7B对)=%d loss(3B对->7B错)=%d neither=%d | McNemar exact p=%.4f"
          % (cond, both, b, c, neither, p))
    bg = defaultdict(lambda: [0, 0])
    for r in gain:
        bg[r["qtype"]][0] += 1
    for r in loss:
        bg[r["qtype"]][1] += 1
    for q in sorted(bg, key=lambda k: -(bg[k][0] - bg[k][1])):
        print("       %-28s +%d / -%d  net=%+d" % (q, bg[q][0], bg[q][1], bg[q][0] - bg[q][1]))

# --- hypothesis test: does refusal-with-hit shrink with scale? ---
print("\n" + "=" * 78)
print("HYPOTHESIS: 命中后拒答随规模下降?")
tab = {}
for name in RUNS:
    rag = data[name]["rag"]
    hitrows = [r for r in rag if r["gold_recall"] and r["gold_recall"] > 0]
    lit = [r for r in rag if LIT.search(r["pred"])]
    tab[name] = {"hit_all": len(hitrows),
                 "hit_lit": sum(1 for r in hitrows if LIT.search(r["pred"])),
                 "fail": [r for r in rag if not r["ok"]]}
for name in RUNS:
    t = tab[name]
    print("  %s: 命中题 %d 中字面拒答 %d (%.4f) | 失败 %d 中命中后拒答 %d (%.4f)"
          % (name, t["hit_all"], t["hit_lit"], t["hit_lit"] / t["hit_all"], len(t["fail"]),
             sum(1 for r in t["fail"] if LIT.search(r["pred"]) and r["gold_recall"] > 0),
             sum(1 for r in t["fail"] if LIT.search(r["pred"]) and r["gold_recall"] > 0) / len(t["fail"])))
# paired McNemar on literal-refusal flag over rag rows with recall>0
k3 = {r["qid"]: r for r in data["3B"]["rag"]}
k7 = {r["qid"]: r for r in data["7B"]["rag"]}
hk = [q for q in k3 if q in k7 and k3[q]["gold_recall"] > 0 and k7[q]["gold_recall"] > 0]
b = sum(1 for q in hk if LIT.search(k7[q]["pred"]) and not LIT.search(k3[q]["pred"]))
c = sum(1 for q in hk if not LIT.search(k7[q]["pred"]) and LIT.search(k3[q]["pred"]))
print("  paired on hit-rag qids (n=%d): 3B拒/7B答=%d , 3B答/7B拒=%d -> McNemar exact p=%.4f"
      % (len(hk), c, b, stats.binomtest(c, b + c, 0.5).pvalue if b + c else 1.0))
# unpaired 2-prop z on hit-refusal among all rag questions
for nm, t in tab.items():
    pass
x3, n3 = tab["3B"]["hit_lit"], tab["3B"]["hit_all"]
x7, n7 = tab["7B"]["hit_lit"], tab["7B"]["hit_all"]
ct = [[x3, n3 - x3], [x7, n7 - x7]]
chi2, pf, _, _ = stats.chi2_contingency(ct, correction=False)
print("  命中题字面拒答率 3B %.4f vs 7B %.4f | chi2=%.2f p=%.4f (unpaired)"
      % (x3 / n3, x7 / n7, chi2, pf))
# accuracy difference test
o3 = sum(r["ok"] for r in data["3B"]["rag"]); o7 = sum(r["ok"] for r in data["7B"]["rag"])
print("  rag acc 3B %d/500=%.3f vs 7B %d/500=%.3f | chi2 p=%.4f"
      % (o3, o3 / 500, o7, o7 / 500,
         stats.chi2_contingency([[o3, 500 - o3], [o7, 500 - o7]], correction=False)[1]))

# --- cost of pass ---
print("\n" + "=" * 78)
print("COST OF PASS")
for name in RUNS:
    for cond in ("rag", "none"):
        rs = data[name][cond]
        acc = sum(r["ok"] for r in rs) / len(rs)
        tok = sum(r["tokens"] for r in rs) / len(rs)
        lat = [r["latency_s"] for r in rs]
        latc = [r["latency_s"] for r in rs if r["idx"] < RESUME_START]
        med = statistics.median(latc)
        print("  %-3s %-4s acc=%.3f tok/q=%.0f  tok-per-correct=%.0f  "
              "sec/q mean=%.1f median=%.1f  sec-per-correct(median)=%.0f (%.1f min)"
              % (name, cond, acc, tok, tok / acc if acc else float("nan"),
                 sum(lat) / len(lat), med,
                 med / acc if acc else float("nan"),
                 med / acc / 60 if acc else float("nan")))

# --- latency contamination timeline reconstruction ---
print("\n" + "=" * 78)
print("LATENCY CONTAMINATION (7B): reconstructed per-row wall time")
import datetime
t0 = datetime.datetime(2026, 10, 3, 22, 52, 22)
rag7 = data["7B"]["rag"]
tot_lat = sum(r["latency_s"] for r in data["7B"]["rows"])
wall_crash = (datetime.datetime(2026, 10, 4, 1, 33) - t0).total_seconds()
n_pre = sum(1 for r in data["7B"]["rows"] if r["idx"] < RESUME_START)
scale = wall_crash / sum(r["latency_s"] for r in data["7B"]["rows"] if r["idx"] < RESUME_START)
print("  rows idx<492: n=%d, sum(latency)=%.0fs, real window=%.0fs -> wall/lat factor %.3f"
      % (n_pre, wall_crash / scale, wall_crash, scale))
cum = 0.0
abl = datetime.datetime(2026, 10, 3, 23, 56)
abl_end = datetime.datetime(2026, 10, 4, 0, 3)
in_abl = []
for r in sorted(data["7B"]["rows"], key=lambda r: (r["idx"], r["cond"])):
    est = t0 + datetime.timedelta(seconds=cum * scale)
    cum += r["latency_s"]
    if r["idx"] < RESUME_START and abl <= est <= abl_end:
        in_abl.append(r)
print("  rows whose reconstructed time falls in ablation window 23:56-00:03: n=%d" % len(in_abl))
for cond in ("rag", "none"):
    sub = [r for r in in_abl if r["cond"] == cond]
    if sub:
        print("     %s in-window lat mean=%.2fs (n=%d)" % (cond, sum(r["latency_s"] for r in sub) / len(sub), len(sub)))
    sub_keys = {(r["idx"], r["cond"]) for r in in_abl if r["cond"] == cond}
    rs = [r for r in data["7B"][cond] if r["idx"] < RESUME_START]
    ex = [r for r in rs if (r["idx"], "rag" if cond == "rag" else "none") not in sub_keys]
    print("     %s all(idx<492) mean=%.2fs | minus ablation window mean=%.2fs (n=%d)"
          % (cond, sum(r["latency_s"] for r in rs) / len(rs),
             sum(r["latency_s"] for r in ex) / len(ex), len(ex)))
