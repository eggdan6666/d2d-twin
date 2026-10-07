# D2D-Twin 交接文档（2026-10-07 上午，交接给下一位 AI）

> [!WARNING]
> **【历史归档 / 旧口径废止声明】**
> 本文件为 2026-10-07 早期的阶段性记录，文中的早期四芯片数据、保留位推断及部分结论已被后续实测否证。
> **最新权威交接与基准状态请唯一参考根目录：[HANDOFF.md](file:///e:/HD-Agent·分层记忆RAG的电子Dstasheet智能问答/HANDOFF.md)**。请勿将本文档的早期数据作为定稿引用。
本文件自包含：不依赖任何会话历史即可接管。配合 `PROOFREAD_QUEUE.md`（晨间人工核验队列）使用。

## 0. 一句话现状

D2D-Twin（数据手册→数字孪生基准）Phase 1 已通：**四颗芯片（TMP1075/BMP280/TMP102/BME280）完成 MinerU 解析 → 金标 IR → Coder 生成 → pytest 断言判分 的全链路 k-trial**，首版数字已出；TMP100 解析产物已就绪（第 5 颗原料）；等待用户人工核验 IR 开放问题（`PROOFREAD_QUEUE.md`，最要紧：保留位约定裁决——影响 TMP102/BME280 共 23 份样本的分数），然后铺第 5-10 颗芯片。

## 0.5 （四芯片） 首版基准数字（全部 temp0.7 × 3 seeds × 4 样本，12 份/芯片）

| 芯片 | 全绿 | 断言级 | 统治性失败模式 |
|---|---|---|---|
| TMP1075 | 1/12 (8%) | 57% | OS 位「读恒 0」92% 挂 |
| BMP280 | 4/12 (33%) | 79% | RO 寄存器写保护 67% 挂 |
| TMP102 | 0/12 | 67% | 保留位硬连 0 100% 挂（**待裁**） |
| BME280 | 0/12 | 38% | RO 保护 83% ＋ 保留位 92% ＋ 软复位完整性 67% |

结论雏形：①reset 值层四芯片 0 失败（表格抄写已被 14B 解决）；②失败模式随芯片而变且被断言层精确定位；③三处 erratum 被抓（TMP1075 Table 7-11 TYPE 列笔误、Bosch reset 键 0xB6→0x86 OCR 系统性替换跨两文档复现、TMP102 Table 6-10 OCR 残缺）——「人工金标+确定性断言」方法论的实证。

## 1. 访问与工作流（先读这段，全是踩过的坑）

- 服务器：SCNet 华中一区 A 区 Notebook `261006223004959`（ mineru295 镜像：DTK 25.04.1 / torch 2.4.1+cuda / transformers 4.51.1 / Python 3.10.18 / MinerU 2.5.4，模型预装在镜像 HF 缓存）。
- SSH：`ssh -p 12461 root@ssh.zzai.scnet.cn`（密码问用户，会话内提供；端口随实例可能变，控制台「SSH 登录」列可查）。**本机无 sshpass，用 paramiko 脚本驱动**：本地 `C:\Users\ZhuanZ\AppData\Local\Temp\ssh_dcu.py`（模式：`run '<cmd>'` / `putstdin <local> <remote>`；密码走环境变量 `SSH_DCU_PASS`，端口 `SSH_DCU_PORT`）。
- **代理铁律**：公网 TCP 直连全封，唯一出口 `http://preset:6e298f07@10.16.1.51:3128`。交互 shell 自动 source `/root/private_data/.ai_user_info/ai_proxy`，**非交互 SSH 必须手动 export**，否则误判"出网断"。凭据变化时从 PID1 环境拿：`cat /proc/1/environ | tr '\0' '\n' | grep proxy`。
- **杀进程铁律**：PID 1 命令行含 `/opt/conda/bin/jupyter`，`pgrep -f conda` 一类宽泛模式会杀掉容器 init → 整机宕（血案已发生过一次，控制台重启+秒保存环境可恢复）。用字符类正则 `pkill -f "g[e]n_code.py"` 或 ps 核对 PID。
- **配额**：`/root/private_data` 硬配额 **50G**（df 显示的 9.2P 是存储池不是配额！）。当前 29G（仅 Qwen2.5-Coder-14B-Instruct 28G）。写满后 putstdin 静默写 0 字节 + 删后配额回收有 **3-5 分钟滞后**。模型下载用 `sh /root/dl_repo.sh <型号名>`（ModelScope 4 路 wget，~180MB/s，内置逐文件 SIZE_CHECK；历史已证 `Qwen2.5-14B` 无后缀=base，**必须带 -Instruct/-Coder 后缀**）。
- 其他：`/tmp` 不可写（用 /root）；`HF_HUB_OFFLINE=1` 必带（否则 MinerU/transformers 卡死 etag 在线检查）；Git Bash 传参前 `export MSYS_NO_PATHCONV=1`；Windows Python 的本地路径用 `E:/` 风格；GPU 跑 mineru 用 `-d cuda`（CPU 213s/页不可用）。

## 2. 基准架构（d2d/，本地与服务器 /root/private_data/d2d 双端同步）

```
数据手册 PDF ──MinerU(-d cuda)──> Markdown ──人工提炼+校对──> 金标 IR (ir/<CHIP>_gold_ir.json)
                                                                    │
   Coder 模型 ←── gen_code.py（prompt=基类+IR+任务书）────────────────┘
        │ 生成 n 份 <chip>_simulator.py（沙盒隔离）
        ▼
   test_d2d_blackbox.py（IR 驱动断言，换芯片零改动）──pytest──> results_gen_<tag>.json
```

- `rtl/base_sensor.py`：黑盒接口契约（read/write_register(addr, nbytes)）
- `rtl/<chip>_reference.py`：人工金标实现——**加新芯片时必写**，先验证 testbench 本身（本地 `D2D_IR=<ir> pytest` 必须全绿才准上服务器评测）
- `eval/test_d2d_blackbox.py`：六断言（复位值/RO 保护/RW 位域持久/RW内RO位保护/写触发位/单字节/W寄存器软复位键），由 IR 注解驱动，自动跳过不适用的
- `eval/gen_code.py`：`--ir <file> --tag <t> --n 4 --temperature 0.7 --seeds 1,2,3`（与 HD-Agent k-trial 同口径）
- 本地 pytest 在 `C:\Users\...\Python311\python.exe`，环境变量 `D2D_IR=...`

## 3. 待人工项（用户醒来做，见 PROOFREAD_QUEUE.md）

1. **TMP102 Q0**：保留位 [3:0] 硬连 0（现编码）vs 放宽 RW——决定 0/12 是否翻绿
2. BMP280 Q1-3：press/temp_msb 复位 0x80、reset 键 0xB6 确认、normal 模式写忽略是否入 Phase 1.5
3. TMP102 Q1-4：config 复位 0x60A0 逐位核对（Table 6-10 OCR 残）、OS 位读回语义、R1/R0/AL 只读确认

## 4. 下一步路线

1. **第 4-10 颗芯片**（语料现成 PDF：TI/TMP100、TMP101、TMP103、TMP104、Bosch/BME280、TI/LM83……`corpus/data/raw_pdf/` 共 456 份）。单颗流程 ≈30 分钟：上传 PDF→mineru 解析→拉 md→提炼 IR（开放问题标注页码）→参考实现→本地回归→push→k-trial→拉结果。加芯片时 IR 开放问题一律同步进 PROOFREAD_QUEUE.md。
2. **Phase 2**：多模态解析规模化（MinerU 已就绪；VLM 对比可选 Qwen2-VL，DTK 试点未做）；Reader 抽取实验（IR 抽取准确率 vs 人工金标）。
3. **Phase 3 消融**：Arm A（扁平文本+RAG）/A'（分节检索）/B（多模态端到端）/C（D2D-Twin 双脑）——HD-Agent 的 rag/ 与 ctx 机制可直接复用做 Arm A/A'。
4. HD-Agent 交付包（`HD-Agent_delivery_20261007.zip`）已冻结勿动；DCU 规模轴数字（3B 31.7%→7B 35.8%→14B 43.6%）是论文动机部分。

## 5. 关键文件索引

- 本地：`d2d/`（全架构）、`d2d/PROOFREAD_QUEUE.md`、`d2d/eval/results_gen_*.json`、`d2d/parsed/<CHIP>/auto/<CHIP>.md`、`corpus/data/raw_pdf/`（456 份原 PDF）、`_setup/dcu_runner.py`（HD-Agent QA 评测器，dtype 兼容已修）
- 服务器：`/root/private_data/d2d/`（同构）、`/root/pilot/`（PDF 与解析产物）、`/root/dl_repo.sh`、`/root/dcu_diag.py`（tokenizer 闸门诊断）、`/root/private_data/models/Qwen2.5-Coder-14B-Instruct`
- 计费：BW 卡限时免费（¥0/时）；机时余量 ~45 卡·时；单实例 72h 时限可「修改」；NFS 数据跨开关机持久
