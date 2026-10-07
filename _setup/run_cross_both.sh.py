# -*- coding: utf-8 -*-
import subprocess, sys, time, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
for model in ("qwen2.5:3b-instruct", "qwen2.5:7b-instruct-q4_K_M"):
    t0 = time.time()
    cmd = [sys.executable, "eval/qa100/run.py", "--only", "cross", "--perdoc",
           "--k", "3", "--model", model]
    log = open(f"_setup/cross_{model.split(':')[1]}.log", "w", encoding="utf-8")
    subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT)
    log.close()
    print(model, "done in", round((time.time()-t0)/60, 1), "min", flush=True)
print("ALL_DONE")
