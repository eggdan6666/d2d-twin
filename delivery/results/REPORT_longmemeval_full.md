# LongMemEval-S 500 题全量基线报告

- **运行时间**：2026-10-03 19:12:05 → 20:31:50（约 80 分钟，单次运行完成，无中断/重启）
- **配置**：`python eval/run_longmemeval.py --n 500 --k 3`，模型 `qwen2.5:3b-instruct`（Ollama 0.35.1，GPU），检索器 BM25（会话级，top-k=3，上下文上限 9000 字符），判分为宽松 substring/关键词包含（`correct()` 于 run_longmemeval.py）
- **结果文件**：`eval/results/smoke_20261003_191205.jsonl`（1000 行 = 500 题 × 2 条件，qid 去重后无重复）
- **日志**：`_setup/lme_full.log` / `_setup/lme_full.err`（err 为空）

## 总体统计

| 条件 | 准确率 | 平均 tokens/题 | 平均延迟 |
|---|---|---|---|
| rag（BM25 会话检索增强） | **0.222** (111/500) | 1442 | 6.7s |
| none（裸模型直答） | **0.016** (8/500) | 96 | 2.7s |

- rag 相对 none 提升约 **14 倍**，证明检索增强有效。
- rag 条件 **gold 会话召回率均值 = 0.849**（含 gold 会话标注的 500 题）；93.6% 的题目至少检索命中一个 gold 会话。

## 按 question_type 分组

| question_type | 题数 | rag acc | none acc |
|---|---|---|---|
| single-session-assistant | 56 | 0.732 | 0.107 |
| single-session-user | 70 | 0.529 | 0.000 |
| knowledge-update | 78 | 0.231 | 0.000 |
| multi-session | 133 | 0.053 | 0.000 |
| temporal-reasoning | 133 | 0.060 | 0.015 |
| single-session-preference | 30 | 0.000 | 0.000 |

短板集中在 **multi-session（0.053）**、**temporal-reasoning（0.060）** 和 **preference（0.000）**；后两类各占 133/30 题，是主要失分来源。

## 失败样本分析（rag 条件，389 题失败）

| 失败模式 | 数量 | 占失败比例 |
|---|---|---|
| 拒答（INSUFFICIENT_CONTEXT） | 302 | 77.6% |
| **检索命中 gold 会话但仍拒答** | 275 | **70.7%** |
| 检索命中但答错（非拒答） | 82 | 21.1% |
| 检索未命中 | 32 | 8.2% |

关键结论：**检索侧基本没问题**（gold 召回 0.849，未命中仅 8.2%），瓶颈在生成侧——约七成失败是"上下文里已有答案，3b 模型仍选择拒答"，属小模型指令遵循/信心阈值问题，而非检索问题。拒答源于 SYS 提示"excerpts are insufficient → 回复 INSUFFICIENT_CONTEXT"被过度触发。

## 与论文参照对比（LongMemEval-S, Qwen2.5-7B）

| 方案 | 准确率 |
|---|---|
| MemTier 裸长上下文（论文） | ≈0.05 |
| 本次 none（无上下文裸答） | 0.016 |
| 本次 rag（qwen2.5:3b + BM25 会话检索 k=3） | **0.222** |
| MemTier 分层记忆（论文） | ≈0.382 |

本次结果落在预期区间（0.05 ~ 0.382）内、偏中段。差异归因：

1. **模型规模**：本次用 qwen2.5:3b-instruct，论文用 Qwen2.5-7B。3b 生成能力弱是本跑与 0.382 差距的主因（大量命中检索却拒答），换 7b（已部署，约 15 tok/s）预计可显著收敛。
2. **检索/记忆结构**：本次是 BM25 会话级 top-3 截断（9000 字符、单会话截 6000），multi-session 需跨多会话聚合、temporal 需日期推理，截断+词面匹配对这两类天然不利；MemTier 分层记忆保留跨会话摘要与时间线，正是为这些题型设计。
3. **判分方式**：本次为宽松 substring/关键词包含判分，通常会让数字**偏高**；论文用 GPT-4o judge。即便如此仍只有 0.222，进一步说明瓶颈在检索命中后的生成/拒答，而非判分。注意 preference 类在 substring 判分下全 0——该题型 gold 是开放表述，宽松判分也不匹配，此题型的 0.000 有判分口径成分，不可直接跨设定比较。
4. **none 对照口径不同**：论文"裸长上下文"是把全部历史塞进上下文，本次 none 是完全不给上下文，0.016 < 0.05 属合理（信息更少）。

## 复现/后续建议

- 相同脚本跑 `--model qwen2.5:7b-instruct`（或其他已部署 7b）对照，验证"拒答瓶颈随模型规模缓解"的归因。
- multi-session / temporal 类可考虑提高 k、放宽 MAX_CHARS 或引入分层摘要（即 MemTier 思路）后再评。

---
*统计脚本：`_setup/analyze_full.py`（只读分析，未改动 rag/ 与 eval/run_longmemeval.py）。*
