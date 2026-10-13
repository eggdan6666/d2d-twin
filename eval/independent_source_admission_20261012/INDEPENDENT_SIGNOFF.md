# 独立来源签审：20芯片 / 572字段

审校日期：2026-10-12（Asia/Shanghai）。签审身份：Codex 独立AI来源审校主任务，配合三个项目SCI-Skills独立审查子任务；非人类专家签字、非厂商认证、非实物验证。待审对象为用户指定的七份v2报告/政策/manifest，实际证据来自 corpus/data/raw_pdf 的原始厂商PDF。未使用参考通过或模型得分裁决来源。

**签审结论：审校与候选交付完成；当前输入全面准入为 REPAIR，正式新一轮生成冻结为 NOT_ADMITTED。** M4保持部分通过，未推进阶段。

## 逐项审查结果

20芯片572个既有inventory字段全部对应一条独立账本，无缺项、重复或分母扩大；每字段审查reset、access、合法编码、读清零、触发完成、条件写入、保留位七维，共4004条维度记录。额外空字段EEPROM/命令/范围缺口在register_scope_gaps.json单列，不计入572分母，也不外推当前selected register set为全芯片认证。

|逐字段结论|数量|含义|
|---|---:|---|
|PASS|135|所引原页与限定的字段事实/契约可接受；不代表全部动态功能已执行验证|
|REPAIR|96|现输入/政策需修订，或遗漏副作用/域/门控；候选尚未在新harness兑现|
|CONDITIONAL|302|事实有来源，但断言必须附具体版本、模式、复位边界、事件或抽象前提|
|EXCLUDE|39|该字段相关主oracle缺定义或有不可裁决冲突；可分别保留已知reset等其他事实|

每条维度同时保留MANUFACTURER_FACT、ABSTRACTION_ASSUMPTION、UNDEFINED_BEHAVIOR、SOURCE_CONFLICT分类。无独立读清/触发规定的维度标EXCLUDE及适用范围；不把手册未给动作证明为“没有任何副作用”。status是对旧inventory的审查结论，候选几何位置与新字段名在candidate_source_policy的inventory_field_id/candidate_bit_mask中显式映射。

## 本轮决定性差异

- TMP117：T/nA=0才对HIGH/LOW读CONFIG清零；THERM模式HIGH依阈值更新、LOW恒0，CONFIG读不清。EUN=0仍更新易失scratch/config/limits寄存器，只是不编程EEPROM。典型编程7ms，Busy需完成后再写；CONFIG的EEPROM-backed位、门限、TEMP_OFFSET复位不能无条件固定出厂值。三个无字段EEPROM寄存器另列门控；EEPROM2标题与图表reset冲突新增保留。
- 动态转换与告警：TMP100 OS受POL和比较器迟滞影响，不能恒read_as1；TMP102 OS是转换状态、AL受POL反相，EM=1改变TEMP/门限位格式。TMP1075限非N，OS触发需SD1；写TM清fault count/alert history。INA219/INA226/INA3221转换标志的读/写清条件、单次完成及校准副作用单列，权限不等于恒定快照。
- 读清零范围：TMP126 Alert_Status要求single-register read且无auto increment；TEMP_RESULT还清DATA_READY，ONE_SHOT完成置MODE1，Comparator→Interrupt清状态。LM83、TMP461清flag需模式/致因/转换窗口；ALERT引脚解除与寄存器flag清除分开。HDC2021 MEAS_TRIG在测量开始自清，DRDY完成另判，多输出读址可清DRDY，INT_MODE编码说明需修复。
- 确定输入错误：LIS2DW12 OUT_T_L数据在bits7:4、零位在3:0，旧位域颠倒；TMP100用12位完整TEMP寄存器格式并按分辨率置未用LSB。TMP461 STATUS与ONE_SHOT的POR为N/A，移除旧0候选。TPS23861 FIRMWARE_REV地址应0x41而非0xFE；GENERAL_MASK.M250是sense resistor选择，非250ms。
- 模式与门控：Bosch config写需sleep；BME ctrl_hum需后续ctrl_meas写commit，模式切换存在等待/忽略窗口。BMP280的10同01都是forced；XLSB高半字节承载数据。LIS3DH七个STATUS字段Table47有Default0，不宜全部以“14动态字段无默认”排除；XDA该版缺描述行及输出数值未定义分别保留。AD5592R IO_LOCK与readback使能、MPU睡眠/中断清条件、TPS EEPROM解锁/Auto改写/端口动作都作为条件规则。

## 不裁决的来源冲突

TMP117 DEVICE_ID高四位Rev及Soft_Reset图/表、INA3221 0Eh图/表、TPS23861 R17[3:1]总览/详细粒度冲突保持UNRESOLVED。主oracle仍用TMP117 DID低12位、INA3221仅0x8001一致reset位并排除0Eh写/保护裁决、TPS歧义位保留首次观测值而不固定0。新增INA226 DIE_ID/AFF、INA219 CNVR章节、TMP117 EEPROM2、INA3221 TCF单比特11h、AD通用命令位布局、LIS2 FIFO/MPU描述等内部冲突也未择多数为真。

完整逐项 competing_evidence 与locator在conflict_ledger.json；分区额外冲突卡保留。所有冲突、推断和策略都不称官方勘误。候选输入的历史审校话语移到legacy_ir_annotations.json，避免把旧“Gold/已通过/erratum”注释当下一轮厂商事实。

## 证据与完整性

本轮21份本地PDF身份（包含MPU的RM与PS）已复核SHA-256；4356处短原文引用在原PDF文本读取/排序读取中精确匹配，关键位图已渲染目视。文本匹配证明引用存在，不代替事实支持性判断；逐字段判断见账本，分区签审记录其所读页与视觉边界。不是4356条独立来源事实。

109条候选属性补丁仅应用到新目录的20份candidate_ir；结构检查无位域重叠/越界，candidate policy逐字段映射对齐。另有84条差异记录，同一机制可能跨多个字段，不当作互异硅缺陷数。candidate_ir保留572字段，空字段补建建议另存，未来若扩充须重新冻结分母。

受保护的12563个既有文件SHA-256复核全部不变，包括d2d/ir、所有现有test_d2d_blackbox.py、完整v2目录和历史模型结果清单；v2 manifest的44项匹配。未运行模型/参考测试、SCNet、外部API、实物或总线时序。本轮评分计数来自来源审查分类，不是重新评分。

## 交付与输入冻结

field_evidence.json与dimension_evidence.csv提供572字段/4004维度证据；field_verdicts.csv、per_chip_verdicts.csv提供快速筛查。revision_candidates.json、applied_candidate_patches.json、DIFFERENCES.md提供修订候选和差异。candidate_ir与candidate_source_policy.json为来源约束输入草案，schema刻意与旧v2区分，**不能作为旧harness的替换输入**。

audit_bundle_manifest.json冻结本次审校材料；input_freeze_candidate_manifest.json仅冻结可评审输入候选字节，production_generation_ready=false。INPUT_FREEZE_RECOMMENDATION.md列出准入门控、事件定义与新生成上下文应保存的指纹，GENERATION_PROMPT.zh.md提供后续可复制模板。冲突被排除的方面必须仍在新一轮报告中显式披露。

唯一下一步行动卡：在独立新版本中落实候选IR/policy与事件/完成/模式门控的harness，先验证实际适用掩码、合法刺激、非零事件与负向故障夹具，再冻结精确生成提示词和模型revision；通过后才启动新一轮生成。本步材料齐全，无需SCNet或购买实物。
