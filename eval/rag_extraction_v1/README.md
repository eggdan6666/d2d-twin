# rag_extraction_v1 —— 上游 RAG 抽取适配（试探性原型）

本目录是「上游 RAG 抽取」的第一块可运行原型。它回答 AEI 方案中的问题：
**能否在不依赖人工 Gold IR 的前提下，从原始数据手册 PDF 试探性地抽取寄存器字段候选？**

## 定位（Silver 候选区，不是正式 IR）

数据流目标（对齐 `eval/aei_proposal_review_20261014/REVIEW.md`）：

```
PDF/解析文本 → 检索证据 → Silver 候选 → schema/来源/条件审核 → 单写入者晋升 → 只读 Gold
```

本目录只产出**第三阶段「Silver 候选」**：

- 每条记录 `status = "silver_candidate"`；
- 永不写 `d2d/ir/`（正式 Gold IR，schema `d2d-ir-v1`）；
- 测试 oracle 不从同一份未经审核的 Silver 生成，避免错误规范与实现相互印证。

## 产出字段

候选 JSONL 每条记录包含（schema：`rag-silver-v1`）：

| 字段 | 含义 |
|---|---|
| `run_id` | 抽取运行 ID（批次溯源） |
| `pdf_sha256` | PDF 字节级 SHA-256（锁定来源版本） |
| `page` | PDF 物理页号（1 起），证据定位 |
| `address` / `address_int` | 寄存器地址（`0x..` 归一化） |
| `bit_hi` / `bit_lo` | 位域端点 |
| `bit_mask` | 有效位掩码 = `bits_to_mask(hi, lo)` |
| `access` / `reset` | 访存属性与复位值；**未知保持 `null`，不猜测** |
| `evidence` | 命中的原文片段（≤ 200 字符） |
| `confidence` | `low / medium / high`（启发式置信度，仅作审阅优先级） |
| `status` | 固定 `silver_candidate` |

## 运行

```bash
python -m eval.rag_extraction_v1.run \
  --pdf corpus/data/raw_pdf/TI/TMP100.pdf \
  --out eval/rag_extraction_v1/candidates.jsonl
```

## 已知局限（如实声明）

- **纯启发式**：基于 PyMuPDF 表格结构重建 + 正则字段行回退，跨页表格、图像型寄存器表（无文本层）无法覆盖，漏抽/弃答属预期而非缺陷。
- **位宽按最高位推断（8/16/32）**：未从来源逐片确认，`reg_width` 仅作占位，晋升 Gold 前必须人工校对。
- **不做来源审核**：`confidence` 只决定审阅顺序，不替代逐条对原著核验。
- **不写正式 IR**：晋升动作由单写入者/其他流程负责，本模块无写 `d2d/ir/` 的入口。