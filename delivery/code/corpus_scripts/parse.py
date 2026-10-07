# -*- coding: utf-8 -*-
"""PDF -> Markdown 解析 + 章节切片 + 元数据索引（计划书 4.2 节）。
输出:
  data/parsed/{id}.md           全文 Markdown（按章节加标题）
  data/chunks/{id}/{sec}.md     章节切片（超长自动分块）
  data/index/corpus_index.jsonl 元数据索引
  data/index/corpus_stats.json  统计报告
用法: python parse.py [limit]
"""
import sys, os, re, json, glob, datetime
sys.stdout.reconfigure(encoding="utf-8")
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
RAW, PARSED, CHUNKS, INDEX = (os.path.join(DATA, d) for d in
                              ("raw_pdf", "parsed", "chunks", "index"))
MAX_CHARS = 8000

# 章节判定：按优先级排列，命中即切换当前章节
SECTION_RULES = [
    ("abs_max",   r"absolute\s+(?:maximum\s+)?ratings?|stress\s+ratings?|maximum\s+ratings?"),
    ("elec_chars",r"electrical\s+(?:characteristics|specifications|data|limits?)|specs?\.?(?:\s|$).{0,20}operating"),
    ("typ_app",   r"typical\s+applications?|application(s|s\s+information)?\s+(circuit|information|diagram|example)s?|design\s+information|layout\s+(guideline|example)"),
    ("package",   r"package(?:s|ing|ing\s+and|$|\s+(?:info|material|outline|dimensions|diagram))|mechanical\s+(?:data|info|specifications|details)|order(?:ing|ing\s+info)|land\s+pattern|carrier\s+and\s+package"),
    ("pin_desc",  r"pin(?:s)?(?:out)?s?\s+(?:description|configuration|functions?|information|diagram|assignment)|terminal(?:s)?\s+(?:function|configuration|description)|pin\s+configuration"),
    ("func_desc", r"functional\s+(?:block\s+)?diagram|block\s+diagram|theory\s+of\s+operation|principle\s+of\s+operation|device(?:\s+(?:functional\s+)?description|description|operation)|operating\s+(?:principles?|modes?|and\s+features)|detailed\s+(?:description|description\.?.{0,5}description)|functional\s+(?:description|overview)"),
    ("overview",  r"^features?|^applications?|^description(s)?|^general\s+(description|overview)|^overview$|^product\s+(description|summary)|^introduction$|^summary$|^device\s+(comparison|overview|function)"),
]
SECTION_COMPILED = [(k, re.compile(p, re.I)) for k, p in SECTION_RULES]

# 页眉页脚噪声
NOISE = re.compile(
    r"^(?:www\.|https?://|copyright|©|SNLS|SNAS|SLVS|SBAS|SDAS|SBCS|SBMS|SCES|SPNS|ZCSG|CD00|DS\d|ES\d|RM\d|Rev\.|Preliminary\s+Data|Datasheet\s+short|Short-form|Page\s+\d+\s+of\s+\d+|\d+\s*/\s*\d+$|www\.)", re.I)
MONTHS = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?"

def classify_line(line):
    s = line.strip()
    if not s or len(s) > 70:
        return None
    if s.endswith("."):
        return None
    upper_ratio = sum(c.isupper() for c in s if c.isalpha()) / max(1, sum(c.isalpha() for c in s))
    if upper_ratio < 0.6 and not re.match(r"^\d+(\.\d+)*[\s\-–]", s):
        return None
    for key, rx in SECTION_COMPILED:
        if rx.search(s):
            return key
    return None

def clean_lines(text):
    out = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s or NOISE.match(s):
            continue
        out.append(s)
    return out

def extract_year(doc_text, doc):
    m = re.search(MONTHS + r"[\s,.-]+((?:19|20)\d{2})", doc_text)
    if m:
        return int(m.group(1))
    cd = (doc.metadata or {}).get("creationDate") or ""
    m2 = re.match(r"D:(\d{4})", cd)
    if m2:
        return int(m2.group(1))
    m3 = re.search(r"\bRev[.\s]+[A-Z]?[, ]+((?:19|20)\d{2})\b", doc_text, re.I)
    return int(m3.group(1)) if m3 else None

def table_to_md(table):
    rows = table.extract()
    rows = [[(c or "").replace("\n", " ").strip() for c in r] for r in rows]
    rows = [r for r in rows if any(r)]
    if len(rows) < 2:
        return ""
    ncol = max(len(r) for r in rows)
    rows = [r + [""] * (ncol - len(r)) for r in rows]
    lines = ["| " + " | ".join(rows[0]) + " |",
             "|" + "---|" * ncol]
    lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(lines)

def split_long(text):
    if len(text) <= MAX_CHARS:
        return [text]
    parts, buf = [], []
    size = 0
    for para in re.split(r"\n\s*\n", text):
        if size + len(para) > MAX_CHARS and buf:
            parts.append("\n\n".join(buf)); buf, size = [], 0
        buf.append(para); size += len(para) + 2
    if buf:
        parts.append("\n\n".join(buf))
    return parts

def parse_pdf(pdf_path, tables_budget_s=20.0):
    import time
    man = os.path.basename(os.path.dirname(pdf_path))
    part = os.path.splitext(os.path.basename(pdf_path))[0]
    doc = pymupdf.open(pdf_path)
    TABLE_HINT = re.compile(r"electrical|characteristic|rating|specification|limit", re.I)
    t0 = time.time()
    sec_texts, sec_order = {}, []
    current = "front"
    for page in doc:
        lines = clean_lines(page.get_text("text"))
        body = []
        for ln in lines:
            key = classify_line(ln)
            if key:
                sec_texts.setdefault(key, []).append("## " + ln)
                if key not in sec_order:
                    sec_order.append(key)
                current = key
                continue
            body.append(ln)
        tbl_md = []
        if time.time() - t0 < tables_budget_s:
            ptxt = " ".join(body[:50])
            if TABLE_HINT.search(ptxt) or len(body) < 120:
                try:
                    for t in page.find_tables().tables:
                        md = table_to_md(t)
                        if md and md.count("|") > 8:
                            tbl_md.append(md)
                except Exception:
                    pass
        sec_texts.setdefault(current, []).extend(body)
        if tbl_md:
            sec_texts.setdefault(current, [])
            sec_texts[current].append("\n\n[表格]\n\n" + "\n\n".join(tbl_md))
    full_parts = []
    for sec in sec_order + [k for k in sec_texts if k not in sec_order]:
        body = "\n".join(sec_texts.get(sec, [])).strip()
        if not body:
            continue
        full_parts.append(f"# {sec}\n\n{body}")
    full_md = f"---\npart: {part}\nmanufacturer: {man}\n---\n\n" + "\n\n".join(full_parts)
    return doc, part, man, sec_texts, sec_order, full_md

def _index_entry(did, part, man, pdf, doc, chunks):
    first3 = " ".join(" ".join(clean_lines(doc[p].get_text("text"))[:200])
                      for p in range(min(3, doc.page_count)))
    return {
        "id": did, "part": part, "manufacturer": man,
        "pdf": os.path.relpath(pdf, DATA), "md": os.path.join("parsed", did + ".md"),
        "n_pages": doc.page_count, "year": extract_year(first3, doc),
        "chunks": chunks, "n_chunks": len(chunks),
        "sections": sorted({c["section"] for c in chunks}),
        "bytes": os.path.getsize(pdf)}

def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    pdfs = sorted(glob.glob(os.path.join(RAW, "*", "*.pdf")))
    if limit:
        pdfs = pdfs[:limit]
    os.makedirs(PARSED, exist_ok=True)
    os.makedirs(CHUNKS, exist_ok=True)
    os.makedirs(INDEX, exist_ok=True)
    entries, stats = [], {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "docs": 0, "chunks": 0, "by_manufacturer": {}, "by_section": {},
        "no_section_parsed": []}
    for i, pdf in enumerate(pdfs, 1):
        try:
            man = os.path.basename(os.path.dirname(pdf))
            part = os.path.splitext(os.path.basename(pdf))[0]
            did = re.sub(r"[^\w.-]", "_", f"{man}__{part}")
            cdir = os.path.join(CHUNKS, did)
            if (os.path.isfile(os.path.join(PARSED, did + ".md"))
                    and os.path.isdir(cdir)):
                doc = pymupdf.open(pdf)
                chunks = []
                for name in sorted(os.listdir(cdir)):
                    if not name.endswith(".md"):
                        continue
                    sec = re.sub(r"__\d+$", "", name[:-3])
                    p = os.path.join(cdir, name)
                    chunks.append({"section": sec, "file": name,
                                   "chars": os.path.getsize(p)})
                entries.append(_index_entry(did, part, man, pdf, doc, chunks))
                doc.close()
                stats["docs"] += 1
                stats["chunks"] += len(chunks)
                stats["by_manufacturer"][man] = stats["by_manufacturer"].get(man, 0) + 1
                if not chunks:
                    stats["no_section_parsed"].append(did)
                continue
            doc, part, man, sec_texts, sec_order, full_md = parse_pdf(pdf)
        except Exception as e:
            print(f"[ERR ] {pdf}: {e}")
            continue
        with open(os.path.join(PARSED, did + ".md"), "w", encoding="utf-8") as f:
            f.write(full_md)
        os.makedirs(cdir, exist_ok=True)
        chunks = []
        for sec, body in sorted(((k, "\n".join(v).strip()) for k, v in sec_texts.items()),
                                key=lambda x: -len(x[1])):
            body = re.sub(r"\n## [^\n]*\n", "\n", body).strip()
            if len(body) < 200:
                continue
            for j, piece in enumerate(split_long(body), 1):
                name = f"{sec}.md" if len(split_long(body)) == 1 else f"{sec}__{j}.md"
                with open(os.path.join(cdir, name), "w", encoding="utf-8") as f:
                    f.write(piece)
                chunks.append({"section": sec, "file": name, "chars": len(piece)})
            stats["by_section"][sec] = stats["by_section"].get(sec, 0) + 1
        entries.append(_index_entry(did, part, man, pdf, doc, chunks))
        stats["docs"] += 1
        stats["chunks"] += len(chunks)
        stats["by_manufacturer"][man] = stats["by_manufacturer"].get(man, 0) + 1
        if not chunks:
            stats["no_section_parsed"].append(did)
        doc.close()
        if i % 50 == 0 or i == len(pdfs):
            print(f"progress {i}/{len(pdfs)}")
    with open(os.path.join(INDEX, "corpus_index.jsonl"), "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    with open(os.path.join(INDEX, "corpus_stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"\n解析完成: {stats['docs']} 文档 / {stats['chunks']} 章节切片")
    print("厂商分布:", stats["by_manufacturer"])
    print("章节分布:", stats["by_section"])

if __name__ == "__main__":
    main()
