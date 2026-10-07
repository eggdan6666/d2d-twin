# -*- coding: utf-8 -*-
"""分层检索（MemTier 式三层）：
Tier1 文档画像粗检 → Tier2 候选内切片精检（BM25+向量 RRF 融合）
→ Tier3 同文档邻接切片扩展。"""
from __future__ import annotations
import os, pickle
from .corpus import load_chunks, CORPUS
from .bm25 import BM25, tokenize
from . import embed

TIER1_SNIPPET = 300
MAX_CONTEXT = 6000
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache_index.pkl")
BM25_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache_bm25.pkl")


class HierarchicalRetriever:
    def __init__(self, use_cache=True):
        self.chunks = load_chunks()
        self.docs = {}
        for i, c in enumerate(self.chunks):
            d = self.docs.setdefault(c.doc_id, {"part": c.part, "manufacturer": c.manufacturer,
                                                "category": c.category, "year": c.year,
                                                "sections": set(), "chunk_ids": []})
            d["sections"].add(c.section)
            d["chunk_ids"].append(i)
        self.doc_ids = sorted(self.docs)
        profiles = [self._profile(did) for did in self.doc_ids]
        meta = {"n_chunks": len(self.chunks),
                "chars": sum(len(c.text) for c in self.chunks)}
        loaded = None
        if use_cache and os.path.isfile(BM25_CACHE):
            try:
                loaded = pickle.load(open(BM25_CACHE, "rb"))
                if loaded.get("meta") != meta:
                    loaded = None
            except Exception:
                loaded = None
        if loaded:
            self.tier1, self.tier2 = loaded["tier1"], loaded["tier2"]
        else:
            self.tier1 = BM25(profiles)
            self.tier2 = BM25([c.text for c in self.chunks])
            try:
                pickle.dump({"meta": meta, "tier1": self.tier1, "tier2": self.tier2},
                            open(BM25_CACHE, "wb"), protocol=4)
            except Exception:
                pass
        self.vec_matrix = None
        if embed.available():
            meta = {"model": embed.MODEL(), "n_chunks": len(self.chunks)}
            if use_cache and os.path.isfile(CACHE):
                try:
                    cached = pickle.load(open(CACHE, "rb"))
                    if cached.get("meta") == meta:
                        self.vec_matrix = cached["matrix"]
                except Exception:
                    self.vec_matrix = None
            if self.vec_matrix is None:
                self.vec_matrix = embed.encode([c.text[:1500] for c in self.chunks])
                pickle.dump({"meta": meta, "matrix": self.vec_matrix},
                            open(CACHE, "wb"))

    def _profile(self, did):
        d = self.docs[did]
        head = self.chunks[d["chunk_ids"][0]].text[:TIER1_SNIPPET]
        return f"{d['part']} {d['manufacturer']} {d['category']} " \
               f"{' '.join(sorted(d['sections']))}\n{head}"

    def retrieve(self, query, k=5, tier1_n=8, tier2_n=200, rrf_c=60):
        hits1 = self.tier1.search(query, top_k=tier1_n)
        if not hits1:
            return []
        cand = set()
        for idx, _s in hits1:
            cand.update(self.docs[self.doc_ids[idx]]["chunk_ids"])
        fused = {}
        for rank, (i, s) in enumerate(self.tier2.search(query, top_k=tier2_n)):
            if i in cand:
                fused[i] = fused.get(i, 0) + 1.0 / (rrf_c + rank + 1)
        if self.vec_matrix is not None:
            for rank, (i, s) in enumerate(embed.topk(query, self.vec_matrix,
                                                      sorted(cand), tier2_n)):
                fused[i] = fused.get(i, 0) + 1.0 / (rrf_c + rank + 1)
        best = sorted(fused, key=lambda i: -fused[i])[:k]
        return [self._result(i, fused[i]) for i in best]

    def _result(self, i, score):
        c = self.chunks[i]
        return {"chunk_id": c.chunk_id, "part": c.part, "doc_idx": i,
                "manufacturer": c.manufacturer, "section": c.section,
                "score": round(score, 4), "path": c.path, "text": c.text}

    def _doc_ids_for_part(self, part):
        pu = part.upper().replace(" ", "")
        return [did for did, d in self.docs.items()
                if d["part"].upper().replace(" ", "") == pu
                or pu in d["part"].upper().replace(" ", "")]

    def context_for_parts(self, query, parts, k=3, total=8000):
        """跨文档题: 每个型号各取 top-k. 排名用词重叠(实测优于BM25分桶: cross 4/27 vs 1/27)."""
        per = max(800, total // max(1, len(parts) * k))
        blocks, hits = [], []
        for p in parts:
            for did in self._doc_ids_for_part(p)[:1]:
                cand = self.docs[did]["chunk_ids"]
                qtok = set(tokenize(query + " " + p))
                scored = []
                for i in cand:
                    ov = len(qtok & set(tokenize(self.chunks[i].text[:800])))
                    if ov:
                        scored.append((i, ov))
                scored.sort(key=lambda x: -x[1])
                order = [i for i, _ in scored[:k]] or cand[:1]
                for i in order:
                    c = self.chunks[i]
                    blocks.append(f"[{c.part} §{c.section}]\n{c.text[:per]}")
                    hits.append(self._result(i, dict(scored).get(i, 0)))
        return "\n\n---\n\n".join(blocks), hits

    def doc_text(self, part):
        dids = self._doc_ids_for_part(part)[:1]
        if not dids:
            return ""
        return "\n".join(self.chunks[i].text for i in self.docs[dids[0]]["chunk_ids"])

    def expand(self, hits, window=1):
        """Tier3：把每个命中切片扩展为同文档相邻 window 个切片的连续上下文。"""
        extra = {}
        for h in hits:
            i, d = h["doc_idx"], None
            for j in range(i - window, i + window + 1):
                if 0 <= j < len(self.chunks) and self.chunks[j].doc_id == self.chunks[i].doc_id \
                        and j != i:
                    extra.setdefault(j, self.chunks[j].text)
        return extra

    def context_for(self, query, k=3, max_chars=MAX_CONTEXT):
        hits = self.retrieve(query, k=k)
        neighbors = self.expand(hits)
        parts, used, seen = [], 0, {h["doc_idx"] for h in hits}
        for h in hits:
            block = f"[{h['part']} §{h['section']}]\n{h['text']}"
            if used + len(block) > max_chars:
                break
            parts.append(block); used += len(block)
        for j in sorted(neighbors):
            c = self.chunks[j]
            block = f"[{c.part} §{c.section}]\n{neighbors[j]}"
            if used + len(block) > max_chars * 0.6:
                break
            parts.append(block); used += len(block)
        return "\n\n---\n\n".join(parts), hits
