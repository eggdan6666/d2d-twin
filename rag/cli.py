# -*- coding: utf-8 -*-
"""检索 CLI。用法（项目根目录）:
  python -m rag.cli "TPS5430 absolute maximum input voltage" -k 3
  python -m rag.cli "LM317 output voltage range" --json
"""
import sys, json, argparse
sys.stdout.reconfigure(encoding="utf-8")
from .hierarchical import HierarchicalRetriever


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("-k", type=int, default=5)
    ap.add_argument("--json", action="store_true", help="输出完整 JSON")
    args = ap.parse_args()
    r = HierarchicalRetriever()
    print(f"[语料] {len(r.docs)} 文档 / {len(r.chunks)} 切片 / "
          f"向量后端: {'ON' if r.vec_matrix is not None else 'OFF(BM25)'}")
    for hit in r.retrieve(args.query, k=args.k):
        if args.json:
            print(json.dumps(hit, ensure_ascii=False))
        else:
            print(f"\n=== {hit['part']} [{hit['manufacturer']}] "
                  f"§{hit['section']} score={hit['score']}")
            print(hit["text"][:400])

if __name__ == "__main__":
    main()
