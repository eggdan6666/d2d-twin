# -*- coding: utf-8 -*-
"""收官链: k-trial(3B×3seeds, 7B-loose×3seeds, temp0.7) → v4全量(7B-loose) → 打包."""
import subprocess, sys, os, time
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
PY = sys.executable
# k-trial 必须锁 v3(120题)：run.py 不给 --ds 时会自动取最新数据集，v4 落地后它就变成 150 题了
V3 = ["--ds", "eval/qa100/datasheet_qa100_v3.json"]
R3 = ["eval/qa100/run.py", "--model", "qwen2.5:3b-instruct", "--temperature", "0.7"] + V3
R7 = ["eval/qa100/run.py", "--model", "qwen2.5:7b-instruct-q4_K_M", "--loose",
      "--temperature", "0.7"] + V3
RUNS = [(f"kt3b_s{s}", R3 + ["--seed", str(s), "--tag", f"kt_rag3b_s{s}"]) for s in (1, 2, 3)]
RUNS += [(f"kt7b_s{s}", R7 + ["--seed", str(s), "--tag", f"kt_rag7b_s{s}"]) for s in (1, 2, 3)]
RUNS += [("v4_7bloose", ["eval/qa100/run.py", "--model", "qwen2.5:7b-instruct-q4_K_M",
                         "--loose", "--ds", "eval/qa100/datasheet_qa100_v4.json",
                         "--tag", "v4_rag7b_loose"])]
for name, cmd in RUNS:
    t0 = time.time()
    with open(f"_setup/final_{name}.log", "w", encoding="utf-8") as lg:
        rc = subprocess.run([PY] + cmd, stdout=lg, stderr=subprocess.STDOUT).returncode
    print(f"{name}: rc={rc} {round((time.time()-t0)/60,1)}min", flush=True)
subprocess.run([PY, "_setup/package.py"], stdout=open("_setup/final_package.log", "w",
               encoding="utf-8"), stderr=subprocess.STDOUT)
print("FINAL_CHAIN_DONE", flush=True)
