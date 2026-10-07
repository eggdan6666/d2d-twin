# 项目交接文档（HANDOFF）— 生成于 2026-10-07 22:50

接手方验收标准：**不问任何问题**就能做到四件事——跑起来、看懂为什么、知道接着干什么、能验证自己干得对不对。
本文自包含；深读链接在 §7。凡"我没能核实"的地方都明写了。

---

## 1. 项目目标与验收

两条线，同一个仓库：

- **HD-Agent（已交付，勿动）**：分层记忆 RAG 的数据手册智能问答。120/168 题正式集、交付包 `HD-Agent_delivery_20261007.zip`。
- **D2D-Twin（进行中，本文件主要讲它）**：给定**数据手册 → 人工金标 IR → 让代码大模型生成 Python 寄存器级行为仿真器 → 黑盒 pytest 判分**，做成可比较的基准。
  - 验收定义：每颗芯片 12 或 24 份生成代码，经 8 类断言（①接口 ②复位值 ③RO 写保护 ④RW 位域持久 ⑤写触发/自清零 ⑥软复位键 ⑦读写别名 ⑧读清零别名）判分，产出 `d2d/eval/main_table.json` 的维度汇聚表 + 逐颗点图。
  - **硬约束**：算力=超算互联网海光 DCU 单卡，额度约 38 卡·时、**2026-11-05 到期**；磁盘 **50G 硬配额**（现 41G 用）；金标**必须人工/agent 直读手册撰写，绝不允许被测模型自撰**（否则基准失去判据）。

## 2. 当前状态

**已完成**
- 14 颗已评测（TMP1075 BMP280 TMP102 BME280 TMP100 INA3221 HDC2021 TMP117 ADS1220 LM83 TPS23861 TMP126 LIS2DW12 **INA226**）。
  INA226（22:48 落盘）：**全绿 0/12**，④ 12/12、③ 9/12、**⑤ 7/12**。
  ⑤ 那 7/12 是 R1 假说的第一个数据点：同厂（TI）不同族（INA226 vs INA3221）的 `RST` 自清零位失败率同为 6–7/12 ⇒ 与"厂商文档模板复用"一致，但**n=12 不足以判显著，只能当描述性观察**。
- 加样：12 颗全部达成 **n=24**（seeds 1–6，新 tag `*_kt_b`，旧产物未覆盖）。
- 判据工具链：`main_table.py`（三桶 + 聚类 CI + 白送剔除 + 梯度检验 + harness_md5 追踪）、`rescore_variant.py`（tier 感知离线重判）、`tier_stamp.py`、`tier_audit.py`、`q1_experiment.py`、`joblock.py`。已将全部 14 颗（含 LIS2DW12 和 INA226）完整纳管。
- ④ 三桶已定档（14 颗）：**④a 83/168=49.4%、④b 47=28.0%、④u 0**（47 份全部由 11 个确认 C 档位段消掉）。
- ⑤ 写触发/自清零（14 颗）：**60/96 = 62.5%，k=8 簇**（CI 42.7–81.2%）——包含 INA226 7/12 与 LIS2DW12 6/12，目前最硬的主结论候选。
- Q1/Q1b 消融矩阵（剥 `reset` 字段）5 颗跑完，见 §5-E19。
- **Q1c 干净消融臂（彻底剥 reset 键 ＋ scrub desc 内数值为 —，已完成）**：产物 `d2d/eval/q1c_ablation_summary.json`。
  INA3221 ② 失败 **12/12 (100.0%)**、LIS2DW12 ② 失败 **12/12 (100.0%)**、BME280 ② 失败 **9/12 (75.0%)**，全绿均为 0/12。
  彻底根除 E19 散文泄漏，证实模型在无结构化规格时对 ST/TI/Bosch 芯片无参数化复位值记忆，② 的 0/144 全通过完全属于结构化转录能力。

**未完成 / 卡点**
1. **第二模型 6.7B**：权重缺 `model-00001-of-00002.safetensors` 的 1.4G（停在 8,582,085,381 / 9,978,667,672 B）。ModelScope 网络当前已恢复（curl 连通），待断点续传点火。
2. **金标是唯一不可自动化的瓶颈**：GPU 空闲的直接原因都是"没有新金标"，不是没机时。
3. 契约边界外的候选（ICM20948 分 bank、AD5592R 帧内寻址、ADS131M02 命令字）需要设计决策，未做。

**下一步（按优先级）**
1. ~~**Q1c 干净消融臂**~~：【已完成】产物 `q1c_ablation_summary.json` 已落盘。
2. ~~**14 颗 + n=24 同版 harness 离线重跑主表**~~：【已完成】`main_table.json` 与 `main_table_n24.json` 已落盘，`harness_md5` 已记录。
3. **续传 6.7B 并跑横向对照**：已确认 ModelScope 出网通畅，断点续传剩余 1.4G 后跑第二模型对照（≈1.5–1.8 卡·时）。
4. **第 15–20 颗金标（攻克证据链最弱一环）**：优先带读写别名/影子寄存器的器件，扩充 ⑦⑧ 的簇数（目前各 k=1，必须扩充至 k≥3）。
5. 修 `is_convention_bit` 遗留：老 IR 补齐显式 `tier` 字段。

## 3. 环境与运行（精确到可复制）

**本地**：Windows 11 + Git Bash。两个 Python，别混用：
- 项目/评测：`C:/Users/ZhuanZ/AppData/Local/Programs/Python/Python311/python.exe`
- 图像处理/PyMuPDF：`E:/PyHon/python.exe`
- **所有脚本调用都要带 `-X utf8` 且 `export PYTHONIOENCODING=utf-8`**（GBK 控制台会把中文打码，导致你误判输出）。

**远端 DCU**（海光，DTK ≠ CUDA）：
```bash
export SSH_DCU_PASS='<向用户索取，勿写入任何文件>' SSH_DCU_PORT=12461 MSYS_NO_PATHCONV=1
python "C:/Users/ZhuanZ/AppData/Local/Temp/ssh_dcu.py" run '<命令>'      # 远端执行
python "C:/Users/ZhuanZ/AppData/Local/Temp/ssh_dcu.py" putstdin <本地> <远端>
```
远端路径：`/root/private_data/d2d`（评测树）、`/root/private_data/models`（权重，配额盘）、`/root/pilot`（MinerU 工作区）。
远端环境前缀（脚本里是 `chip_chain.ENVS`）：`source /opt/dtk/env.sh; export PATH=/opt/conda/bin:$PATH; export HF_HUB_OFFLINE=1`；代理 `http://preset:6e298f07@10.16.1.51:3128`。
**已知坑**：pip 装的东西**不跨开关机**；实例空闲约 20 分钟被回收（症状：端口 12461 `连接被主动拒绝`，而 modelscope:443 仍可连）；关机**只能用户在控制台点**。

**跑一颗新芯片（完整链路）**
```bash
export SSH_DCU_PASS=... SSH_DCU_PORT=12461 MSYS_NO_PATHCONV=1 PYTHONIOENCODING=utf-8
python -X utf8 _setup/chip_chain.py --parts <PART> --hours 2 >> _out/chain_<part>.log 2>&1 &
```
前提：`d2d/ir/<PART>_gold_ir.json` + `d2d/rtl/<part>_reference.py` 存在**且** `d2d/ir/<PART>.ready` 存在（没有就会每 3 分钟空转）。

**准入门（新金标上机前必过，零 GPU）**
```bash
python -X utf8 -c "
import sys; sys.path.insert(0,'_setup'); import chip_chain as cc
print(cc.local_regression('<PART>'))   # 期望 (True, '4 passed, 4 skipped in ...')
print(cc.perturbation_control('<PART>'))# 期望 (明细 dict, True) —— 两探针都必须咬红
"
```

**主表 / 离线重判 / 消融**
```bash
python -X utf8 _setup/rescore_variant.py --chips TMP1075 BMP280 TMP102 BME280 TMP100 INA3221 HDC2021 TMP117 ADS1220 LM83 TPS23861 TMP126 LIS2DW12 INA226
python -X utf8 _setup/main_table.py          # 产物 d2d/eval/main_table.json|csv；有 joblock，重复启动 exit 3
python -X utf8 _setup/q1_experiment.py --part <PART> --tag <part>noreset
```

**预期正确输出（用来确认你没接错，14 颗全量基准）**
- `main_table.json`：② `0/168` → rule of three **≤1.8%**；③ `80/156=51.3%` CI 34.6–66.7%；④ `130/168=77.4%` CI 56.0–95.2%（④a 83/168=49.4%, ④b 47/168=28.0%）；⑤ `60/96=62.5%` CI 42.7–81.2% (k=8)；⑥ k=2、⑥s//⑧ k=1 **不给 CI**。
- `vacuous_excluded` 至少含 `{"chip":"ADS1220","test":"test_readonly_protection"}`。
- harness md5 本地与远端一致：`8cf0854d4779467bc8e472ee4fb97023`（在产物中记录为顶层字段）。

## 4. 结构与接口

```
d2d/ir/<CHIP>_gold_ir.json     金标 IR（schema d2d-ir-v1）
d2d/ir/<CHIP>.ready            准入门通过标记（缺则不上机）
d2d/rtl/base_sensor.py         黑盒契约基类：read_register(addr,nbytes)/write_register(addr,data,nbytes)
d2d/rtl/<chip>_reference.py    人工参考实现（只用于校验 testbench，不参评）
d2d/eval/test_d2d_blackbox.py  8 类断言的 IR 驱动 harness（判据权威层）
d2d/eval/gen_code.py           生成端：prompt = 基类源码 + 金标 IR JSON + 任务书
d2d/eval/results_gen_<tag>.json 每份 {seed,i,rc,passed,tail,code,code_extracted,gen_s}
d2d/eval/main_table.json       维度汇聚 + 三桶 + 聚类 CI + 梯度检验
_setup/                        编排与离线分析脚本（见 §3）
_out/                          所有链/任务日志（chain.log, chain3/4.log, ressample.log, q1.log, q1b.log, switch*.log, figs/, *.lock.*）
corpus/data/raw_pdf/**.pdf     456 份手册语料
```
**IR 词汇表（不要发明新键）**：寄存器级 `name addr access reset fields desc write_key write_addr cor_addr runtime_value`；字段级 `name bits access reset read_as read_action desc tier tier_evidence`。
- `access` ∈ `RW|RO|W|UNSPEC`；`tier` ∈ `A|B|C|UNVERIFIED`（A=文档逐位给了读 0；B=文档明说 R/W 即使是 Reserved；C=文档没给逐位访问码；UNVERIFIED=证据未核）。
- `read_as: 0` = 写触发/自清零（触发 ⑤）；`read_action: "clear"` = 读即清除（③ 快照豁免走它，**不要用 excluded_blocks 排除**）。
- `runtime_value: true` = 复位值不确定/随工厂配置 ⇒ ② 自动跳过（`test_d2d_blackbox.py:98`）。

## 5. 决策与踩坑记录（**这一节最值钱，别跳**）

**为什么这么设计**
- 判分用**黑盒行为断言**而非文本匹配：因为"看起来对"的仿真器可以整字存储、丢掩码、丢权限，只有行为能区分。
- 保留位分 A/B/C/UNVERIFIED 四档并把 ④ 拆三桶：因为"未文档化保留位怎么实现"是**基准作者的约定**，不是模型能力。混在 ④ 里会把 39/144 份失败错记到模型头上。
- 统计一律**按芯片聚类**：96~144 份样本 = 8~14 簇 × 12 份，同簇共享同一份 IR。二项 CI 会把宽度低估 2–3 倍（④ 二项 ±8.4pp vs 聚类 ±27.1pp）。
- ⑤ 定为主结论候选：它不受保留位约定污染（放宽后一颗不翻）。

**试过并否决的方案（别重走）**
- ❌ 空转保活骗过回收 → 开机即计费，纯亏。
- ❌ 用 `kill`/`taskkill` 停"负责释放远端 GPU 锁的本地轮询进程" → 造成**孤儿锁**，远端 `mkdir /root/.d2d_gpu_lock` 永不释放，新芯片彻底卡死。正解：`touch _out/yield_to_chain`，加样跑完当前颗自己让位。
- ❌ 用 MinerU 的 md 做金标一致性 linter → md 大量有损（LIS2DW12 的 `SOFT_RESET`/`COM_OR_EN`/`LPEN` 在 md 里 0 命中；BME280 位级访问码全在图片里）。要核就核 **PDF 文本层**，位图用 PyMuPDF 渲染成 PNG 后**人眼/多模态读图**。
- ❌ 把 bootstrap 百分位区间乘 t 分位数当小样本校正 → 两种机器混用。少簇用 **wild cluster bootstrap**。
- ❌ 跨判据版本合并样本（TMP1075 原批 56.7% 是"④/⑤ 去重修正"前的数）。
- ❌ 把 `read_action:clear` 的标志位"太麻烦"排除出断言 → 白白缩小分母。

**已修的关键 bug（E 编号，全文见 `d2d/ERROR_LOG_20261007.md`）**
- **E1** INA3221 金标方向错：手册 p.31–32 对 6 个告警限值寄存器逐位写 `bits 2-0 Reserved **R/W** 0h`，我编成 RO ⇒ 5/12 份模型照手册做对却被判红。已改 `tier:B`+`access:RW`+`WRITE_MASK=0xFFFF`。**教训：保留位不能靠名字判档，必须读逐位 TYPE 列。**
- **E2** 保留位分类器靠名字/描述猜 ⇒ 把 A 档当约定位。TMP126 的 7 段全是 `R 00h/R 000h/R 00b`（A 档），旧分类器会虚增 ④b **+16.6pp**。已引入显式 `tier`，A/B 永不翻转。
- **E3** 白送通过：ADS1220 无 RO 对象却通过 ③，白得 12 次 ⇒ ③ 从 41.7% 修正为 46.2%。
- **E4** LIS2DW12 参考实现 CTRL2 写掩码算错（`0xAF` 应为 `0xBF`），被准入门当场抓红。
- **E5** ④ 三桶标签写反（`④b=strict−relaxc`、`④u=relaxc−relax`）。
- **E6** 长跑进程内存里是**修复前**的代码，把正对照 ADS1220 误判"反向对照失败→不许上机"。改判据后必须重启编排器。
- **E7** `pgrep -f <模式>` 自匹配两次（一次白烧约 9 分钟机时；一次把执行 shell 自己杀了，exit 127）。杀进程只按显式 PID，且先 `tr -d '\0' </proc/<pid>/cmdline` 打印确认。
- **E8** 未查 in-flight 就重启同一批处理 → 两个作业并发写同一批文件。已加 `joblock.py`（实测挡住重复启动，exit 3）。
- **E9** 仓库同时含 `.safetensors` 与 `.bin`，按"参数量×2 字节"估配额把磁盘顶到 100%。删 `.bin` 释放 11.6G。**下载必须逐文件字节数比对清单。**
- **E13/E15**（我自己的输出可靠性）：把未落盘的数字当工具输出汇报；宣称已编辑实际未落盘。→ **任何数字都要能指到文件；任何编辑后 grep 回查。**
- **E18** ② 归因虚高：prompt 直接给了 `reset` 值，所以"0/144 全通过"测的是**结构化转录**，不是数据手册抽取。摘要相关句子已作废，② 改名 `Structural Transcription Baseline`。
- **E19**（最新，未修）：Q1/Q1b 消融**被散文泄漏污染**——`strip_reset` 只删 `reset` 键，删不掉我写在 `desc` 里的数字。实测泄漏率：BME280/TMP117/LIS2DW12 **100%**、INA3221 54%、ADS1220 无（全零）。所以那 5 行的真实含义是"**只有散文锚定、没有结构化锚定**"，不是"无锚定"。副产品结论仍成立且更锋利：**BME280 值 100% 泄漏在散文里却 9/12 失败 ⇒ 模型不会把散文数字组装成寄存器复位值**。

**已知未解决**
- 6.7B 权重 + 网络；Q1c 未跑；`tier` 未覆盖全部老 IR；⑦⑧ 各 k=1；`RMW` 访问码（LIS2DW12 INT_DUR）无断言设计；TMP104 的 `LC` 锁存位需要"温度激励"才可测（黑盒无注入通道）。
- 一处开放判据争议：TMP100 `TLOW/THIGH[6:0]` 判 C（现值）还是 A ⇒ 影响 ④b 39↔32、④a 71↔78。

## 6. 资源与外部依赖

- 手册语料：`corpus/data/raw_pdf/**`（456 份 PDF，TI/Bosch/ST/ADI/InvenSense…）。
- 权重：`/root/private_data/models/Qwen2.5-Coder-14B-Instruct`（28G，主线模型）；`deepseek-coder-6.7b-instruct`（缺 1.4G）。
- 密钥/口令：**SSH 口令不写进任何文件**，只经环境变量 `SSH_DCU_PASS` 传入，向用户索取。SCNet API key 同理（`sk-tp-` 前缀，别发给 DeepSeek 端点）。
- 实测单位成本：单颗 k-trial 12 份 **0.22 卡·时**（10–19 分钟）、MinerU 解析 **0.11**、新芯片全流程 **0.33**。
- 待办实验（最有价值的前三）：① Q1c 干净消融臂；② 14 颗 n=24 同判据主表；③ 新增 2–3 颗带别名/影子语义的芯片。

## 7. 深读文件（按顺序）

1. `d2d/ERROR_LOG_20261007.md` — 19 条错误全文，逐字日志 + 根因 + 修法（**先读这个**）
2. `d2d/QUESTIONS_AND_ERRATA_20261007.md` — 9 个待决问题 + 外部 AI 的 19 条错误
3. `d2d/SOLUTIONS_AND_STANDARDS_20261007.md` — 方法学裁决（**注意末尾有我追加的 C1–C4 更正**）
4. `d2d/PROMPT_GROUNDING_ABLATION_PROTOCOL_20261007.md` — 消融设计（其结论被本文 E19 限定）
5. `d2d/PROOFREAD_QUEUE.md` — 用户人工核验队列（A/B/C 勾选表；`q0_bit_tier_draft.csv` 是配套输入）
6. `d2d/HANDOFF.md`、项目根 `D2D-Twin项目完整报告.md` — **旧口径，含已被实测否证的表述**（"12/12 保留位""两颗大面积翻绿""解析丢失 17-19%"），别当定稿引用。

## 8. 交接缺口与闭环状态（接手 AI 已闭环状态标记）

1. ~~**仓库不是 git 仓库**~~：**【已闭环】** 接手 AI 已初始化 Git 仓库，更新规范化 `.gitignore` 并完成了基线提交（Commit 已记录）。
2. ~~**14 颗同判据离线重跑与 harness_md5 追踪**~~：**【已闭环】** `_setup/rescore_variant.py` 与 `main_table.py` 已纳管全部 14 颗（含 LIS2DW12 和 INA226），实测跑通并记录 `harness_md5: 8cf0854d4779467bc8e472ee4fb97023`，§2/§3 数字已与最新落盘产物完全对齐。
3. **算力任务推进（待机时规划）**：Q1c 干净消融臂（约 0.66 卡·时）、6.7B 第二模型对照（约 1.5~1.8 卡·时，待网络）、新语义簇金标。
