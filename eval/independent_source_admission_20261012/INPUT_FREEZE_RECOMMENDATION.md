# 新一轮生成的输入冻结建议

当前建议：**审校证据可以冻结归档；正式生成输入暂不准入。** 本包提供20份已应用来源补丁的IR草案、572字段七维规则与具体冲突/排除，完成本步独立来源审查。candidate schema不是旧v2接口；未经配套新harness实施不要把候选改名成全面Gold。

## 1. 固定来源与科学范围

锁定reviewed_source_manifest的全部本地原PDF字节、器件orderable/手册版本、PDF物理页/印刷页与表号。TMP1075范围non-N；TMP117固定factory EEPROM仅作为显式情景，而非任意器件复位保证；TPS必须区分POR、输入RESET、RESAL/RESP以及供电轨。MPU使用RM作寄存器主要证据，产品规格作补充。572是既有inventory单位，空字段EEPROM及未映射命令保持另列，若新增字段/地址要重新确定分母。

保留所有SOURCE_CONFLICT项，主评分只使用无冲突方面。TMP117 DEVICE_ID reset用0x0FFF；INA3221 0Eh reset只用0x8001且写/保护排除；TPS R17[3:1]首次观测保持，reset/access不确定位不得填0。任何diagram/text优先模型要用命名exploratory profile单列，不写官方勘误。未定义非法编码输入不给钳位、忽略、异常或读零oracle。

## 2. 修订候选与生成输入分开冻结

candidate_ir为新目录中的来源草案，candidate_source_policy每条以inventory_field_id追踪原572身份，同时field/bits/candidate_bit_mask指向修复后的实际几何。LIS2 ZERO_7_4→ZERO_3_0与TMP100位宽改变已经对齐。未确认reset移除/置null/标runtime，来源冲突保留，不直接推全字段恒值。历史审校注释保存在legacy_ir_annotations，生成时不得把其过去的Gold、通过或erratum表述作为事实。

准入前必须实际验证新schema的IR、policy、harness三者共享相同字段名/地址/掩码、动作属性与范围。CONDITIONAL规则是输入契约的一部分，不能只写在报告里让harness忽略。每一REPAIR必须有闭环项：已应用的输入修订、是否需harness变更、验证证据、剩余排除；未闭环不得改PASS。记录每个使用的合法值与被排除值/组合，默认或未知保留位只作输入约束，不当RW/RO实证。

## 3. 明确静态与事件两套范围

可在新协议定义“已完成复位、初次转换完成前、无外部状态变化”的静态契约，但必须明说它是寄存器抽象。RO仅表示软件写权限，不能在时间推进、读清或MODE/POL副作用发生时做整快照相等。动态mask、相同事件窗口及逐字段保护必须实际执行。没有可观察非默认刺激的对象skip而不是通过。

动态契约若纳入，须先声明受控事件接口/调度：conversion_started、conversion_completed（含AVG次数）、NVM/POR_load_completed、EEPROM_program_completed、threshold/hysteresis/fault-count、CRC_fail、FIFO读/溢出、power/classification等。事件名是基准抽象约定，不是实测厂商时间；典型时间不能当保证超时。完成归一化与即时读回必须分开：LIS2 BOOT/reset完成自清、HDC MEAS_TRIG开始自清、TMP102 OS转换状态、TMP126 ONE_SHOT读恒0但完成MODE1等不能共享一个read_as0裁决。

读清必须构造非零flag，核对read返回的preclear数据、postclear状态、受保护未清位、重触发条件和跨地址clear。TMP117 TNA限定、TMP126 single read/no auto increment+TEMP清DR、HDC多读地址、LM83/TMP461致因解除、INA配置写清、TPS CoR清0与summary重算都需落实。没有事件接口的方面保留CONDITIONAL/EXCLUDE，读0→0不算该功能覆盖。

EEPROM须区分易失写与持久编程：TMP117 EUN0可写scratch，EUN1且Busy0才编程，Busy两位置镜像，完成后再允许下一写，reset加载持久副本；TPS需unlock/地址/AIN/自动锁定等条件。I/O锁、Bosch commit/sleep、MPU/LIS模式条件、校准有效与阈值关系均须按规则执行。若暂不实现，排除对应功能，不能让独立普通RW存储代替门控。

## 4. 准入验收与生成溯源

在新目录运行source/schema对齐、适用分母、合法刺激和掩码检查；用有区别的故障夹具验证“错误readback、无条件清除、从不清除、无条件复位、不复位、忽略门控、过早完成、非法刺激”等确实被抓住。参考通过只证明harness与参考的一致，不能改来源标签；完整来源账本继续作为事实权威。避免重复无意义的全量历史重评。

通过后再创建production_generation_manifest，哈希锁定原PDF索引、修复IR、policy、精确harness、test-values/known-masks/exclusion清单、base simulator、完整system/user提示词、模板展开后的每芯片prompt、依赖/运行命令与模型revision/参数/seed（不可得项明确缺失）。生成前计划分母与分组关系，生成后保存逐次代码SHA、响应/解析/重试轨迹。新生成与旧720次历史队列分别报告，不能后补哈希重建旧提示词或把重评分变化称学习进步。

input_freeze_candidate_manifest的哈希是本轮可评审材料快照；harness_hash=null是未实施门控的明确信号，不代表通过冻结。任何输入字节变动都产生新版本manifest，不覆盖本包或历史。

唯一下一步：在独立新目录实现并验证候选契约/harness，关闭96项REPAIR对应的准入缺口及条件规则，再冻结正式生成上下文。所需资料本地已齐，无需账号、SCNet或实物采购。
