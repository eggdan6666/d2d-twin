# -*- coding: utf-8 -*-
"""QA-100 严格判分器（fork 自 run.py 的 correct，规则见 REPORT_qa100_baseline.md 判分观察节）。
规则: 数值(含负号)精确 + 单位强制(gold带单位则pred必须同单位) + 范围双端点。
用法: python eval/qa100/score2.py  → 重判 results_*.json, 输出 results2_*.json + 对照表"""
import sys, os, json, re, glob
sys.stdout.reconfigure(encoding="utf-8")

UNIT_RX = re.compile(
    r"(°C/W|°C|[µuMmnkp]?A|V|GHz|MHz|kHz|Hz|[kM]?Ω|[mnuµ]?F|mW|MW|W|dB|ps|ns|[µu]s|mil)", re.I)
NUM_RX = re.compile(r"[-−]?\d+(?:\.\d+)?")

def norm_unit(u):
    u = u.replace("µ", "u").replace("μ", "u").upper()
    return {"UA": "UA", "MA": "MA", "NA": "NA", "PA": "PA", "K": "K"}.get(u, u)

def items(s):
    """按数值切段, 每个数值配其后最近单位(8字符内)。"""
    out = []
    for m in NUM_RX.finditer(s.replace("−", "-")):
        num = m.group(0)
        tail = s[m.end():m.end() + 9].lstrip(" -–	").lstrip("-– ")
        um = UNIT_RX.match(tail)
        unit = norm_unit(um.group(1)) if um else ""
        # 排除误把单词首字母当单位: 单位后紧跟字母视为伪匹配
        if um and re.match(r"[A-Za-z]", tail[um.end():um.end() + 1] or ""):
            unit = ""
        out.append((num, unit))
    return out

def correct(gold, pred):
    gi = items(gold)
    if not gi:
        return False
    pi = items(pred)
    for num, unit in gi:
        if unit:
            if not any(n == num and u == unit for n, u in pi):
                return False
        else:
            if not any(n == num for n, _ in pi):
                return False
    return True

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    files = sorted(glob.glob(os.path.join(here, "results_*.json")))
    files = [f for f in files if "results2" not in f and "results_" in os.path.basename(f)]
    print(f"{'文件':26s} {'旧acc':>8s} {'新acc':>8s} {'param':>12s} {'cross':>12s} {'翻转 ok→no / no→ok':>18s}")
    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        old = sum(x["ok"] for x in d)
        flips = []
        by = {"param": [0, 0], "cross": [0, 0]}
        for x in d:
            new = correct(x["gold"], x["pred"])
            t = x["type"] if x["type"] in by else "param"
            by[t][0] += new; by[t][1] += 1
            if new != x["ok"]:
                flips.append((x["qid"], x["ok"], new, x["gold"][:18], x["pred"][:34]))
            x["ok2"] = new
        n = len(d)
        name = os.path.basename(f)
        out = os.path.join(here, name.replace("results_", "results2_"))
        json.dump(d, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        p, c = by["param"], by["cross"]
        print(f"{name:26s} {old/n:>7.1%} {sum(x['ok2'] for x in d)/n:>7.1%} "
              f"{p[0]:>4d}/{p[1]:<6d} {c[0]:>4d}/{c[1]:<6d} "
              f"↓{sum(1 for _,o,nn,_,_ in flips if o and not nn)} ↑{sum(1 for _,o,nn,_,_ in flips if nn and not o)}")
        for q, o, nn, g, pr in flips[:4]:
            print(f"    {q}: {'✓→✗' if o else '✗→✓'} gold={g!r} pred={pr!r}")
    print("\n新明细已存 results2_*.json")

if __name__ == "__main__":
    main()
