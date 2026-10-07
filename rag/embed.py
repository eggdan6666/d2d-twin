# -*- coding: utf-8 -*-
"""向量后端：sentence-transformers 本地模型（如 BAAI/bge-small-zh-v1.5，
经 RAG_EMBED_MODEL 环境变量启用）。模型名以 'ollama:' 开头时走 Ollama
/api/embed（如 nomic-embed-text）。"""
from __future__ import annotations
import os, json, urllib.request

MODEL = lambda: os.environ.get("RAG_EMBED_MODEL", "")
_model = None

def available():
    return bool(MODEL())

def is_ollama():
    return MODEL().startswith("ollama:")

def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL())
    return _model

def _ollama_embed(texts):
    body = json.dumps({"model": MODEL().split(":", 1)[1], "input": texts}).encode()
    req = urllib.request.Request("http://localhost:11434/api/embed",
                                 data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)["embeddings"]

def encode(texts, batch_size=32):
    import numpy as np
    if is_ollama():
        out = []
        for i in range(0, len(texts), 64):
            out.extend(_ollama_embed(texts[i:i + 64]))
        v = np.asarray(out, dtype="float32")
    else:
        v = np.asarray(_get_model().encode(texts, batch_size=batch_size,
                                           normalize_embeddings=True), dtype="float32")
    norms = np.linalg.norm(v, axis=1, keepdims=True)
    return v / np.clip(norms, 1e-9, None)

def topk(query, matrix, cand_idx, k):
    import numpy as np
    if not available() or matrix is None or len(cand_idx) == 0:
        return []
    q = encode([query])[0]
    sims = matrix[cand_idx] @ q
    order = np.argsort(-sims)[:k]
    return [(cand_idx[i], float(sims[i])) for i in order]
