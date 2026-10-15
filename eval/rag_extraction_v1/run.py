# -*- coding: utf-8 -*-
"""CLI：python -m eval.rag_extraction_v1.run --pdf <path> [--out <jsonl>]

输出到 eval/rag_extraction_v1/ 内的候选文件，绝不写 d2d/ir/。
"""
from __future__ import annotations

import argparse
import os
import sys

from .extractor import extract_pdf
from .schema import dump_candidates

DEFAULT_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "candidates.jsonl")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="寄存器字段 Silver 候选抽取器（试探性）")
    p.add_argument("--pdf", required=True, help="数据手册 PDF 路径")
    p.add_argument("--out", default=DEFAULT_OUT, help="候选 JSONL 输出路径")
    p.add_argument("--max-pages", type=int, default=None, help="仅处理前 N 页（调试）")
    p.add_argument("--run-id", default=None, help="抽取运行 ID（默认自动生成）")
    args = p.parse_args(argv)

    if not os.path.isfile(args.pdf):
        print(f"[ERROR] PDF 不存在：{args.pdf}", file=sys.stderr)
        return 2

    cands = extract_pdf(args.pdf, run_id=args.run_id, max_pages=args.max_pages)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    dump_candidates(cands, args.out)
    print(f"[OK] 产出 {len(cands)} 条 Silver 候选 -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())