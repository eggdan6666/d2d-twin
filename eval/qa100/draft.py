# -*- coding: utf-8 -*-
"""Datasheet-QA-100 候选生成器（计划书 §4.5 题型 50/30/20）。
输出:
  eval/qa100/drafts_param.jsonl    参数提取候选(自动,带证据原文)
  eval/qa100/drafts_cross.jsonl    跨芯片对比候选(自动配对)
  eval/qa100/drafts_app.jsonl      应用电路素材清单(人工出题用)
  eval/qa100/review.csv            人工校验表(ok/edit/drop + 修正gold)
用法: python eval/qa100/draft.py"""
import sys, os, json, re, csv, random, itertools
from collections import defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.stdout.reconfigure(encoding="utf-8")
from rag.corpus import load_chunks

HERE = os.path.dirname(os.path.abspath(__file__))
UNIT = r"(?:V|mA|A|mV|GHz|MHz|kHz|Hz|°C/W|°C|uF|µF|nF|pF|k?Ω|m?W|dB|ns|us|μs|ps|ma)"
VAL_RX = re.compile(
    rf"\d+(?:\.\d+)?(?:\s*(?:[-–~]|to|and)\s*\d+(?:\.\d+)?)?(?:\s*(?:max|min|typ))?\s*{UNIT}", re.I)
COND_RX = re.compile(r"^\s*(?:@|at\b|[A-Z]{1,5}[\w()×\*\-]{0,8}\s*[=<>≤≥])", re.I)
NUM = re.compile(r"\d")
# 句式抽取: "supply voltage range from 4.5 V to 40 V" / "input voltage up to 100 V"
SENT_RX = re.compile(
    rf"([A-Za-z][A-Za-z ,\-/()]{{6,44}}?)\s+(?:range|of|is|from|up to|to)?\s*"
    rf"((?:from\s+)?\d+(?:\.\d+)?(?:\s*(?:[-–~]|to|and)\s*\d+(?:\.\d+)?)?\s*{UNIT})", re.I)
CANON = {
    "input voltage": r"input.{0,12}voltage|supply voltage|operating voltage|v(in|dd)?\b.{0,8}range",
    "output current": r"output.{0,10}current|load current|max(imum)?.{0,8}current",
    "operating temperature": r"operating.{0,12}temp|ambient.{0,12}temp|storage.{0,10}temp",
    "switching frequency": r"switch(ing)?.{0,8}frequenc|oscillator.{0,8}frequenc",
    "quiescent current": r"quiescent.{0,8}current|standby.{0,8}current|supply current.{0,6}(?:closed|shutdown)",
    "output voltage": r"output.{0,10}voltage|reference voltage|feedback voltage",
}

def is_param_line(s):
    if not s or NUM.search(s) or len(s) > 46 or len(s) < 6:
        return False
    return bool(re.search(r"voltage|current|temperature|power|frequency|resistance|range|rating|threshold|quiescent|ripple", s, re.I))

def table_pairs(text, part=""):
    """Markdown 表格行配对: 首列=参数名, 其后第一个含单位单元格=值(列语义歧义留人审)."""
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not (s.startswith("|") and s.endswith("|")) or "---" in s:
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 2 or not cells[0]:
            continue
        param = re.sub(r"\s+", " ", cells[0])
        if NUM.search(param) or len(param) < 5 or len(param) > 48 or not is_param_line(param + " x"):
            continue
        if part and re.search(re.escape(part) + r"[\w\-]*", param, re.I):
            continue
        valcell = next((c for c in cells[1:]
                        if c and VAL_RX.search(c) and not COND_RX.match(c)), None)
        if valcell:
            m = VAL_RX.search(valcell)
            out.append((param.lower(), " | ".join(cells)[:100],
                        re.sub(r"\s+", " ", m.group(0)).strip(), "mdtable"))
    return out

def extract_pairs(text, part=""):
    # 挖掉型号自身(含型号内数字),防 "UCC28780"→28780 us 这类污染
    if part:
        text = re.sub(re.escape(part) + r"[\w\-]*", " P/N ", text, flags=re.I)
    lines = [l.strip() for l in text.splitlines() if l.strip() and not l.startswith("#")]
    pairs = []
    for a, b in zip(lines, lines[1:]):
        if is_param_line(a) and VAL_RX.search(b) and not COND_RX.match(b):
            pairs.append((re.sub(r"\s+", " ", a.lower()), re.sub(r"\s+", " ", b)[:80],
                          re.sub(r"\s+", " ", VAL_RX.search(b).group(0)).strip(), "table"))
    for m in SENT_RX.finditer(text):
        subj, val = m.group(1).strip().lower(), re.sub(r"\s+", " ", m.group(2)).strip()
        if len(subj) >= 8 and is_param_line(subj + " x"):
            pairs.append((subj, re.sub(r"\s+", " ", m.group(0))[:90], val, "sent"))
    return pairs

def canon_key(param):
    for k, rx in CANON.items():
        if re.search(rx, param, re.I):
            return k
    return None

def main():
    random.seed(42)
    chunks = load_chunks()
    by_doc = defaultdict(list)
    for c in chunks:
        by_doc[c.doc_id].append(c)

    # ---- 参数提取候选 ----
    seen_parts, param_rows = set(), []
    for did, cs in by_doc.items():
        pool = [c for c in cs if c.section in ("abs_max", "elec_chars")] or \
               [c for c in cs if c.section in ("front", "overview")]
        for c in pool:
            tp = table_pairs(c.text, c.part)
            pairs = tp if len(tp) >= 2 else tp + extract_pairs(c.text, c.part)
            for pname, ev, val, src in pairs:
                param_rows.append({"doc_id": did, "part": c.part, "manufacturer": c.manufacturer,
                                   "section": c.section, "param": pname, "gold": val,
                                   "evidence": ev, "src": src, "canon": canon_key(pname)})
    bypart = defaultdict(list)
    for r in param_rows:
        if r["gold"] not in {x["gold"] for x in bypart[r["doc_id"]]}:
            bypart[r["doc_id"]].append(r)
    drafts = []
    for did, rs in bypart.items():
        good = [r for r in rs if r["src"] == "table"] + [r for r in rs if r["src"] == "sent"]
        for r in good[:2]:
            drafts.append({**r,
                "question": f"What is the specified value for '{r['param']}' of {r['part']} ({r['manufacturer']})?",
                "type": "param"})
    random.shuffle(drafts)
    json.dump(drafts, open(os.path.join(HERE, "drafts_param.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # ---- 跨芯片对比候选: 同类别 + 相同参数名 ----
    cats = defaultdict(list)
    for d in drafts:
        cat = next((c.category for c in chunks if c.doc_id == d["doc_id"]), "")
        cats[cat].append(d)
    cross = []
    for cat, rows in cats.items():
        if cat in ("", "flyback_power", "power_management", "analog_ic", "sensor", "memory", "driver_actuator"):
            byname = defaultdict(list)
            for r in rows:
                if r.get("canon"):
                    byname[r["canon"]].append(r)
            for pname, rs in byname.items():
                docs = {}
                for r in rs:
                    docs.setdefault(r["doc_id"], r)
                if len(docs) >= 2:
                    for a, b in itertools.islice(itertools.combinations(list(docs.values())[:4], 2), 2):
                        cross.append({"type": "cross", "category": cat, "param": pname,
                                      "a_part": a["part"], "a_gold": a["gold"],
                                      "b_part": b["part"], "b_gold": b["gold"],
                                      "question": f"For '{pname}', which is larger: {a['part']} or {b['part']}? Give both values.",
                                      "evidence": a["evidence"] + " || " + b["evidence"]})
    random.shuffle(cross)
    json.dump(cross[:40], open(os.path.join(HERE, "drafts_cross.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # ---- 应用电路素材清单(人工出题) ----
    app = []
    for did, cs in by_doc.items():
        for c in cs:
            if c.section == "typ_app" and len(c.text) > 600:
                app.append({"doc_id": did, "part": c.part, "manufacturer": c.manufacturer,
                            "file": os.path.relpath(c.path, os.path.join(HERE, "..", "..")),
                            "excerpt": c.text[:400]})
                break
    json.dump(app[:60], open(os.path.join(HERE, "drafts_app.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    # ---- 人工校验表 ----
    with open(os.path.join(HERE, "review.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "type", "question", "gold(校验/修正)", "evidence", "verdict(ok/edit/drop)", "note"])
        for i, d in enumerate(drafts[:70]):
            w.writerow([f"P{i:03d}", "param", d["question"], d["gold"], d["evidence"][:90], "", ""])
        for i, d in enumerate(cross[:30]):
            w.writerow([f"C{i:03d}", "cross", d["question"], f"{d['a_part']}:{d['a_gold']}|{d['b_part']}:{d['b_gold']}", d["evidence"][:90], "", ""])
    print(f"param候选 {len(drafts)} | cross候选 {len(cross[:40])} | app素材 {min(len(app),60)}")
    print(f"校验表: {os.path.join(HERE,'review.csv')}（Excel/WPS 打开，verdict 列填 ok/edit/drop）")

if __name__ == "__main__":
    main()
