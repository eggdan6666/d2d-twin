# -*- coding: utf-8 -*-
"""Progress snapshot for the loose-prompt run (read-only)."""
import sys; sys.stdout.reconfigure(encoding="utf-8")
import json, os, time, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(ROOT, "eval", "results", "smoke_20261004_020225.jsonl")
LOG = os.path.join(ROOT, "_setup", "lme_loose.log")
ERR = os.path.join(ROOT, "_setup", "lme_loose.err")
START = datetime.datetime(2026, 10, 4, 2, 2, 24).timestamp()

rows = [json.loads(l) for l in open(F, encoding="utf-8") if l.strip()] if os.path.exists(F) else []
done = max((r["idx"] for r in rows), default=-1) + 1
elapsed = time.time() - START
rate = done / elapsed if elapsed else 0
eta = (500 - done) / rate / 60 if rate else 0
print("now=%s done_items=%d/500 elapsed=%.1fmin rate=%.2f/min ETA=%.0fmin (~%s)"
      % (datetime.datetime.now().strftime("%H:%M:%S"), done, elapsed / 60, rate, eta,
         (datetime.datetime.now() + datetime.timedelta(minutes=eta)).strftime("%H:%M")))
for c in ("rag", "none"):
    rs = [r for r in rows if r["cond"] == c]
    if rs:
        ref = sum(1 for r in rs if "insufficient" in r["pred"].lower())
        print("  %-5s n=%-4d acc=%.4f refused=%d avg_tok=%.0f avg_lat=%.2fs"
              % (c, len(rs), sum(r["ok"] for r in rs) / len(rs), ref,
                 sum(r["tokens"] for r in rs) / len(rs), sum(r["latency_s"] for r in rs) / len(rs)))
logtxt = open(LOG, encoding="utf-8", errors="replace").read() if os.path.exists(LOG) else ""
print("log_bytes=%d err_bytes=%d summary=%s"
      % (len(logtxt.encode()), os.path.getsize(ERR) if os.path.exists(ERR) else -1,
         "汇总" in logtxt))
