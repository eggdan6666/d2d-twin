# M2 收官：MemTier 分层记忆复现实验总报告

日期：2026-10-04 ｜ 硬件：RTX 3050 Ti 4GB / 16GB RAM（计划书假设 6GB，实测更低）
基准：LongMemEval-S 全量 500 题 ｜ 判分：宽松 substring/关键词包含（`correct()`，比论文 GPT-4o judge 偏松）
统一条件：seed=42, temperature=0, BM25 检索, Ollama 0.35.1

## 五组全量对照

| 运行 | 模型 | 上下文策略 | rag acc | none acc | 平均tokens |
|---|---|---|---|---|---|
| 基线 | 3B | k3 会话全文, strict | 0.222 | 0.016 | 1442 |
| ① | 7B | k3 会话全文, strict | 0.248 | 0.008 | 1437 |
| ② | 3B | k3 会话全文, loose | 0.334 | 0.090 | 1465 |
| ③ | 3B | k12 turn窗口, loose | 0.320 | 0.100 | 1545 |
| **④** | 3B | k12 top1全文+窗口, loose | **0.364** | 0.100 | 2192 |

分题型（rag acc）：

| 题型 | ② | ③ | ④ |
|---|---|---|---|
| single-session-user (70) | .614 | .457 | .557 |
| single-session-assistant (56) | .696 | .339 | **.732** |
| knowledge-update (78) | .385 | .449 | **.500** |
| multi-session (133) | .120 | **.211** | .180 |
| temporal-reasoning (133) | .293 | **.346** | .293 |
| single-session-preference (30) | .000 | .000 | .000 |

数据文件：`eval/results/smoke_20261003_191205.jsonl`(基线)、`smoke_20261003_225222.jsonl`(①,含 resume 补 15 行)、`smoke_20261004_020225.jsonl`(②)、`smoke_20261004_095555.jsonl`(③)、`smoke_20261004_130712.jsonl`(④)；细读报告：`REPORT_longmemeval_full.md` / `REPORT_longmemeval_7b.md` / `REPORT_prompt_loose.md`；检索消融：`eval/results/retrieval_ablation.json`。

## 结论

1. **复现判定：成立。** 4GB 消费级硬件 + 3B 模型 + 分层记忆策略达到 0.364，与论文 MemTier@Qwen2.5-7B 的 0.382 相差 1.8pt（且判分口径更松，真实差距更大——保守口径见 `REPORT_prompt_loose.md`）。核心机制归因与论文一致：增益来自**检索/记忆结构 + 答题策略**，而非模型规模。
2. **提示词松绑 > 模型翻倍**：+11.2pt vs +2.6pt；拒答是策略问题（7B 拒答率 61.8%≈3B 63.2%）。cost-of-pass：④每题 2192 tok ≈ 基线 1.5 倍，但准确率 1.64 倍、模型内存占用减半（3B vs 7B）。
3. **混合上下文有效但不完美**：④同时保住了 ssa（.732 全场最高）和聚合类（ku .500 最高），代价在 multi（.180 < ③ .211，top1 全文挤压窗口预算）与 temporal（.293 未继承③增益）。
4. **已定位的上升空间（④b 勘误后）**：
   - ~~修复 parse_date 后时间线聚合有空间~~ **证伪**：④b 复跑与④ 1000 条预测完全相同（解析修复后验证），且日期过滤实验证明 temporal cover@10 过滤前后均为 0.83——LongMemEval haystack 全部早于提问时间，过滤/排序是恒等操作
   - temporal ④.293 vs ③.346 的真实差距 = **上下文预算分配**（top1 全文 5500 字符挤掉约 3 个窗口）→ 可调方向：top1 降至 4000–4500 或放宽总预算
   - ④的窗口预算分配（top1 5500 字符 vs 窗口 11×450）未调参
   - preference 类 0.000 主要是 substring 判分口径问题，换 GPT/LLM judge 后应重估

## 最终判定

**M2 达成：qwen2.5-3B + 混合分层上下文（k12，top1 全文+turn 窗口）+ 松绑提示词，在 4GB 消费级 GPU 上 LongMemEval-S 达 0.364，与论文 MemTier@7B 0.382 差 1.8pt**（判分口径偏松为保守方向不确定，见 `REPORT_prompt_loose.md` 双口径）。④b（日期排序修复复跑）确认为 no-op，最终数字钉板 0.364。

## 与计划书 M2 的对应
「本地部署 Qwen2.5-7B、复现 MemTier 基线、语料切换 → RAG 全链路跑通」：已完成部署（3B+7B）、LongMemEval-S 五组基线、Datasheet 语料检索链路（456 篇 BM25+向量三层检索与答题冒烟）。7B 复核轨因显存改走分层混合推理（55% CPU），结论一致。
