# -*- coding: utf-8 -*-
"""Silver 候选区数据契约（rag_extraction_v1）。

这里定义的只是【候选】字段，对应 AEI 方案中
「PDF/解析文本 → 检索证据 → Silver 候选 → 来源/条件审核 → 单写入者晋升 → 只读 Gold」的
Silver 环节。任何由此 schema 产出的记录都被标记为 status="silver_candidate"，
不得与 d2d/ir/ 下的 Gold IR（schema "d2d-ir-v1"）混用或互相印证。

字段设计对齐 REVIEW 的「字段几何」门禁最小集：
身份溯源（pdf_sha256 / page）+ 字段几何（address / bit_mask）+ 行为占位（access/reset）。
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict

SCHEMA_VERSION = "rag-silver-v1"
STATUS = "silver_candidate"

# 抽取本身是启发式的，允许低置信度候选；不要伪造高置信度。
CONFIDENCES = ("low", "medium", "high")


def bits_to_mask(bit_hi: int, bit_lo: int) -> int:
    """把 [bit_hi:bit_lo] 转成整数位掩码（含端点）。例：15:7 -> 0xFF80。"""
    if bit_hi < bit_lo:
        bit_hi, bit_lo = bit_lo, bit_hi
    width = bit_hi - bit_lo + 1
    return ((1 << width) - 1) << bit_lo


@dataclass
class RegisterFieldCandidate:
    run_id: str            # 抽取运行 ID，用于溯源本轮批次
    pdf_path: str          # 输入 PDF 绝对路径
    pdf_sha256: str        # PDF 字节级 SHA-256，锁定来源版本
    device: str            # 器件名（从文件名/标题推断，可能不准确）
    vendor: str | None     # 厂商（从 PDF 父目录名推断，弱证据）
    page: int              # PDF 物理页号（1 起）
    address: str           # 寄存器地址，规范化为 "0x.." 小写
    address_int: int
    field_name: str        # 字段名（启发式，可能为空串占位）
    reg_width: int         # 寄存器位宽（默认 16，需来源确认）
    bit_hi: int
    bit_lo: int
    bit_mask: int          # 有效掩码 = bits_to_mask(bit_hi, bit_lo)
    access: str | None     # "RO"/"RW"/"R"/"W" 等；未知为 None（不猜）
    reset: str | None      # 原始复位值字符串；未知为 None
    evidence: str          # 命中的原文片段（≤ 200 字符）
    confidence: str        # low/medium/high
    status: str = STATUS

    def to_dict(self) -> dict:
        return asdict(self)


def dump_candidates(candidates: list[RegisterFieldCandidate], out_path: str) -> None:
    """以 JSONL 写候选区；不覆盖主 IR。空候选也写空文件，记录运行事实。"""
    with open(out_path, "w", encoding="utf-8") as f:
        for c in candidates:
            f.write(json.dumps(c.to_dict(), ensure_ascii=False) + "\n")