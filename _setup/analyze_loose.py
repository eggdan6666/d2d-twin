# -*- coding: utf-8 -*-
"""Loose-prompt experiment analysis. Copy of _setup/analyze_full.py logic (unchanged
scoring conventions) extended to compare several runs. Read-only over eval/results."""
import sys; sys.stdout.reconfigure(encoding="utf-8")
import json, os, glob, datetime, random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "eval", "results")
START_EPOCH = int(open(os.path.join(ROOT, "_setup", "loose_start.txt")).read().strip())

RUNS = {
    "strict-3B": "smoke_20261003_191205.jsonl",
    "7B-strict": "smoke_20261003_225222.jsonl",
}


def find_loose_file():
    cands = []
    for f in glob.glob(os.path.join(RES, "smoke_2026*.jsonl")):
        mt = os.path.getmtime(f)
        base = os.path.basename(f)
        if base in RUNS.values():
            continue
        if mt >= START_EPOCH and base.startswith("smoke_20261004"):
            cands.append((mt, base))
    if not cands:
        return None
    return sorted(cands)[-1][1]


def load(fname):
    path = os.path.join(RES, fname)
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    latest = {}
    for r in rows:
        latest[(r["cond"], r["qid"])] = r
    return path, list(latest.values())


def agg(rs):
    n = len(rs) or 1
    return {
        "n": len(rs),
        "acc": sum(r["ok"] for r in rs) / n,
        "tok": sum(r["tokens"] for r in rs) / n,
        "lat": sum(r["latency_s"] for r in rs) / n,
    }


def refuse(r):
    return "insufficient" in r["pred"].lower()


def describe(name, rows, verbose=True):
    print("\n" + "=" * 60)
    if not rows:
        print("%s  rows=0 (file not flushed yet)" % name)
        return []
    print("%s  rows=%d unique_qids=%d" % (name, len(rows), len({r["qid"] for r in rows})))
    idxs = {r["idx"] for r in rows}
    print("idx range: %d..%d (%d items)" % (min(idxs), max(idxs), len(idxs)))
    for cond in ("rag", "none"):
        s = agg([r for r in rows if r["cond"] == cond])
        print("%-5s n=%-4d acc=%.4f  avg_tokens=%.1f  avg_latency=%.2fs"
              % (cond, s["n"], s["acc"], s["tok"], s["lat"]))
    print("\nqtype, n, rag_acc, none_acc")
    for q in sorted({r["qtype"] for r in rows}):
        sub = {c: [r for r in rows if r["cond"] == c and r["qtype"] == q] for c in ("rag", "none")}
        print("  %-26s %-4d %.3f %.3f" % (q, len(sub["rag"]),
              sum(r["ok"] for r in sub["rag"]) / max(1, len(sub["rag"])),
              sum(r["ok"] for r in sub["none"]) / max(1, len(sub["none"]))))
    rg = [r["gold_recall"] for r in rows if r["cond"] == "rag" and r["gold_recall"] is not None]
    if rg:
        print("\nrag gold_recall mean=%.4f  recall>0 ratio=%.4f (n=%d)"
              % (sum(rg) / len(rg), sum(1 for v in rg if v > 0) / len(rg), len(rg)))
    rag_all = [r for r in rows if r["cond"] == "rag"]
    if rag_all:
        print("\nrag rows refusing (INSUFFICIENT) anywhere: %d / %d = %.4f"
              % (sum(1 for r in rag_all if refuse(r)), len(rag_all),
                 sum(1 for r in rag_all if refuse(r)) / len(rag_all)))
    fails = [r for r in rows if r["cond"] == "rag" and not r["ok"]]
    if fails and verbose:
        f = len(fails)
        ref = [r for r in fails if refuse(r)]
        hr = [r for r in fails if r["gold_recall"] and r["gold_recall"] > 0 and refuse(r)]
        hw = [r for r in fails if r["gold_recall"] and r["gold_recall"] > 0 and not refuse(r)]
        miss = [r for r in fails if not r["gold_recall"] or r["gold_recall"] == 0]
        print("\nrag failures=%d" % f)
        print("  refused (INSUFFICIENT)          %4d  %.4f" % (len(ref), len(ref) / f))
        print("  retrieval-hit but refused       %4d  %.4f" % (len(hr), len(hr) / f))
        print("  retrieval-hit wrong (non-refuse)%4d  %.4f" % (len(hw), len(hw) / f))
        print("  retrieval miss                  %4d  %.4f" % (len(miss), len(miss) / f))
        return hw
    return []


def paired(a_rows, b_rows, la, lb):
    """Paired per-qid flips between two runs on the rag condition."""
    A = {r["qid"]: r for r in a_rows if r["cond"] == "rag"}
    B = {r["qid"]: r for r in b_rows if r["cond"] == "rag"}
    ks = sorted(set(A) & set(B))
    w = sum(1 for k in ks if B[k]["ok"] and not A[k]["ok"])
    l = sum(1 for k in ks if A[k]["ok"] and not B[k]["ok"])
    print("\npaired rag comparison %s -> %s over %d common qids: gained %d, lost %d, net %+d (%.4f -> %.4f)"
          % (la, lb, len(ks), w, l, w - l,
             sum(A[k]["ok"] for k in ks) / len(ks), sum(B[k]["ok"] for k in ks) / len(ks)))
    print("  per-qtype net flips:")
    for q in sorted({A[k]["qtype"] for k in ks}):
        sub = [k for k in ks if A[k]["qtype"] == q]
        ww = sum(1 for k in sub if B[k]["ok"] and not A[k]["ok"])
        ll = sum(1 for k in sub if A[k]["ok"] and not B[k]["ok"])
        print("    %-26s n=%-4d gained=%-3d lost=%-3d net=%+d" % (q, len(sub), ww, ll, ww - ll))
    return ks


def main():
    loose = find_loose_file()
    if not loose:
        print("!! no loose result file newer than start epoch yet")
    data = {}
    for name, fname in RUNS.items():
        if os.path.exists(os.path.join(RES, fname)):
            data[name] = load(fname)[1]
    if loose:
        print("loose file:", loose, datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(RES, loose))))
        data["loose-3B"] = load(loose)[1]

    hw_by_run = {}
    for name in ("strict-3B", "loose-3B", "7B-strict"):
        if name in data:
            hw_by_run[name] = describe(name, data[name])

    common = None
    for name, rows in data.items():
        q = {r["qid"] for r in rows if r["cond"] == "rag"}
        if not q:
            continue
        common = q if common is None else (common & q)
    if common and len([1 for r in data.values() if r]) > 1:
        print("\n" + "=" * 60)
        print("common qid intersection across available runs: %d" % len(common))
        print("run, rag_acc_on_common, none_acc_on_common")
        for name, rows in data.items():
            if not rows:
                continue
            rc = [r for r in rows if r["cond"] == "rag" and r["qid"] in common]
            nc = [r for r in rows if r["cond"] == "none" and r["qid"] in common]
            print("  %-11s %.4f (%d)   %.4f (%d)"
                  % (name, agg(rc)["acc"], len(rc), agg(nc)["acc"], len(nc)))

    if "strict-3B" in data and "loose-3B" in data and data["loose-3B"]:
        paired(data["strict-3B"], data["loose-3B"], "strict-3B", "loose-3B")
    if "strict-3B" in data and "7B-strict" in data:
        paired(data["strict-3B"], data["7B-strict"], "3B", "7B (both strict sys)")

    for name, hw in hw_by_run.items():
        if not hw:
            continue
        random.seed(42)
        samp = random.sample(hw, min(5, len(hw)))
        print("\n--- %s: 5 sampled hit-but-answered-wrong (non-refusal) rag preds ---" % name)
        for r in samp:
            print("  qid=%s [%s] recall=%.2f\n    gold: %s\n    pred: %s"
                  % (r["qid"], r["qtype"], r["gold_recall"] or 0.0, r["gold"], r["pred"]))


if __name__ == "__main__":
    main()
