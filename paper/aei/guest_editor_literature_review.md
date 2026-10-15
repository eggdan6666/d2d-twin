# AEI 特刊客座编辑代表论文调研报告（2023–2026）

> **用途**：为 `paper/aei/main.tex` 的 Introduction 与 Related Work 提供引用素材与"对话点"。
> **检索日期**：2026-10-14。BibTeX 条目见同目录 `references_guest_editors.bib`（键名沿用 `lastname+year+keyword` 约定，可直接与 `references.bib` 合并）。

---

## 1. 调研方法与数据来源

| 环节 | 来源 |
|---|---|
| 特刊信息 | Elsevier 官方特刊页（sciencedirect.com/special-issue/331510） |
| 身份消歧 | ORCID（0009-0004-3430-8502 等）、Crossref 作者机构、OpenAlex 作者实体、Semantic Scholar |
| 论文列表 | OpenAlex works API（按作者实体过滤 + 2023–2026 + 引用数排序） |
| 元数据/摘要 | Crossref API、Semantic Scholar API、出版商页面快照、机构库（PolyU / A*STAR / Portsmouth 等） |
| 引用计数 | OpenAlex 为主，Semantic Scholar / Scopus 快照 / Google Scholar 快照为辅（三者差异大，正文以区间标注） |

**计数口径提醒**：OpenAlex、Semantic Scholar、Scopus、Google Scholar 对同一篇论文的引用数可能相差 2–3 倍（如 Lee 2023 scoping review：OpenAlex 74 / SS 61）。投稿前如需精确数字，建议以目标期刊认可的数据库为准并统一口径。

**身份消歧结论**（均已交叉确认）：

| 编辑 | 确认身份 | ORCID | 学术画像（2023–2026 侧重） |
|---|---|---|---|
| Ching-Hung Lee | 西安交通大学 公共政策与管理学院 | 0000-0002-4093-556X | 人因工程、Kansei 工程、可解释 AI（神经符号）、不确定性管理、AI 驱动的数字化转型；与 Chun-Hsien Chen、Amy Trappey 高频合著 |
| Chun-Hsien Chen | 南洋理工大学 机械与宇航工程学院 | 0000-0003-2193-5270 | 设计科学/工程信息学、数字孪生（调度/供应链/维护）、工业知识图谱、LLM×设计、人因与绩效管理。**自 2013 年 1 月起担任 AEI 主编（Editors-in-Chief，与 TU Berlin 的 Timo Hartmann 共同担任）** |
| Chun-Yi Wu | Intel Corporation（Chandler, AZ；ORCID 登记 Santa Clara）数据科学家（OTF Yield 部门） | 0009-0004-3430-8502 | NTHU 工业工程博士；曾任职 TSMC（制造技术研发）、Corning（数据分析）、IBM Research-Almaden；专利分析、知识工程（本体/语义）、生成式 AI 与 RAG 工作流 |
| Mey Goh | 拉夫堡大学 Wolfson 机械、电气与制造工程学院 | 0000-0002-5028-9506 | Through-life engineering、数字孪生人机交互界面、XAI 需求工程、生理信号认知负荷测量 |

**学术网络提示**（对引言措辞有用）：
- Lee 与 Chen 合著多篇（AEI 2023 scoping review、KBS 2024 VALIO），引其一时可自然带出另一人；
- Lee 与 Wu 还共同担任 *World Patent Information* 另一特刊"LLM/GenAI/Agentic AI for IP analytics"的客座编辑（Trappey 任 managing editor）；
- Amy J.C. Trappey（清华大学（新竹）教授、WPI 主编、AEI Special Content Editor）是 Lee 与 Wu的紧密合作者，本报告多篇论文的通讯/第一作者——引用时可视为该共同体的框架代言人。

---

## 2. 特刊背景速览（写作时可直接引用的框架）

- 全称：*Advanced Theories and Practices for Trustworthy Hybrid Human Agentic-AI Empowered Engineering Systems: Risk, Reliability, Explainability, and Accountability in a Global VUCA World*
- VSI 标识（投稿时须选）：`VSI: ADVEI_Trustworthy Hybrid Human Agentic-AI Eng Sys`；投稿窗口 2026-03-20 至 2026-12-31。
- 官方论证的三大现实（可作引言立意）：**Risk Chasm**（能力跃迁带来的目标错泛化、设计幻觉、不透明安全推理、偏见传播）、**Governance Lag**（保障框架滞后于 AI 部署）、**Co-evolution Imperative**（人–AI 深度协同中的认知依赖与技能侵蚀风险）。
- 四大主题群：Risk Engineering for Trustworthy Hybrid Systems；Reliability & Resilience in VUCA Environments；Explainability & Interpretability for Joint Cognition；Accountability & Governance Frameworks / Human Factors & Cognitive Sustainability；Cross-Domain & Systemic Perspectives（含"simulation and digital twin environments for stress-testing hybrid system trustworthiness"）。
- ⚠️ **影响因子待核实**：稿中现写 IF 11.5；公开来源（JCR 转引）显示 AEI 2023/2024 JIF 为 9.9。建议标注年份或复核后再定稿（README 已列"待核实"）。

---

## 3. Ching-Hung Lee（西安交通大学）——人机协同 / 可解释 AI / 不确定性

**精选论文（5 篇）**

| # | 论文 | 期刊 / 年份 | 引用（区间） | 对应特刊主题 |
|---|---|---|---|---|
| 1 | Artificial intelligence-enabled digital transformation in elderly healthcare field: Scoping review | *Advanced Engineering Informatics*, 55, 101874, 2023 | 61–74 | AI 赋能工程系统 / 数字化转型 |
| 2 | How to manage and balance uncertainty by transdisciplinary engineering methods focusing on digital transformations of complex systems | *Advanced Engineering Informatics*, 59, 102330, 2024（Editorial） | 10–17 | 不确定性量化与治理 |
| 3 | VALIO: Visual attention-based linear temporal logic method for explainable out-of-the-loop identification | *Knowledge-Based Systems*, 299, 112086, 2024 | 16–18 | 可解释性 / 联合认知 |
| 4 | A New Era in Human Factors Engineering: A Survey of the Applications and Prospects of Large Multimodal Models | *Int. J. Human–Computer Interaction*, 41(18), 11867–11880, 2025 | 11–17 | 人因与认知可持续 |
| 5 | Human-AI collaboration for engineering designs and services in the evolution of Industry 5.0 and beyond – A synthesis of the special issue portfolio | *Advanced Engineering Informatics*, 69, 103906, 2026（Editorial） | 2 | 混合人–智能体系统总框架 |

**备选**：[可选] Connecting humans and machines: Deep integration of advanced HCI in intelligent engineering（AEI 62, 102824, 2024，6 次）；[可选] Virtual Co-Pilot: Multimodal LLM-enabled Quick-access Procedures for Single Pilot Operations（IEEE CAI 2024, 1501–1506，12 次——智能体式副驾驶案例）。

**核心学术观点**

1. **`lee2023artificial`**：AI 是加速老龄健康照护领域数字化转型的" potent instrument"，用于应对高成本、动态、不可预测的用户环境；基于 2000–2021 年 Web of Science 63 篇文献的范围综述，发现多个老龄健康子领域已落地 AI 系统与应用场景，且 AI 产生实质性正向影响；以 Smart Product-Service Systems（SPSS）组织"数字产品 + 服务系统"的融合。
2. **`trappey2024how`**（Editorial，Trappey 第一作者、Lee 为共同作者）：数字化转型是数字技术向多域渗透引发根本性变革的过程，其四大要素为目标实体、转型范围与重点、技术采纳与方法、情境与收益目标；数字孪生、云计算、边缘计算、CPS、AI、大数据、VR/AR/MR 等构成"数字智能"的主要形态；复杂系统数字化转型的关键难题是**如何在不确定的内外部情境下强化内外部系统间的智能共享与相互质询**，主张以跨学科工程（transdisciplinary engineering）方法管理与平衡不确定性。
3. **`lyu2024valio`**：航空自动化导致飞行员"Out-of-the-Loop（OOTL）"状态，威胁安全；既有黑箱机器学习缺乏可解释性。VALIO 将座舱 AOI 与注视时长编码为 Visual Attention Traces，用线性时序逻辑（LTLf）生成**人类可读公式**来分类行为并解释 OOTL（神经符号 AI 路线）；10–75 s 时间窗内 F1 稳定在 0.769–0.815，短于 30 s 时显著优于机器学习法（更及时）。
4. **`li2025new`**：大模型（LMM）既是人因研究的**新研究对象**（LMM-based smart systems）也带来**新研究范式与方法**；通过"专家–LMM 协同"的文献与专利综述，梳理 LMM 在事故分析、人体建模、干预设计中的应用，并讨论人因工程在 LMM 时代的范式变革与挑战。
5. **`trappey2026human`**：数字化转型已使每个工程制品成为数据丰富、算法中介的信息物理系统，连通性在释放设计自由的同时放大了网络安全、技能错配与伦理困境；Industry 4.0 的技术中心效率逻辑 → Industry 5.0 的人本价值逻辑；定义 **HAIC（Human-AI Collaboration）为"人类专长（情境、伦理、直觉）与 AI（速度、规模、模式识别）的目的性共创伙伴关系"**；提出超越效率的四个充分性准则：创造力、福祉、可持续性、韧性；多模态共创（EEG/EMG、触觉微手势、空间音频、对话式 LLM 构成单一交互层）。

---

## 4. Chun-Hsien Chen（南洋理工大学）——数字孪生 / 知识工程 / LLM×设计

**精选论文（5 篇，主题覆盖最全的一位编辑）**

| # | 论文 | 期刊 / 年份 | 引用（区间） | 对应特刊主题 |
|---|---|---|---|---|
| 1 | A digital twin-based decision support approach for AGV scheduling | *Engineering Applications of Artificial Intelligence*, 130, 107687, 2024 | 35–46 | 数字孪生决策支持 |
| 2 | Graph-enabled cognitive digital twins for causal inference in maintenance processes | *Int. J. Production Research*, 62(13), 4717–4734, 2024（2023 在线） | 30–31 | 认知数字孪生 / 因果推断 |
| 3 | Incorporating supply and production digital twins to mitigate demand disruptions in multi-echelon networks | *Int. J. Production Economics*, 273, 109258, 2024 | 39 | 可靠性与韧性（VUCA） |
| 4 | A multi-hierarchical aggregation-based graph convolutional network for industrial knowledge graph embedding towards cognitive intelligent manufacturing | *Journal of Manufacturing Systems*, 76, 320–332, 2024 | 28–29 | 知识工程 |
| 5 | Examining the impact of large language models on design: Functions, strengths, limitations, and roles | *Design and Artificial Intelligence*, 1(2), 100017, 2025 | 23 | Agentic AI×设计 |

> 注：*Design and Artificial Intelligence* 为 Elsevier 2025 年新创 OA 期刊（ISSN 3050-7413），评审人可能不熟悉，引用时可加全称。

**核心学术观点**

1. **`gao2024digital`**：港口 AGV 调度受动态复杂环境（冲突、故障、电池约束）影响；提出数字孪生决策支持框架——**物理空间映射到虚拟空间并保持同步，用于"在虚拟空间中验证调度解"**；数学规划 + Q-learning 生成考虑充电的调度计划，在中小规模算例上优于 GA/PSO；敏感性分析给出 AGV/任务最优配置以提高电池利用率、缩短完工时间。→ "孪生体作为决策的虚拟验证场"是其 DT 观的核心。
2. **`lim2024graph`**：传统 DT 在互操作、知识共享与因果推断上存在局限；**认知数字孪生（CDT）**管理互连系统的协同网络，用工业知识图谱（iKG）+ 设计结构矩阵（DSM）建模依赖关系并经语义转换入图；Louvain + PageRank 图序列化自动生成可行解并经仿真验证以最小化生产中断；能识别新产品设计中的潜在中断（预防性）；印刷生产线案例展示了 CDT 的因果推断与**解的可解释性**。
3. **`lim2024incorporating`**：供应链与制造运营内在耦合（FMCG 多级网络）；现有 DT 方案各自为政、缺乏上下文，导致方案不合逻辑；提出**四层技术栈**的"供应–生产（S&P）DT 系统"，整合韧性评估、供应链重规划与车间重调度；F&B 需求激增案例表明混合 S&P DT 提升需求满足率、缩短制造周期。→ "跨域上下文集成"是韧性工程的关键。
4. **`liu2024multi`**：认知计算推动制造向"认知智能"范式转变，知识是高级认知的使能要素；KG 是认知智能制造的核心工具，KG 补全（嵌入）决定知识质量；既有嵌入模型在关系特定变换、邻居区分、中间信息利用上不足；提出多层聚合 GCN（关系感知 + 实体感知 PREA 块 + 跨块聚合），在 3D 打印 KG 链接预测上验证。→ 知识表示质量是下游一切认知任务的门槛（与本项目 Gold IR 质量门禁同构）。
5. **`zhou2025examining`**：以双菱形（Double Diamond）模型为框架系统检视 LLM 对设计的影响——识别出 LLM 贯穿设计各阶段的 **16 项功能**；作为设计工具的优势（如打破设计固着）与作为设计材料的优势（如增强情感连接）；局限（数据依赖、情境误读等）；LLM 可承担设计推理、设计可视化等角色，但**对问题/困境/区域情境的敏感性等本质设计师角色必须由人类承担**。→ 人机分工的实证依据。

---

## 5. Mey Goh（拉夫堡大学）——数字孪生人机交互 / XAI / 认知负荷

**精选论文（5 篇）**

| # | 论文 | 期刊 / 年份 | 引用（区间） | 对应特刊主题 |
|---|---|---|---|---|
| 1 | A Conceptual Model Framework for XAI Requirement Elicitation of Application Domain System | *IEEE Access*, 11, 108080–108091, 2023 | 7–17 | 可解释性 / 问责 |
| 2 | Determining Cognitive Workload Using Physiological Measurements: Pupillometry and Heart-Rate Variability | *Sensors*, 24(6), 2010, 2024 | 8–33 | 人因与认知可持续 |
| 3 | The Need for a Symbiotic Interface for a Digital Twin | *Advances in Transdisciplinary Engineering*（IOS Press）, 2023 | 2 | 人机交互 / 联合认知 |
| 4 | Personas to inform cognitive interaction with a Digital Twin | *J. Industrial Information Integration*, 47, 100893, 2025（开放获取） | 3–13 | 数字孪生需求工程 |
| 5 | A human-centric framework for enhancing usability in a vineyard digital twin system | *Computers and Electronics in Agriculture*, 244, 111490, 2026 | 2 | 以人为本的 DT 设计 |

**核心学术观点**

1. **`aslam2023conceptual`**：AI 接受度受"不透明模型"阻碍；XAI 的核心价值在于引入问责通道，且**理解解释所需的认知努力是关键人因变量**；心理模型（Mental Models）是 XAI 评价的前提但当前利用不足；提出用心理模型引导解释需求获取，并以**本体驱动（Ontology-Driven）概念模型**促进用户对解释的学习与理解，从而提升理解、满意、信任与绩效。
2. **`ma2024determining`**：工业 4.0 技术普及背景下，制造环境转向以人为本，仅测物理负荷不够，**操作者认知负荷监测成为关键**；提出定义并验证"任务复杂度–认知负荷–专业水平–绩效"关系的认知负荷指数方法；17 名操作者装配 Wankel 发动机实验显示，基于 HRV 与瞳孔测量的认知负荷指数在四个复杂度等级上均有统计显著差异，且比既有指标更灵敏；专家负荷更低（需进一步确认）。
3. **`palmer2023need`**：人与数字孪生的交互是尚无共识定义的新兴概念，关于"人与 DT 认知交互"的研究极少；在动态变化环境中需要**能适应情境、技能、需求与偏好的智能自适应界面**——即"共生界面（symbiotic interface）"：能学习、演化，为决策、问题解决与未预见事件提供支持；生态界面设计（EID）是合适的界面设计方法论。
4. **`palmer2025personas`**：DT 的可用性取决于"人需要知道什么"；给出**以人为中心的 DT 定义 + 需求层级矩阵**；采用"people-led"方法：对用户画像（Personas）做控制任务分析（ConTA）→ 决策阶梯（decision ladders）→ UML 信息流图建模认知交互；以工业齿轮箱产品服务 DT 为案例并经工业企业代表验证；是 ConTA 与决策阶梯在 DT 语境的首个应用。
5. **`zareiee2026human`**：农业 DT 偏重技术性能，导致数据过载、缺乏角色化界面、非技术用户信任下降等可用性问题；将 Personas + ConTA + Decision Ladders 系统集成为连贯的人本 DT 开发框架（葡萄园自动化案例），改善决策支持、用户参与与系统效率；框架可迁移到农业以外。→ 人本方法是 DT 可信采纳的操作化路径。

---

## 6. Chun-Yi Wu（Intel）——知识工程 / 生成式与智能体 AI（人机混合理解）

**精选论文（4 篇；另附窗口外奠基工作说明）**

| # | 论文 | 期刊 / 年份 | 引用（区间） | 对应特刊主题 |
|---|---|---|---|---|
| 1 | Generative AI approach for inventive process visualisation – enhancing human-AI hybrid understanding and comparing of patents | *Journal of Engineering Design*, 2025（在线优先，1–43） | 7 | Agentic AI / 人机混合理解 |
| 2 | Generative AI-based intelligent patent summarization for intellectual property knowledge communication and cooperation | *World Patent Information*, 83, 102410, 2025 | 2–6 | 知识工程 / 生成式 AI |
| 3 | A Technology-Function-Guided Patent Drafting Framework Incorporating eTFM and RAG-Based Large Language Model | SSRN 7243293, 2026（**预印本，未经同行评审**） | 0 | RAG + 多阶段智能体工作流 |
| 4 | Intellectual property (IP) data analytics for innovation, research and development, and strategic management – Adopting state-of-the-art AI and ML approaches | *World Patent Information*, 85, 102440, 2026 | 0 | 知识工程综述 |

> 说明：Wu 的公开成果面集中于**知识产权/专利知识工程与生成式 AI**（其 Intel 岗位为 OTF Yield 部门数据科学家，半导体制造成果多以专利/内部形式产出，公开期刊论文少）；窗口内（2023–2026）期刊论文即以上 4 篇。若需数字孪生直接对话点，建议以 Chen 的 DT 三篇为主、Wu 作为"智能体工作流 + 人在环路验证"的代表。
> 窗口外奠基工作（供背景引用）：Automatic patent document summarization for collaborative knowledge systems and services（2009，其被引最高工作，59 次）；Using Patent Ontology Engineering for Intellectual Property Defense Support System（2012）。

**核心学术观点**

1. **`trappey2025inventive`**（Wu 为共同作者，Intel  Chandler）：GenAI/LLM 结合 BERT 抽取用于**阅读与解释专利语义、抽取发明过程以供人类可视化与系统间智能比较**——这些是专利撰写、申请、答复、诉讼中关键且耗时的工作；采用**人类智能驱动的 AI 系统设计：以人类专长微调语言模型**，改善流程图生成中的上下文理解与逻辑推理；以 6G 电信专利为例；相似度分析子系统检测专利流程中的相似文本节点，支持可专利性、有效性与潜在侵权调查。
2. **`trappey2025patent`**（Wu 为共同作者）：2023 年全球专利申请超 355 万件，人工提取解读关键知识耗时、昂贵、主观且缺乏验证；构建基于 LLama 3 + LoRA 的智能专利摘要系统（V2X 专利案例），可在**消费级硬件高效运行**；与专家撰写专利的语义结构相似度近 90%；ROUGE 与 BERTScore 优于 GPT-3.5/Pegasus/BART/XLNet/GPT-4o 及多智能体+RAG 的 EvoPat 等既有方法。
3. **`kuo2026technology`**（Wu 为共同作者）：传统专利起草是创新产业的瓶颈；将计算机辅助 Technology-Function Matrix（**eTFM**）从分析工具扩展为**生成控制层**——高技术潜力"技术–功能"对直接引导起草方向，同一矩阵再用于校验草稿是否落在目标单元，形成**"生成–验证"闭环**（区别于 TRIZ 式结构化构思与整篇生成）；**本体检索 + RAG 将 LLM 锚定于领域现有技术**；提示工程协调多阶段流水线产出发明构思、摘要、标题、说明书、权利要求书与 IPC 分类；可持续储能案例验证；作者明确将结果定位为"**支持专家复核初稿的可行性证据，而非法律新颖性或可专利性判定**"。
4. **`fan2026intellectual`**（Wu 为共同作者）：综述面向创新、研发与战略管理的 IP 数据分析中最新 AI/ML 方法的采纳（与 Carsten Guderian、Anthony Trippe 等 IP 分析学者合著）。

---

## 7. 对 `paper/aei/main.tex` 的引用与对话建议

### 7.1 Introduction 可用锚点（建议句位）

| 写作意图 | 建议引用 | 可用论点 |
|---|---|---|
| 点明特刊立场/混合人–智能体系统 | `trappey2026human` | HAIC 定义；Industry 5.0 四充分性准则（创造力、福祉、可持续、韧性） |
| 论证"AI 不确定性须被架构性约束" | `trappey2024how` | 数字化转型四要素；内外部系统智能共享；跨学科工程的不确定性平衡 |
| 论证可解释性是可信性组成 | `lyu2024valio` | 黑箱 ML 的不可解释风险；人类可读 LTLf 公式的神经符号路线 |
| 论证人因/认知维度不可省 | `li2025new`、`ma2024determining` | LMM 时代人因研究范式；认知负荷的操作者侧测量 |
| 引出"source-constrained + bounded verification"动机 | `zhou2025examining` | LLM 能力边界与人类专属角色的实证划分 |

### 7.2 Related Work 定位建议

- **数字孪生谱系**：`gao2024digital`（孪生体作为调度决策的虚拟验证场）、`lim2024graph`（认知 DT + iKG + 因果推断 + 解的可解释性）、`lim2024incorporating`（跨供应–生产域的上下文集成与韧性）。对比表中可列为"DT-driven decision support / cognitive DT"一支。
- **知识工程一支**：`liu2024multi`（工业 KG 嵌入补全质量门槛）；`palmer2025personas`/`zareiee2026human`（DT 需求的人本获取方法）。
- **LLM/智能体工程应用一支**：`zhou2025examining`（设计领域 LLM 功能地图）、`trappey2025inventive`/`trappey2025patent`/`kuo2026technology`（专利知识工程的生成–验证闭环、RAG 锚定、人在环路复核）。
- **可信/可解释一支**：`aslam2023conceptual`（XAI 需求 + 心理模型对齐）、`lyu2024valio`。

### 7.3 对话点（差异化定位，审稿人大概率关心的）

1. **验证边界**：Chen 一系的 DT 以"虚拟空间仿真验证决策"（`gao2024digital`、`lim2024graph`）为核心；本工作将其推进到**寄存器行为层**，并以确定性黑盒断言（冻结 MD5 harness）替代 LLM-as-a-judge，且明确只宣称"数据手册约束下的有界验证"、不宣称硅片等价——可主动划清边界以迎合特刊对 V&V 严谨性的强调。
2. **不确定性治理**：`trappey2024how` 停留在工程组织/方法论层面讨论 DT 不确定性；本工作把未知**显式建模**（`known_mask` 掩码、Silver→Gold 准入门禁、patch rejection），是"架构性嵌入不确定性"的一个具体实例。
3. **知识来源与质量门禁**：`liu2024multi` 用图嵌入补全 KG；本工作用**源锚定抽取**（PDF SHA-256 + 物理页）约束每一跳知识的出处，可对照讨论"知识保真度 vs 知识覆盖率"的权衡。
4. **人机分工**：`zhou2025examining` 证明某些设计角色必须留给人；本工作的 Gold IR 人工核验 + 独立验收机制即是该论断在基准构造中的操作化。
5. **可解释/可审计**：`lyu2024valio`、`aslam2023conceptual` 强调"人类可读解释/心理模型对齐"；本工作的八维度失败分类学 + 可审计闭环可定位为面向非专家利益相关方的"解释供给"。

### 7.4 引用注意事项

- 引用计数以 2026-10-14 快照为准，不同数据库差异大；如稿中需要"高被引"表述，请统一到一个数据库口径。
- `kuo2026technology` 为 SSRN 预印本（未同行评审）：若审稿人对严谨性敏感，可仅在论述 RAG 工作流时引用并注明"preprint"，或改用 `trappey2025patent` 代表 Wu 的生成式 AI 应用。
- Chen 为 AEI 主编——在 Related Work 中引用其成果时保持学术化表述（"as the guest editor and long-time EiC of this journal has argued…"之类可省则省，避免过度抬举）。
- Wu 的论文多与 Trappey 合著且主题为专利/IP；除非特刊"Cross-Domain"方向需要，否则引言中一句带过即可，重点放在 Chen（DT/KE）与 Lee（HAIC/可信）一侧。

---

## 8. 局限与待核实

1. Scopus 全文库无直接访问权限，本报告以 OpenAlex + Semantic Scholar + Crossref 三角验证替代；个别引用计数为 Google Scholar/Scopus 网页快照，可能与库内实时值有偏差。
2. 部分 Elsevier 论文摘要来自出版商页面快照/机构库（PolyU、A*STAR OAR、Portsmouth、OUCI 等）；正式引用其具体论断前，建议核对原文 PDF。
3. 窗口内论文总量：Lee 35 篇、Chen 68 篇、Goh 17 篇、Wu 4 篇（OpenAlex 口径；作者实体拆分可能导致少量遗漏）。本报告按主题相关性与引用数精选，未穷尽——如需某位编辑的完整清单可按同方法复现。
4. AEI 影响因子（11.5 vs 公开来源 9.9）与 Lee 所属学院（公共政策与管理学院）等待核实项已在前文标注。
