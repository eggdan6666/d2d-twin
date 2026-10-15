# -*- coding: utf-8 -*-
"""寄存器字段抽取器（启发式原型）。

从数据手册 PDF 中试探性地抽取寄存器地址 + 位域 + 访存属性，产出 Silver 候选记录。

设计原则：
- 只做【候选】，不下结论：所有输出 status="silver_candidate"；
- 来源可溯源：每条记录带 pdf_sha256 与物理页码；
- 允许漏抽与弃答，不伪造；未知字段（access/reset）保持 None；
- 本模块独立读写 eval/rag_extraction_v1/ 下的候选文件，不触碰 d2d/ir/。

抽取策略（表格优先）：用 PyMuPDF 的页面结构分析重建寄存器表，将其归属到
「N.N.N <Name> Register (Address = XXh) [reset = XXh]」标题所声明的地址；
无表格结构时退化为逐行正则启发式。

上游现实：rag/hierarchical.py 仅有文档粗检 + BM25/向量融合，rag/orchestrate.py 输出
问答文本与 chunk_id，rag/corpus.py 的 chunk 元数据无完整 PDF 页/表格映射——本原型是
补齐「寄存器字段抽取 + 证据定位」缺口的第一块。
"""
from __future__ import annotations

import hashlib
import os
import re
import uuid

from .schema import RegisterFieldCandidate, bits_to_mask

# ---- PDF 页文本与表格结构 ----

def pdf_sha256(pdf_path: str) -> str:
    with open(pdf_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# 寄存器标题：`8.6.1 Temp_Result Register (Address = 00h) [reset = 0000h]`
_REG_HEAD_RE = re.compile(
    r"(?P<name>[A-Za-z_][A-Za-z0-9_ /-]*?)\s+Register"
    r"[\s\S]{0,80}?(?:Address\s*=\s*)?(?P<addr>[0-9A-Fa-f]{1,4})[hH]"
    r"[\s\S]{0,40}?\[reset\s*=\s*(?P<reset>[0-9A-Fa-fxX]+)[hH]?\]")

# 字段行（回退用）：`15:2  Temp_Result[13:0]  R  0000h`
_FIELD_ROW_RE = re.compile(
    r"^\s*(?P<bits>\d{1,2}\s*[:,\-]\s*\d{1,2}|\d{1,2})\s+"
    r"(?P<field>[A-Za-z_][A-Za-z0-9_\[\]:]*)\s+"
    r"(?P<type>R/W|R/RC|R-0|RW|RO|WO|RC|R|W)\s+"
    r"(?P<reset>[0-9A-Fa-fxX]+[hHbB]?)")


def _infer_device(pdf_path: str) -> tuple[str, str | None]:
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    parent = os.path.basename(os.path.dirname(pdf_path))
    return base, parent


def _norm_access(raw: str | None) -> str | None:
    if not raw:
        return None
    r = raw.strip().upper().replace(" ", "").replace("-", "")
    if r in ("R/W", "RW", "READWRITE"):
        return "RW"
    if r in ("R", "RO", "READONLY", "R0"):
        return "RO"
    if r in ("RC", "R/C", "READTOCLEAR", "RC0"):
        return "RC"
    if r in ("W", "WO", "WRITEONLY"):
        return "WO"
    return None


def _bits_from_spec(spec: str) -> tuple[int, int] | None:
    spec = spec.strip()
    m = re.fullmatch(r"(\d{1,2})\s*[:,\-]\s*(\d{1,2})", spec)
    if m:
        hi, lo = int(m.group(1)), int(m.group(2))
        return (hi, lo) if hi >= lo else (lo, hi)
    m = re.fullmatch(r"(\d{1,2})", spec)
    if m:
        b = int(m.group(1))
        return (b, b)
    return None


def _reg_width_for(bit_hi: int, bit_lo: int) -> int:
    top = max(bit_hi, bit_lo)
    if top <= 7:
        return 8
    if top <= 15:
        return 16
    if top <= 31:
        return 32
    return 64


def _clean_field(raw: str) -> str:
    s = raw.replace("\n", " ").replace("\r", " ")
    s = re.sub(r"\s+", " ", s).strip()
    s = s.strip(" _")
    return s


# ---- 表格结构抽取 ----

def _iter_tables(doc):
    """遍历每个 PDF 页，产出 (page_no, y0, rows)。"""
    for i in range(len(doc)):
        page = doc[i]
        try:
            tabs = page.find_tables()
        except Exception:
            tabs = None
        if not tabs:
            continue
        for t in tabs.tables:
            rows = t.extract()
            if not rows:
                continue
            try:
                y0 = float(t.bbox[1])
            except Exception:
                y0 = 0.0
            yield (i + 1, y0, rows)


def _iter_headings(doc):
    """按文档顺序产出 (page_no, y0, name, address_str, addr_int, reset)。"""
    for i in range(len(doc)):
        page = doc[i]
        d = page.get_text("dict")
        for block in d.get("blocks", []):
            for line in block.get("lines", []):
                text = "".join(s.get("text", "") for s in line.get("spans", []))
                m = _REG_HEAD_RE.search(text)
                if not m:
                    continue
                try:
                    y0 = float(line["bbox"][1])
                except Exception:
                    y0 = 0.0
                addr_int = int(m.group("addr"), 16)
                yield (i + 1, y0, m.group("name").strip(),
                       f"0x{addr_int:x}", addr_int, m.group("reset"))


def _is_field_table(header: list[str]) -> bool:
    joined = " ".join((c or "") for c in header[:4]).lower()
    return "bit" in joined and "field" in joined


def _is_regmap_table(header: list[str]) -> bool:
    joined = " ".join((c or "") for c in header).lower()
    return "address" in joined and "register" in joined


def extract_pdf(pdf_path: str, run_id: str | None = None,
                max_pages: int | None = None) -> list[RegisterFieldCandidate]:
    import pymupdf

    run_id = run_id or uuid.uuid4().hex[:12]
    digest = pdf_sha256(pdf_path)
    device, vendor = _infer_device(pdf_path)

    doc = pymupdf.open(pdf_path)
    try:
        # 事件流：寄存器标题 + 字段表 + 寄存器总表，按文档顺序归并
        events: list[tuple[int, float, str, object]] = []
        for pno, y0, name, addr, addr_int, reset in _iter_headings(doc):
            events.append((pno, y0, "head", {"name": name, "addr": addr,
                                            "addr_int": addr_int, "reset": reset}))
        regmap: dict[str, dict] = {}
        for pno, y0, rows in _iter_tables(doc):
            header = [(c or "").replace("\n", " ") for c in rows[0]]
            if _is_field_table(header):
                events.append((pno, y0, "fields", rows[1:]))
            elif _is_regmap_table(header):
                # 总表：登记 acronym/寄存器名 → 地址（弱证据，仅作归属兜底）
                for r in rows[1:]:
                    first = (r[0] or "").strip()
                    am = re.match(r"([0-9A-Fa-f]{1,4})[hH]\s+(R/W|R/RC|R-0|RW|RO|WO|RC|R|W)", first)
                    if not am:
                        continue
                    addr_int = int(am.group(1), 16)
                    key = first.upper()
                    regmap[key] = {"addr": f"0x{addr_int:x}",
                                   "access": _norm_access(am.group(2))}
        events.sort(key=lambda e: (e[0], e[1]))

        candidates: list[RegisterFieldCandidate] = []
        seen: set[tuple[int, str, int, int]] = set()
        cur: dict | None = None

        for pno, _y, kind, payload in events:
            if max_pages and pno > max_pages:
                continue
            if kind == "head":
                cur = payload
                continue
            if kind == "fields":
                for row in payload:
                    if not row or len(row) < 4:
                        continue
                    bits_spec = (row[0] or "").strip()
                    field = _clean_field(row[1] or "")
                    typ = (row[2] or "").strip()
                    reset = (row[3] or "").strip()
                    bits = _bits_from_spec(bits_spec)
                    if not bits or not field:
                        continue
                    addr = cur["addr"] if cur else None
                    access = _norm_access(typ) or None
                    if addr is None:
                        continue  # 无地址证据 → 弃答
                    reset = None if reset.lower().startswith("x") else reset
                    key = (pno, addr, bits[0], bits[1])
                    if key in seen:
                        continue
                    seen.add(key)
                    w = _reg_width_for(bits[0], bits[1])
                    candidates.append(RegisterFieldCandidate(
                        run_id=run_id, pdf_path=os.path.abspath(pdf_path),
                        pdf_sha256=digest, device=device, vendor=vendor,
                        page=pno, address=addr, address_int=int(addr, 16),
                        field_name=field, reg_width=w,
                        bit_hi=bits[0], bit_lo=bits[1],
                        bit_mask=bits_to_mask(bits[0], bits[1]),
                        access=access, reset=reset,
                        evidence=f"{field} {bits_spec}",
                        confidence="high" if cur else "medium",
                    ))

        if not candidates:
            candidates = _fallback_lines(doc, pdf_path, digest, device, vendor, run_id)
        return candidates
    finally:
        doc.close()


def _fallback_lines(doc, pdf_path, digest, device, vendor, run_id):
    """无表格结构时的纯文本逐行回退（保守，通常候选较少）。"""
    candidates: list[RegisterFieldCandidate] = []
    for i in range(len(doc)):
        text = doc[i].get_text()
        for ln in text.splitlines():
            ln = ln.strip()
            if not ln or len(ln) > 160:
                continue
            m = _FIELD_ROW_RE.match(ln)
            if not m:
                continue
            bits = _bits_from_spec(m.group("bits"))
            if not bits:
                continue
            candidates.append(RegisterFieldCandidate(
                run_id=run_id, pdf_path=os.path.abspath(pdf_path), pdf_sha256=digest,
                device=device, vendor=vendor, page=i + 1, address="",
                address_int=0, field_name=_clean_field(m.group("field")),
                reg_width=_reg_width_for(bits[0], bits[1]),
                bit_hi=bits[0], bit_lo=bits[1], bit_mask=bits_to_mask(bits[0], bits[1]),
                access=_norm_access(m.group("type")), reset=m.group("reset"),
                evidence=ln[:200], confidence="low"))
    return candidates