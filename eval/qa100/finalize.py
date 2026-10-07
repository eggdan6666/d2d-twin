# -*- coding: utf-8 -*-
"""review.csv → datasheet_qa100.jsonl 定稿 + 校验。
用法: python eval/qa100/finalize.py [--require-verdict]"""
import sys, os, json, csv, re, argparse
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))

def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip().lower()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--require-verdict", action="store_true")
    a = ap.parse_args()
    rows = list(csv.DictReader(open(os.path.join(HERE, "review.csv"), encoding="utf-8-sig")))
    out, issues = [], []
    for r in rows:
        v = ((r.get("verdict(ok/edit/drop)") or r.get("verdict")) or "").strip().lower()
        if a.require_verdict and v != "ok":
            continue
        if v == "drop":
            continue
        q, gold, ev = r["question"].strip(), r["gold(校验/修正)"].strip(), r["evidence"]
        if not q or not gold:
            issues.append((r["id"], "empty question/gold")); continue
        nums = re.findall(r"\d+(?:\.\d+)?", gold)
        if nums and not any(n in ev for n in nums):
            issues.append((r["id"], f"gold数值{nums}不在evidence中"))
        out.append({"qid": r["id"], "type": r["type"], "question": q, "gold": gold,
                    "evidence": ev, "note": r.get("note", "")})
    json.dump(out, open(os.path.join(HERE, "datasheet_qa100.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    import collections
    print("定稿", len(out), collections.Counter(x["type"] for x in out))
    if issues:
        print("警告(需人工确认):")
        for i in issues: print("  ", i)

if __name__ == "__main__":
    main()
