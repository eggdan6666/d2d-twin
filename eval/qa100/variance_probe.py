# -*- coding: utf-8 -*-
"""方差探针: 30 题(分层抽样) × 3 seeds × temp=0.7, RAG-3B v3.1 上下文。
报告每题准确率波动的均值±std, 回应计划书 k-trial 可复现协议。"""
import sys, os, json, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.stdout.reconfigure(encoding="utf-8")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
from rag import llm
from rag.hierarchical import HierarchicalRetriever
sys.path.insert(0, "eval/qa100")
from run import build_ctx, SYSTEM
from score2 import correct

ds = json.load(open("eval/qa100/datasheet_qa100_v3.json", encoding="utf-8"))
random.seed(42)
sample = (random.sample([q for q in ds if q["type"] == "param"], 21) +
          random.sample([q for q in ds if q["type"] == "cross"], 9))
retr = HierarchicalRetriever()
ctxs = [(q, build_ctx(retr, q, 5)[0]) for q in sample]
trials = {}
for seed in (1, 2, 3):
    hits = 0
    per = {}
    for q, ctx in ctxs:
        r = llm.chat(f"Datasheet excerpts:\n{ctx}\n\nQuestion: {q['question']}",
                     system=SYSTEM, temperature=0.7, seed=seed, timeout=600)
        ok = correct(q["gold"], r["text"])
        per[q["qid"]] = ok
        hits += ok
    trials[seed] = {"acc": hits / len(ctxs), "per": per}
    print(f"seed{seed}: acc={hits}/{len(ctxs)}={hits/len(ctxs):.3f}", flush=True)
accs = [t["acc"] for t in trials.values()]
mean = sum(accs) / len(accs)
std = (sum((a - mean) ** 2 for a in accs) / (len(accs) - 1)) ** 0.5
flip = sum(1 for q, _ in ctxs
           if len({trials[s]["per"][q["qid"]] for s in trials}) > 1)
out = {"n": len(ctxs), "seeds": [1, 2, 3], "accs": accs,
       "mean": round(mean, 4), "std": round(std, 4), "flip_questions": flip}
json.dump(out, open("eval/qa100/variance_probe.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("mean±std = %.3f±%.3f | 至少一次翻转的题 %d/%d" % (mean, std, flip, len(ctxs)))
