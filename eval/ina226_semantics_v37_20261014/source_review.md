# INA226 v37 来源精读卡（有界直接任务）

## 1. Bibliographic position / 来源身份

Texas Instruments，INA226 36V, 16-Bit, Ultra-Precise I2C Output Current, Voltage, and Power Monitor With Alert；SBOS547C，June 2011，revised August 2026（p1/页眉）。用户持有完整 41 页数据手册，非论文。PDF SHA256 `c9b67f886d4a5241a5e070723f7b61867409eeb27eed768b9cdd9cb17e03ca2d`；账本 SHA256 `0905059f5f981f89137533d8b6f34d33cde5b673a05707c6b7141d521bb54711`。后者只是范围清单。本卡不主张文件字节已经在线 TI 官网核验。

## 2. Research question / 任务问题

六个原始 REPAIR 字段 / 六个维度能否形成来源约束的数字有界规则？如何避免把整寄存器 R/W、POR 初值、结果寄存器更新、物理 conversion 和清除前读回混为同一事实？

## 3. Background route / 背景路线

原文路线是 ADC 测量→当前值及功率计算→累积平均→完整结果发布；告警阈值检查发生在相关转换 / 计算边界（pp11-13，Figure6-1），其结果更新粒度与 CVRF 全过程完成不同。CONFIG、CALIBRATION、MASK_ENABLE 的字级 R/W 表述不提供未命名位逐位访问分类。

## 4. Unresolved pain point / 未解决的问题

三组未命名位没有非默认写后的保证。RST self-clear 没有 completion latency 与 pending 读值保证。AFF CONFIG 写清除有源内冲突。读 MASK_ENABLE 可诊断来源，但精确 preclear 取样顺序和字节 / 时钟清除位置未定义；缺失不可由数字模型补为硅片事实。

## 5. Core insight / 核心判断

有界闭环可继续实现：保留位采取排除而保留 POR；RST 区分请求 / 完成；CVRF 必须由全流程完成置位；AFF 按 LEN 条件处理并保留冲突后 unknown。数字协议抽象必须单独标注，所有建议均交 orchestrator 验收，绝不晋升整个字段。

## 6. Method overview / 独立审阅方法

先读取专家合同 / evidence labels / zero-api / stage boundary / playbook，再实际 SHA 输入，pypdf 提取完整 41 页，Poppler 渲染并目视 pp11-13、22-28，另目视 pp19/21 的完整读时序图、表格脚注；另目视 pp19/21 的完整读时序图、表格脚注；补读 pp1/3/10/16-21 全页文字并搜索全文相关词。实现审阅前清单已单独写入，此任务未阅览或执行候选代码、Gold、旧 Harness。所有辅助与输出只写指定 sandbox。

## 7. Module or mechanism logic / 六个维度

| 字段 | 原始维度 | 来源与有界建议 |
|---|---|---|
| CALIBRATION.UNNAMED_15 | access | p26 Table7-11：POR0，非默认访问 oracle 排除 |
| CONFIG.RST | trigger_completion | p23：写1→复位→self-clear；完成前 unknown |
| CONFIG.UNNAMED_14_12 | access | p22 Table7-2：POR100，合法写维持100，非默认排除 |
| MASK_ENABLE.AFF | read_clear | pp13/27：LEN 条件 + CONFIG 写冲突；共通 profile unknown |
| MASK_ENABLE.CVRF | read_clear | pp11/27 完成置位 / 清除；p24 MODE0/4 例外 |
| MASK_ENABLE.UNNAMED_9_5 | access | p26 Table7-12：POR00000，非默认排除 |

MASK read 可同时影响 AFF/CVRF，但前置事件与 LEN 条件不能合并。AFF 的非零故障→透明模式下一无故障相关转换才清；锁存模式下一无故障转换保持、MASK read 清。无故障刺激撤销不代表发生了该转换。

## 8. Essential formulas and assumptions / 位规则与假设

保留位模式：CONFIG mask=0x7000,value=0x4000；CALIBRATION mask=0x8000,value=0；MASK_ENABLE mask=0x03e0,value=0。在输入协议中 `(word & mask)==value` 限定合法刺激；这是研究抽象，非非法写硬件响应。已知 POR 不推出 runtime 恒定。CVRF 完成谓词 `conversions_complete ∧ averaging_complete ∧ maths_complete ∧ current_config_epoch` 表示全流程；各谓词是事件协议声明，不是通过写任意结果值证明。MODE0/4 powerdown 例外限定非 RST 事务；RST completion 优先回默认。读返回 snapshot→clear 作为 A_READ_SNAPSHOT，不提供总线取样时序保证。

## 9. Data, material, benchmark / 材料和边界

唯一事实权威为本地 TI 原始 PDF。input_identity 与六字段 target_fields 仅限定范围；旧账本仅身份 / inventory。真实硬件样本=0；候选实现执行=0；整字段晋升=0。提取和渲染属于本地执行证据，不是芯片性能或模型实验结果。

## 10. Experimental design, metrics, baselines / 实现前验收设计

已提交 independent_source_checklist.md；须用非零前置状态检验 read-clear，覆盖 LEN 两态、MODE0/4 两例外、非 powerdown 写清、数据寄存器读不误清、partial average / math pending 不置位、stale epoch 排除、RST pending unknown 与完成默认、保留位合法 pattern 和非默认 exclusion。共通 AFF CONFIG-write 必须 unknown；可选 source profiles 独立命名。指标只报告六维度的条件准入 / 排除覆盖，不能将零读回 vacuous success 算正确清除。

## 11. Experiment-to-claim evidence table / 来源声明表

这是来源→规则表，未执行实验。

| Claim ID | 类别 | 来源 | 结论 |
|---|---|---|
| INA226_C01_CAL_POR | SOURCE_FACT | p26 / Table 7-11 | CALIBRATION D15 is unnamed (dash) and POR=0; register 05h is R/W, but table does not assign per-bit write protection. |
| INA226_C02_CFG_POR | SOURCE_FACT | p22 / Table 7-1 and 7-2 | CONFIG D14:D12 are unnamed with POR bits 1,0,0; register 00h is R/W, POR 0x4127. |
| INA226_C03_MASK_POR | SOURCE_FACT | p26 / Table 7-12 | MASK_ENABLE D9:D5 are unnamed with POR=00000; AFF and CVRF POR=0; register 06h is R/W. |
| INA226_C04_RESERVED_WRITE_GAP | UNDEFINED_BEHAVIOR | p22 / Table 7-2, p26 / Table 7-11 and 7-12 | The three target unnamed ranges have no per-bit RO, ignore-write, permanent-constant-read or nondefault-write-response guarantee in reviewed original definitions. Whole-register R/W does not establish them. |
| INA226_C05_RESERVED_PROTOCOL | ABSTRACTION_ASSUMPTION | p22 / Table 7-2, p26 / Table 7-11 and 7-12 | Keep unnamed bits at their POR pattern in admitted writes; exclude access oracles for nondefault writes. POR knownness is retained only at defined reset boundary; later constant reads are not inferred. |
| INA226_C06_RST_REQUEST | SOURCE_FACT | p23 | Setting RST=1 generates system reset equal to power-on reset, resets all registers to defaults, and RST self-clears. |
| INA226_C07_RST_TIMING_GAP | UNDEFINED_BEHAVIOR | p23, p11 | RST prose does not specify reset completion duration or any transient readback value while reset is pending. Powerdown recovery 40us on p11 is not an RST timing guarantee. |
| INA226_C08_RST_COMPLETION_PROTOCOL | ABSTRACTION_ASSUMPTION | p23, p22 / Table 7-1 and 7-2, p26 / Table 7-11 and 7-12 | Separate reset request from explicit abstract completion. During pending reset, affected readback knownness is unknown; on declared completion restore defined PORs and RST=0. Atomic completion is an alternative only if explicitly named an abstraction. |
| INA226_C09_AFF_FAULT_SET | SOURCE_FACT | p12 / Table Figure 6-1, p13, p26, p27 | Selected alert function compares against Alert Limit after its related conversion/calculation and asserts AFF upon alert condition. Highest enabled alert-function bit D15-D11 has priority; conversion-ready notification can coexist. |
| INA226_C10_AFF_LATCH_READ | SOURCE_FACT | p13, p27 | With LEN=1 latch mode, AFF persists following fault and clears when MASK_ENABLE is read. Fault absence on next conversion is not the latch-mode clear event. |
| INA226_C11_AFF_TRANSPARENT | SOURCE_FACT | p27 | With LEN=0 transparent mode, AFF clears following the next conversion that does not result in an alert condition; LEN prose describes return to idle when fault cleared. |
| INA226_C12_AFF_CONFIG_P13 | SOURCE_FACT | p13 | p13 says latched AFF and Alert remain asserted until Configuration Register is written OR Mask/Enable Register is read. |
| INA226_C13_AFF_CONFIG_P27 | SOURCE_FACT | p27 | p27 AFF prose says latch-mode AFF clears ONLY when Mask/Enable Register is read; LEN prose agrees with Mask/Enable read. |
| INA226_C14_AFF_COMMON_PROFILE | ABSTRACTION_ASSUMPTION | p13, p27 | Common profile excludes definitive AFF readback after latched CONFIG-write: mark AFF unknown because source disagrees. Optional separately named p13-clear or p27-preserve profiles may retain each interpretation; neither is hardware-verified. |
| INA226_C15_CVRF_COMPLETE | SOURCE_FACT | p11, p12 / Table Figure 6-1, p27 | CVRF is set after ALL conversions, averaging, and multiplication operations complete; output registers retain previous completed results until replacement, and reading data output registers does not affect conversion in progress. |
| INA226_C16_CVRF_CLEAR | SOURCE_FACT | p11, p27 | CVRF clears on MASK_ENABLE read or Configuration Register write except selecting power-down mode. |
| INA226_C17_MODE_ENCODING | SOURCE_FACT | p24 / Table 7-6 | MODE[2:0] 000 and 100 are both power-down/shutdown; 001/010/011 are triggered; 101/110/111 are continuous. |
| INA226_C18_CVRF_COMPLETION_PROTOCOL | ABSTRACTION_ASSUMPTION | p11, p12 / Table Figure 6-1, p22, p27 | A source-qualified completion event must represent every conversion required by current mode, configured averaging completion and math completion in a current configuration epoch. A bare result update does not prove the condition. Stale/partial events must not set CVRF in the admitted protocol. |
| INA226_C19_READ_DIAGNOSTIC | SOURCE_FACT | p12, p27 | Reading MASK_ENABLE CVRF/AFF following alert identifies the alert source; thus source describes useful read observation of flags despite read-clear side effects. |
| INA226_C20_READ_ORDER_GAP | AI_ANALYSIS | p12, p19 / Table Figure 6-5, p27 | No reviewed sentence or read-word diagram explicitly timestamps flag clear relative to sampling or each data byte. Return-before-clear is a reasonable functional protocol convention, supported indirectly by diagnostic purpose, rather than a byte-accurate silicon guarantee. |
| INA226_C21_CNVR_SCOPE | SOURCE_FACT | p27 | CNVR bit10 enables Alert pin assertion when CVRF is asserted; it is not stated to be a precondition for CVRF state generation. |
| INA226_C22_CONFIG_SIDE_EFFECTS | SOURCE_FACT | p22, p11 | Reading CONFIG does not affect settings/conversion; writing CONFIG halts in-progress conversion until write completes, with next conversion based on new contents. Rewriting a triggered mode triggers a new single-shot even if unchanged. |
| INA226_C23_BUS_TIMING_LIMIT | SOURCE_FACT | p21 / Table 6-3 footnote 1 | Table 6-3 footnote states bus timing min/max derive from one-time sample statistical analysis, are not guaranteed, and are not production tested. |

## 12. Conclusion boundary / 结论边界

审阅完成不等于实现通过，也不等于 M4 通过。三个 access 维度建议 EXCLUDE_NONDEFAULT_ACCESS_ORACLE；RST、AFF、CVRF 三维度仅建议有条件事件规则。保留 source conflict / unknown / exclusion 后可以获得有界准入，仍不得全面字段晋升、硅片时序/精度证明或把数字事件称为物理数字孪生。

## 13. Author-stated limitations / 厂商原文限制

p21 Table6-3 脚注明示总线 timing min/max 基于一次设备样本的统计分析、not guaranteed、not production tested。p10 Note 限制真实输入不超过36V；本任务不验证这些物理边界。原文并未给出的 reserved write、RST latency、read-clear byte timing 属于本审阅识别的缺失，不能伪称厂商已写“局限”。

## 14. Critical assessment / 冲突及风险

冲突 `INA226_CONFLICT_AFF_CONFIG_WRITE` 保持 UNRESOLVED：`INA226_C12_AFF_CONFIG_P13` 指 CONFIG 写或 MASK 读清；`INA226_C13_AFF_CONFIG_P27` 指 only MASK 读清。不能自动以章节更具体、较后或看似更合理为由消除冲突。共通 profile 的 disputed write 后 AFF unknown 可限定研究范围，但不是 manufacturer conflict resolved。p12/p27 读取诊断支持先观察 flag 的功能用途，却没有“清前快照于第几位”保证；协议约定与来源事实分开。

## 15. Reusable knowledge and connections / 可复用接口原则

IR 的 reset-known、runtime-known、access-admitted、event-complete、source-conflict 应分离。来源清单按 claim ID 与精确 locators 保持追踪；外部辅助 sandbox 不写当前任务。只有主写入者整合，stage authority 仍为 sci-skills。排除异常刺激应返回验证协议状态，避免声称芯片一定 error/ignore。

## 16. Testable follow-up ideas / 可证伪后续与下一步

研究假设 H1：显式 full-completion + epoch gate 能减少 CVRF 因 partial / stale result 误置位；与原文不同是增加可审计事件契约。所需证据为独立测试轨迹；反证为任何 incomplete / stale event 获得 known CVRF1；最小版本是 pending-average、pending-math、stale-epoch 三类；风险是 event 声明自证。

研究假设 H2：AFF conflict 的 unknown 共通规则可避免强选段落形成伪正确结论；证据需 named profiles 差异与 common knownness 测试；反证为 common profile 确定值泄漏；最小版本为 latch fault→CONFIG write→inspect knownness；风险是 unknown 扩散削弱覆盖，需清晰报告。以上不宣称新颖。

唯一下一步：由主写入者按 independent_source_checklist.md 整合六维度来源建议并独立验收，保留未解决厂商冲突与排除项。
