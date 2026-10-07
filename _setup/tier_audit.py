# -*- coding: utf-8 -*-
"""给 Q0 的 20 个「保留位段」找手册原文证据，把 A 档（文档明说读 0）与 C 档（文档没给访问码）分开。

为什么要它：`is_convention_bit` 现在靠位段**名字/描述**猜档位，而我写金标时的 desc 对 A、C
两档都用了「恒 0」这种措辞 ⇒ 分类器无法区分。④b 那行因此只在操作定义下成立。
本脚本不改判据，只把每条判据要的证据（PDF 第几页、原话片段）拉出来供人勾，
输出 d2d/eval/q0_bit_tier_draft.csv（我填证据，用户勾 A/C）。
"""
import sys, os, io, re, csv, glob, json

try:
    import pymupdf as fitz
except ImportError:
    import fitz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_setup"))
sys.stdout.reconfigure(encoding="utf-8")
from rescore_variant import TAGS, is_convention_bit

PDFDIR = os.path.join(ROOT, "corpus", "data", "raw_pdf")


def find_pdf(part):
    for p in glob.glob(os.path.join(PDFDIR, "**", "*.pdf"), recursive=True):
        if os.path.basename(p)[:-4].upper() == part.upper():
            return p
    return None


def excerpts(doc, regname, bits, kw=("Reserved", "reserved", "Unused", "unused", "RS")):
    hits = []
    for pno in range(doc.page_count):
        t = doc[pno].get_text()
        if regname.upper() not in t.upper():
            continue
        flat = re.sub(r"\s+", " ", t)
        for k in kw:
            for m in re.finditer(re.escape(k), flat):
                seg = flat[max(0, m.start() - 110):m.start() + 150]
                if re.search(r"\bR/W\b|\bR\b|\bW\b|\bRS\b|Read|read", seg):
                    hits.append((pno + 1, k, seg))
        if hits:
            break
    return hits[:3]


rows = []
for part in TAGS:
    ip = os.path.join(ROOT, "d2d", "ir", "%s_gold_ir.json" % part)
    if not os.path.exists(ip):
        continue
    ir = json.load(io.open(ip, encoding="utf-8"))
    segs = [(r, f) for r in ir["registers"] if r.get("access") == "RW"
            for f in r.get("fields", []) if is_convention_bit(f)]
    if not segs:
        continue
    pdf = find_pdf(part)
    doc = fitz.open(pdf) if pdf else None
    for r, f in segs:
        ex = []
        if doc:
            ex = excerpts(doc, r["name"], f["bits"])
        rows.append({
            "chip": part, "reg": r["name"], "addr": r["addr"], "field": f["name"],
            "bits": f["bits"], "ir_desc": str(f.get("desc", ""))[:90],
            "pdf": os.path.basename(pdf) if pdf else "缺 PDF",
            "页码": ex[0][0] if ex else "",
            "命中关键词": ex[0][1] if ex else "",
            "手册原话片段": ex[0][2] if ex else "（未在同页找到 Reserved 行，需人眼）",
            "档位A或C": "", "人工裁决": "",
        })
    if doc:
        doc.close()

out = os.path.join(ROOT, "d2d", "eval", "q0_bit_tier_draft.csv")
with io.open(out, "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print("写出 %s：%d 个位段" % (out, len(rows)))
for r in rows:
    print("\n%-8s %-14s %-4s %s[%s]  ir_desc=%s" % (r["chip"], r["reg"], r["addr"], r["field"], r["bits"], r["ir_desc"][:56]))
    print("   p%s  %s" % (r["页码"], r["手册原话片段"][:180]))
