# 软硬件大模型评估基准元数据核实报告

> **用途**：核实 `paper/aei/main.tex` Related Work 所引 6 个基准的官方权威出版元数据，并提供"评估对象 / LLM-as-a-judge"对比表。
> **检索日期**：2026-10-14。数据源：Crossref API（DOI 论文）、OpenAlex API、DBLP/ACM DL/NeurIPS 论文集、官方 GitHub/项目页、论文 PDF 快照。
> **修正已应用**：`paper/references.bib` 与 `paper/aei/references.bib` 两个文件的 6 处条目已按本报告结论更新（引用键不变，`main.tex` 无需改动）。

---

## 1. 核实结论总表

| # | 基准 | 用户 bib 原文 | 核实结论（权威元数据） | 处理 |
|---|---|---|---|---|
| 1 | **HumanEval** (Chen et al., 2021) | arXiv:2107.03374 | **arXiv 预印本（OpenAI 技术报告），无同行评审会议/期刊版本**。常被误引为 NeurIPS 2021 D&B——四库均无论文集记录（DBLP/ACM/NeurIPS proceedings/Crossref） | 原文正确，已补 DOI 10.48550/arXiv.2107.03374 及澄清 note |
| 2 | **SWE-bench** (Jimenez et al., 2024) | ICLR 2024 | **ICLR 2024（Oral Presentation，2024-01-16 接收）**，OpenReview 论坛 VTF8yNQM66；ICLR 无页码、无 DOI（官方推荐引用即 OpenReview URL） | 已补 url + Oral 标注；booktitle 规范为 "The Twelfth International Conference on Learning Representations" |
| 3 | **VerilogEval / Thakur et al.** (2023) | DATE 2023, pp. 1–6 | **DATE 2023, pp. 1–6, DOI 10.23919/DATE56975.2023.10137086**（元数据正确）。⚠️ 但该论文实为 **VGen benchmark**（arXiv:2212.11140，17 designs，CodeGen 微调），**并非名为 "VerilogEval" 的基准** | 已补 DOI 与 VGen 说明；另新增真正的 VerilogEval 条目 `liu2023verilogeval`（见下） |
| 4 | **RTLLM** (Lu et al., 2024) | IEEE TCAD 2024；作者含 "Xu, Siyuan"；标题 "…with Natural Language" | **错误**。唯一正式版本：**ASP-DAC 2024（29th Asia and South Pacific Design Automation Conference），pp. 722–727，DOI 10.1109/ASPDAC58780.2024.10473904**；作者 Yao Lu, Shang Liu, **Qijun Zhang**, Zhiyao Xie（HKUST）；标题 "RTLLM: An Open-Source Benchmark for **Design RTL Generation with Large Language Model**"。OpenAlex/Crossref/DBLP 均**不存在 TCAD 期刊版** | 已整条替换为 ASP-DAC 正确元数据 |
| 5 | **ChipNeMo** (Liu et al., 2023) | ICCAD 2023 proceedings；作者含 Ebrahimi/Shen/Galal | **部分错误**。权威记录为 **arXiv:2311.00176（2023-10-31 提交，v5 2024-04）**；ICCAD 2023 上以 Bill Dally  keynote 报告，但**未进入 ICCAD 2023 论文集**（IEEE/Crossref/DBLP 无论文集 DOI，DBLP 仅 CoRR 记录）。作者前几位的正确写法：Mingjie Liu, **Teodor-Dumitru Ene**, Robert Kirby, Chris Cheng, Nathaniel Pinckney … Haoxing Ren（原 bib 中 Ebrahimi/Shen/Galal 非本文作者） | 已改为 arXiv 条目 + "Presented at ICCAD 2023" note |
| 6 | **RAG** (Lewis et al., 2020) | NeurIPS 33, pp. 9459–9474 | **正确**。Advances in NeurIPS 33（NeurIPS 2020），pp. 9459–9474，Article No. 793（ACM DL 记录 DOI 10.5555/3495724.3496517，Curran Associates） | 已补 DOI 与 Article No. |

---

## 2. 对比表格（供 Related Work 直接使用）

| 基准 | 官方出处（会议/期刊全称 · 年份 · 页码/DOI） | 评估对象 | LLM-as-a-judge？ | 评估机制细节 | 规模/领域 |
|---|---|---|---|---|---|
| **HumanEval** | arXiv:2107.03374（2021，OpenAI 技术报告） | **可执行行为** | **否** | 164 道手写 Python 函数补全题（docstring→函数体）；每题平均 ~7.7 个隐藏单元测试；生成代码在沙箱内**执行**，pass@k（n=200, k≤100 无偏估计） | 164 题 / 通用 Python（非硬件、非文档驱动） |
| **SWE-bench** | The Twelfth International Conference on Learning Representations (ICLR) · 2024 · OpenReview VTF8yNQM66（Oral） | **可执行行为** | **否** | 2,294 个真实 GitHub issue（12 个 Python 仓库）；Docker 容器内应用模型补丁并运行仓库测试套件，FAIL_TO_PASS + PASS_TO_PASS 双指标 | 2,294 实例 / 软件工程（仓库级修复） |
| **Thakur et al.（VGen）** | 2023 Design, Automation & Test in Europe Conference & Exhibition (DATE) · 2023 · pp. 1–6 · DOI 10.23919/DATE56975.2023.10137086 | **可执行行为** | **否** | 微调 CodeGen；评估框架 = 语法检查流 + **testbench 功能分析（仿真）**；报告 syntactically correct 25.9%、functionally correct 6.5% | 17 designs / RTL 生成（自建小型设计） |
| **VerilogEval（NVIDIA）** | 2023 IEEE/ACM International Conference on Computer-Aided Design (ICCAD) · 2023 · pp. 1–8 · DOI 10.1109/ICCAD57390.2023.10323812（Invited Paper） | **可执行行为** | **否** | 156 个 HDLBits 题目（组合电路→FSM）；沙箱内 Icarus Verilog 仿真，**对比 generated design 与 golden solution 的 transient simulation outputs** | 156 题 / RTL 生成（教学题目，非真实数据手册） |
| **RTLLM** | 2024 29th Asia and South Pacific Design Automation Conference (ASP-DAC) · 2024 · pp. 722–727 · DOI 10.1109/ASPDAC58780.2024.10473904 | **可执行行为** | **否** | 三层次目标：**syntax**（VCS 编译）、**functionality**（testbench 仿真）、**design quality**（综合后 PPA vs 人工参考设计）；v1.0 共 30 个设计 | 30 designs / RTL 生成（自建模块级设计） |
| **ChipNeMo** | arXiv:2311.00176（2023；ICCAD 2023 keynote 报告，未进论文集） | **均非**（领域应用评测，非公开基准） | **否**（用**人类专家评测**，非 LLM 评判） | 域适应（tokenizer/DAPT/SFT/RAG）后在 3 个内部应用上评测：工程助手聊天机器人（专家 Likert 1–7，6.0/7）、EDA 脚本生成（简单脚本 >70% 正确）、bug 摘要（专家评分 >5/7）；另有多选 AutoEval（chip-MMLU 类） | 内部数据 / 芯片设计 LLM 系统（基准不公开、不可复现） |
| **RAG** | Advances in Neural Information Processing Systems 33 (NeurIPS 2020) · pp. 9459–9474 · Article No. 793 · DOI 10.5555/3495724.3496517 | **均非**（生成式 QA 方法论文） | **否**（2020 年该范式尚未出现） | NQ / TriviaQA / WebQuestions / Jeopardy / MS MARCO 上的 **EM / F1 答案重叠度** | 5 个知识密集型 NLP 任务 / 检索增强生成方法 |
| **（本文）D2D-Twin** | 本刊投稿 | **可执行行为** | **否** | 冻结的确定性黑盒 pytest harness（MD5 8cf0854d…）；8 个行为规范维度；源锚定 Silver→Gold 门禁 + 显式未知掩码 | 17–20 芯片 / 数据手册约束的寄存器行为 |

**表格可直接支持的 Related Work 论点**：
1. HumanEval / SWE-bench 虽为"可执行"评测，但面向**通用软件**，且 SWE-bench 依赖仓库测试套件而非**规范文档**；
2. Thakur(VGen) / RTLLM / VerilogEval 已进入"仿真验证"层面，但均为**自建小型合成设计**，无文档级溯源（无 SHA-256/页码锚定），也不宣称对厂商文档的忠实度；
3. ChipNeMo 代表"领域适应 + 人类专家评测"路线，基准内部、不可复现；
4. RAG 是方法论文，以答案重叠度评分，与可执行验证正交；
5. D2D-Twin 的差异化 = **数据手册约束 + 源锚定 + 确定性黑盒断言 + 有界声明**。

---

## 3. 需要作者知晓的 4 个引用陷阱

1. **"VerilogEval" 名称混淆**：`thakur2023verilogeval` 键名下的 Thakur et al. (DATE 2023) 论文实际是 **VGen** benchmark；名为 VerilogEval 的基准是 NVIDIA 的 Liu et al. (ICCAD 2023)。已在两个 bib 中新增 `liu2023verilogeval` 条目；若正文只谈"Verilog 生成基准"而不特指 NVIDIA 基准，可继续用 Thakur 条目，但**不要在正文中把 Thakur 的工作称作 VerilogEval**（建议改称 "Thakur et al.'s VGen benchmark" 或直接描述为 "an early Verilog generation benchmark"）。
2. **RTLLM 无期刊版**：原 bib 的 TCAD 版本不存在（题名、作者、出处三处均错）。若评审人去查 TCAD 会查不到，必须用 ASP-DAC 版本（已修正）。
3. **ChipNeMo 非 ICCAD 论文集论文**：改为 arXiv 引用并在 note 中说明"ICCAD 2023 keynote 报告"最稳妥；若想保留 ICCAD 字样，至少不应写成 "Proceedings of ICCAD"。
4. **HumanEval 无会议版本**：arXiv 引用是社区标准做法（lm-evaluation-harness、HuggingFace 均如此），保持现状即可，勿改为 NeurIPS。

---

## 4. 已应用的 BibTeX 修正（两个文件同步）

`paper/references.bib` 与 `paper/aei/references.bib`：

- `thakur2023verilogeval`：补 DOI + VGen note；**新增** `liu2023verilogeval`（NVIDIA VerilogEval，ICCAD 2023）
- `lu2024rtllm`：整条替换为 ASP-DAC 2024 正确元数据（@inproceedings，作者 Lu/Liu/**Zhang**/Xie，pp. 722–727，DOI 10.1109/ASPDAC58780.2024.10473904）
- `liu2023chipnemo`：改为 arXiv:2311.00176，修正作者列表，note 注明 ICCAD 2023 keynote + 人类专家评测
- `jimenez2024swebench`：booktitle 规范化 + OpenReview URL + Oral 标注
- `chen2021evaluating`：补 DOI + "no peer-reviewed venue" note
- `lewis2020retrieval`：补 DOI 10.5555/3495724.3496517 + Article No. 793

> 注：`paper/aei/references.bib` 中由客座编辑文献拼接进来的若干**注释行**存在编码乱码（仅注释，不影响 BibTeX 编译与文献列表），如需清理可再处理。

---

## 5. 局限

- ICLR/NeurIPS 论文本身无 DOI/页码（ICLR 用 OpenReview，NeurIPS 用 Curran 论文集 + ACM DL 记录），表中以官方推荐的 OpenReview URL / ACM DOI 代替；
- ChipNeMo 的评测数字（6.0/7、>70% 等）取自论文 v5 附录表格快照，与 v1 早期版本数字不同（v1 曾报 7.4/10 等），引用具体数值时请以所引版本为准；
- 引用计数本次未逐一采集（非本任务目标）；RTLLM 在 Google Scholar 约 329 次、OpenAlex 176 次（2026-10-14 快照），如需可在稿中统一口径。
