# -*- coding: utf-8 -*-
"""rag_extraction_v1 —— 上游 RAG 抽取适配（试探性原型）。

本目录为 Silver 候选区，只产出【候选 JSON】，绝不写入正式 IR（d2d/ir/）。
"""
from .schema import SCHEMA_VERSION, RegisterFieldCandidate
from .extractor import extract_pdf

__all__ = ["SCHEMA_VERSION", "RegisterFieldCandidate", "extract_pdf"]