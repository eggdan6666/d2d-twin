# -*- coding: utf-8 -*-
"""语料加载：读取 corpus/data/index/corpus_index.jsonl 与章节切片。"""
from __future__ import annotations
import json, os, re
from dataclasses import dataclass, field

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "corpus", "data")


@dataclass
class Chunk:
    chunk_id: str          # {doc_id}::{section}::{n}
    doc_id: str
    part: str
    manufacturer: str
    category: str
    section: str
    path: str              # 绝对路径
    year: int | None = None
    _text: str = field(default="", repr=False)

    @property
    def text(self):
        if not self._text:
            with open(self.path, encoding="utf-8") as f:
                self._text = f.read()
        return self._text


def _manifest_categories():
    try:
        import sys
        sys.path.insert(0, os.path.join(ROOT, "corpus", "scripts"))
        from manifest import build_entries
        return {e["part"].upper(): e["category"] for e in build_entries()}
    except Exception:
        return {}


def load_chunks(corpus_dir=CORPUS):
    index = os.path.join(corpus_dir, "index", "corpus_index.jsonl")
    cats = _manifest_categories()
    chunks = []
    with open(index, encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            cdir = os.path.join(corpus_dir, "chunks", e["id"])
            for c in e["chunks"]:
                chunks.append(Chunk(
                    chunk_id=f"{e['id']}::{c['file'][:-3]}",
                    doc_id=e["id"], part=e["part"],
                    manufacturer=e["manufacturer"],
                    category=cats.get(e["part"].upper(), ""),
                    section=c["section"], path=os.path.join(cdir, c["file"]),
                    year=e.get("year")))
    return chunks
