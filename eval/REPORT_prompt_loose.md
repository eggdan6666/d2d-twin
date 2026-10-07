# LongMemEval-S 提示词松绑实验报告（实验②）

- **实验**：只改 system 提示词（strict → loose），其余口径与前两次全量完全一致。
- **命令**：`python eval/run_longmemeval.py --n 500 --k 3 --sysmode loose`（默认模型 `qwen2.5:3b-instruct`，未传 `--model`）
- **启动方式**：`powershell -File _setup/run_loose.ps1`（Start-Process 脱离，优先级 BelowNormal），stdout→`_setup/lme_loose.log`，stderr→`_setup/lme_loose.err`
- **运行时间**：2026-10-04 02:02:24 → 03:53:10（约 **111 分钟**，单次完成，无中断、无重启；stderr 全程 0 字节）
- **结果文件**：`eval/results/smoke_20261004_020225.jsonl`（1000 行 = 500 题 × 2 条件，qid 去重后无重复）
- **提示词差异**（`eval/run_longmemeval.py:14-20`）：
  - strict：`... using ONLY these excerpts ... if the excerpts are insufficient, reply INSUFFICIENT_CONTEXT.`
  - loose：`... Answer the question as best you can ... Even if the answer is only implied or partial, give your most likely concrete answer. Never refuse. Be concise.`

## 0. 单变量有效性与并发说明

| 校验项 | 结论 | 来源 |
|---|---|---|
| 检索器/后端未改动 | `rag/bm25.py`(10-02 23:28)、`rag/llm.py`(10-03 16:30) 的 mtime 均**早于**严格版基线运行（10-03 19:12–20:31），本次未修改 | `ls --time-style` |
| 数据未改动 | `data/eval/longmemeval_s.json` mtime 10-03 07:45 | 同上 |
| 检索结果逐题一致 | 三次运行 rag 的 `gold_recall` 均值 **0.8489**、recall>0 比例 **93.60%** 完全相同 | `_setup/analyze_loose.out` |
| 采样确定性 | `llm.chat(temperature=0.0, seed=42)` | `rag/llm.py:9` |
| 脚本改动范围 | `eval/run_longmemeval.py`（10-04 00:11）仅新增 `SYS_LOOSE` 与 `--sysmode`（默认 strict，原路径不变） | 代码审阅 |

**并发事件（需注明）**：
1. 步骤0 检查时（02:00），7B 全量已在 01:33 因 Ollama 瞬断崩溃（`_setup/lme_7b.err` URLError，日志止于 `[492][rag]`、无「汇总」），进程已消失 → 按指令不再等待，直接启动本实验。
2. 03:12–03:18 期间，另一会话的 `_setup/resume7b.py` 并行补跑了 7B 缺失的 idx 492–499（15 行，追加回 `smoke_20261003_225222.jsonl`，03:17:42 写入），因此 **7B 对照现在是 500 题完整**，本实验未受其影响（无重启）。
3. 重叠污染仅限延迟：7B 的补跑说明亦称其延迟被模型切换污染、准确率不受影响。本实验 rag 在重叠窗口（idx 300–345）平均延迟 10.84s，剔除该窗口后 8.61s（总体 8.81s）→ 对总体延迟影响约 +0.2s，可忽略。

## ① 三组对照表（n=500，同一 500 题，k=3，BM25 会话级）

| 运行 | 模型 | 提示词 | rag acc | none acc | rag 字面拒答 | rag 语义回避(宽口径) | rag 平均tokens | rag 平均延迟 | rag completion tokens |
|---|---|---|---|---|---|---|---|---|---|
| strict-3B（基线） | qwen2.5:3b-instruct | strict | **0.2220** | 0.0160 | 302 (60.4%) | 316 (63.2%) | 1442.1 | 6.74s | 18.2 |
| loose-3B（本实验） | qwen2.5:3b-instruct | loose | **0.3340** | 0.0900 | **0 (0.0%)** | 145 (29.0%) | 1464.5 | 8.81s¹ | 29.6 |
| 7B-strict（对照） | qwen2.5:7b-instruct-q4_K_M | strict | **0.2480** | 0.0080 | 308 (61.6%) | 309 (61.8%) | 1436.9 | 15.57s² | 12.9 |

¹ 剔除并行重叠窗口后 8.61s。² 含 03:12–03:18 并行补跑的 7 题，延迟不可比。

- 来源：strict-3B 见 `eval/REPORT_longmemeval_full.md` 及 `eval/results/smoke_20261003_191205.jsonl`；loose-3B 见 `eval/results/smoke_20261004_020225.jsonl`，并与 `_setup/lme_loose.log` 汇总行（`rag acc=0.33 平均tokens=1464 平均延迟=8.8s / none acc=0.09 平均tokens=121 平均延迟=4.3s`）一致；7B-strict 见 `eval/results/smoke_20261003_225222.jsonl`（`_setup/lme_7b.log` 汇总行 `rag acc=0.248 (124/500) | none acc=0.008 (4/500)`）。全部数字由 `_setup/analyze_loose.py` / `_setup/analyze_loose_extra.py` 重算（口径复制自 `_setup/analyze_full.py`，原文件未改）。
- 「字面拒答」= pred 含 `insufficient`（忽略大小写）；「语义回避」= 额外匹配 `not contain / don't have / no information / cannot determine / not specified / unable to answer …` 等改写型拒答（启发式，见 `_setup/analyze_loose_extra.py`）。

### 分 question_type（rag 条件准确率）

| question_type | 题数 | strict-3B | loose-3B | loose-3B 保守³ | 7B-strict | loose none | loose none 保守 |
|---|---|---|---|---|---|---|---|
| temporal-reasoning | 133 | 0.060 | **0.293** | 0.241 | 0.128 | 0.180 | 0.090 |
| single-session-assistant | 56 | 0.732 | **0.696** ↓ | 0.679 | 0.786 | 0.107 | 0.089 |
| single-session-user | 70 | 0.529 | **0.614** | 0.614 | 0.486 | 0.043 | 0.043 |
| knowledge-update | 78 | 0.231 | **0.385** | 0.385 | 0.295 | 0.013 | 0.000 |
| multi-session | 133 | 0.053 | **0.120** | 0.098 | 0.045 | 0.083 | 0.030 |
| single-session-preference | 30 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

³ 「保守」= 剔除「判对但语句实为回避」的疑似判分假阳性（宽松 substring/关键词包含判分下，回避句常因含 gold 的单位词如 "days/weeks" 而误判为正确）。来源 `_setup/analyze_loose_qtype.py`。

## ② 松绑增益量化

- **总体**：rag acc 0.2220 → **0.3340**，绝对 **+11.2pt**、相对 **+50.5%**；保守口径 0.2220 → 0.3120（**+9.0pt**）。
- **成对（同题同检索，逐 qid 翻转）**：净 +56 题（**变对 61 / 变错 5**）。分题型净翻转：temporal-reasoning **+31**、knowledge-update **+12**、multi-session **+9**、single-session-user **+6**、single-session-preference 0、single-session-assistant **−2**。来源 `_setup/analyze_loose.out`。
- **拒答消除**：字面 `INSUFFICIENT_CONTEXT` 302 → **0**；失败样本中的拒答占比 81.2% → 40.2%（宽口径）。基线报告的「拒答占失败 77.6%、命中后拒答 70.7%」在本轮已无对应物——loose 的 rag 失败 333 题里，**301 题（90.4%）是「作答了但答错」**，仅 32 题（9.6%）是检索未命中。即失败构成从"不肯答"整体迁移为"答得不对"。
- **对照「换更大模型」的收益**：3B→7B（两者都 strict）仅 0.2220 → 0.2480（**+2.6pt**，净 +13 题：变对 30 / 变错 17），且 7B 的拒答率 61.8% 与 3B 的 63.2% 基本持平。**同一块 GPU 上，一句提示词松绑（+11.2pt）的收益是模型规模翻倍（+2.6pt）的 4 倍以上。**

### 修正基线报告的一处归因

`eval/REPORT_longmemeval_full.md` §归因1 预期「3b 拒答属小模型信心阈值问题，换 7b 预计可显著收敛」。**实测不支持**：7B 的字面/语义拒答率与 3B 相同（61.6% / 61.8% vs 60.4% / 63.2%），准确率只提高 2.6pt；而不动模型、只把提示词从 strict 换成 loose，拒答直接归零并带来 +11.2pt。→ 拒答是**提示词策略**问题（SYS 明确给了"insufficient 就回复 INSUFFICIENT_CONTEXT"这条出口），不是模型规模问题。

## ③ 瞎猜副作用（pred 非拒答但错误）

**存在，但量级可控，且集中在「无证据」场景。**

1. **无证据裸答（none 条件）是最干净的瞎猜度量**：严格提示下模型几乎全拒（483/500 语义回避），acc 0.016；松绑后禁止拒答，acc 表面升到 **0.090**（×5.6），保守口径 **0.048**（vs 严格 0.012）。即凭空作答仍能蒙对一部分题（temporal-reasoning 的 none acc 高达 0.180，保守口径 0.090；multi-session 0.083/保守 0.030）——这些题的 gold 是短数值（"3 days"、"8 days"），模型给出同数量级的具体数字就可能命中。**生产含义：用户会看到关于自己生活的、语气肯定但无依据的答案。**
2. **rag 条件下瞎猜影响小**：loose 的 167 条判对里只有 11 条是回避语句（疑似假阳性），保守 acc 0.312 vs 0.334，差 2.2pt；且 rag−none 的检索贡献不降反升（strict：+20.6pt；loose：+24.4pt；保守口径 +26.4pt）→ 松绑**没有**让模型无视上下文乱答。
3. **5 条 strict→loose 翻错题逐条核验**（全部 5 条，非抽样）：

| 题型 | gold | loose 答案 | 性质 |
|---|---|---|---|
| temporal-reasoning | `'The Nightingale' by Kristin Hannah` | `"The Alice Network" by Kate Quinn` | **真幻觉** |
| multi-session | `$200` | `...is $120` | **真幻觉（算错）** |
| single-session-assistant | `C D E F G A B A G F E D C` | `G G G G A G F` | **真幻觉（编造序列）** |
| single-session-assistant | `The Chiefs played the Jaguars 12 times at Arrowhead Stadium.` | `Of the 12 games played between the ...` | 判分未匹配（改写） |
| single-session-assistant | `ratio is 1:10, meaning one part tea tree oil` | `1 part tea tree oil to 10 parts carrier oil` | 判分未匹配（语义正确） |

→ 5 条里 3 条真幻觉（占全体 0.6%），2 条是宽松判分对改写句的误杀。**single-session-assistant 是唯一净退步题型**（0.732→0.696，保守 0.679）：该题型 gold 要求原样复述助手历史回答，strict 下模型照抄易命中，loose 下它改写+加推理（completion tokens 18.2→29.6，+63%），既抬高判分不匹配概率，也带来少量编造。

4. **loose rag 条件抽样 5 条「非拒答但错误」**（`_setup/analyze_loose.out`，seed=42，从 301 条命中却答错中抽）：

| qid | 题型 | gold | loose pred |
|---|---|---|---|
| gpt4_ab202e7f | multi-session | 替换/维修了 5 件厨房物品 | `2 items: coffee maker and espresso machine`（漏项，recall 仅 0.20） |
| 86b68151 | single-session-user | `IKEA` | `I don't have that information…`（**改写型拒答**） |
| 8cf4d046 | multi-session | `3.83` | `excerpts do not contain information about the GPA`（**改写型拒答**） |
| 0ea62687 | multi-session | `2` | `Your car was getting 30 miles per gallon`（答错对象） |
| 9ee3ecd6 | multi-session | `100` | `You need to earn 300 points…`（数字读错） |

→ 5 条中 **2 条仍是拒答，只是换了措辞**：`Never refuse` 消除了指令 token，但没消除"回避"行为本身（宽口径统计 145/500 = 29.0%）。

## ④ 生成侧瓶颈的结论与建议

**结论**
1. 生成侧瓶颈已被证实且**主要不是模型规模问题**：检索三次运行完全一致（gold 召回 0.8489、命中 93.6%），strict 下七成失败是"命中却拒答"，把提示词的拒答出口关掉即可回收这七成中的绝大部分（+11.2pt）。
2. 松绑后瓶颈性质改变：按基线口径（只认字面 `INSUFFICIENT_CONTEXT`）333 题失败里 90.4% 是"答了但答错"、仅 9.6% 检索未命中；但其中 **134/333（40.2%）实为换了措辞的回避**，真做答却答错的约 200 题，错误内容是抽取/算数/跨会话聚合。→ 下一步该治的是**证据抽取与结构化推理**，而不是继续调语气。
3. 松绑的代价可接受：延迟 6.74→8.81s（+31%，去污染 8.61s）、completion tokens 18.2→29.6（+63%）、总 tokens 几乎不变（1442→1465，提示占绝对大头）。

**建议（按性价比排序）**
1. **默认 system 提示词改为 loose 方向**，并补两句：`Do not say you lack information; give a concrete answer or your best estimate.`（压掉 29% 的改写型回避）与 `If uncertain, append "confidence: low" after the answer.`（把瞎猜从"看不出来"变成"可标注"）。
2. **拒答改为系统策略而非模型自觉**：按检索置信门限分流——`gold_recall=0` 的那 32 题（6.4%）走拒答/追问分支，其余强制作答。这样既保住 +11.2pt，又消除无证据瞎猜风险（本实验 none 条件已证明"强制作答=会蒙对"）。
3. **补测 `7B + loose`**（当前缺失的关键单元格）：两者增益若可叠加，temporal/knowledge-update 有望接近论文 MemTier 的 0.382。
4. **multi-session 与 temporal 剩余短板回到检索/记忆结构**：k=3 的 `session_cover` 仅 0.549 / 0.677，k=8–12 升到 0.774–0.82 / 0.82–0.865（来源 `_setup/ablation.log` 实验①）；对这两类单独提高 k 或引入跨会话分层摘要（MemTier 思路），预计继续放大 loose 的 +31/+9 净翻转。
5. **判分口径需要收紧**：preference 类恒为 0.000（gold 为开放表述，substring 判分不可能命中），而本轮新暴露的问题是反向的——回避句因含单位词被误判为正确（none 条件 45 条判对里 21 条如此）。建议下一阶段换 LLM judge 或"必须命中数值+单位"的双条件判分，否则松绑实验的表面增益约有 1～2pt（rag）与 4pt（none）是测量噪声。

---
### 产物与来源清单
- 结果：`eval/results/smoke_20261004_020225.jsonl`（本实验）、`smoke_20261003_191205.jsonl`（strict-3B 基线）、`smoke_20261003_225222.jsonl`（7B-strict，含 resume7b 补跑）
- 日志：`_setup/lme_loose.log`（含「汇总」行）、`_setup/lme_loose.err`（0 字节）、`_setup/loose_monitor.log`（15 分钟一次快照，02:02→04:08 共 7 次）、`_setup/lme_7b.log`/`lme_7b.err`
- 启动器：`_setup/run_loose.ps1`；进度探针：`_setup/loose_progress.py`
- 分析脚本（`_setup/analyze_full.py` 的口径副本，均未改动原文件与原结果）：`_setup/analyze_loose.py`、`_setup/analyze_loose.out`、`_setup/analyze_loose_extra.py`、`_setup/analyze_loose_qtype.py`
- 基线对照数据取自：`eval/REPORT_longmemeval_full.md`（rag 0.222 / 拒答占失败 77.6% / 命中后拒答 70.7%）、`_setup/ablation.log`（实验①检索覆盖）
