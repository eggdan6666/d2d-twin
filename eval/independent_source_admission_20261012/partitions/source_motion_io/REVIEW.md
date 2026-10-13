# 四器件独立来源审校签审候选

日期：2026-10-12。任务：source_motion_io；SCI-Skills paper-deep-reading 有界 M4 REVIEW。此为独立 AI 审校意见，不是人类签字或硬件认证；不推进或改变阶段。

结论：**REPAIR**。已覆盖 AD5592R 22、LIS3DH 34、LIS2DW12 55、MPU6050 29，共 **140 字段、980 维度记录**。逐项记录见 fields.json；总体 {'CONDITIONAL': 116, 'REPAIR': 16, 'PASS': 8}。PASS仅表示所列来源事实与适用范围，无动作定义的维度仍明确 EXCLUDE，不能读为整芯片功能通过。

## 范围与输入

用户指定七份文档/JSON是待审对象，相关chip字段及全局认证表述已读；厂商证据只来自 corpus/data/raw_pdf 的五份本地PDF。sources.json保留器件、版本、SHA-256、来源角色。MPU6050字段以RM镜像Rev4.2为主；同名MPU6050.pdf是PS Rev3.4，仅补充产品规格，不互换物理/印刷页码。所有新输出仅本目录，未改d2d/ir、v2、冻结harness或历史模型记录。

## 关键差异

- **LIS2DW12 OUT_T_L位域颠倒**：p.35 Table22实际bits7:4为TEMP3:0、bits3:0为0，p.18明确12bit left-justified。已渲染目视确认，候选将TEMP_3_0改7:4、ZERO_7_4改3:0并重命名ZERO_3_0。
- **LIS3DH STATUS默认排除过宽**：p.39 Table47明确七位Default0（mask0xFE）；p.31的Output标签不覆盖这些事实。XDA在Table46有位名但Table47无描述行；仍不推补初值。六个OUT字段仍无数值默认。初值已知不等于运行时不变，也没有来源指定STATUS的各项清除条件。
- **动态清除边界**：LIS2 WAKE_UP_SRC §8.28未规定FF_IA自读清；p.53 §8.31明确读ALL_INT_SRC reset相关已routing到INT pads的function flags，轴标志具体映射不补推。MPU RM p.26/28明确INT_RD_CLEAR0只读INT_STATUS清、1任意read清；当前29字段未映射中断block，读已映射地址的跨寄存器副作用也尚未建模。
- **AD配置门控与SPI抽象**：IO_LOCK和idle/noADC/noReadback前置条件缺失；CONFIG_READ_AND_LDAC selector、REG_RD_EN、next SPI read及完成自清未映射。0x5AC复位动作有出处，但任意错误key无副作用不是本地原文保证。250µs期间不写为厂商事实，atomic completed reset为模型假设。
- **模式副作用**：LIS2 BOOT只重载trimming且不影响control，SOFT_RESET仅原文all control registers；BDU在双byte读完前禁止更新。MODE2单次完成依CTRL3 trigger与输出可用，typ.T_on不能当严格上界。FIFO FTH0时FIFO_FTH0；切换首样discard；offset功能依CTRL7 enable/weight和FDS0。

## 来源冲突与来源未定义

保留AD Table10通用bits10:9保留与REP9/SWkey10:0的不同表述；DAC_RD_EN正文11使能与两位组表0/1文字歧义继续只用00/11。保留LIS2 Table55的trigger deasserted/100终态FIFO与§5.3.4–5.3.5正文trigger event/continuous差异。保留MPU DLPF7在divider正文有disabled解释、filter表为Reserved的歧义；GYRO总表high3bits“-”与细表named ST布局差异仅detail-first条件解释。均无官方勘误核验，不能改称厂家勘误。

MUST_BE_ZERO的must0不是RO；普通Reserved的默认0也不是硬编码0。MPU WHO_AM_I bit0/7有hardcoded0独立证据，可保留该特例。LIS3 ST的旧UNSPEC是基准排除而不是厂商类型，候选可改合法0/1/2的RW并独立排除analog selftest。

## 证据与执行

原始PDF相关页实际抽取，三个关键图页实际渲染/目视。全部1515个字段维度locator摘录出现位置已在原PDF文本中验证；这验证引用存在，不自动证明每项推理。json字段身份和七维覆盖已经本地检查。未跑参考或模型、未用SCNet、未购硬件、无外部API、未搜厂商现时勘误。没有把参考通过或模型高分用作来源证据。

## 交付与冻结建议

fields.json逐inventory键保留原identity、原bits、旧值和候选dimensions；findings.json为差异清单；candidate_ir_annotation_patch.json为可审的输入属性候选，candidate_policy.json为可冻结策略建议；register_gaps.json防止把子集称全器件coverage。不得直接merge或重写历史结果。先选择候选修订、条件范围和排除项，再用新编号冻结PDF/IR/policy/完整prompt与模型版本；新一轮生成单独队列。当前来源冲突继续UNRESOLVED，原模型代码是旧输入产生，不据此推断修正输入后的能力。

唯一下一步：主编排逐项接受候选修订和条件/排除规则，冻结新的来源与输入版本后才用于新一轮生成。
