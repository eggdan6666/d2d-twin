# -*- coding: utf-8 -*-
"""候选芯片筛选（零 GPU，只读 PDF 文本层）——给 D2D-Twin 第 6+ 颗排队。

判据来自已做过的 5 颗共同特征：有寄存器地图/位域表、有复位值、有 R/W 访问码、有总线接口章节、
寄存器地址用 0xNN 书写。已做的芯片与已判定不适合的型号自动排除。

用法: python _setup/pick_chips.py [--top 25] [--out eval/qa100/chip_candidates.json]
"""
import sys, os, re, glob, json, argparse, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
import pymupdf  # noqa: E402

DONE = {"TMP1075", "BMP280", "TMP102", "BME280", "TMP100"}
# 明显不适合本基准的类型：无寄存器映射（功率器件/连接器/模块/纯线性器件）
NEG = re.compile(r"transistor|diode|connector|mosfet|relay|inductor|capacitor|module|antenna|fuse", re.I)


def signals(txt):
    t = txt.lower()
    return {
        "reg_map": len(re.findall(r"register map|register summary|register description|bit description|field description", t)),
        "cfg_reg": len(re.findall(r"configuration register|control register|mode register", t)),
        "reset": len(re.findall(r"reset value|power[- ]?up.{0,24}reset|default value", t)),
        "access": len(re.findall(r"read[- ]only|read/write|\br/w\b|\bros\b|\br?w\b", t)),
        "bus": len(re.findall(r"i2c|smbus|two-wire|\bspi\b|\buart\b", t)),
        "hex_addr": len(re.findall(r"0x[0-9a-f]{2}\b", txt)),
        "bit_table": len(re.findall(r"bit\s*\d|\[\s*\d+\s*:\s*\d+\s*\]|\bd[0-7]\b", t)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--out", default=os.path.join(ROOT, "eval", "qa100", "chip_candidates.json"))
    ap.add_argument("--maxpages", type=int, default=60)
    args = ap.parse_args()

    pdfs = sorted(glob.glob(os.path.join(ROOT, "corpus", "data", "raw_pdf", "**", "*.pdf"), recursive=True))
    out = []
    for i, p in enumerate(pdfs):
        name = os.path.basename(p)[:-4].upper()
        if name in DONE or NEG.search(name):
            continue
        try:
            d = pymupdf.open(p)
            n = len(d)
            txt = "".join(pg.get_text() for pg in list(d)[:args.maxpages])
            d.close()
        except Exception as e:
            print("[warn] 打不开 %s: %s" % (name, str(e)[:60]), flush=True)
            continue
        s = signals(txt)
        score = (s["reg_map"] * 3 + s["cfg_reg"] * 2 + s["reset"]
                 + min(s["access"], 20) * 0.5 + min(s["hex_addr"], 40) * 0.2
                 + min(s["bit_table"], 30) * 0.1)
        out.append({"part": name, "vendor": os.path.basename(os.path.dirname(p)), "pages": n,
                    "score": round(score, 2), **s, "path": os.path.relpath(p, ROOT).replace("\\", "/")})
        if (i + 1) % 50 == 0:
            print("  已扫 %d/%d" % (i + 1, len(pdfs)), flush=True)
    out.sort(key=lambda r: -r["score"])
    json.dump(out, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n== 候选前 %d（共 %d 份，已排除做过/不适用）==" % (args.top, len(out)))
    print("%-4s %-16s %-10s %5s %6s %6s %5s %5s %5s %5s" % ("#", "part", "vendor", "pages", "score", "reg_map", "cfg", "reset", "acc", "hex"))
    for r in out[:args.top]:
        print("%-4d %-16s %-10s %5d %6.1f %6d %6d %5d %5d %5d" % (
            out.index(r) + 1, r["part"], r["vendor"], r["pages"], r["score"], r["reg_map"],
            r["cfg_reg"], r["reset"], r["access"], r["hex_addr"]))
    print("\n输出:", args.out, os.path.getsize(args.out), "bytes")


if __name__ == "__main__":
    main()
