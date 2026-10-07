# -*- coding: utf-8 -*-
"""补跑 7B 全量中缺失的 (idx,cond) 行，追加回原结果文件。"""
import sys, os, json, time, importlib.util
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
spec = importlib.util.spec_from_file_location("rl", os.path.join(ROOT, "eval", "run_longmemeval.py"))
rl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rl)
from rag import llm

RES = "eval/results/smoke_20261003_225222.jsonl"
MODEL = "qwen2.5:7b-instruct-q4_K_M"
data = json.load(open("data/eval/longmemeval_s.json", encoding="utf-8"))
have = set()
lines = open(RES, encoding="utf-8").read().splitlines()
for l in lines:
    if l.strip():
        r = json.loads(l)
        have.add((r["idx"], r["cond"]))
missing = [(i, c) for i in range(len(data)) for c in ("rag", "none") if (i, c) not in have]
print("missing:", len(missing))
f = open(RES, "a", encoding="utf-8")
for idx, cond in missing:
    item = data[idx]
    ctx, retrieved, golds = rl.build_context(item, 3)
    if cond == "rag":
        prompt = (f"Conversation excerpts:\n{ctx}\n\n"
                  f"Question ({item['question_date']}): {item['question']}")
    else:
        prompt = f"Question ({item['question_date']}): {item['question']}"
    for attempt in range(4):
        try:
            r = llm.chat(prompt, model=MODEL, system=rl.SYS, timeout=900)
            break
        except Exception as e:
            print("retry", idx, cond, type(e).__name__, str(e)[:60]); time.sleep(30)
    else:
        print("GIVE UP", idx, cond); continue
    ok = rl.correct(item["answer"], r["text"])
    recall = (len(set(retrieved) & golds) / len(golds)) if golds else None
    f.write(json.dumps({"idx": idx, "cond": cond, "qid": item["question_id"],
                        "qtype": item["question_type"], "ok": ok,
                        "gold": str(item["answer"])[:120], "pred": r["text"][:120],
                        "gold_recall": recall,
                        "tokens": r["prompt_tokens"] + r["completion_tokens"],
                        "latency_s": r["latency_s"]}, ensure_ascii=False) + "\n")
    f.flush()
    print(f"[{idx:03d}][{cond}] ok={ok} {r['latency_s']}s")
f.close()
print("done, total lines:", len(open(RES, encoding='utf-8').readlines()))
