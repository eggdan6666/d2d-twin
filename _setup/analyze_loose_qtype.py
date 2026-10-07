# -*- coding: utf-8 -*-
"""Per-qtype conservative accuracy (judged-correct minus evasive-judged-correct)
and the paired strict->loose losses."""
import sys; sys.stdout.reconfigure(encoding="utf-8")
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "eval", "results")
ANY = re.compile(r"(insufficient|not contain|don'?t have|do not have|no information|"
                 r"not mention|not specified|not provide|cannot determine|not available|"
                 r"unable to (determin|find|answer)|no mention|it is not clear|not stated|no record)", re.I)


def load(f):
    rows = [json.loads(l) for l in open(os.path.join(RES, f), encoding="utf-8") if l.strip()]
    latest = {}
    for r in rows:
        latest[(r["cond"], r["qid"])] = r
    return list(latest.values())


S = {r["qid"]: r for r in load("smoke_20261003_191205.jsonl") if r["cond"] == "rag"}
L = {r["qid"]: r for r in load("smoke_20261004_020225.jsonl") if r["cond"] == "rag"}
LN = {r["qid"]: r for r in load("smoke_20261004_020225.jsonl") if r["cond"] == "none"}

print("qtype                     n  strict  loose  loose_cons  none  none_cons")
for q in sorted({r["qtype"] for r in S.values()}):
    ks = [k for k in S if S[k]["qtype"] == q]
    sc = sum(S[k]["ok"] for k in ks) / len(ks)
    lc = sum(L[k]["ok"] for k in ks) / len(ks)
    lcons = sum(1 for k in ks if L[k]["ok"] and not ANY.search(L[k]["pred"])) / len(ks)
    nc = sum(LN[k]["ok"] for k in ks) / len(ks)
    ncons = sum(1 for k in ks if LN[k]["ok"] and not ANY.search(LN[k]["pred"])) / len(ks)
    print("%-25s %3d  %.3f   %.3f   %.3f        %.3f  %.3f" % (q, len(ks), sc, lc, lcons, nc, ncons))

print("\n--- strict-correct -> loose-wrong (all %d) ---"
      % sum(1 for k in S if S[k]["ok"] and not L[k]["ok"]))
for k in sorted(S):
    if S[k]["ok"] and not L[k]["ok"]:
        print("  [%s] gold=%s\n    strict pred: %s\n    loose  pred: %s"
              % (S[k]["qtype"], S[k]["gold"][:60], S[k]["pred"][:80], L[k]["pred"][:80]))
