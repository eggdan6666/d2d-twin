# -*- coding: utf-8 -*-
"""轻量 BM25（Okapi），无第三方依赖。"""
from __future__ import annotations
import math, re
from collections import Counter

TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9_\-/]*|\d+(?:\.\d+)?")
SPLIT = re.compile(r"[a-z]+|\d+")

def tokenize(text: str):
    out = []
    for t in TOKEN.findall(text):
        t = t.lower()
        out.append(t)
        if len(t) > 3 and re.search(r"\d", t):
            out += [s for s in SPLIT.findall(t) if len(s) > 1]
    return out

class BM25:
    def __init__(self, docs, k1=1.4, b=0.75):
        self.k1, self.b = k1, b
        self.df = {}
        tokenized = []
        for d in docs:
            toks = set(t for t in tokenize(d) if t)
            tokenized.append(toks)
            for t in toks:
                self.df[t] = self.df.get(t, 0) + 1
        self.doc_toks = [Counter(tokenize(d)) for d in docs]
        self.lens = [sum(c.values()) or 1 for c in self.doc_toks]
        self.avg_len = sum(self.lens) / max(1, len(self.lens))
        self.n = len(docs)

    def search(self, query, top_k=10):
        q = set(tokenize(query))
        scores = [0.0] * self.n
        for t in q:
            df = self.df.get(t)
            if not df:
                continue
            idf = math.log(1 + (self.n - df + 0.5) / (df + 0.5))
            for i, cnt in enumerate(self.doc_toks):
                f = cnt.get(t)
                if f:
                    scores[i] += idf * f * (self.k1 + 1) / (
                        f + self.k1 * (1 - self.b + self.b * self.lens[i] / self.avg_len))
        order = sorted(range(self.n), key=lambda i: -scores[i])[:top_k]
        return [(i, scores[i]) for i in order if scores[i] > 0]
