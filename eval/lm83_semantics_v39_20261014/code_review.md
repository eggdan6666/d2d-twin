# LM83 v39 独立实现验收

## Scope and inputs

固定清单及原始 PDF §1.2–1.3、Figures4–7、§2.3 独立核对。SR1：LCRIT0、D2CRIT1、D2RHIGH4、LHIGH6；SR2：D1CRIT0、D3CRIT1、D3RHIGH4、D1RHIGH7。所有代码、测试和输出仅写入本专家 sandbox。

八字段 overall REPAIR；逐维 REPAIR=0；选定八条 read_clear CONDITIONAL；其他24条保留。固定 HIGH70、共享 CRIT90、未屏蔽测试设置明确不代表 POR。

## Specialist findings

有界实现 PASS。独立非零预期验证 SR1=0x53、SR2=0x93，地址局部读清、读前值、持续故障多地址聚合引脚保持、对应通道完成才重置高、单独采样不更新、错误/重复/过期/畸形事件原子拒绝、A8/48保留掩码、HIGH/CRIT阈值边界。

common_source 对持续 CRIT 读后提供未知位；下一次明确超温对应完成恢复已知置位。已退役转换→所在寄存器读取的八条来源交集规则单独检验。CRIT等值保持仅为保守配置；恢复前读取历史不作闭环认证。

## Evidence and execution status

最终 **169/169通过**：101行为/边界测试、19实际执行代码变异（全部检出）、49准入测试。其中20条逐一缺失真实见证返回 PARTIAL；内容/类型伪造（False vs 0，0.0 vs 0，NaN）与6类真实来源字节修改返回 REJECTED。20场景380步是数字事件见证，不是物理或模型样本。

最终 pytest 8.22秒；运行器总9.68秒。执行前后实现三文件、独立来源审阅、冻结清单、账本和原来源哈希一致。JUnit、日志及命令见 execution_manifest.json。

首轮161项158通过、3失败为审阅测试自身缺陷：两引脚变异仅清SR1时被SR2持续热故障聚合掩盖；来源工况补充后精确元数据字典需更新。修正探针为两地址读取，保留首轮记录；没有为此修改实现。

## Three reviewer lenses

贡献：来源约束、精确库存与独立测试形成可审计闭环；不得将其写成八个REPAIR维度或整字段提升。

方法：C01原厂内部冲突、C02 CRIT等值、C03读取/恢复顺序、C04延迟泛化均未解决。请求 Figure 解释和来源交集范围分开保存是有界准入所需。

表述：460ms typ、600ms max携带工况；480ms/120ms/采样后60ms为正文近似。没有真实墙钟转换、GPIO或硅器件测量，不能承诺普适0..600ms重新置位。

## Deliverables

test_independent.py、run_review.py、package_review.py、最终与首轮 JUnit/日志/执行清单、原厂图示页渲染、完整专家合同 code_review.json。

## Limitations and risks

正式建议 **REPAIR**，整体 readiness NOT_READY；有界实现 PASS 可整合。全部四项来源冲突保留。OPEN、写配置、阈值动态更改、实际I2C竞争/中止读取和模拟ADC不在运行接口内。没有核内编译、外部API、第三方模型调用或硬件执行。

## Quality checks

完整专家合同版本1.0、身份 lm83-v39/code_review、来源和执行证据分层、前后哈希、不越界写入与不改变SCI阶段权限均已检查。源审阅仍为独立上游，不将回放相等替代独立行为预期。

## One next action

由 Single Writer 整合有界条件验收并保留四项来源冲突，再核验受保护输入及归档哈希。
