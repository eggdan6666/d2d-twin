# HD-Agent 交付清单

打包时间 2026-10-07 01:00（第三次打包，产物 `HD-Agent_delivery_20261007.zip`）。
前两次留档：`HD-Agent_delivery_20261006.zip`（14:13 版）、`HD-Agent_delivery_20261006_0652.bak.zip`（06:52 版）。
打包脚本 `_setup/package.py`；机读摘要 `delivery/package_summary.json`（zip 名与大小以该文件为准）。

**本版相对 10-06 14:13 版新增**：`results_app36fix_7bloose.json`（检索路由修复后的 app 批次三重测）、`ctx_v3_k5.json` / `ctx_v6_k5.json`（预导出检索上下文，供跨硬件比较）、`_setup/dcu_runner.py`（DCU/transformers 侧评测器）、更新后的 `app_tier_summary.json`（含 Fisher 精确检验判定）。
**本版含一处对前一版结论的更正**：批次三题干改动破坏了 `run.py` 的型号定位正则，app 分档数字已按修复后重跑值替换（详见文末「更正记录」第 4 条）。

---

## 压缩包

- 名称：`HD-Agent_delivery_20261007.zip`（项目根，与 `delivery/` 同级），大小见 `delivery/package_summary.json` 的 `zip_mb`（33.8 MB / 8156 条目）
- **不含** 456 份 PDF 原件（合计 0.98 GB），只含清单 `delivery/corpus/raw_pdf_manifest.json`（path + bytes）
- **不含** 检索缓存 `rag/.cache_bm25.pkl`、`rag/.cache_index.pkl` → 接手方需自跑 `python rag/build_vectors.py`（约 9 分钟，CPU）重建向量索引；BM25 缓存首次检索自动重建（冷约 25s）

## 交付物

| 类别 | 内容 | 位置 |
|---|---|---|
| 评测集·**正式** | `datasheet_qa100_v3.json` 120 题 = param 83 + cross 37，全部人工审校，严格判分 | `delivery/qa100/` |
| 评测集·**含 app** | `datasheet_qa100_v5.json` 132 = v3 + app 12；`datasheet_qa100_v6.json` **168** = v5 + app 36；app 48 题按取证章节分两档（`app_tier_summary.json`） | `delivery/qa100/` |
| 评测集·**子集** | `datasheet_qa100_app36.json` 36 题（批次三，用于跨硬件/跨模型重跑） | `delivery/qa100/` |
| 预导出上下文 | `ctx_v3_k5.json`（120 题）、`ctx_v6_k5.json`（168 题）：每题的检索上下文 + sources + ctx_flag，**已验证与主矩阵 120/120 逐题一致** → 跨硬件比较用它可保证检索恒等 | `delivery/qa100/` |
| 评测集·**参考** | `datasheet_qa100_v4.json` 150 题 = v3 + 30 道 app **auto-draft 未经人工审校**（16 道经核实为型号字符串残片），不可用于结论 | `delivery/qa100/` |
| 审校留痕 | `review.csv`(229 行含 verdict)、`review_app.csv` + `.orig.csv`、`review_app3.csv` + `.json`、`review_app2.superseded.csv` | `delivery/qa100/` |
| 语料 | `corpus_index.jsonl`（456 行）、`corpus_stats.json`（docs=456 / chunks=**7579**）、7579 切片 + 456 份解析全文 | `delivery/corpus/`、zip 内 `corpus/data/` |
| 报告 | `REPORT_qa100_baseline.md`（主矩阵 + 判分观察 + 守卫日志 + app 第二轮 + v6 分口径 + **检索路由更正节**）、`REPORT_ktrial.md`、`REPORT_prompt_loose.md`、`REPORT_memtier_repro.md`、`REPORT_longmemeval_7b.md`、`REPORT_longmemeval_full.md` | `delivery/results/` |
| 结果 json | 36 个 `results_*.json`（v3 主矩阵、API 基线、k-trial 6 seed、v4、app 两轮、app36fix）；M2 LongMemEval-S 逐题日志 9 个 `.jsonl` 共 6060 行；`retrieval_ablation.json` | `delivery/qa100/`、`delivery/results/` |
| 图 | `fig_pareto_cost.png`、`fig_pareto_latency.png` + 数据表 `pareto_summary.csv`（前沿只连协议 v3.1/temp=0/120 题的 6 个配置） | `delivery/qa100/` |
| 代码 | `rag/` 11 模块、`corpus/scripts/{download,manifest,parse}.py`、`run_longmemeval.py`、`eval/qa100/` 出题判分链（含修复后的 `run.py`、`gen_app_drafts.py`） | `delivery/code/`、`delivery/qa100/` |
| 流水线副本 | `package.py`、`pareto.py`、`finalize_app.py`、`dcu_runner.py`（`.gitignore` 默认排除 `_setup/`，故在包内留副本） | `delivery/code/setup/` |

## 核心数字（RAG-7B-loose = qwen2.5:7b-instruct-q4_K_M，严格判分 `eval/qa100/score2.py:correct()`）

| 项 | 数值 | 来源 |
|---|---|---|
| v3 120 题 · temp=0 | 41.7%（param 42/83、cross 8/37） | `results_v31_rag7b_loose.json` |
| v3 120 题 · temp=0.7×3 seeds | mean **41.7% ± 1.7pp**，95%CI [37.5, 45.8]（t=4.303） | `results_kt_rag7b_s{1,2,3}.json` |
| RAG-3B · temp=0.7×3 seeds | mean 33.6% ± 2.9pp，CI [26.3, 40.9] | `results_kt_rag3b_s{1,2,3}.json` |
| **7B − 3B = 8.1pp** | Welch 差值 CI **[−0.3, +16.4]pp 含 0 → 分辨不出**（该检验可分辨下限约 11pp，8.1pp 在其下） | `REPORT_ktrial.md` |
| 本地 7B-loose vs 商用 API | API(DeepSeek-V4.1-Flash，同检索协议) 36.7%（temp=0 单次、无 seeds）；7B-loose CI 下界 37.5% > 36.7% → **方向成立，属单向检验**；且 API 侧 2727 tok/题 vs 本地 3001（本地多 10.0%），非严格等信息量对照 | `results_v31_api_rag.json` |
| API 裸答（无检索） | 21.7% | `results_v31_api_bare.json` |
| **app 档 A**（typ_app 原理图图注，n=22，人工审校） | **7/22 = 31.8%**（第一轮 3/12 + 批次三 typ_app 源 4/10，两批 Fisher p=0.65 可并档） | `app_tier_summary.json` |
| **app 档 B**（overview/func_desc 选型表，n=26，人工审校） | **2/26 = 7.7%** | 同上 |
| **A − B = 24.1pp** | **Fisher 精确检验双侧 p = 0.0607 → 方向明确但未达 0.05 显著**（正态近似 CI [1.4,46.8] 不含 0，但 app-B 仅 2 次成功、期望频数<5，以 Fisher 为准） | 同上「统计判定」节 |
| app 48 混装（仅内部对账） | 9/48 = 18.8% | 同上 |
| v4 未审校 app（清洗前后对照） | 3/30 = 10.0% | `results_v4_rag7b_loose.json` |
| LongMemEval-S（M2 记忆层复现） | ④ 混合上下文 3B-loose = **0.364**，论文 MemTier@7B = 0.382 → 复现成立 | `REPORT_memtier_repro.md` |

## 已知局限（引用前必读）

1. **app 列不能给单一分数**。档 A/B 取证位置不同（原理图图注 vs 选型表）、题干不同（`typical application circuit` vs `application design guidance`）；合并 18.8% 会同时低估 A 档能力、掩盖 B 档异质性。档 B 是为满足计划书"30 道应用题"配额而扩源引入的。
2. **规模增益不显著**：3 seeds（n=3）带宽大，7B 对 3B 的 +8.1pp 落在 CI 内；loose 增益（3B 0.0pp / 7B +2.5pp）也小于各自半宽 → 只能写方向不能写幅度。
3. **cross 与 app-B 是短板**（7B-loose 分题型 cross 27.0%±2.7，n=37；app-B 7.7%，n=26）。失败主因经实测为**生成侧的值—对象绑定错配**，不是检索未命中：app-B 修复检索后重算，gold 值仍在上下文内而模型答不出。
4. **严格判分口径**：负号精确、gold 带单位则 pred 必须同单位、范围需双端点；bound-type 题（`<10kΩ`、`≤207Ω`、`≥ 1000 µf`、`<10kΩ`）不等号**不参与判分**，"满足约束的更小值"会被判错，共 4 题，note 已标注。
5. **延迟数字不可跨轮混比**：模型冷热、上下文长度影响大（app 列两轮 33.3s 与 9.2s/题；DCU 14B-bf16 实测 12.5 tok/s，慢于本地 7B-q4 的 15.2）；成本/帕累托结论只用同轮同配置数据。
6. **语料侧结构损失**：`parse.py` 的 PyMuPDF `find_tables` 把多行单元格压成一个字符串，表格列结构在解析期丢失 → 表格级问答在本语料上不可行，是 app-B 与 cross 失分的上游原因之一。
7. **PDF 原件未随包交付**（版权与体积），复现需按 `raw_pdf_manifest.json` 自取或替换同型号器件。

## 复现

```
pip install pymupdf requests numpy matplotlib torch transformers   # 见 README.md
# 1) 语料：corpus/scripts/{manifest,download,parse}.py（PDF 需自备或用清单内直链）
# 2) 检索冒烟：python -m rag.cli "LM2596 absolute max input voltage"
#    标准环境：HF_HUB_OFFLINE=1  RAG_EMBED_MODEL=BAAI/bge-small-zh-v1.5（不设则纯 BM25）
# 3) 评测（**必须显式 --ds**，不给时 run.py 会按"存在即最新"自动选数据集）：
python eval/qa100/run.py --ds eval/qa100/datasheet_qa100_v3.json \
       --model qwen2.5:7b-instruct-q4_K_M --loose --tag rag7b_loose
python eval/qa100/run.py --ds eval/qa100/datasheet_qa100_app36.json --tag app36fix --loose
# 4) 判分复核：python eval/qa100/score2.py（离线重判已有 pred，零 GPU）
# 5) 帕累托图：python _setup/pareto.py
# 跨硬件/更大模型（DCU 等）：python _setup/dcu_runner.py --ctx-file eval/qa100/ctx_v3_k5.json \
#       --model-path <safetensors目录> --ds eval/qa100/datasheet_qa100_v3.json --loose
#    （--ctx-file 使检索恒等由构造保证，无需上传语料；--retrieval-check 可核自己语料版本）
# API 侧：.env 里 SCNET_API_KEY=...（勿提交），RAG_LLM_MODEL=scnet:<模型ID>
```

## 安全核查（本次外发前）

- `.env` **不在** delivery/ 与 zip 内；`.env` 已被 `.gitignore` 排除
- 逐条目扫描 `sk-tp-*` / `SCNET_API_KEY=`：**无真实密钥**；唯一命中是 `api_pretest.py` 文档字符串里的占位 `sk-tp-xxx`
- 456 份 PDF 只出清单不出包，避免重新分发厂商文件

## 更正记录

1. `FINAL_CHAIN_DONE` 实际写盘时刻 **05:44:38**（06:52 版正文写 05:47/05:48）——依据 `_setup/final_chain.log` 的 mtime 与 `v4_7bloose: rc=0 84.9min` 行。
2. 链日志共 **7 个评测段、6 段 rc=0**（06:52 版写"全部 8 段中 7 段 rc=0"，把 `FINAL_CHAIN_DONE` 行误计为一段）。`kt_rag7b_s1` 首跑 rc=-1 零产出，由另一会话 05:47:30–06:43 以同协议同 tag 补跑成功，未删除或覆盖任何结果文件。
3. 06:52 版缺「已知局限」小节，本版已补（上节 7 条）。
4. **（10-07 新增）检索路由缺陷与 app 分档重测**：批次三题干改为 `application design guidance for X` 后，`run.py` 的型号定位正则 `of ([\w\-.]+) \(` 对 **36/36 不命中**，这些题退化成全局检索。已在 `run.py` 加与措辞无关的兜底修复，**回归证明 v3 的 120 题上下文修复前后 120/120 逐题相同**（主矩阵、k-trial、帕累托、第一轮 app 均不受影响）。修复后重跑：app-B **11.5% → 7.7%**、合并 20.8% → 18.8%、A−B 差 20.3pp → 24.1pp。**同时撤回一处说法**：先前称"app-B 读数被污染不可信"，实测净影响只有 1 题，量级在噪声内；分档结论与"扩源到 overview 是负收益"的判断不变且修复后更强。统计判定改用 Fisher 精确检验（app-B 期望频数<5，正态近似不可信）：**p = 0.0607，方向明确但未达显著**。
5. **（10-07 新增）撤回一条对第三方结论的采信**：外部审阅意见称"提示词松绑对 3B 有效、对 7B 反作用"——该读数出自 v3.0 协议；当前 v3.1 下为 3B +0.0pp / 7B +2.5pp，方向相反且均小于噪声，两版都不可作幅度结论。
