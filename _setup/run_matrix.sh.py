# -*- coding: utf-8 -*-
"""v3 官方矩阵驱动: 5 配置顺序跑 + 汇总。"""
import subprocess, sys, os, time, json, glob
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
BASE = [sys.executable, "eval/qa100/run.py"]
MODELS = {"3b": "qwen2.5:3b-instruct", "7b": "qwen2.5:7b-instruct-q4_K_M"}
RUNS = [
    ("bare3b",      BASE + ["--bare", "--model", MODELS["3b"], "--tag", "m_bare3b"]),
    ("rag3b",       BASE + ["--perdoc", "--model", MODELS["3b"], "--tag", "m_rag3b"]),
    ("rag3b_loose", BASE + ["--perdoc", "--loose", "--model", MODELS["3b"], "--tag", "m_rag3b_loose"]),
    ("rag7b",       BASE + ["--perdoc", "--model", MODELS["7b"], "--tag", "m_rag7b"]),
    ("rag7b_loose", BASE + ["--perdoc", "--loose", "--model", MODELS["7b"], "--tag", "m_rag7b_loose"]),
]
logdir = "_setup"
for name, cmd in RUNS:
    t0 = time.time()
    with open(f"{logdir}/matrix_{name}.log", "w", encoding="utf-8") as lg:
        rc = subprocess.run(cmd, stdout=lg, stderr=subprocess.STDOUT).returncode
    print(f"{name}: rc={rc} {round((time.time()-t0)/60,1)}min", flush=True)

# 汇总
import re
sys.path.insert(0, "eval/qa100")
from score2 import correct
summary = {}
for name, _ in RUNS:
    p = f"eval/qa100/results_m_{name}.json"
    if not os.path.exists(p):
        summary[name] = None
        continue
    d = json.load(open(p, encoding="utf-8"))
    tot = sum(correct(x["gold"], x["pred"]) for x in d)
    by = {}
    for x in d:
        a = by.setdefault(x["type"], [0, 0])
        a[0] += correct(x["gold"], x["pred"]); a[1] += 1
    tok = sum(x["tokens"] for x in d) / len(d)
    lat = sum(x["latency_s"] for x in d) / len(d)
    summary[name] = {"acc": round(tot/len(d), 4), "n": len(d),
                     "by_type": {k: [v[0], v[1]] for k, v in by.items()},
                     "avg_tokens": round(tok), "avg_latency_s": round(lat, 1)}
    print(name, json.dumps(summary[name], ensure_ascii=False), flush=True)
json.dump(summary, open("eval/qa100/matrix_summary.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("MATRIX_DONE", flush=True)
