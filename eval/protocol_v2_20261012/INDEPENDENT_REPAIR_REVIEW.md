# 第二版协议：修订候选独立来源复核

日期：2026-10-12。任务：`/root/repair_review`。评审者：独立 AI 子任务；不是人类专家签字，也不是实物验证。当前审查只针对已准备的修订候选，阶段决策由 SCI-Skills 主编排任务负责。

## 审查结论与边界

**有条件接受修订候选用于第二版协议验证；不能无条件作为全部芯片的来源认证。**

12 项最终字段复位修订：8 项来源支持、4 项有条件支持；TMP100 的 4 项最终位宽修订均来源支持。这里的条件是：INA3221 来源内部冲突，TMP117 门限仅覆盖出厂 EEPROM 默认状态，TMP117 DEVICE_ID 的高 4 位不应硬编码成确定值。若 v2 明确记录这些条件并执行相应已知位掩码或排除策略，数值修订可进入有界协议验证。

`repair_manifest.json` 记录的是 **18 条顺序编辑记录**；TMP100 的两个 reset 先按旧 9 位字段调整、再随位宽调整，因此不能将 18 条记录理解为 18 个互异的最终修订。最终共有 12 个 reset 属性和 4 个 bits 属性修订，另有 TMP100 来源说明更新。

20 份候选 IR 均已读取并与冻结快照逐项比较；候选清单中的 23 个文件 SHA-256 全部匹配。共有 572 个字段，558 个同时具有寄存器和字段 reset 的比较项，候选中发现 0 个数值不一致；LIS3DH 的 14 个动态字段缺少静态 reset，已单列，不以 0 填补。这些结构检查**不等同于 572 字段的逐项来源认证**。来源内容审查只覆盖下表的修订项及其必要上下文。

## 逐项来源判断

页码均指 PDF 的 1 起算物理页；核对相关页后与页脚印刷页码相同。字段 reset 是未左移的字段数值，寄存器 reset 是完整总线读回值。

| 编号 | 最终修订 | 判定 | 原始来源定位与范围 |
|---|---|---|---|
| R01 | INA3221 `SHUNT_SUM_LIMIT.SVL.reset`: 4095 → 16383 (`0x3FFF`) | CONDITIONAL | SBOS576C p.33 §8.2.15、Table 8-31 与标题支持寄存器 `0x7FFE`；Table 8-32 却给相同数据位只读、reset 0。候选 `bits=15:1` 对 `0x7FFE` 的抽取是 `0x3FFF`，只能证明内部一致。图中 SIGN 与 SVL 是独立字段，不能把当前合并字段视为完整逐位来源认证。 |
| R02 | TMP100 `TLOW.L.reset`: 0 → 1200 (`0x4B0`) | PASS | SBOS231I p.18 §7.5.4、Tables 13–14 给 12 位门限；p.9 Table 1 给 75°C 对应 `0x4B0`；完整读回值 `0x4B00`。 |
| R03 | TMP100 `THIGH.H.reset`: 0 → 1280 (`0x500`) | PASS | SBOS231I p.18 §7.5.4、Tables 11–12；p.9 Table 1 给 80°C 对应 `0x500`；完整读回值 `0x5000`。 |
| R04 | TMP102 `TLOW.L.reset`: 0 → 1200 (`0x4B0`) | PASS | SBOS397I p.19 §6.5.4、Tables 6-15–6-16（后表续至 p.20），上电门限 75°C；p.15 §6.4.2 和 p.17 Table 6-11 确认默认 EM=0，按 12 位正常模式。此结论不覆盖 EM=1 的 13 位格式。 |
| R05 | TMP102 `THIGH.H.reset`: 0 → 1280 (`0x500`) | PASS | SBOS397I p.19 §6.5.4、Tables 6-13–6-14，上电门限 80°C；与 R04 相同的默认模式范围。 |
| R06 | TMP1075 `LLIM.L.reset`: 0 → 1200 (`0x4B0`) | PASS | SBOS854F p.23 §7.5.1.3、Figure 7-14、Table 7-9，直接给 `15:4`、字段 reset `4B0h`、寄存器 reset `4B00h`。 |
| R07 | TMP1075 `HLIM.H.reset`: 0 → 1280 (`0x500`) | PASS | SBOS854F p.23 §7.5.1.4、Figure 7-15、Table 7-10，直接给字段 reset `500h`、寄存器 reset `5000h`。 |
| R08 | TMP117 `TEMP.T.reset`: 0 → 32768 (`0x8000`) | PASS | SNOSD82D p.25 Table 7-3；p.26 §7.6.2、Figure 7-13、Table 7-5 明确复位后为 `0x8000`，直到首次转换及平均完成。只支持复位瞬间的确定值，不支持整个运行期间恒定。 |
| R09 | TMP117 `THIGH.H.reset`: 0 → 24576 (`0x6000`) | CONDITIONAL | SNOSD82D p.25 Table 7-3 脚注 1；p.29 §7.6.4、Table 7-8：`0x6000` 是 factory default，复位后从 EEPROM 装载，用户改写 EEPROM 后可不同。v2 必须声明出厂 EEPROM 默认范围。 |
| R10 | TMP117 `TLOW.L.reset`: 0 → 32768 (`0x8000`) | CONDITIONAL | SNOSD82D p.25 Table 7-3 脚注 1；p.29 §7.6.5、Table 7-9；与 R09 相同的出厂 EEPROM 默认条件。 |
| R11 | TMP117 `DEVICE_ID.ID.reset`: 0 → 279 (`0x0117`) | CONDITIONAL | SNOSD82D p.32 §7.6.11、Figure 7-22、Table 7-15。低 12 位 DID=`0x117` 确定；图中高 4 位 Rev 标 `R-x`，表给 0，来源表达不一致。当前全 16 位 ID 不能无条件认证；建议已知 mask=`0x0FFF`，仅比较 `(value & 0x0FFF)==0x0117`，明确高 4 位未评分。 |
| R12 | TPS23861 `INTERRUPT.FLAGS.reset`: 0 → 128 (`0x80`) | PASS | SLUSBX9I p.47 §7.5.1 POR 行：D7 SUPF=1，其余 0，寄存器只读。支持 reset/POR 初值，不支持运行中恒为 `0x80`。 |
| W01 | TMP100 `TLOW.L.bits`: `15:7` → `15:4` | PASS | SBOS231I p.18 Tables 13–14 将 L11…L0 映射到 15:4；末段明确所有 ADC 分辨率均使用 12 位门限，低 3 个门限有效位在 9 位转换模式也影响 ALERT。 |
| W02 | TMP100 `TLOW.UNUSED.bits`: `6:0` → `3:0` | PASS | SBOS231I p.18 Table 14 将第二字节低四位画为 0；12 位门限有效位占 15:4。此处只认可门限寄存器的低四位固定零格式。 |
| W03 | TMP100 `THIGH.H.bits`: `15:7` → `15:4` | PASS | SBOS231I p.18 Tables 11–12 与末段，依据同 W01。 |
| W04 | TMP100 `THIGH.UNUSED.bits`: `6:0` → `3:0` | PASS | SBOS231I p.18 Table 12 与末段，依据同 W02。 |

## 对代码与协议的影响

TMP100 候选参考实现的门限 `WRITE_MASK=0xFFF0` 与上述门限位宽一致；旧 `0xFF80` 会错误丢弃 bit6:4。该判断是静态来源与代码核对，本子任务没有重跑模型或参考实现。原有 `tmp100_sensitivity.json` 也不能代替本子任务执行证据。

TMP100 的历史审校记录和参考实现旧说明仍包含“门限 9 位”的错误旧结论。候选顶层 `source_repair_note` 和参考实现首段说明已声明旧注释被替代，因此不构成新数值错误；正式交付时应将旧记录清楚标成历史，否则新接手者可能误读。TEMP 默认 9 位的上下文与门限 12 位是两个不同事实，不能一起改成“全部 12 位”。

INA3221 的冲突不能通过选取多数文字、当前参考实现通过或模型分数不变解决。最低修复是把冲突登记为来源未定，v2 对冲突位的 reset/access 断言排除或采用明确命名的条件策略。若保留图示策略，必须将它标为基准约定而非已验证的器件行为。已一致的 SIGN/保留位 reset 可分开保留，但不能暗中把 Table 8-32 标成官方勘误。

TMP117 ID 高四位的屏蔽必须在所有使用该期望值的检查中一致生效，例如整寄存器复位、只读字段比较和软复位快照；只在初始 reset 测试屏蔽仍会重新引入相同的未知位假设。

## 三个审查视角

1. **贡献**：修复可提高基准对来源的忠实度；不能把协议变更后得分变化写成模型能力提高，也不能据此宣称真实硬件验证完成。
2. **方法**：明确出厂 EEPROM、默认模式、复位瞬间以及未知位/来源冲突的范围；原始协议和分数应保留并分别标版本。
3. **表达**：18 条操作记录、16 个最终字段属性、572 个结构检查字段与有限来源复核是不同计数，应分别报告。

## 核对与证据状态

- `VERIFIED_USER_MATERIAL`：20 候选、20 冻结快照和候选 manifest 均实际读取；23 文件 SHA-256 与 manifest 匹配。
- `VERIFIED_SOURCE`（本地原始资料范围）：6 份 TI PDF 的必要原页与相关上下文实际读取；TMP100 p.18、TMP1075 p.23、TMP117 pp.29/32、TPS23861 p.47、INA3221 p.33 的既有整页渲染实际目视核对。TMP102 pp.15/17/19/20 为完整原页文本核对。
- `EXECUTED_LOCAL`：本子任务实际进行了 SHA-256、冻结/候选差异和 reset 对齐检查；原始 harness MD5 仍为 `8cf0854d4779467bc8e472ee4fb97023`。
- `NOT_EXECUTED`：本子任务没有运行 v2、没有新增模型生成、没有实物/总线波形验证、没有验证下载源的现时官网字节。
- `PENDING_VERIFICATION`：INA3221 冲突的物理真实行为、TMP117 各硬件修订号，及其余未作逐字段来源复核的部分。

## 原始来源指纹

所有路径均相对仓库根目录；SHA-256 用于锁定此次实际审查的本地版本，不等于验证版权、许可或当前官网版本。

| 本地文件 | 版本 | SHA-256 |
|---|---|---|
| `corpus/data/raw_pdf/TI/TMP100.pdf` | SBOS231I, Nov 2015 | `4099b7e562d9333140b60526c32908a082ef300d019266161e9a2b118e52fc29` |
| `corpus/data/raw_pdf/TI/TMP102.pdf` | SBOS397I, Jun 2024 | `c9da6620ef95f75ce94372f670a84d168e05922dd32cebfaa6517083f15ebfaf` |
| `corpus/data/raw_pdf/TI/TMP1075.pdf` | SBOS854F, Jun 2024 | `266c9a50a80b100884e9cf378b320ea51412023057fed8ba4fbdf85502340cf2` |
| `corpus/data/raw_pdf/TI/TMP117.pdf` | SNOSD82D, Sep 2022 | `afe974873c80a7a4e1d342e9044e71c6f905caf4f04c1f0ea0df5c6ba35f980e` |
| `corpus/data/raw_pdf/TI/TPS23861.pdf` | SLUSBX9I, Jul 2019 | `65262ce4766a5f8e3b9f580ac02782ad7d5e35b39045fa5346288c21e240c093` |
| `corpus/data/raw_pdf/TI/INA3221.pdf` | SBOS576C, Sep 2026 | `6ef5bf2263e34332fce7ea2547d9824ff5d3900418d51d59e5e3b711dcdc98d0` |

## 专家返回契约

```yaml
contract_version: "1.0"
expert_skill: sci-skills-presubmission-review
project_id: d2d-twin
paper_family: M
stage_id: M4
task_id: /root/repair_review
task_status: COMPLETE
inputs_reviewed: ["repair_manifest.json", "20 candidate and 20 frozen IR files", "six local original TI PDFs", "candidate TMP100 reference mask"]
outputs: ["eval/protocol_v2_20261012/INDEPENDENT_REPAIR_REVIEW.md", "eval/protocol_v2_20261012/independent_repair_review.json"]
evidence_status: ["VERIFIED_USER_MATERIAL", "VERIFIED_SOURCE for bounded claims with conflicts retained", "EXECUTED_LOCAL for hash and reset checks", "NOT_EXECUTED for v2 and hardware", "PENDING_VERIFICATION for conflicts and unreviewed fields"]
assumptions: ["TMP102 default EM=0", "TMP117 factory EEPROM defaults", "local source SHA-256 lock", "independent AI rather than human signoff"]
author_input_needed: []
manual_actions: []
quality_checks: ["23 manifest hashes match", "20 candidate files compared", "558 reset pairs with zero mismatches", "14 nonstatic reset fields separate", "original harness MD5 unchanged"]
conflicts: ["IR-INA3221-0E-SOURCE", "IR-TMP117-ID-REV"]
conflict_resolution_status: UNRESOLVED
merge_permission: orchestrator_only
recommended_next_action: Implement the conditional scopes and masks or exclusions in v2, then run reference admission.
stage_acceptance_recommendation: REPAIR
```

## 唯一下一步

由主编排任务将上述四项条件落实为 v2 的显式范围与掩码/排除规则，运行参考实现准入后再对现有样本分别重评；原冻结协议与原始分数继续保存。此意见是 `REPAIR` 建议，不代表 M4 或投稿审查通过。
