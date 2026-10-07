# -*- coding: utf-8 -*-
"""守卫专用只读打分: 用 eval/qa100/score2.py 的 correct() 重判指定 tag 的 results_*.json。
不写任何 results2_*.json, 不覆盖既有文件。输出各 seed 的 param/cross/总分 acc + seed 间翻转统计。
用法: python _setup/guard_score.py kt_rag7b_s2 kt_rag7b_s3 ...
"""
import sys, os, json, math, statistics
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "eval", "qa100"))
from score2 import correct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TVAL = {2: 6.314, 3: 4.303}

def score(tag):
    p = os.path.join(ROOT, "eval", "qa100", f"results_{tag}.json")
    if not os.path.exists(p):
        return None
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception as e:
        print(f"{t:20s} PARSE_FAIL(busy/partial) {type(e).__name__}")
        return None
    by = {}
    per = {}
    for x in d:
        ok = bool(correct(x["gold"], x["pred"]))
        t = x["type"] if x["type"] in ("param", "cross") else "param"
        by.setdefault(t, [0, 0])
        by[t][0] += ok
        by[t][1] += 1
        per[x["qid"]] = ok
    n = len(d)
    tot = sum(1 for v in per.values() if v)
    return {"tag": tag, "path": os.path.relpath(p, ROOT).replace("\\", "/"), "n": n,
            "param": by.get("param", [0, 0]), "cross": by.get("cross", [0, 0]),
            "total": tot, "acc": tot / n if n else 0.0, "per": per,
            "stored_ok": sum(bool(x.get("ok")) for x in d), "mtime": None}

def flips(datasets):
    """多 seed 间逐题判分不一致。"""
    qids = sorted(set().union(*[set(x["per"]) for x in datasets]))
    allc = [q for q in qids if all(x["per"].get(q, False) for x in datasets)]
    allw = [q for q in qids if not any(x["per"].get(q, False) for x in datasets)]
    fl = [q for q in qids if q not in allc and q not in allw]
    pair = {}
    for i in range(len(datasets)):
        for j in range(i + 1, len(datasets)):
            a, b = datasets[i]["tag"], datasets[j]["tag"]
            pair[f"{a}↔{b}"] = sum(1 for q in qids if datasets[i]["per"].get(q) != datasets[j]["per"].get(q))
    return len(qids), len(allc), len(allw), fl, pair

def main():
    tags = sys.argv[1:]
    ds = []
    for t in tags:
        r = score(t)
        if r is None:
            print(f"{t:20s} MISSING")
            continue
        import time
        r["mtime"] = time.strftime("%m-%d %H:%M", time.localtime(
            os.path.getmtime(os.path.join(ROOT, "eval", "qa100", f"results_{t}.json"))))
        ds.append(r)
        print(f"{t:20s} n={r['n']:3d} total={r['total']:3d} acc={r['acc']:.1%} "
              f"param={r['param'][0]}/{r['param'][1]}({r['param'][0]/max(r['param'][1],1):.1%}) "
              f"cross={r['cross'][0]}/{r['cross'][1]}({r['cross'][0]/max(r['cross'][1],1):.1%}) "
              f"stored_ok={r['stored_ok']} mtime={r['mtime']}")
    if len(ds) >= 2:
        accs = [x["acc"] for x in ds]
        mean = statistics.mean(accs)
        std = statistics.stdev(accs) if len(accs) > 1 else 0.0
        nn = len(accs)
        half = TVAL.get(nn, 0.0) * std / math.sqrt(nn) if nn in TVAL else (
            statistics.stdev(accs) if nn > 1 else 0.0)
        print(f"\nmean={mean:.1%} std={std:.1%} n={nn} 95%CI=[{mean-half:.1%}, {mean+half:.1%}] "
              f"half={half:.1%} t={TVAL.get(nn)} range={max(accs)-min(accs):.1%}")
        for kind in ("param", "cross"):
            a = [x[kind][0] / x[kind][1] for x in ds if x[kind][1]]
            if a:
                m = statistics.mean(a)
                s = statistics.stdev(a) if len(a) > 1 else 0.0
                print(f"  {kind}: mean={m:.1%} std={s:.1%}")
        qn, ac, aw, fl, pair = flips(ds)
        print(f"  翻转: 题数={qn} 全对={ac} 全错={aw} 翻转={len(fl)}({len(fl)/qn:.1%}) pair={pair}")
        print("  翻转题: " + ", ".join(sorted(fl)))
        bytype = {}
        for x in ds:
            pass
        print("  分题型翻转: param=" + str(sum(1 for q in fl if q.startswith("P"))) +
              " cross=" + str(sum(1 for q in fl if q.startswith("C"))) +
              " X=" + str(sum(1 for q in fl if q.startswith("X"))))

if __name__ == "__main__":
    main()
