# INA3221 v38 有界语义任务

协议 `3.8-ina3221-20261014`；原账本三字段／三维度：CONFIG.RST.trigger_completion、MASK_ENABLE.CVRF.read_clear、MASK_ENABLE.TCF.read_clear。M4仍未全面通过，不准入正式生成上下文。主任务单写入者整合；所有辅助工具、测试和专家材料在 `sandbox/ina3221_v38/`。

归档前执行 `python -B sandbox/ina3221_v38/run_task.py` 产生实际见证。归档后只读，用 `python -B sandbox/ina3221_v38/verify_archive.py` 验证哈希；`--replay` 仅在内存重放。独立pytest精确命令、JUnit和被测输入哈希见独立执行清单。

## 来源与解释边界

用户持有的原TI SBOS576C（revised September2026）50页PDF为事实权威；旧字段账本只限定库存身份。19条原文／冲突／协议声明和8项保留冲突见source_review。原始实现前清单保存在code_acceptance_checklist；实现已经存在后的来源澄清另存source_clarification_checklist与supplement，不倒签。

`read_masked` 是一次完整16位寄存器读取后的投影；清除前快照、随后作用及无事件穿插是线性化协议约定，不是部分字节清除或真实I2C竞态证明。未知位mask=0不是位值0；含未知位的观察在评测入口拒绝。

- RST请求与完成分开；后者绑定最新request_epoch，等值重请求也有新代际。pending数值观察拒绝。PV逻辑输出在software reset保持直到资格化检测完成，不推所有引脚等同POR；该历史的PVF数值关系标未知。
- 配置启用集合、模式、AVG和conversion time由configuration_epoch绑定；结果及完成事件另绑定sequence_id。所有六种active MODE与七种非空通道组合可验证。禁用通道不等待，空集合不能假通过。
- `qualified_filtered_result` 供给已经处理的对应寄存器输出，strict boolean表明处理完成。每个转换结果即时更新该对应寄存器，全当前选定信号完成才置CVRF。p16的递归滤波不实现为“等AVG个整轮”；实际滤波算术、舍入及物理处理时间均未实现。
- CONFIG写MODE0/4保留此前CVRF已知／未知；active且all3-enabled可清0。任何partial／all-disabled选择的CONFIG写清行为标UNKNOWN，保持未定义disable-mode的来源歧义。资格化已启用集合完成可再确定1，MASK读独立确定0。
- TC从默认启动环境的CH1阈值资格化事件开始，随后四个默认三通道完整周期的CH2未达事件可形成逻辑TC-low状态。cycle_index须为下一唯一周期，startup_epoch须当前；仍无法证明注入事件来自四个不同真实周期。
- 早期CONFIG写取消TC直到powercycle／software reset重新建立启动代际；读取／写控制MASK不重启TC。common_source的TCF数值reset及故障极性均未知，不把TCpin-low推成已认证flag0或flag1。
- bitmap_pin_candidate和bitmap_active_high_candidate是互相区分的来源条件候选；其default1来自header／bitmap，与11h文字冲突仍保留。候选非零TCF读取用于协议区分，不认证真实TCF极性。
- 0Eh sum-limit默认及访问有原文冲突，整个支撑oracle隔离；不据旧IR／reference选一段原文。普通TCF／CVRF的R/W持久性、非零status/reserved写、SUM数据路径、阈值算法、实际PV/TC电气、28.6ms及模拟采样均排除。
- 支撑PV检测事件只准当前默认配置／默认limit、明确完成资格化的逻辑输出；PV limit写入要求对齐且sign0。它不测量电压或证明阈值检测硬件。

OutsideContract表示评测范围拒绝，不是硅片异常行为。六种配置组合之类的测试重复、元数据表与合成错误不能计为新芯片样本、独立来源事实或模型实测缺陷。所有whole_field_promoted和whole_dimension_closed保持false。
