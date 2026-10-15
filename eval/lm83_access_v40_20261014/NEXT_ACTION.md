# 唯一下一步行动卡

- 当前站：M4部分通过；v40八条access有界验收，原CONDITIONAL状态不变，Gold/正式生成仍NOT_ADMITTED。
- 下一动作：v41单独选择LM83同八字段的8条CONDITIONAL trigger_completion规则，固定原身份及资格化转换条件，不从v39/v40的软件事件成功推断硅片时序。
- 仍保留：另外8条conditional_write未选；v39读清/v40访问原CONDITIONAL与C01–C04/U01–U02未知不自动关闭。
- 验收：原厂采样→转换完成→对应状态与引脚更新、轮询顺序及持续/退役故障边界；严格区分460typ/600max规定工况、约480整轮及约60ms采样至更新。非零事件、未完成/错序/重复资格拒绝、独立源/行为/故障/证据拒绝及旧依赖保全。
- 执行：根任务唯一Single Writer；所有辅助代码/测试/专家资料只在新的sandbox；新eval仅证据归档。不改旧档、Gold、Harness、账本或历史分数；完整墙钟记录，11/15范围收口保持。

可复制提示词：

> 继续M4 v41，固定LM83同八字段的8条CONDITIONAL trigger_completion规则，保持overall REPAIR/0逐维REPAIR身份。依原厂与固定驱动核对采样、对应通道转换完成、状态/pin更新和轮询条件，继承v39/v40及C01–C04/U01–U02未知，不把事件模型或典型时间当硅片实测保证。只在新sandbox实现与独立来源/行为/实际故障/证据拒绝验证，由根任务单写入者整合新eval。另8条conditional_write和旧档不动，不晋升Gold、不改历史分数；记录完整墙钟，输出一个下一步行动卡。
