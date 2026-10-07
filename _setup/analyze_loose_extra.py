# -*- coding: utf-8 -*-
"""Supplementary checks for the loose-prompt run: semantic-refusal detection,
completion-token verbosity from the run logs, and lucky-guess sampling."""
import sys; sys.stdout.reconfigure(encoding="utf-8")
import json, os, re, random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "eval", "results")
FILES = {
    "strict-3B": ("smoke_20261003_191205.jsonl", "lme_full.log"),
    "loose-3B": ("smoke_20261004_020225.jsonl", "lme_loose.log"),
    "7B-strict": ("smoke_20261003_225222.jsonl", "lme_7b.log"),
}
LIT = re.compile(r"insufficient", re.I)
ANY = re.compile(r"(insufficient|not contain|don'?t have|do not have|no information|"
                 r"not mention|not specified|not provide|cannot determine|not available|"
                 r"unable to (determin|find|answer)|no mention)", re.I)


def load(f):
    rows = [json.loads(l) for l in open(os.path.join(RES, f), encoding="utf-8") if l.strip()]
    latest = {}
    for r in rows:
        latest[(r["cond"], r["qid"])] = r
    return list(latest.values())


def comp_tokens(logpath):
    """Parse 'tok=prompt+completion' per condition from the run log."""
    out = {"rag": [], "none": []}
    for line in open(logpath, encoding="utf-8", errors="replace"):
        m = re.match(r"\[\d+\]\[(rag|none)\s*\].*tok=(\d+)\+(\d+)", line)
        if m:
            out[m.group(1).strip()].append(int(m.group(3)))
    return {k: (sum(v) / len(v) if v else 0, len(v)) for k, v in out.items()}


for name, (jf, lf) in FILES.items():
    rows = load(jf)
    for cond in ("rag", "none"):
        rs = [r for r in rows if r["cond"] == cond]
        n = len(rs)
        lit = sum(1 for r in rs if LIT.search(r["pred"]))
        any_ = sum(1 for r in rs if ANY.search(r["pred"]))
        fails = [r for r in rs if not r["ok"]]
        fany = sum(1 for r in fails if ANY.search(r["pred"]))
        okrow = [r for r in rs if r["ok"]]
        okev = [r for r in okrow if ANY.search(r["pred"])]
        print("%-10s %-4s n=%-4d literal=%-4d(%.3f) evasive_all=%-4d(%.3f) evasive_of_fail=%-4d/%-4d(%.3f)"
              % (name, cond, n, lit, lit / n, any_, any_ / n, fany, len(fails),
                 fany / max(1, len(fails))))
        print("           judged-correct=%-4d(%.3f)  of which evasive=%-3d -> suspicious FPs; "
              "conservative acc (correct AND not evasive)=%.4f"
              % (len(okrow), len(okrow) / n, len(okev), len(okrow) / n - len(okev) / n))
        for r in okev[:2]:
            print("             e.g. [%s] gold=%s | pred=%s" % (r["qtype"], r["gold"][:45], r["pred"][:75]))
    lp = os.path.join(ROOT, "_setup", lf)
    if os.path.exists(lp):
        ct = comp_tokens(lp)
        print("   completion tokens mean: rag=%.1f (n=%d)  none=%.1f (n=%d)"
              % (ct["rag"][0], ct["rag"][1], ct["none"][0], ct["none"][1]))
    print()

rows = load(FILES["loose-3B"][0])
random.seed(7)
lucky = [r for r in rows if r["cond"] == "none" and r["ok"]]
print("loose-3B none-condition correct WITH NO CONTEXT (pure guesses): %d / %d"
      % (len(lucky), len([r for r in rows if r["cond"] == "none"])))
for r in random.sample(lucky, min(5, len(lucky))):
    print("  qid=%s [%s] gold=%s | pred=%s" % (r["qid"], r["qtype"], r["gold"][:60], r["pred"][:90]))
