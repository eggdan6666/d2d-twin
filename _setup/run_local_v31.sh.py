# -*- coding: utf-8 -*-
import subprocess, sys, os, time
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
RUNS = [
    ("rag3b", [sys.executable, "eval/qa100/run.py", "--model", "qwen2.5:3b-instruct",
               "--tag", "v31_rag3b"]),
    ("rag7b", [sys.executable, "eval/qa100/run.py", "--model", "qwen2.5:7b-instruct-q4_K_M",
               "--tag", "v31_rag7b"]),
]
for name, cmd in RUNS:
    t0 = time.time()
    with open(f"_setup/v31_local_{name}.log", "w", encoding="utf-8") as lg:
        rc = subprocess.run(cmd, stdout=lg, stderr=subprocess.STDOUT).returncode
    print(f"{name}: rc={rc} {round((time.time()-t0)/60,1)}min", flush=True)
print("LOCAL_V31_DONE", flush=True)
