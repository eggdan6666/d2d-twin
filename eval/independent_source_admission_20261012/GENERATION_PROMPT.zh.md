# 后续新输入实施与生成提示词模板

使用条件：仅在INPUT_FREEZE_RECOMMENDATION的harness准入门控通过后用于正式生成；当前可用于新版本实施/评审。不得把本包状态改写成无条件Gold。

请根据指定芯片的candidate_ir与candidate_source_policy.field_rules实现约定接口的寄存器模型。原始厂商事实以field_evidence七维事实及原PDF定位为准；source conflicts、undefined input和未实施事件方面必须按policy排除，不能猜测硬件行为。inventory_field_id仅作追踪，字段位置使用候选field/bits/candidate_bit_mask。数字reset必须应用known mask、epoch、EEPROM/orderable/模式前提；未知位不补零。

严格区分直接软件存储、动作触发、动态读状态、读清、完成时刻及条件写入。RO不能自动写成恒值；写触发不能写成普通RW镜像；EEPROM锁定不等于TMP117 volatile write无效；read_as0不自动意味着操作完成。按冻结的事件接口和调度实现已纳入事件，未纳入功能保留排除。每个案例使用独立合法基线，并保持保留位输入/锁/模式/commit前置条件。

请只以本轮完整展开且SHA锁定的prompt、IR、policy、harness、接口为输入生成代码；不要读取历史模型得分或参考源码来构造答案。输出代码与实现的范围/排除说明；所有响应、重试、参数和版本由运行者原样归档。调用不在本步执行。
