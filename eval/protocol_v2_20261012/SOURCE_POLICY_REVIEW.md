# 第二版评分协议：有限范围独立来源审查

审查日期：2026-10-12。审查者：独立并行审查任务 `source_policy_review`。这是第二版协议的**来源规则建议**，不是 20 芯片或 572 字段的全面金标认证，也不晋升正式 IR 或修改第一版分数。

证据为七份本地原始厂商 PDF 的完整相关页、正式 IR 与修订候选 IR，以及既有 SOURCE_AUDIT.md 和 repair_manifest.json。四芯片主要规则核对后，补充了 Bosch 两芯片 UNUSED 与 HDC2021 访问类型缺省位的有限核对。已用 PDF 文本定位并直接看过关键表格页面；本报告没有运行模型，也没有以参考代码通过代替来源证据。页码均为 PDF 物理页码，与这些文档的印刷页码相同。PDF 和两套 IR 的 SHA-256 见 source_policy_review.json。

## 建议的规范边界

第二版以“**明确定义的合法配置下的直接寄存器契约**”为主范围。访问码 R/W 不能覆盖同一行的禁止写入规则，保留编码没有定义其写回、钳位、忽略或报错行为。应分别记录 `legal_values`、必要的跨字段前置条件、`known_mask`、`expected`、排除原因和来源定位。

复位断言采用 `(observed & known_mask) == (expected & known_mask)`。未知位不转换成零；`known_mask=0` 应记无适用断言，而不是 passed。无合法刺激或无被保护对象时同样 skip，并报告排除项。各字段测试使用新实例或复位后的基线，加明确的合法前置条件，避免前一个字段的写入造成下一个字段的非法组合。

本报告中合法刺激的选择属于 **AI 分析与协议定义**；厂商表格中编码、默认值和约束属于 **原文事实**。直接寄存器的存储读回通过不证明采样频率、模拟性能、时序或实物忠实性。

## LIS3DH：合法编码与组合

来源：`corpus/data/raw_pdf/ST/LIS3DH.pdf`，DocID17530 Rev 2。正式/候选 IR 的本次相关字段相同。

| 对象 | 原文定位与事实 | 第二版规则建议 | 判断 |
|---|---|---|---|
| CTRL_REG1.ODR[7:4] | p.35 Tables 29–31 定义编码 0x0–0x9，没有定义 0xA–0xF | `legal_values=[0,1,2,3,4,5,6,7,8,9]`；不得写 0xF 并要求读回 0xF | 已核实；旧排除注解应执行 |
| ODR=8 | p.35 Table 31 只列 low-power 1.60 kHz | 写 ODR=8 前保证 LPen=1、HR=0；没有组合约束能力时暂仅测 0–7、9，并明确排除 8 的覆盖缺口 | 已核实的条件，刺激选择为协议定义 |
| LPen 与 HR | p.16 Table 10 明确 LPen=1/HR=1 为 Not allowed | 不产生该组合；测 HR=1 前 LPen=0；测 LPen=1 前 HR=0 | 已核实 |
| CTRL_REG4.ST[2:1] | p.37 Tables 37–39 定义 00 normal、01 self-test 0、10 self-test 1，11 为未定义 `--` | 当前 IR 为 UNSPEC，第二版可以保守保留排除；若单独纳入则 override 为合法值 `[0,1,2]`，排除 3，限存储契约，不能声称自检响应已验证 | 原文已核实；纳入范围尚待主协议选择 |
| BLE | p.37 Table 37 脚注仅高分辨率模式可激活 BLE 功能 | 若测试功能，BLE=1 前 HR=1/LPen=0；普通寄存器读回不能证明字节序功能 | 已核实 |
| CTRL_REG0[6:0] | p.34 Table 25 与 Note 要求保持默认值，固定低七位为 0x10 | 合法刺激保持 `(value & 0x7F)==0x10`；不对写成相反值后的行为作裁决；复位已知值仍可检查 | 已核实 |
| STATUS 与 OUT_* | p.31 Table 21 输出项无静态默认值，而 WHO_AM_I 与配置项列明确默认值 | 保留动态输出的固定复位值排除；无输出模型时不把连续读取稳定性自动写成硅保证 | 已核实的默认值缺省；动态行为待专门协议 |

代码可用的 ODR 刺激序列示例：对 0–7 和 9，以 HR=0、LPen=0 作基线，写 `CTRL_REG1=(odr<<4)|0x07`；对 8 以 HR=0、LPen=1，写 `0x8F`。每次只比较 ODR 掩码 0xF0，并另外保留已启用普通配置字段的保护比较。ODR=9 在 normal 下有定义；序列无需假设其在所有模式均同频率。

## ADS1220：五个保留编码、三处旧注释误述

来源：`corpus/data/raw_pdf/TI/ADS1220.pdf`，SBAS501D，May 2026。正式和候选 IR 在这些字段上相同。

| 寄存器/字段 | 合法字段值 | 排除字段值 | 原文定位 |
|---|---|---|---|
| CONFIG0.MUX[7:4] | 0–14 | 15 | p.43 Figure 8-32、Table 8-10 |
| CONFIG0.GAIN[3:1] | **0–7 全部合法** | 无独立保留编码 | p.43 Table 8-10：7 为 gain 128 |
| CONFIG1.DR[7:5] | 0–6 | 7 | p.44 Table 8-12，normal/duty-cycle/turbo 均同样排除 7 |
| CONFIG1.MODE[4:3] | 0、1、2 | 3 | p.44 Table 8-11 |
| CONFIG2.VREF[7:6] | **0–3 全部合法** | 无独立保留编码 | p.45 Table 8-13：3 为 analog supply |
| CONFIG2.IDAC[2:0] | **0–7 全部合法** | 无独立保留编码 | p.45 Table 8-13：7 为 1500 µA |
| CONFIG3.I1MUX[7:5] | 0–6 | 7 | p.46 Table 8-14 |
| CONFIG3.I2MUX[4:2] | 0–6 | 7 | p.46 Table 8-14 |
| CONFIG3.RESERVED[0] | **仅 0** | 写 1 的行为不评分 | p.46 Table 8-14：虽然访问码 R/W，但明写 always write 0 |

必须更正此前 SOURCE_AUDIT.md 的范围表述：**IDAC 不是保留编码对象**，而 DR 是。此外，旧 IR 的 GAIN 描述把 111b 称为 Reserved、VREF 描述把 11b 称为 Reserved，均与当前本地 PDF 不符；CM 的“0=单端、1=差分”也不符，p.44 Table 8-11 实为 **single-shot / continuous conversion**。这些错误影响提示词含义，第二版 policy 覆盖正确刺激并不能代替重新生成输入的修复与冻结。

跨字段约束必须单独处理：

- p.43 Table 8-10：MUX=8–11 必须 PGA_BYPASS=1，且 GAIN≤2。MUX=12/13 描述明确 PGA bypassed；建议这两值也用 PGA_BYPASS=1/GAIN=0 的保守前置条件。
- 同表：PGA 仅可在 gain 1/2/4 下 disabled，GAIN 编码 3–7 始终使能 PGA，不论 bypass 标志。测试 bypass=1 用 GAIN=0，GAIN 高编码用 MUX=0/PGA_BYPASS=0，避免把功能覆盖写成仅位存储的结论。
- p.45 Table 8-13：非零 FIFTY_SIXTY 仅与 normal 20 SPS 或 duty-cycle 5 SPS 组合使用，即 MODE=0/1、DR=0；其他 DR/MODE 组合保持 FIFTY_SIXTY=0。字段本身的四个编码均有定义。
- CONFIG3 任何合法刺激均保持 bit0=0。该位只有一个合法值，无法构造合法的 0→1 持久性对照；相关变位测试应记 skip 或无适用刺激，不能宣称该位不可写、忽略写入、读恒零，亦不能宣称其值 1 可存储。

代码可用的最小字段基线：MUX 0–7/14 时 CONFIG0 的低四位=0；MUX 8–13 时低四位=1。DR 遍历 0–6 时 MODE=0 且 CONFIG2.FIFTY_SIXTY=0。MODE 遍历 0–2 时 DR=0、FIFTY_SIXTY=0。FIFTY_SIXTY 遍历 0–3 时 MODE=0、DR=0。I1MUX/I2MUX 遍历 0–6 时另一个路由为 0、bit0 为 0。所有 CONFIG0–3 的默认值 0x00 在 pp.43–46 一致，可保留全 8 位 reset known_mask=0xFF。

## TMP117 DEVICE_ID：低十二位确定，高四位保留冲突

来源：`corpus/data/raw_pdf/TI/TMP117.pdf`，SNOSD82D，September 2022。

p.25 Table 7-3 与 p.32 标题给 DEVICE_ID reset=0117h；p.32 Figure 7-22 高四位 Rev[3:0] 为 R-x，但 Table 7-15 reset 列写 0h。低十二位 DID 在位图、表格、标题中均为 117h。高四位还明确代表器件 revision，不能把单一零值无条件推广到所有版本。

推荐主协议：`DEVICE_ID reset known_mask=0x0FFF, expected=0x0117`。复位和 RO 保护只检查已知低十二位；高四位不规定固定值。当前聚合 ID[15:0] 字段必须接受寄存器级比较掩码或拆分 policy 字段，不能因候选把 field.reset 修到 279 就认定高四位冲突已解决。

保留一个明确的冲突记录 `TMP117_REV_RESET_CONFLICT`。全 16 位 0117h 可作为“假定 revision=0 的模板配置”补充结果，不能作为跨器件版本主评分。本地来源无 revision 固定为零的独立实物证据，未搜索勘误或新版本，也未进行实物读回。

## INA3221 p.33：保守排除写入裁决，保留一致的复位位

来源：`corpus/data/raw_pdf/TI/INA3221.pdf`，SBOS576C，September 2026。

p.33 §8.2.15 标题写 SHUNT_SUM_LIMIT(0Eh) reset=7FFEh；Table 8-31 全位标 RW，bit14:1=1、bit15/0=0。紧邻 Table 8-32 却把 SIGN、SVL、Reserved 全列为 R、reset=0。两者确有冲突，来源文件已直接核对，不能把候选内部 reset 一致视作解决了厂商冲突。

推荐主协议：

- 0Eh reset 比较 `known_mask=0x8001, expected=0x0000`，仅检查两套表述一致的 bit15 与 bit0；bits14:1 从固定复位断言中排除。
- 整个 0Eh 的普通 RW 持久性、RO 保持和写掩码断言均排除，因为访问类型全域冲突；不要先假定可写，再把表格的 R 含义解释成笔误。
- 测试未知地址时 0Eh 仍是已映射地址，不能改当未定义地址；读取宽度检查若没有源语义假设仍可保留。
- 若采用 title+diagram 优先解释，必须作为单独的 `diagram_priority_exploratory`：reset=7FFEh，SIGN15 与 SVL14:1 为 RW，bit0 访问仍有冲突，先不判非零写入行为。记录采用理由为门限功能、标题与逐位图一致，反方为 Table 8-32；这是 AI 裁决假设，不是已核实的硅真值。

当前正式/候选 IR 聚合 SVL[15:1] 混合 sign 与 14 位 data；以后正式来源修复宜拆成 SIGN[15] 与 SVL[14:1]，但本任务没有修改两套 IR。候选 reset=16383 符合 bit14:1=1/sign=0 的图表优先解释，只证明内部一致。

MASK_ENABLE 补充：p.34 §8.2.16 明说写入不清除 flag，CF/SF/WF 读后清除；p.35 Table 8-34 continued 说明 CVRF 在规定的 CONFIG 写入或读 Mask/Enable 后清除。访问列的 R/W 标签不允许忽略这些行为而要求 flag 存储任意写值。建议普通 RW 比较仅包括 SCC/WEN/CEN 的掩码 0x7C00；RSVD15 无功能规范且仅列 reserved/RW，保守保持 0 并排除翻转刺激；CF/SF/WF/CVRF 的 write-persistence 排除，read-clear 需要受控事件注入后才可验证（没有事件触发的“读0再读0”不是有效覆盖）。PVF 对应外部 power-valid 条件，TCF 与 timing 状态相关，也不要写值模拟事件。p.34 表头的 0002h 和 TCF 默认 high 支持新实例初始 TCF=1，但不证明事件运行中永久为 1。

## 补充：Bosch UNUSED 与 HDC2021 缺省访问类型

来源：BME280 本地 PDF 首页标 BST-BME280-DS001-24 revision 1.24 February 2024，但核对页的 footer 仍标 BST-BME280-DS001-23 Revision_1.23_012022。报告保留此内部版本标识差异，按完整文件 SHA-256 确定来源，不把页脚猜成另一个文件。BMP280 为 BST-BMP280-DS001-26 revision 1.26 October 2021。HDC2021 为 SNAS773A June 2020。

| 对象 | 已核实原文 | 规则建议与限制 |
|---|---|---|
| BME280 config.UNUSED[1]、BMP280 config.UNUSED[1] | BME280 p.27 Table 18、BMP280 p.24 Table 18 此位灰色；legend 分别为 do not change、do not write。配置字段详细表 BME p.30 Table 26/BMP p.26 Table 23 只列 7:5、4:2、0，未给 bit1 RW 语义 | 隔离该字段的 RW/RO 翻转断言，所有合法配置刺激保持 bit1=0；旧 IR 编为 RW 没有本页支持。配置 reset 状态表均 00，可保留初始0的已知事实；不能推断非零写入会钳位、保存或忽略 |
| BME280 ctrl_hum.UNUSED[7:3]，两芯片 status.UNUSED[7:4]/UNUSED2[2:1] | 同一 memory map 中为灰色 reserved，并有 do not change/do not write 图例；reset state 为00 | 不翻转灰位、不测试恒零读回保护；可保守从 runtime 比较排除。若 reset 采用更保守 mask，ctrl_hum 仅0x07、status 仅0x09；这是减小主协议范围，并非原文缺少 reset=00 |
| 两芯片 press_xlsb.UNUSED[3:0]、temp_xlsb.UNUSED[3:0] | 同一表明确四个逐位 0，并与数据部分一起为黄色 read only；reset state00 | **保留已知低4位0与RO定义**。BME tier UNVERIFIED 是此前文本层审查状态，已核对此位图后不能再仅凭字段名或旧 tier 排除已定义的0位。可由 policy 精确 override 为 known0/RO；不要外推到灰色区域 |
| HDC2021 STATUS.UNUSED[2:0] | p.23 Table7-16，TYPE列空白，RESET列每位明确0 | 初始复位值0已知，可保留reset；访问行为未定义，排除RO保护/持久性，刺激保持0 |
| HDC2021 INTERRUPT_ENABLE.UNUSED[2:0] | p.25 Table7-22，同样TYPE空白、RESET0 | 同上。不能把没有访问码等同没有复位证据，也不能把有reset0等同RO硬连0 |
| HDC2021 MEAS_CONFIG.TACC/HACC | p.31 Table7-38 定义0=14bit、1=11bit、2=9bit、3=NA | 合法域分别[0,1,2]，排除3的行为；此前普通RW全1刺激无功能保证 |
| HDC2021 MEAS_CONFIG.MEAS_CONF | 同表0=humidity+temperature、1=temperature-only、2/3=NA | 合法域[0,1]，排除2/3 |
| HDC2021 MEAS_CONFIG.RES[3] | 同表明确R/W、reset0、description Reserved，无写0强制文本 | 记录已核实R/W标签，但保守主协议可仅保持0，排除无功能说明的翻转断言；若按纯RW存储协议测试，应显式标明定义和范围，不能与TYPE空白的两组位混为一类 |

补充约束：BME280 p.30 §5.4.6、BMP280 p.26 §4.3.5 说明正常模式配置写入可能忽略、睡眠模式不会忽略。测试 config 普通存储前必须在独立基线保持 ctrl_meas.mode=0，不能在前次字段测试残留 normal mode 下写 config 后要求任意持久性。BME280 p.27 §5.4.3 说明 ctrl_hum 的配置生效依赖后续写 ctrl_meas；这区别于仅读回存储值，不可宣称传感器功能已覆盖。

## 交接与尚未解决项

审校状态：**有限范围规则事实已核实，第二版主协议可按明确排除继续实现；全面来源准入仍为 REPAIR**。TMP117/INA3221 的原文冲突保留，未检索厂商勘误、未接入硬件、未评估所有动态模型。本报告独立核实约束，不认证原论文主表。

唯一下一步：由主任务把本报告规则落实到独立编号第二版 policy，验证合法刺激与掩码确实被执行；输出各项适用/排除数和第一版对照，保留原始生成与评分记录。
