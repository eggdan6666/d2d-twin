# -*- coding: utf-8 -*-
"""编排层（计划书 §4.4）: 查询解析→分层检索→小模型作答→归属校验→按需升级API。"""
from __future__ import annotations
import os, re
from . import llm
from .hierarchical import HierarchicalRetriever
from .verify import check_attribution

SMALL = os.environ.get("RAG_SMALL_MODEL", "qwen2.5:3b-instruct")
BIG = os.environ.get("RAG_ESCALATE_MODEL", "scnet:DeepSeek-V4.1-Flash-Event")
SYSTEM = ("You are an electronics datasheet QA assistant. Give exact values with units "
          "from the excerpts. Be concise.")


class Orchestrator:
    def __init__(self, retriever=None, small=None, big=None, escalate=True, k=5):
        self.retr = retriever or HierarchicalRetriever()
        self.small, self.big, self.escalate, self.k = small or SMALL, big or BIG, escalate, k

    @staticmethod
    def parse_parts(question: str):
        parts = []
        m = re.search(r"larger:\s*([\w\-.]+)\s+or\s+([\w\-.]+)\?", question)
        if m:
            parts = [m.group(1), m.group(2)]
        m2 = re.search(r"of ([\w\-.]+) \(", question)
        if m2 and m2.group(1) not in parts:
            parts = parts or [m2.group(1)]
        return parts

    def answer(self, question: str):
        parts = self.parse_parts(question)
        if parts:
            ctx, hits = self.retr.context_for_parts(question, parts, k=self.k)
        else:
            ctx, hits = self.retr.context_for(question, k=self.k)
        flag = "none" if len(ctx) >= 200 else "ctx_empty"
        prompt = f"Datasheet excerpts:\n{ctx}\n\nQuestion: {question}"
        r = llm.chat(prompt, model=self.small, system=SYSTEM, timeout=600)
        rec = {"model": self.small, "ctx_flag": flag, "escalated": False,
               "verify": None, "sources": [h["chunk_id"] for h in hits]}
        if len(parts) >= 2:
            docs = {p.upper(): self.retr.doc_text(p) for p in parts}
            v = check_attribution(r["text"], ctx, doc_texts=docs)
            rec["verify"] = {"first_ok": v["ok"], "n_err": len(v["errors"])}
            if not v["ok"] and self.escalate:
                r = llm.chat(prompt, model=self.big, system=SYSTEM, timeout=600)
                rec.update({"model": self.big, "escalated": True})
                v2 = check_attribution(r["text"], ctx, doc_texts=docs)
                rec["verify"]["retry_ok"] = v2["ok"]
        rec["text"] = r["text"]
        rec["prompt_tokens"] = r["prompt_tokens"]
        rec["completion_tokens"] = r["completion_tokens"]
        rec["latency_s"] = r["latency_s"]
        return rec
