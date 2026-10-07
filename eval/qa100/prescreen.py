# -*- coding: utf-8 -*-
"""review.csv 预筛：给可疑行打 auto_flag 列（不改动人工列）。
用法: python eval/qa100/prescreen.py"""
import sys, os, csv, re
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))

FAMILY = {
    "V": "volt", "A": "amp", "MA": "amp", "UA": "amp", "K": "amp",
    "°C/W": "thermres", "°C": "temp", "HZ": "freq", "MHZ": "freq", "KHZ": "freq", "GHZ": "freq",
    "Ω": "ohm", "KΩ": "ohm", "MΩ": "ohm", "F": "farad", "UF": "farad",
    "NF": "farad", "PF": "farad", "W": "watt", "MW": "watt", "DB": "db",
    "NS": "time", "US": "time", "PS": "time", "S": "time", "MIL": "len",
    "/W": "thermres",
}
def unit_family(gold):
    u = re.findall(r"°C/W|°C[^\s]*|[A-Za-zΩµ]+", gold)
    u = [x for x in u if x.lower() not in ("to", "and", "or", "max", "min", "typ", "a")]
    if not u:
        return None
    key = u[-1].upper().replace("Î©", "Ω")
    return FAMILY.get(key, "other")

PARAM_HINT = [
    (r"power suppl|supply voltage|vs\b|vcc|vee", "volt"),
    (r"volt|vdd|vin|vout|swing|headroom|threshold", "volt"),
    (r"current|iq|quiescent|standby", "amp"),
    (r"thermal resistance|theta|\bja\b", "thermres"),
    (r"temp", "temp"), (r"frequenc|clock|oscillat|bandwidth|bw", "freq"),
    (r"resist|impedance", "ohm"), (r"capacit", "farad"),
    (r"power (?:dissipation|consum|rating)|output power", "watt"),
    (r"gain|psrr|cmrr", "db"), (r"delay|rise|fall|time|durat", "time"),
]

def expect(param):
    for rx, fam in PARAM_HINT:
        if fam and re.search(rx, param, re.I):
            return fam
    return None

def flags_for(row):
    f = []
    gold, ev, param = row["gold(校验/修正)"], row["evidence"], row["question"]
    m = re.search(r"for '([^']+)'", param)
    pname = m.group(1) if m else (row.get("param") or "")
    uf, ef = unit_family(gold), expect(pname or gold)
    if uf and ef and uf != ef and "range" not in (pname or "").lower():
        f.append(f"unit_mismatch({pname}:{uf}?exp{ef})")
    nums = re.findall(r"\d+(?:\.\d+)?", gold)
    evn = ev.replace(" ", "")
    if nums and not any(n in evn for n in nums):
        f.append("gold_not_in_evidence")
    if re.search(r"^(figure|table|note|test|typical app|layout)", (pname or ""), re.I):
        f.append("param_not_spec")
    if len((pname or "").split()) > 7:
        f.append("param_too_long")
    v = re.findall(r"(\d+(?:\.\d+)?)", gold)
    if row["type"] == "cross":
        segs = [s.split(":", 1)[1] if ":" in s else s for s in gold.split("|")]
        xs = [float(x) for seg in segs for x in re.findall(r"\d+(?:\.\d+)?", seg)][:2]
        if xs and (xs[0] > 1600 or any(abs(x) > 1e5 for x in xs)):
            f.append("value_extreme")
    elif v:
        x = float(v[0])
        if uf == "volt" and x > 1600: f.append("value_extreme")
        if uf == "temp" and not (-80 <= x <= 400): f.append("value_extreme")
        if uf == "freq" and x > 100000 and "MHz" not in gold and "GHz" not in gold:
            f.append("value_extreme")
    rng = re.search(r"(\d+(?:\.\d+)?\s*(?:V|A|mV|mA|MHz|kHz|Hz|°C)\s*(?:to|[-–~])\s*\d+(?:\.\d+)?\s*\S{0,3})", ev, re.I)
    if rng and "to" not in gold and "-" not in gold:
        f.append("gold_truncation")
    if row["type"] == "cross":
        mm = re.match(r"(.+?):(.+?)\|(.+?):(.+?)$", gold.replace(" ", ""))
        if mm and mm.group(2) == mm.group(4):
            f.append("both_equal(trivial)")
    return f

def main():
    path = os.path.join(HERE, "review.csv")
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    fields = list(rows[0].keys())
    if "auto_flag" not in fields:
        fields.append("auto_flag")
    import collections
    cnt = collections.Counter()
    for r in rows:
        fl = flags_for(r)
        r["auto_flag"] = ";".join(fl)
        cnt["clean" if not fl else fl[0].split("(")[0]] += 1
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    print("预筛结果:", dict(cnt))
    print(f"建议审校顺序: 先看 auto_flag 为空的 {cnt['clean']} 行(可直接 ok)，再看带标记的")

if __name__ == "__main__":
    main()
