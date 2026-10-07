# -*- coding: utf-8 -*-
"""gold 清洗: 以 evidence 原文为准修复截断类脏 gold → datasheet_qa100_v2.json,
再用 score2 严格判分重评 results_*.json。原数据集备份为 .bak。"""
import sys, os, json, re, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")
from score2 import correct, items

HERE = os.path.dirname(os.path.abspath(__file__))
DS = os.path.join(HERE, "datasheet_qa100.json")

RANGE_RX = re.compile(r"([-−]?\d+(?:\.\d+)?)\s*([°VA-HzΩµuWwd]|°C|kHz|MHz|GHz|Hz|V|A|mV|mA|uF|nF|pF|W|dB|ns|ps)?\s*(?:to|[-–~])\s*([-−]?\d+(?:\.\d+)?)\s*([°VA-HzΩµuWwd]|°C|kHz|MHz|GHz|Hz|V|A|mV|mA|uF|nF|pF|W|dB|ns|ps)?", re.I)

def try_fix(gold, ev):
    """返回 (新gold或原值, 修复说明)."""
    g = gold.strip()
    nums = re.findall(r"[-−]?\d+(?:\.\d+)?", g)
    if not nums:
        return g, None
    single = len(nums) == 1 and "to" not in g.lower()
    m = RANGE_RX.search(ev)
    if single and m:
        a, ua, b, ub = m.groups()
        unit = (ub or ua or "").strip()
        if re.sub(r"[-−]", "", a) == re.sub(r"[-−]", "", nums[0]) or a.lstrip("-−") == nums[0]:
            new = f"{a} {unit} to {b} {unit}".replace("  ", " ").strip()
            return new, f"range_fix:{gold!r}->{new!r}"
        if b == nums[0]:  # gold 是右端点
            new = f"{a} {unit} to {b} {unit}".strip()
            return new, f"range_fix_r:{gold!r}->{new!r}"
    # 负号: gold 数字在 evidence 中只以负数形式出现
    n = nums[0]
    if not g.startswith("-") and not any(x.lstrip("-") != x for x in nums):
        if re.search(rf"[-−]\s*{re.escape(n)}\s*(?:{''})?", ev) and not re.search(rf"(?<![-−.]){re.escape(n)}\s*(?:V|A|°C|Hz|kHz|MHz|mA|uA)", ev):
            new = "-" + g
            return new, f"sign_fix:{gold!r}->{new!r}"
    return g, None

def main():
    ds = json.load(open(DS, encoding="utf-8"))
    if not os.path.exists(DS + ".bak"):
        shutil.copy(DS, DS + ".bak")
    fixes = []
    for q in ds:
        new, why = try_fix(q["gold"], q.get("evidence", ""))
        if why:
            fixes.append({"qid": q["qid"], "why": why, "type": q["type"]})
            q["gold"] = new
            q["note"] = (q.get("note", "") + "|" + why)[:120]
    json.dump(ds, open(os.path.join(HERE, "datasheet_qa100_v2.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"清洗 {len(fixes)} 条 gold → datasheet_qa100_v2.json（原件在 .bak）")
    for f in fixes:
        print("  ", f["qid"], f["type"], f["why"])
    # 重判三基线
    by_qid = {q["qid"]: q for q in ds}
    print("\n== v2 gold + 严格判分 重评 ==")
    import glob
    for f in sorted(glob.glob(os.path.join(HERE, "results_rag*.json")) + sorted(glob.glob(os.path.join(HERE, "results_bare*.json")))):
        d = json.load(open(f, encoding="utf-8"))
        n = len(d)
        old_ok = sum(x["ok"] for x in d)
        new_ok = 0
        byt = {"param": [0, 0], "cross": [0, 0]}
        for x in d:
            q = by_qid.get(x["qid"])
            if not q:
                continue
            ok = correct(q["gold"], x["pred"])
            x["ok_v2"] = ok
            new_ok += ok
            t = x["type"] if x["type"] in byt else "param"
            byt[t][0] += ok; byt[t][1] += 1
        name = os.path.basename(f).replace(".json", "_v2.json")
        json.dump(d, open(os.path.join(HERE, name), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        p, c = byt["param"], byt["cross"]
        print(f"{os.path.basename(f):22s} 旧宽松{old_ok/n:.1%} → v2严格{new_ok/n:.1%} | param {p[0]}/{p[1]} cross {c[0]}/{c[1]}")

if __name__ == "__main__":
    main()
