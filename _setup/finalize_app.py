# -*- coding: utf-8 -*-
"""app 审校表(verdict) + 已定稿数据集 → 下一版数据集。

不复用 eval/qa100/finalize.py：它硬编码读 review.csv，且会把 datasheet_qa100.json 覆盖掉。
默认参数复现第一轮（review_app.csv → v5）；后续轮次显式给 --review/--base/--out。
用法:
  python _setup/finalize_app.py                      # review_app.csv → datasheet_qa100_v5.json
  python _setup/finalize_app.py --review review_app3.csv --pristine review_app3.json \
         --base eval/qa100/datasheet_qa100_v5.json --out .../datasheet_qa100_v6.json \
         --app-out .../datasheet_qa100_app36.json
"""
import sys, os, json, csv, io, re, argparse, collections

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
QA = os.path.join(ROOT, "eval", "qa100")
sys.path.insert(0, QA)
from score2 import items as strict_items

# 第一轮审校人只填 verdict，gold 改动由脚本执行；后续轮次 gold 直接在表里改，此项留空即可
GOLD_EDIT_V1 = {"A008": "<10kΩ", "A011": "≤207Ω"}
BOUND = re.compile(r"^[<>≤≥]")
BOUND_NOTE = "bound-type: 严格判分按数值+单位精确匹配，不等号不参与判分（满足约束的更小值会判错）"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", default=os.path.join(QA, "review_app.csv"))
    ap.add_argument("--pristine", default=os.path.join(QA, "review_app.orig.csv"),
                    help="审校前的原表(csv)或生成器落的同名 json，用于识别被人工改过的 gold")
    ap.add_argument("--base", default=os.path.join(QA, "datasheet_qa100_v3.json"))
    ap.add_argument("--out", default=os.path.join(QA, "datasheet_qa100_v5.json"))
    ap.add_argument("--app-out", default=None, help="只输出本轮新增 app 题的数据集(供 run.py --ds)")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    if os.path.exists(a.out) and not a.force:
        print(f"已存在 {a.out} —— 不覆盖。要重生成请加 --force 或换新 --out")
        return 1

    rows = list(csv.DictReader(io.StringIO(open(a.review, "rb").read().decode("utf-8-sig"))))
    if os.path.splitext(a.pristine)[1] == ".json":
        pri = {d["qid"]: d for d in json.load(open(a.pristine, encoding="utf-8"))}
    else:
        pri = {r["id"]: r for r in csv.DictReader(
            io.StringIO(open(a.pristine, "rb").read().decode("utf-8-sig")))}

    stem_tag = "round2-batch3(guidance题干/扩源)" if "app3" in os.path.basename(a.review) \
        else "round1(original circuit题干/typ_app)"
    apps, issues = [], []
    for r in rows:
        v = (r.get("verdict(ok/edit/drop)") or r.get("verdict") or "").strip().lower()
        if v == "drop":
            continue
        if v not in ("ok", "edit"):
            issues.append((r["id"], f"verdict 非法: {v!r}"))
            continue
        qid, ev, q = r["id"], r["evidence"], r["question"].strip()
        gold = r["gold"].strip()
        note = [f"human-reviewed {stem_tag}"]
        p = pri.get(qid)
        if p:
            pgold = (p.get("gold") or "").strip()
            if gold != pgold:
                note.append(f"edited gold: {pgold!r}→{gold!r}")
                if BOUND.match(gold):
                    note.append(BOUND_NOTE)
            elif qid in GOLD_EDIT_V1 and GOLD_EDIT_V1[qid]:
                gold = GOLD_EDIT_V1[qid]
                note.append(f"script-edited gold→{gold!r}; {BOUND_NOTE}")
        elif qid in GOLD_EDIT_V1 and GOLD_EDIT_V1[qid] and not BOUND.match(gold):
            gold = GOLD_EDIT_V1[qid]
            note.append(f"script-edited gold→{gold!r}; {BOUND_NOTE}")
        if BOUND.match(gold) and not any("bound-type" in x for x in note):
            note.append(BOUND_NOTE)
        nums = re.findall(r"\d+(?:\.\d+)?", gold)
        if nums and not any(n in ev for n in nums):
            issues.append((qid, f"gold {gold!r} 的数值不在 evidence 中"))
            continue
        if re.search(r"circuit of (\S+)", q):
            note.append("stem=typical application circuit")
        else:
            note.append("stem=application design guidance(扩源改口径)")
        apps.append({"qid": qid, "type": "app", "question": q, "gold": gold,
                     "evidence": ev, "note": " | ".join(note)})

    base = json.load(open(a.base, encoding="utf-8"))
    dup = {x["qid"] for x in base} & {x["qid"] for x in apps}
    if dup:
        print("qid 冲突(应换 --qid-start 重生成候选):", sorted(dup))
        return 2
    out = base + apps
    json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if a.app_out:
        json.dump(apps, open(a.app_out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{os.path.basename(a.out)} = {len(out)} 题", dict(collections.Counter(x['type'] for x in out)))
    print(f"本轮新增 app: {len(apps)} / 表内 {len(rows)}（drop {len(rows)-len(apps)-len(issues)}）"
          f"→ {os.path.basename(a.app_out) if a.app_out else '未单独输出'}")
    for x in apps:
        if "bound-type" in x["note"]:
            gi = strict_items(x["gold"])
            print(f"   bound-type {x['qid']} gold={x['gold']!r} 判分项={gi}")
    if issues:
        print("需人工处理:")
        for i in issues:
            print("  ", i)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
