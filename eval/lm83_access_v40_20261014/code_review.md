# LM83 v40 access 独立实现验收

## Scope and inputs

独立读取原厂 PDF §1.9、§2.1、§2.3及固定467行Linux源文件。八字段地址/位号从原厂表独立转录，未导入实现映射作oracle。固定根任务预审清单与最终独立来源意见先于最终执行核对。写入仅 sandbox/lm83_v40/code_review。

八字段 overall REPAIR；逐维REPAIR=0；只选八条CONDITIONAL access。旧八条read_clear、C01–C04和其余16条件规则保持。整字段、整维度不提升。

## Specialist findings

有界实现 **PASS**。动态RO代表软件存储写保护，与硬件转换/消费性读相容；重复读不要求相等。所有八字段均验证非零映射、read_field先读取整个SR再投影、同地址兄弟字段被消费、跨地址不消费、原始读前字节与known_mask保留。

软件write_status在零、非零、未知位、未完成采样四类状态下保持完整快照不变，包含flags、unknown、温度、引脚cause、pending、used_ids及计数器；typed输入和严格schema拒绝原子保持。持续CRIT未知投影为known=false/value=null。仅对应合格转换完成再置位，单独采样与拒绝写不能替代转换；继承资格条件和SR1 A8/SR2 48掩码。

Linux公共alarm属性0444及temp_write不支持alarm是软件路线约束；regmap_config没有writable_reg，底层default透传。不得把适配器guard写成任意regmap/I2C写的原厂拒绝、ACK/NACK或no-op事实。

## Evidence and execution status

最终首轮 **255/255通过**：168行为/边界测试、26实际执行适配器代码变异（全部检出）、61准入测试。准入含22逐一缺失真实见证→PARTIAL、30内容/类型/未知抹除伪造→REJECTED、8实际来源/旧核心/独立意见字节替换→REJECTED、1真实见证接受。

22场景662步为数字事件见证；不是硅器件、模型生成或独立物理样本。pytest8.04秒，完整运行器8.921470秒。JUnit记录255项无失败；命令、UTC起止和16输入前后SHA256在execution_manifest.json。执行前后三实施文件、旧核心、前后独立意见、原厂/驱动/备忘录、账本、冻结清单、target/scope和测试源码均一致。没有实施代码修复或首轮失败。

## Three reviewer lenses

贡献：精确条件库存和来源约束、独立验收形成有界审计证据；没有足以推进整M4或Gold的依据。

方法：保留C01–C04；持续CRIT来源冲突、等值历史和时间泛化没有解决。软件guard和物理写行为严格区分。原厂RO不能支持消费性读取后的稳定性oracle。

表述：双寄存器读取是两个操作，间隙可插入转换；实际Linux第二读错误不会回滚第一次成功读。未模拟失败物理读进展/副作用，不量化事件损失率，不声称原子硬件快照。

## Deliverables

独立test_independent.py、run_review.py、package_review.py、JUnit、日志、执行清单、完整专家合同code_review.json及本报告。实际字节故障副本保留在本sandbox/source_faults，用于复核，保护原文件未改。

## Limitations and risks

正式建议 **REPAIR**；有界实现PASS，整体NOT_READY。继承四个source冲突及两个access UNKNOWN边界：非支持物理写ACK/副作用、失败物理读进展/副作用。未执行真实总线、GPIO、硅器件、内核编译或第三方模型；软件畸形事件原子拒绝不证明物理失败读无副作用。

## Quality checks

完整专家合同1.0、身份lm83-access-v40/code_review、来源/执行/推断分层、实际JUnit与哈希、独立source oracle、实执行变异、严格写入范围、无阶段推进均核对。证据回放相等仅为一致性检查，不替代168个独立行为/边界预期。

## One next action

由 Single Writer 整合八条access有界证据，保留条件身份与未知边界，再核验归档和全部受保护文件哈希。
