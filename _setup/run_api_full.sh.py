# -*- coding: utf-8 -*-
import subprocess, sys, os, time
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
M = "scnet:DeepSeek-V4.1-Flash-Event"
RUNS = [
    ("api_bare", [sys.executable, "eval/qa100/run.py", "--bare", "--model", M, "--tag", "v31_api_bare"]),
    ("api_rag",  [sys.executable, "eval/qa100/run.py", "--model", M, "--tag", "v31_api_rag"]),
]
for name, cmd in RUNS:
    t0 = time.time()
    with open(f"_setup/v31_{name}.log", "w", encoding="utf-8") as lg:
        rc = subprocess.run(cmd, stdout=lg, stderr=subprocess.STDOUT).returncode
    print(f"{name}: rc={rc} {round((time.time()-t0)/60,1)}min", flush=True)
print("API_FULL_DONE", flush=True)
