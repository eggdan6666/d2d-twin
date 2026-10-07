# -*- coding: utf-8 -*-
import subprocess, sys, os, time
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
RUNS = [
    ("rag3b_loose", [sys.executable, "eval/qa100/run.py", "--loose", "--model",
                     "qwen2.5:3b-instruct", "--tag", "v31_rag3b_loose"]),
    ("rag7b_loose", [sys.executable, "eval/qa100/run.py", "--loose", "--model",
                     "qwen2.5:7b-instruct-q4_K_M", "--tag", "v31_rag7b_loose"]),
    ("variance", [sys.executable, "eval/qa100/variance_probe.py"]),
]
for name, cmd in RUNS:
    t0 = time.time()
    with open(f"_setup/night_{name}.log", "w", encoding="utf-8") as lg:
        rc = subprocess.run(cmd, stdout=lg, stderr=subprocess.STDOUT).returncode
    print(f"{name}: rc={rc} {round((time.time()-t0)/60,1)}min", flush=True)
print("NIGHT_RUNS_DONE", flush=True)
