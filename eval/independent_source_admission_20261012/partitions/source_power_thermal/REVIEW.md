# 独立来源签审：power / thermal 分区

日期：2026-10-12。身份：独立 AI 来源审校子任务 `source_power_thermal`，SCI-Skills presubmission-review。审查范围：HDC2021、LM83、TMP461、TPS23861；阶段为M4有界来源准入，不推进或宣告阶段通过。只写本次新目录分区。

已逐项生成149个inventory字段、每字段7维共1043对象。判定计数：{"CONDITIONAL": 33, "REPAIR": 28, "EXCLUDE": 22, "PASS": 66}。分芯片：{"HDC2021": {"CONDITIONAL": 6, "REPAIR": 8, "EXCLUDE": 3, "PASS": 22}, "LM83": {"CONDITIONAL": 7, "REPAIR": 8, "PASS": 19}, "TMP461": {"CONDITIONAL": 4, "REPAIR": 9, "PASS": 22, "EXCLUDE": 12}, "TPS23861": {"CONDITIONAL": 16, "REPAIR": 3, "PASS": 3, "EXCLUDE": 7}}。每条保留原始PDF路径、SHA-256、版本、物理页/印刷页、表号或节号及短原文；部分字段共用同一真实表，但结论单列。PASS仅指明示来源事实及明确抽象范围可接受；CONDITIONAL须未来harness落实门控，EXCLUDE可能仍保留已知reset，不是整体删字段。此审查不以20/20参考通过、模型得分或内部reset一致代替来源证据。

## 重大修订候选

1. TMP461 Table4(p17)将STATUS、ONE_SHOT的POR列为N/A；既有00及8个状态位/START的0不能冻结为厂商事实。状态位随ADC/连接/比较器变化；温度register 00/01/10/15的POR00可保留，但只在新测量前。读温度字节锁配对字节的保证仅到另一寄存器被读之前。
2. TMP461 p19的LHIGH/LLOW/RHIGH/RLOW/OPEN在ALERT模式读清必须致因消失。THERM2模式仅OPEN保持该读清锁存；温度高flag/引脚用THERM和HYS行为，low flags无THERM2输出效应。读STATUS不清ALERT interrupt latch；master服务sensor address且状态/致因解除才清脚。ONE_SHOT须SD=1、按LEN/REN选通道，payload任意且不存储，结束回shutdown。
3. HDC2021 MEAS_TRIG在measurement **starts**时自清，不是完成时；完成由DRDY_STATUS表示。SOFT_RES在RESET之后清0，旧read_as0不能作为时序恒定事实。INT_MODE真实含义为0 clear-on-read、1 comparator。DRDY经读00/01/02/03/04任一地址清；threshold flags在模式0锁存至STATUS读，模式1反映当前转换；输出enable和状态本身分开。MAX仅one-shot模式、最后reset后的峰值。
4. TPS23861五组CoR地址03/05/07/09/0B返回preclear整字节并清0，不能写成restore POR；事件注入必须非零并冻结新事件窗口。Interrupt summary由剩余event latches重算。POFF/RESP/Off mode对detect/fault/start/status/enables的清除、对power-event的置位均须建模。RESET命令CLRAIN清事件+interrupt+释放INT，CLINP仅释放INT，RESAL是power-up-equivalent，RESP是port reset；旧desc混淆三者。
5. TPS23861 Supply p54只列POR30h；RESET输入/RESAL的VDUV/VPUV取决于供电轨，不能把30h无条件推广。VDUV/VPUV是VDD/VPWR UVLO事件，不是未启用检测。M250表示250/255mΩ sense resistor而非250ms。R27 Reserved非ROM。FIRMWARE_REV为0x41，IR0xFE是可确定地址错误但无inventory字段；保留runtime未知值。
6. TPS23861 POEP在Auto分类完成/power-on前由硬件自动改写，任意RW持久性须隔离Auto事件；功能上需ICUT匹配。原手册完整register set远超当前inventory，尤其0x11 EEPROM AUTO/SLA、0x12 mode、0x14 enables未列，但控制当前字段前提。EEPROM要求broadcast30h unlockAA、临时地址、AIN selection、寄存器11h写、自动锁定永久保存；约100ms timeout；reset后至少22ms，program后读验证建议100ms；25次endurance。只读标签在unlock期间变RW，不能按常规RO翻转测试替代。
7. LM83全正文印刷页=PDF物理页−1。状态HIGH/CRIT的图注称read清flag、正文将flags/output解除与温度比较联合，必须保存解释粒度/时序不确定性；仅退休致因且冻结conversion的窗口作候选确定oracle，active fault重置位行为排除。OPEN由外部conversion前的连接检测决定，缺单独读清证据，不能沿用HIGH/CRIT clear。CONFIG reserved6/0有明文“write1 returns0”，可保留硬证据，与其它器件保留字段分开。

## 冲突与范围

TPS23861 R17[3:1]保留`SOURCE_CONFLICT`：Table10总览80h、详细表Reserved。只保留非冲突位数值初值，R17[3:1]保持新实例观测值、排除访问/固定数值断言；R17[1]不是ROM/revision。此分区没有裁定TMP117/INA3221的冲突，主任务须维持原冲突状态；本报告没有厂商勘误来源，不称任何候选为官方勘误。

读取源/输出源事实、R/W静态寄存器抽象、NA/undefined行为、内部冲突分别用MANUFACTURER_FACT、ABSTRACTION_ASSUMPTION、UNDEFINED_BEHAVIOR、SOURCE_CONFLICT。默认无read-clear/trigger的对象是明确`applicable=false`的范围标注，不是证明手册不存在任何副作用。动态RO只保护software write权限；无法保证时间推进后读值不变。

## 新输入冻结建议

`ir_patches.json`只列可定位的候选属性修改；不得原位覆盖旧IR、旧v2或历史生成材料。新IR必须去除无来源数值reset，保留掩码/来源冲突/EEPROM条件，修正错误desc和TPS revision地址，扩展缺字段commands或明确排除。这些候选未经新harness兑现，不能把静态IR先冻结成全面Gold。

新harness候选门控：独立reset事件类型及供电/EEPROM状态；事件注入与conversion scheduler；preclear read值和postclear状态；读取alias依赖；MEAS_TRIG开始与DRDY完成分离；ALERT/THERM/comparator模式；POEP自动改写及POFF/RESP副作用；任意受保护动态位用匹配事件窗口或dynamic mask，而非整快照相等。没有门控能力的维度必须CONDITIONAL/EXCLUDE，0→0不能记动态功能覆盖；atomic action只可写明completed-event抽象，不能宣称实际时序验证。

将源SHA、候选IR/policy/harness、版本、命名冲突、适用掩码、被排除值/地址、抽象范围、generation prompt模板完整哈希，再允许新一轮生成。原始历史成绩与旧提示词事实继续独立保存。

## 证据与交付

`fields.json`149条、`findings.json`13项、`register_gaps.json`8项、`sources.json`4份、`ir_patches.json`属性候选、`quality_checks.json`机械核验及七输入指纹、`expert_return.json`1.0完整契约。技术页完整文本逐页读取，TMP461 p17/19、HDC2021 p31、TPS23861 p63/66、LM83 PDF10/印刷9已渲染目视；其它页用完整原始页文本核对。版本与source hash均以本地文件身份冻结，不声称当前官网下载字节核验。没有运行模型、reference tests、SCNet、外部API或实物；没有需要用户账号/购买的动作。

Contribution视角：改进来源准入与测试有效性，不能称为模型学习能力提高。Methods视角：事件、版本、未知reset与模式门控仍需新协议实施。Communication视角：149条ledger与硬件功能覆盖是不同计数，冲突不能修辞抹平。独立签审为 **REPAIR / NOT_READY for unconditional hardware-faithful admission**；阶段裁决权仅属于主编排。

唯一下一步：由主编排汇总分区，建立上述事件/模式/完成门控的新输入与新harness冻结候选，保留命名冲突后再审批正式生成。
