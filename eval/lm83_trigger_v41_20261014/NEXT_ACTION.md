# 唯一下一步行动卡

- 当前站：M4部分通过；v41八条trigger_completion有界验收，全部原CONDITIONAL保留，正式输入NOT_ADMITTED。
- 下一动作：v42单独固定LM83同八字段的8条CONDITIONAL conditional_write，首先审查合法写入口及维度适用性。原厂状态RO/无data-write别名，不可虚构W1C/W0C/host trigger或非法写silicon no-op。
- 继承：v39读清、v40访问、v41转换资格及C01–C04/U01–U02完整保留；软件writeguard已有证据不代替物理写/ACK结论。若无合法字段写条件，只能给有来源的有界适用性/排除候选，原账本不自动改N/A/PASS。
- 验收：原厂command选读与data-write分开，固定Linux公开hwmon与底层regmap区别，非零/pending/unknown状态软件guard保护与证据伪造拒绝，独立来源/行为/故障验证与全旧档依赖保全。
- 执行：根任务唯一Single Writer；所有辅助代码/测试/专家资料只在新sandbox，新eval只归档证据；不改Gold/账本/Harness/旧档/分数，完整墙钟记录，11/15范围收口保持。

可复制提示词：

> 继续M4 v42，固定LM83同八字段的8条CONDITIONAL conditional_write，保持overall REPAIR/0逐维REPAIR。先按原厂状态RO、命令地址与固定Linux驱动核对合法写入口和维度适用性，不虚构W1C/W0C/host trigger或非法物理写no-op/ACK。继承v39/v40/v41及C01–C04/U01–U02全部边界，软件guard与物理行为分层；若无合法写条件，仅给有界适用性候选，不改旧账本。全部辅助代码/测试/专家材料在新sandbox，根任务单写入者整合新eval并独立源/行为/实际故障/证据拒绝与全旧档保护。不晋升Gold、不改历史分数，记录完整墙钟，输出一个下一步行动卡。
