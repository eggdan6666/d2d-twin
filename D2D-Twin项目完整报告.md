# D2D-Twin 项目完整报告（交接版）

> [!WARNING]
> **【历史归档 / 旧口径废止声明】**
> 本文件为 2026-10-07 早期的阶段性记录，文中的早期四芯片数据、保留位推断及部分结论已被后续实测否证。
> **最新权威交接与基准状态请唯一参考根目录：[HANDOFF.md](file:///e:/HD-Agent·分层记忆RAG的电子Dstasheet智能问答/HANDOFF.md)**。请勿将本文档的早期数据作为定稿引用。
**日期**：2026-10-07　**交接对象**：Gemini 3.8 Flash　**前置文档**：`d2d/HANDOFF.md`（工程操作手册）、`d2d/PROOFREAD_QUEUE.md`（晨间人工核验队列——有用户未完成的裁决项）
**本文性质**：全项目自包含报告。读完即可接管，无需任何历史会话。

---

## 1. 项目是什么（一句话 + 两级结构）

**D2D-Twin（Datasheet-to-Digital-Twin）**：把芯片数据手册 PDF 自动转化为"可被 pytest 断言判分的 Python 寄存器级行为仿真器"，以此建立**零幻觉、确定性判分**的电子工程 LLM 基准——彻底摆脱"LLM 当裁判"的主观评测。

它建立在前置项目 **HD-Agent**（已完成、交付包冻结）的实证之上：

- HD-Agent = 分层记忆 RAG 的 datasheet 智能问答系统（456 份文档语料、QA 数据集、检索/校验链），交付包 `HD-Agent_delivery_20261007.zip`（33.9MB，SHA-256 bbbfc8f2…be47a，**冻结勿动**）。
- HD-Agent 的关键遗产数字（论文动机用）：
  - DCU 同硬件规模轴（Qwen2.5-Instruct，bf16，temp0.7×3seeds，120 题 v3）：**3B 31.7%±0.8pp → 7B 35.8%±2.2pp → 14B 43.6%±0.5pp**
  - **失败 taxonomy（D2D-Twin 立项的真正地基）**：失败题按"gold 值是否在检索上下文/全语料"三口径分类后，**上游丢失（检索漏捞+解析丢失）合计 40-45%，跨 3B→14B 纹丝不动**——信息不在上下文里，规模无解。生成侧（值在上下文仍答错）26-60% 随口径变化。
  - app 题型（原理图图注/选型表）：93% 是检索漏捞、0% 解析丢失 → 分节检索基线（Arm A'）必须在消融里做。

---

## 2. 当前状态总览（TL;DR）

| 项 | 状态 |
|---|---|
| 基准流水线 | ✅ 四芯片全链路跑通：PDF→MinerU 解析→金标 IR→Coder 生成→沙盒 pytest 判分 |
| 已评测芯片 | TMP1075 / BMP280 / TMP102 / BME280（各 12 份样本，temp0.7×3seeds×4） |
| 首版分数 | 全绿：8% / 33% / 0% / 0%（详见 §4） |
| 等待用户 | **保留位约定裁决（Q0）**+ 各芯片 IR 开放问题人工核验（§6） |
| 基础设施 | SCNet Notebook 在线可用，SSH paramiko 工作流成熟，全部产物本地+服务器双端同步 |
| 机器 | 空闲（限时免费期）；可在控制台关机，NFS 数据持久 |

---

## 3. 已完成工作（时间线）

### 3.1 前置：HD-Agent 收尾（2026-10-06 夜～10-07 凌晨）
1. DCU 探针异常（20 题 5/20、复读系统提示词、全体 out=256 打满）**根因定案**：服务器下载的 4 个模型全是 **base 基座权重**（HF 命名 `Qwen2.5-14B` 无后缀=base）。判据：`tokenizer.eos_token`（base=`<|endoftext|>`/151643，Instruct=`<|im_end|>`/151645）；**两版都有 chat_template 且渲染相同，"有没有 chat_template"判不了**。
2. 修 `dcu_runner.py`：删 `generator=gen`（HF generate 无此参数，temp>0 必崩）、加基座闸门（eos 检查）、`torch_dtype` 兼容分支（transformers 4.51）。
3. 跑通 14B-Instruct 并产出三规模 k-trial 数字（§1）。
4. 发现平台代理真相：公网直连全封，唯一出口 HTTP 代理（§5）；曾误判"出网断"绕弯路。

### 3.2 D2D-Twin 立项评审（10-07 凌晨）
用户拿到一份计划书提案，评审中用 HD-Agent 本地结果文件**实测推翻其核心主张**（"90% 失败是生成侧绑定错位"→实际生成侧 26-60%，上游丢失才是大头且跨规模不变）。评审修正已被采纳：IR 用 SVD 可映射 JSON、模型尺寸对齐 64GB 显存（14B 级）、VLM 试点前置、删"物理总线"措辞、"全球首个"收窄。

### 3.3 基准建设与四芯片评测（10-07 白天～夜间）
- **mineru295 社区镜像**直接消掉 MinerU 部署风险（预装 DTK torch 栈，单实例方案定案：解析+推理同机）。
- harness 全面通用化：一份 `test_d2d_blackbox.py` 测所有芯片（断言全由 IR 注解驱动）；`gen_code.py --ir <file>` 换芯片零代码改动。
- 四芯片 pipeline 完整执行（每颗 ≈30 分钟：上传 PDF→MinerU GPU 解析 ~11 分钟→拉回 md→人工提炼 IR→金标参考实现→本地 harness 回归→推送→k-trial→拉结果）。

---

## 4. 首版基准结果（核心交付）

**协议**：Qwen2.5-Coder-14B-Instruct（bf16，DCU eager），temp=0.7 × 3 seeds × 4 样本（与 HD-Agent k-trial 同口径），每芯片 12 份生成，逐份进独立沙盒跑 pytest。

| 芯片 | 全绿 | 断言级 | 统治性失败模式（12 份中挂的比例） |
|---|---|---|---|
| TMP1075（TI 温度，16 位） | **1/12 (8%)** | 34/60 = 57% | OS 位「写 1 触发转换、读恒 0」：92% 挂 |
| BMP280（Bosch 气压，8 位） | **4/12 (33%)** | 38/48 = 79% | RO 寄存器写保护：67% 挂 |
| TMP102（TI 温度，16 位） | **0/12** | 24/36 = 67% | 保留位硬连 0：100% 挂（**待用户裁决，见 §6-Q0**） |
| BME280（Bosch 温湿压，8 位） | **0/12** | 18/48 = 38% | RO 保护 83% + 保留位 92% + 软复位完整性 67% 三连 |

**四条论文级结论**（都有逐样本证据，`d2d/eval/results_gen_*.json` 含 48 份完整代码+pytest 输出）：
1. **reset 值层四芯片 0 失败**——"照抄寄存器表"已被 14B 解决；基准的信息量在位域语义/权限/时序层。
2. **失败模式逐芯片互补**（位域语义/RO 保护/保留位各占一山）——证明必须逐芯片建金标，纯文本 QA 无法替代。
3. **人工校对抓获 3 处 erratum**：TMP1075 Table 7-11 TYPE 列印 R/W 实为只读（描述+逐位码反证）；Bosch reset 键 **0xB6 被解析文本系统性误识为 0x86**（B→8 字体替换，BMP280/BME280 跨两文档复现，同段自相矛盾）；TMP102 Table 6-10 复位行 OCR 打残（按 §6.5.3.5 prose 重建 0x60A0）。
4. **保留位元问题（Q0，未裁）**：表格无访问码的保留位，我编成"硬连 0"（TI/Bosch 惯例），模型 100% 实现纯寄存器堆（写 1 读 1）→ 影响 TMP102 全部 12 份 + BME280 11 份。维持则分数成立且"保留位处理"成为稳定失败维度；放宽 access→RW 则大面积翻绿。**这是接手后第一件要和用户确认的事。**

---

## 5. 技术架构与环境手册（全是踩过的坑）

### 5.1 基准数据流
```
PDF ──MinerU(-d cuda, HF_HUB_OFFLINE=1)──> Markdown(d2d/parsed/<CHIP>/auto/)
    ──人工提炼+页码标注开放问题──> 金标 IR (d2d/ir/<CHIP>_gold_ir.json, SVD 可映射)
    ──gen_code.py（prompt=基类+IR+任务书, --ir --n --temperature --seeds）──> <chip>_simulator.py ×n
    ──test_d2d_blackbox.py（IR 驱动断言, 沙盒隔离）──> results_gen_<tag>.json
```
- **加新芯片纪律**：先写人工金标参考实现（`rtl/<chip>_reference.py`），本地 `D2D_IR=<ir> pytest` 全绿才准上服务器——这条纪律已三次抓住 harness/IR 自身的 bug。
- 断言七类（IR 注解驱动、自动跳过不适用）：复位值 / RO 保护（前后快照）/ RW 位域持久 / **RW 寄存器内 RO 位保护** / 写触发位（read_as）/ 单字节语义（test_register）/ W 寄存器软复位键（write_key）。
- IR schema：`d2d-ir-v1`，SVD 可映射（register/field/access/reset/bitRange/read_as/write_key/runtime_value）。

### 5.2 服务器与访问
- SCNet 华中一区 A 区 Notebook `261006223004959`，镜像 `jupyterlab-minuer2p5:pytorch2.4.1-dtk25.04.1-py3.10-model`（MinerU 2.5.4 预装；DTK 25.04.1；transformers 4.51.1；64GB 显存 BW 卡，**限时免费 ¥0/时**，机时余量 ~45 卡·时，单实例 72h 时限可「修改」）。
- SSH：`ssh -p 12461 root@ssh.zzai.scnet.cn`（密码问用户；端口随实例变，控制台可查）。**无 sshpass，用 paramiko 脚本**：`C:\Users\ZhuanZ\AppData\Local\Temp\ssh_dcu.py`（`run '<cmd>'` / `putstdin <local> <remote>`；env：`SSH_DCU_PORT`、`SSH_DCU_PASS`）。
- **代理铁律**：公网 TCP 直连全封，唯一出口 `http://preset:6e298f07@10.16.1.51:3128`。凭据在 `/root/private_data/.ai_user_info/ai_proxy`（NFS 持久），交互 shell 自动 source，**非交互 SSH 必须手动 export**，否则误判"出网断"。
- **模型下载**：`sh /root/dl_repo.sh <型号>`（ModelScope 4 路 wget，~180MB/s，逐文件 SIZE_CHECK）。**必须带 -Instruct/-Coder 后缀**（无后缀=base，血泪教训）。
- **配额**：`/root/private_data` 硬配额 **50G**（df 的 9.2P 是池容量不是配额！）。写满后 putstdin 静默写 0 字节、删后配额回收滞后 **3-5 分钟**。当前 29G（仅 Coder-14B）。
- **杀进程铁律**：PID1 命令行含 `/opt/conda/bin/jupyter`，`pgrep -f conda` 类宽泛模式会杀崩整机（发生过一次，控制台重启+秒保存环境可恢复）。用 `pkill -f "g[e]n_code.py"` 字符类正则。
- 其他：`/tmp` 不可写（用 /root）；`HF_HUB_OFFLINE=1` 必带（否则卡死 etag 在线检查）；Git Bash 需 `MSYS_NO_PATHCONV=1`；Windows Python 本地路径用 `E:/` 风格；MinerU GPU 用 `-d cuda`（CPU 213s/页不可用）。

### 5.3 资产索引
- 本地工作区 `E:\HD-Agent·分层记忆RAG的电子Dstasheet智能问答\`：
  - `d2d/`：HANDOFF.md、PROOFREAD_QUEUE.md、ir/（4 份金标 IR）、rtl/（基类+4 份参考实现）、eval/（testbench+gen_code+results_gen_*.json）、parsed/（**5 份**解析产物：TMP1075/BMP280/TMP102/BME280/TMP100）
  - `corpus/data/raw_pdf/`：456 份原 PDF（第 5-10 颗芯片的原料，TI/TMP100-104、LM83、BME280 已在）
  - `_setup/dcu_runner.py`（HD-Agent QA 评测器，已修）、`eval/qa100/`（HD-Agent 数据与结果）
- 服务器 `/root/private_data/`：`d2d/`（同构）、`models/Qwen2.5-Coder-14B-Instruct`、`pilot/`（PDF+解析）、`dl_repo.sh`、`dcu_diag.py`（tokenizer 闸门）

---

## 6. 待办（按优先级）

### P0 用户人工核验（15-30 分钟，清单在 d2d/PROOFREAD_QUEUE.md，全部标了 PDF 页码）
1. **Q0 保留位裁决**：TMP102 CONFIG/TLOW/THIGH [3:0] 与 BME280 ctrl_hum [7:3]——维持"硬连 0"（现编码，0/12 成立）或放宽 RW（翻绿）。**这决定两颗芯片的分数，也决定基准的严格度基调。**
2. BMP280：press/temp_msb 复位 0x80 确认（PDF 第 24 页 Table 18）、reset 键 0xB6 确认、normal 模式写忽略是否入 Phase 1.5
3. TMP102：config 复位 0x60A0 逐位核对（PDF 第 17 页 Table 6-10，OCR 残）、OS 位读回语义（第 18 页）、R1/R0/AL 只读确认
4. BME280：chip_id 0x60、reset 0xB6（PDF 第 27-28 页）、ctrl_hum 时序语义是否入 Phase 1.5

### P1 铺第 5-10 颗芯片（每颗 ≈30 分钟，流水线已固化）
TMP100 解析产物已就绪（`d2d/parsed/TMP100/`，2 寄存器最简芯片）；候选：TMP101/TMP103/TMP104、LM83（远程温度，8+ 寄存器）。目标：10 颗芯片的首版基准表。

### P2 Phase 2/3（设计已在计划书+评审修正中）
- Phase 2：Reader 抽取实验（模型从 Markdown 生成 IR vs 人工金标，测"绑定错位是否被 IR 化解"）；VLM 对比（Qwen2-VL on DTK 试点未做）
- Phase 3 消融四臂：A 扁平文本+RAG / **A' 分节检索（HD-Agent rag/ 代码可复用，防审稿人必做）** / B 多模态端到端 / C D2D-Twin 双脑

---

## 7. 协作规范（与用户打交道的经验）

- 用户中文交流；**极度重视实测验证**——"被实测推翻"比任何论证都有说服力；给数字必须带来源文件。
- 偏好批量授权+自主推进（"选 A"、"继续"、"跑完再汇报"），讨厌算力空转：GPU 干活时持续排任务，干完提醒可关机；token 级诊断（不加载模型）不算烧额度。
- 每次汇报先给 TLDR 结论表，再给证据；不确定的事明说置信度。
- 出了事故（如杀崩容器、写爆配额）直接如实报告+复盘入档，用户接受这个风格。

---

*报告完。接手后第一步：读 `d2d/PROOFREAD_QUEUE.md` 向用户要 Q0 裁决 → 按 §6-P1 铺 TMP100。*
