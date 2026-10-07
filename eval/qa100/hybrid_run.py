# -*- coding: utf-8 -*-
"""混合路由实验: 37 道 cross 题走 Orchestrator(3B+校验+按需升级API),
对照纯3B(5/37)与纯API(8/37), 量化 准确率 vs API调用比例/成本。"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.stdout.reconfigure(encoding="utf-8")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
from rag.orchestrate import Orchestrator
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from score2 import correct

ds = json.load(open("eval/qa100/datasheet_qa100_v3.json", encoding="utf-8"))
cross = [q for q in ds if q["type"] == "cross"]
orc = Orchestrator()
rows, ok_n, esc_n, api_tok = [], 0, 0, 0
for i, q in enumerate(cross):
    r = orc.answer(q["question"])
    ok = correct(q["gold"], r["text"])
    ok_n += ok
    esc_n += r["escalated"]
    if r["escalated"]:
        api_tok += r["prompt_tokens"] + r["completion_tokens"]
    rows.append({"qid": q["qid"], "ok": ok, "escalated": r["escalated"],
                 "verify": r["verify"], "model": r["model"],
                 "tokens": r["prompt_tokens"] + r["completion_tokens"],
                 "pred": r["text"][:160]})
    print(f"[{i:02d}] ok={ok} esc={r['escalated']} | {q['question'][:50]}", flush=True)
n = len(cross)
out = {"n": n, "acc": round(ok_n / n, 4), "escalation_rate": round(esc_n / n, 4),
       "api_tokens_total": api_tok, "rows": rows}
json.dump(out, open("eval/qa100/hybrid_cross.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"\n混合路由: acc={ok_n}/{n}={ok_n/n:.1%} | 升级率 {esc_n}/{n}={esc_n/n:.0%} | API tokens {api_tok}")
print("对照: 纯3B=5/37(13.5%) 纯API=8/37(21.6%)")
