# D2D-Twin 项目终极交接文档 (HANDOFF.md)

> **给接手 AI 的交接总纲**：  
> 本文档是当前项目的最高优先级上下文。新接手 AI 无需向用户提出任何背景询问，严格按照本文档即可独立做到四件事：  
> 1. **把项目从零跑起来**（依赖、命令、预期输出全包含）；  
> 2. **看懂为什么这么做**（核心科学发现、架构设计决策、被否决方案）；  
> 3. **知道接着干什么**（P0 到 P3 优先级任务路线图、现成元数据）；  
> 4. **能验证自己干得对不对**（确定性黑盒测试签名、回归断言）。

---

## 1. 项目目标

### 1.1 要解决的问题
在现代电子设计自动化（EDA）和嵌入式固件开发中，芯片外设的寄存器级行为模拟器（Virtual Peripheral Twins）是芯片流片前软硬件协同验证与驱动开发的基石。现有大模型硬件评测存在两大缺陷：
1. **过于局限在底层可综合 Verilog RTL**（忽视了嵌入式驱动所依赖的外设系统级寄存器语义建模）；
2. **高度依赖主观的 LLM-as-a-Judge 或文本问答（QA）**，存在严重幻觉与评估噪声。

前期诊断发现：在三个 seed 均答错的题目（`all3`）中，固定检索上下文的数值—单位匹配分类将 **全部审校题目的 42.5%–46.7% 归为上游相关**（DCU-3B/7B/14B），占三个 seed 均答错题目的 71.1%–79.7%。该诊断支持将“文档解析”与“逻辑代码合成”解耦，但不能单独证明因果关系或模型规模不变性。

**D2D-Twin（Datasheet-to-Digital-Twin）** 是国际首个完全确定性、零 LLM-as-a-judge 偏见、面向外设寄存器级仿真器合成的代码大模型基准测试套件。

### 1.2 验收标准与硬约束
* **验收核心**：基于人工校验的单写入者黄金中间表示（Gold IR），大模型合成可执行 Python 外设类，由通用冻结黑盒 `pytest` 框架全量注入读写刺激并断言。
* **Harness 绝对冻结**：黑盒测试文件 `d2d/eval/test_d2d_blackbox.py` 的 MD5 必须永远保持为：  
  `8cf0854d4779467bc8e472ee4fb97023`（严禁修改，保证评测的公平可比性）。
* **轻量化约束**：所有评测结果与基准分析必须能在**普通 CPU 单机无 GPU 环境下 1 秒内完成复现**。
* **数据规模**：覆盖 17 颗工业级外设芯片，612 份模型合成代码全量评测样本（Qwen2.5-Coder-14B: $N=408$; DeepSeek-Coder-6.7B: $N=204$），覆盖 8 大硬件行为规范维度。

---

## 2. 当前状态

### 2.1 已完成模块
* [x] **基准测试集与 Gold IR 构建**：17 颗工业芯片（传感器、高精度 ADC、电源监控器、电机驱动、PoE 接口等）的 Gold IR（`d2d/ir/*.json`）和 100% 准入通过的黄金参考模拟器。
* [x] **612 份大模型生成代码黑盒评测**：Qwen2.5-Coder-14B ($n=24$) 与 DeepSeek-Coder-6.7B ($n=12$) 的全量断言数据（`d2d/eval/results_gen_*.json`）。
* [x] **极速复现流水线**：根目录 `run_benchmark.py`，一键输出综合通过率、8 维故障分布、Spearman 复杂度相关性并绘制出版级图表。
* [x] **GitHub 官方开源**：已发布至 `https://github.com/eggdan6666/d2d-twin`（含中英双语文档、Apache-2.0 协议、DOI 与 HuggingFace 徽标）。
* [x] **Hugging Face Datasets 官方收录**：已发布至 `https://huggingface.co/datasets/eggdan666/d2d-twin`（139 个文件全量上线，署名“蓝程童”，标签已就绪）。
* [x] **CERN Zenodo 预印本与国际官方 DOI**：已正式挂网！
  * **DOI 标识符**：`10.5281/zenodo.23262086`
  * **永久页面**：`https://zenodo.org/records/23262086`
  * **已嵌入 4 页标准双栏 PDF 在线阅读器**，首发时间戳与科研命名权已法律级锁定。
* [x] **IEEE 双栏学术论文工程定稿**：位于 `paper/main.tex`、`paper/references.bib`、`paper/figures/`，Overleaf 100% 编译通过，排版无文字溢出，全 ASCII 字符集。
* [x] **Failure-driven repair utility pilot**：在 8 颗芯片上用冻结 Harness 评测最小补丁；Qwen2.5-Coder-14B 严格提升 5/8（Wilson 95% CI `[30.6%, 86.3%]`），DeepSeek-Coder-6.7B 提升 1/8 并出现 1 次回归。原始日志与 IR 约束参考代码位于 `_setup/*repair*`。
* [x] **32 芯片扩展清单**：`EXPANSION_ROSTER.md` 已从现有 456 份 PDF 中筛出 15 颗跨厂商候选；AD5592R、LIS3DH、MPU6050 已完成第一批 Gold IR 与参考 simulator 准入，正式 roster 为 20 颗，仍以 17 颗 baseline 的模型结果为历史比较集。
* [x] **第一批扩容证据与集成**：`_setup/ir_drafts/` 已形成并经独立审校及修复后复核；三颗芯片的正式 IR 位于 `d2d/ir/`，参考 simulator 位于 `d2d/rtl/`，并通过全量参考 admission。结果见 `_setup/CANDIDATE_ADMISSION_REPORT.md`；协议扩展见 `_setup/EXTENDED_PROTOCOL_REPORT.md`。
* [x] **I²C/SPI 扩展协议原型**：LIS3DH/MPU6050 的 I²C 地址选择、自动递增、BDU/BLE、重复 START、NACK、burst、DEVICE_RESET，以及 AD5592R 的 SPI 控制字、读回、250 μs 等待、软复位和 IO_LOCK 已在 `_setup/extended_eval/` 通过 10 项软件测试；未进行实物电气验证，原冻结 harness 未改。

### 2.2 未完成模块与当前卡点
* [ ] **arXiv 预印本挂网（卡点：背书机制 Endorsement）**：
  * **背景**：arXiv 自 2026 年初起，对首次投稿且历史上未发过 arXiv 的新作者全面推行背书政策（即使拥有学校 `.edu.cn` 邮箱也不能自动豁免）。
  * **当前卡点**：用户账号为 `3086708928@qq.com`（桂林电子科技大学），投稿分类 `cs.SE`，页面提示需要一位同行学者背书。
  * **专属背书信息**：
    * 专属背书码：`YFN9PW`
    * 专属直达背书链接：`https://arxiv.org/auth/endorse.php?x=YFN9PW`
    * 暂存提交页面：`https://arxiv.org/submit/8205007/start`

### 2.3 下一步任务清单（按优先级）
1. **【P0】arXiv 背书激活与一键提交**：
   - 任何人（导师、实验室发过 3 篇 cs.* arXiv 的师兄/师姐、或学术同行）点击上述专属链接 `https://arxiv.org/auth/endorse.php?x=YFN9PW` 点一下确认，账号即终身解锁；
   - 解锁后在暂存的提交页面上传 `d2d_paper.zip`（已包含最新修复排版的全部 tex、bib、figures），复制本文第 4 节元数据直接提交。
2. **【P0】重新编译论文并确认页数**：`paper/main.tex` 已加入 failure-driven repair 小节和紧凑表格；需在 Overleaf 以论文目录为根编译，确认 4 页限制、表格不溢出且 Errors=0。
3. **【P1】顶会/顶级期刊投递准备**：
   - 目标会议：DAC（CCF-A 顶会，主打外设数字孪生确定性测试）、DATE（CCF-B）、ICCAD（CCF-B），或 NeurIPS/ICLR（Datasets & Benchmarks Track，主打硬件规范代码大模型三大盲区揭示）；
   - 论文主体（4 页 IEEE 格式）已定稿，可随时输出。
4. **【P2】横向扩展新模型评测**：
   - 在现有的通用 Harness 下接入 Claude 3.5 Sonnet、GPT-4o、DeepSeek-V2.5 等最新模型的合成评测，扩充评测数据矩阵。
5. **【P3】端到端 HD-Agent 上游流水线贯通**：
   - 将工作区中前置的芯片 Datasheet 分层分块 RAG 与结构化抽取模块（HD-Agent）与 D2D-Twin 的 Gold IR 生成对接，形成自动化 Datasheet -> IR -> Digital Twin 工具链。

---

## 3. 环境与运行指南

### 3.1 基础环境要求
* **操作系统**：Windows 10/11、Ubuntu 20.04/22.04、macOS 皆可（纯 Python，零系统依赖）
* **Python 版本**：Python >= 3.10
* **核心依赖库**：`pytest>=7.0`, `pandas>=1.5`, `numpy>=1.20`, `matplotlib>=3.5`, `scipy>=1.9`

### 3.2 依赖安装命令
```bash
# 在项目根目录下执行
pip install -r requirements.txt
```

### 3.3 核心启动与评测复现命令（精确到可复制）

#### 1. 一键离线复现完整基准（耗时 < 2 秒）
```bash
python run_benchmark.py
```
* **预期控制台输出**：
  ```text
  ======================================================================
   D2D-Twin Benchmark: Deterministic Integrity Check
  ======================================================================
    Harness File : d2d/eval/test_d2d_blackbox.py
    Harness MD5  : 8cf0854d4779467bc8e472ee4fb97023 -> [MATCH]
    Gold IRs     : 17/17 present
  ----------------------------------------------------------------------
   Table 1: Main Benchmark Failure Breakdown (Qwen2.5-Coder-14B, N=408 Samples)
   Table 2: Cross-Model Comparison Across 17 Peripherals (N=612 Total Samples)
   [Finding] Spearman rank correlation (Special Registers vs Pass Rate): rho = -0.828, p = 0.0001
  ======================================================================
  ```

该命令校验冻结 Harness、17 份 Gold IR，并显示已记录的两张汇总表。若需要重新生成出版级图表和 LaTeX 表格，另行执行：
```bash
python run_benchmark.py --make-assets
```
生成物位于 `assets/fig1_per_chip_passrate.png`、`assets/fig2_spearman_complexity.png`、
`assets/fig3_dimension_failure_rates.png` 和 `_out/latex/`。

#### 2. 对单颗芯片执行黑盒单元测试
```bash
# 执行全部 17 颗金标参考仿真器的黑盒准入测试
python run_benchmark.py --test-ref all

# 以单颗芯片为例
python run_benchmark.py --test-ref TMP100
```

#### 3. 校验黑盒测试套件 MD5 完整性
```bash
python -c "import hashlib; print('Harness MD5:', hashlib.md5(open('d2d/eval/test_d2d_blackbox.py', 'rb').read()).hexdigest())"
```
* **预期输出**：`Harness MD5: 8cf0854d4779467bc8e472ee4fb97023`

---

## 4. 目录结构与接口契约

### 4.1 目录结构与核心职责
```text
e:\HD-Agent·分层记忆RAG的电子Dstasheet智能问答/
├── run_benchmark.py              # 【极速复现入口】一键统计 612 样本、Spearman 分析与绘图
├── requirements.txt              # 严格版本锁依赖清单
├── LICENSE                       # Apache-2.0 开源许可证
├── README.md                     # 英文官方自述文件（含 Zenodo DOI 与 HF 徽标）
├── README_zh.md                  # 中文官方自述文件
├── DATASET.md                    # 17 颗芯片详细规格说明（HuggingFace 数据集卡片）
├── HANDOFF.md                    # 【当前文件】项目全局交接标准文档
├── d2d_paper.zip                 # arXiv 提交专用自包含 LaTeX 源码包（已校验通过）
├── d2d_paper.pdf                 # 编译好的 4 页标准双栏论文（已在 Zenodo 在线预览）
├── paper/                        # 学术论文完整 LaTeX 工程
│   ├── main.tex                  # IEEEtran 双栏正文（已修复排版溢出与字符集）
│   ├── references.bib            # 规范 BibTeX 文献库
│   └── figures/                  # 论文所用的 9 张高清插图与矢量图表
├── d2d/
│   ├── ir/                       # 17 颗工业外设芯片的单写入者黄金中间表示 (Gold IR)
│   │   ├── ADS1115_ir.json       # 高精度 16-bit ADC
│   │   ├── BME280_ir.json        # 温湿度气压环境传感器
│   │   ├── INA219_ir.json        # 双向电流功率监控器
│   │   ├── MPU6050_ir.json       # 六轴运动处理传感器
│   │   └── ... (共 17 颗)
│   └── eval/                     # 评测套件与数据资产
│       ├── test_d2d_blackbox.py  # 【核心冻结】通用黑盒断言 Harness (MD5 锁定)
│       ├── results_gen_qwen.json # Qwen2.5-Coder-14B 408 次评测明细
│       └── results_gen_deepseek.json # DeepSeek-Coder-6.7B 204 次评测明细
├── assets/                       # 生成并随仓库发布的出版级图表
└── _out/                         # 重新生成的图表与 LaTeX 表格输出
```

### 4.2 外设模拟器接口契约（Bus Protocol Contract）
所有由大模型生成的仿真器类必须严格实现通用单射总线协议接口：
```python
class <ChipName>Emulator:
    def __init__(self):
        """必须按照 Gold IR 中的 reset_value 初始化所有内部寄存器及状态"""
        pass

    def write_register(self, address: int, value: int) -> None:
        """
        向指定 8-bit/16-bit 寄存器地址注入写事务。
        - 必须遵守只读（RO）保护，RO 位域不可被覆盖；
        - 必须遵守自清除（Self-clearing）位逻辑；
        - 若为写入专属寄存器（WO/Write-only），不得污染同地址读取结果。
        """
        pass

    def read_register(self, address: int) -> int:
        """
        从指定寄存器地址读取当前值。
        - 必须返回正确的位域组合整数；
        - 若该地址具有读写别名（Read/Write Aliasing），必须返回只读寄存器的数据。
        """
        pass
```

### 4.3 八大行为验证维度（Behavioral Dimensions）
* **D1 (Reset Fidelity)**：复位初始状态准确率；
* **D2 (RO Field Protection)**：只读位保护防止被外部覆盖；
* **D3 (Bitfield Persistence)**：子寄存器位域写入后，非目标位的持久留存能力；
* **D4 (R/W Aliasing)**：同一物理总线地址对应不同读写寄存器的双指针路由能力；
* **D5 (Self-Clearing Semantics)**：复位位/触发位自清除行为；
* **D6 (Pointer Multi-byte Handling)**：多字节自动递增或指针寄存器映射；
* **D7 (Range Saturation & Masking)**：数值超限掩码与截断保护；
* **D8 (Soft Reset Recovery)**：软件复位命令后的寄存器树全量恢复状态。

---

## 5. 决策与踩坑记录（新 AI 重点阅读）

### 5.1 为什么采用 Gold IR 解耦设计？（避免前车之鉴）
* **试过但失败的方案**：最初尝试直接把商业 Datasheet PDF（通常 30~80 页，包含大量多栏排版、非标表格、跨页时序图）通过 RAG 切片直接塞给 LLM 让其生成驱动仿真器。
* **诊断证据**：对 456 篇数据手册和 120 道审校题的三 seed 评测中，DCU-3B/7B/14B 各有 76、73、64 道题在三个 seed 均答错；其中 54、56、51 道被固定检索上下文的数值—单位分类归为上游相关，分别占全部题目的 45.0%、46.7%、42.5%，占三 seed 均答错题目的 71.1%、76.7%、79.7%。分类是诊断代理，不能把单位匹配缺失直接等同于 PDF 物理信息丢失，也不能用固定上下文分类证明模型规模不变性。
* **最终设计**：采用“专家/高质量脚本建立 Gold IR 规范” -> “基于纯结构化 IR 评估代码大模型系统建模能力”。这减少上游解析噪声，使断言结果可确定性复现；仍需考虑 Gold IR 策展与测试覆盖的边界。

### 5.2 代码大模型的四大系统性缺陷（论文核心论点）
在交接后续实验时，请注意以下四个已证实的模型盲区，不要怀疑是测试脚本错误：
1. **子寄存器位域持久性赤字（71.1% 失败率）**：
   - 现象：模型习惯将寄存器存储为单一大整数（如 `self.reg[0x01] = val`），导致写入某个 2-bit 字段时，直接抹除了同寄存器内的其他有效位域。
2. **读写地址别名 100% 盲区（48/48 全军覆没）**：
   - 现象：当寄存器总线地址同时支持读（如温度数据）和写（如采样配置）时，所有模型均未设计读写分离状态机，而是使用同一个变量，导致写操作直接破坏传感器输出。
3. **厂商 IP 模版污染（53.7% 失败率）**：
   - 现象：模型在预训练时学到了大量固定的开源驱动模板，遇到特殊复位位自清除时，直接照搬套用通用驱动，忽视了 Datasheet 的特定语义。
4. **复杂度雪崩（Spearman $\rho = -0.828, p = 0.0001$）**：
   - 现象：特殊语义寄存器数量越多，模型代码合成的通过率呈断崖式下跌。

### 5.3 历史关键 Bug 修复记录
1. **Overleaf IEEE 双栏表格重叠 Bug**：
   - *问题*：原 Table I 和 Table II 超出单栏限制，导致右侧文字与第二栏及参考文献重叠。
   - *解决*：在 Table 外层包裹 `\resizebox{\columnwidth}{!}{% ... %}`，强制自适应栏宽。
2. **pdflatex 编译 Unicode 崩溃**：
   - *问题*：原文档中使用了带圈字符 `①–⑧`、`④a` 等，在部分 Linux pdflatex 环境报字符编码异常。
   - *解决*：已全量标准化为纯 ASCII：`D1–D8` 与 `D4a–D4u`。
3. **Git 仓库历史大文件排险**：
   - *问题*：早前误提交了 1.58 GB 的 `OllamaSetup.exe`，导致 `git clone` 极慢。
   - *解决*：已使用 `git filter-branch` 彻底从 commit 历史中剔除并重新整理，当前 `.git` 目录轻巧健康（约 36 MB）。**切勿向仓库提交任何大型二进制文件！**

---

## 6. 外部资源、发布元数据与凭证

### 6.1 已发布的外部系统链接
* **GitHub 仓库**：`https://github.com/eggdan6666/d2d-twin`
* **Hugging Face 数据集**：`https://huggingface.co/datasets/eggdan666/d2d-twin`
* **CERN Zenodo 官方预印本**：`https://doi.org/10.5281/zenodo.23262086`

### 6.2 arXiv 待提交元数据（一键复制即可使用）
如果获得背书后在 arXiv 暂存入口继续提交，请直接复制以下内容：
* **Title**：
  ```text
  D2D-Twin: Benchmarking Large Language Models on Datasheet-to-Digital-Twin Synthesis for Peripheral Hardware Emulators
  ```
* **Authors**：
  ```text
  Chengtong Lan
  ```
* **Primary Category**：
  ```text
  cs.SE (Software Engineering)
  ```
* **Cross-Lists**：
  ```text
  cs.AI (Artificial Intelligence), cs.AR (Hardware Architecture)
  ```
* **Comments**：
  ```text
  4 pages, 3 figures, 3 tables after the repair-intervention addition. Benchmark repository available at https://github.com/eggdan6666/d2d-twin and https://huggingface.co/datasets/eggdan666/d2d-twin
  ```
* **Abstract**：
  ```text
  Virtual peripheral prototypes and register-level behavioral emulators serve as foundational infrastructure in modern electronic design automation (EDA) and embedded firmware development. While code-specialized Large Language Models (LLMs) have achieved remarkable success in general software generation and Verilog register-transfer-level (RTL) synthesis, their capacity to synthesize executable, register-accurate digital twins directly from technical datasheets remains largely uncharted.

  In this paper, we introduce D2D-Twin, the first deterministic, zero-LLM-as-a-judge benchmark specifically designed to assess LLMs on datasheet-to-digital-twin synthesis for peripheral IC emulators. D2D-Twin curates 17 representative industrial peripheral ICs spanning sensors, precision ADCs, power monitors, motion controllers, and PoE interfaces. Grounded on single-writer, human-verified Gold Intermediate Representations (Gold IR), code LLMs are prompted to synthesize executable Python register emulators evaluated against a universal blackbox pytest harness (MD5: 8cf0854d4779467bc8e472ee4fb97023) across 8 behavioral specification dimensions.

  Across 612 fully evaluated synthesizer runs (N=408 on Qwen2.5-Coder-14B at n=24, and N=204 on DeepSeek-Coder-6.7B at n=12), our empirical findings reveal critical architectural deficits in code LLMs: 
  (1) Sub-register Bitfield Persistence Deficit: models predominantly adopt a monolithic integer storage antipattern, leading to a 49.2% failure rate in read-only protection and 71.1% in bitfield persistence; 
  (2) Read/Write Address Aliasing Blindness: models exhibit a catastrophic 100.0% failure rate (48/48) on dual-pointer alias registers; 
  (3) Vendor IP Template Contamination: models hallucinate identical templates across product lines, yielding 53.7% failure on self-clearing reset bits; and 
  (4) Complexity Collapse: a strong negative Spearman rank correlation (rho = -0.828, p = 0.0001) between special semantic register counts and synthesis pass rates.
  All evaluation harnesses, Gold IRs, and generated code samples are open-sourced on GitHub and Hugging Face.
  ```

### 6.3 2026-10-10 三芯片扩展模型评测（已完成）
* 本轮在 SCNet DCU 节点完成了 Qwen2.5-Coder-14B-Instruct 与 DeepSeek-Coder-6.7B-Instruct 的三芯片扩展评测：AD5592R、LIS3DH、MPU6050。
* 每个模型/芯片组合使用 seeds `1,2,3`、temperature `0.7`；Qwen 每组合 24 个样本，DeepSeek 每组合 12 个样本，共 **108 个生成样本**。
* 结果：AD5592R 两个模型均为 100% 全绿；LIS3DH 为 Qwen 14B `9/24 = 37.5%`、DeepSeek `0/12 = 0%`；MPU6050 两个模型均为 `0%`。全体合计 `45/108 = 41.7%`。
* 失败集中在可解释的寄存器语义：LIS3DH 的 `WHO_AM_I`/`OUT_X_L`/`STATUS_REG` 只读保护，MPU6050 的 `ACCEL_XOUT_H` 只读保护与 `PWR_MGMT_1.DEVICE_RESET` 写触发；少量样本还暴露 `SMPLRT_DIV`、`YG_ST`、`CTRL_REG0.SDO_PU_DISC` 位域持久性问题。
* 原始 JSON、启动日志和机器汇总：[`_setup/remote_model_eval/`](file:///E:/HD-Agent·分层记忆RAG的电子Dstasheet智能问答/_setup/remote_model_eval/)。分析报告：[`_setup/REMOTE_MODEL_EVAL_REPORT.md`](file:///E:/HD-Agent·分层记忆RAG的电子Dstasheet智能问答/_setup/REMOTE_MODEL_EVAL_REPORT.md)。
* 这组分数只代表冻结 black-box harness 下的生成样本通过率；扩展 I2C/SPI 协议测试仍单独记录在 [`_setup/EXTENDED_PROTOCOL_REPORT.md`](file:///E:/HD-Agent·分层记忆RAG的电子Dstasheet智能问答/_setup/EXTENDED_PROTOCOL_REPORT.md)，未混入本轮 108 样本分母。
* 随后的最小修复干预已完成：对 LIS3DH、MPU6050 各抽取两个模型的首个失败样本，四个候选均未提高严格通过数；DeepSeek/MPU6050 候选发生回归并被门禁拒绝。详情见 [`_setup/EXTENSION_REPAIR_PILOT.md`](file:///E:/HD-Agent·分层记忆RAG的电子Dstasheet智能问答/_setup/EXTENSION_REPAIR_PILOT.md)。该结果应作为负对照记录，不得写成准确率提升。
* 进一步的单维探针已完成：只提供 RO 失败时，Qwen2.5-Coder-14B 的 MPU6050 单样本从 `3 passed, rc=1` 修复到 `4 passed, rc=0`；LIS3DH 两模型未改善。只提供写触发失败时，Qwen 未改善，DeepSeek 回归并被拒绝。这个正结果是单样本干预证据，不改变 24 样本生成通过率。
* RO 稳定性复现已完成：固定 seeds `1,2,3` 各抽取一个失败样本，Qwen14B 在 MPU6050 上 `3/3` 严格提高、`2/3` 全绿；在 LIS3DH 上 `1/3` 提高并全绿。该结果支持 RO 语义修复的局部可迁移性，但剩余 LIS3DH RO 与 MPU6050 写触发失败仍需分开处理。
* `DEVICE_RESET` 写触发稳定性检查已完成：Qwen14B 在 3 个固定样本中 `2/3` 提高、`1/3` 全绿；DeepSeek 在 `1/3` 提高中出现 `2/3` 回归。由于候选同时改变了其他寄存器行为，不能把这些结果写成纯触发语义准确率；必须先做 patch-diff 与语义审计。
* 触发补丁审计已完成：六个候选中 **0/6** 属于干净的 `DEVICE_RESET` 专项修复；Qwen 的部分提升来自额外 RO 防护或仍残留触发失败，DeepSeek 有回归。审计报告为 [`_setup/TRIGGER_PATCH_AUDIT.md`](file:///E:/HD-Agent·分层记忆RAG的电子Dstasheet智能问答/_setup/TRIGGER_PATCH_AUDIT.md)。
* 受限提示词 + 自动 diff 范围门禁复跑已完成：Qwen `0/3` 范围通过，DeepSeek `1/3` 范围通过但无性能提升；干净触发修复仍为 `0/6`。这说明仅靠提示词不能稳定完成单字段补丁，需要结构化补丁接口或更强解码约束。
* 结构化 `write_register` 方法接口已实测：Qwen `1/3` 范围通过、DeepSeek `3/3` 范围通过，但六个候选均未达到完整 Harness 全绿（`0/6` clean green）。结构化接口减少了整文件重写，却尚未解决触发语义本身。详情见 [`_setup/STRUCTURED_PATCH_REPORT.md`](file:///E:/HD-Agent·分层记忆RAG的电子Dstasheet智能问答/_setup/STRUCTURED_PATCH_REPORT.md)。
* 正式参考实现的契约级修复已完成：AD5592R、LIS3DH、MPU6050 均通过候选准入，共 `11 passed, 13 skipped`；扩展 I2C/SPI 协议测试 `10 passed`。这证明 Gold IR 与 Harness 可形成完整可执行参考，但不等同于模型原始生成能力提升。详情见 [`_setup/CONTRACT_REPAIR_FINAL.md`](file:///E:/HD-Agent·分层记忆RAG的电子Dstasheet智能问答/_setup/CONTRACT_REPAIR_FINAL.md)。

---

## 7. 给接手 AI 的第一项任务自检清单

新接手 AI 在开始工作前，请先按以下顺序执行自检：
1. 运行 `python run_benchmark.py`，确认 Harness MD5 与 20/20 Gold IR 完整性通过（其中 17/17 是历史基线，3 个是正式扩展）；需要刷新图表时再运行 `python run_benchmark.py --make-assets`，确认 `assets/` 与 `_out/latex/` 生成成功；
2. 运行 MD5 校验命令，确保 `d2d/eval/test_d2d_blackbox.py` 的哈希值为 `8cf0854d4779467bc8e472ee4fb97023`；
3. 阅读第 5 节的四大缺陷与踩坑记录，不得修改已冻结的测试断言逻辑；
4. 若用户已完成背书，协助用户将 `d2d_paper.zip` 在 arXiv 上完成提交。
