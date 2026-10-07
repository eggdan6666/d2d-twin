# -*- coding: utf-8 -*-
"""构建向量索引缓存（一次性，约30分钟CPU）。
用法（项目根）: python -m rag.build_vectors"""
import os, sys, time
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("RAG_EMBED_MODEL", "BAAI/bge-small-zh-v1.5")
sys.stdout.reconfigure(encoding="utf-8")

from rag.hierarchical import HierarchicalRetriever, CACHE

t0 = time.time()
r = HierarchicalRetriever()
print(f"model={os.environ['RAG_EMBED_MODEL']} chunks={len(r.chunks)} "
      f"matrix={r.vec_matrix.shape} time={time.time()-t0:.0f}s cache={CACHE}")
