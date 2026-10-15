# LM83 v40 CONDITIONAL access 有界准入

结论：同八字段的八条 **CONDITIONAL access** 软件访问契约有界验收通过。overall REPAIR保持，逐维REPAIR=0；v39八条read_clear及C01–C04原记录继承，其他16条trigger_completion/conditional_write保持未闭环。整字段/整维度晋升均为0，M4仍部分通过，正式输入NOT_ADMITTED。

## 冻结范围与原厂依据

SR1 0x02：D2CRIT[1]、D2RHIGH[4]、LCRIT[0]、LHIGH[6]；SR2 0x35：D1CRIT[0]、D1RHIGH[7]、D3CRIT[1]、D3RHIGH[4]。保留位分别A8与48，OPEN未计入本轮。target_fields为冻结账本逐记录副本，scope_freeze列明16未选规则。原厂§2.3明确Read Only，§2.1无SR写别名；§1.9写command byte用于选择读地址，不等同写状态数据。

RO定义为软件接口不能修改状态存储；温度转换与读清仍可改变观测。**冻结转换也不能保证两个消费性读值相同**。本轮不使用连续读相等作RO oracle；状态诊断snapshot只供证据与测试，不伪称非消费性物理读接口。

## 软件与物理接口边界

write_status只接受严格typed地址02/35与0..255 byte，返回RO_REJECTED、storage_write_applied=false，全部状态不变：flags、unknown、温度、引脚原因、待完成采样身份、已消费身份和转换计数。此规则是有界软件保护契约。非法物理status data-write的ACK/NACK/ignore未知（U01）；失败物理读的进度及侧效未知（U02），没有板测或总线仿真。

固定Linux commit的lm83_temp_read对告警每次regmap_read整字节SR再掩码；volatile防止缓存替代真实读取。read_field相应消费所在整个SR，影响同地址兄弟字段，不改变另一SR。known_mask未覆盖字段时返回known=false/value=null，绝不把CRIT未知投影为0。已知返回携带原始读前字节及掩码。

Linux公开hwmon alarm/aggregate权限0444，lm83_temp_write只处理max/crit，其他EOPNOTSUPP；regmap_config没有writable_reg回调，底层regmap_reg_write默认透传SMBus写，**不能声称任意底层写都被驱动拦截**。聚合lm83_chip_read依次SR1→SR2，不是原子快照；第一读成功第二失败没有软件回滚。失败物理事务实际消费副作用不由代码推断。本原型只执行成功读与软件guard，不模拟驱动错误、并发或总线ACK。

## 实施计划、原型功能清单与流程文档

新实现与测试仅位于sandbox/lm83_v40。access_model.py为软件guard及消费性字段访问壳，校验v39运行时SHA256后编译同一字节缓冲区再继承，旧目录不产生字节码。旧转换、读清、pin与unknown模型不改；固定HIGH70°C/CRIT90°C测试设置及两种profile沿用。scenarios.py生成非零访问见证；admission.py独立钉住原资料、备忘录、账本、v39运行时/源意见与新源意见字节，校验精确类型的事件和回放。

执行流程：冻结旧档/库存→独立来源审阅与sandbox候选构建→来源意见钉住→独立源码预期/变异/证据拒绝验收→根任务整合→字节保全→双manifest封存。原型资源为固定本地资料与现有Python，不调用模型或第三方API。风险备选是保留CONDITIONAL/UNKNOWN和不晋升Gold。没有图位需要，未制作流程图。

## 测试准备材料与实际验收

最终独立pytest **255 passed，0失败/错误/跳过**：168项独立行为/边界、26项实际合成代码故障检出、61项准入/伪造拒绝。最终套件8.92秒；输入前后哈希等于当前最终字节。以independent_code_results.xml、日志及执行清单为证，专家只写自己的sandbox；根任务独占eval及项目状态整合。

22场景/662事件步：16逐字段×来源profile场景、4同地址兄弟消费场景、2跨地址间隙转换场景。覆盖非零拒绝写、全零拒绝置位、待转换与未知状态保护、字段消费、跨地址隔离及转换后读值变化。准入缺失真实见证为PARTIAL；内容/类型/profile/事件/来源意见及源字节伪造REJECTED。回放仅验证证据一致性，独立预期负责行为依据。测试/事件/合成故障不是硬件或模型样本。

## 未知保留、保全与排期

C01–C04逐记录与v39源意见一致：持续CRIT读清图文冲突、CRIT等值历史、ack顺序、普适600ms重置高推导边界仍未解决。source_review保留原厂/驱动/软件契约/推断层级，U01/U02单列。v39时间元数据（460typ/600max规定工况、约480整轮、采样至更新约60ms）仅沿用，不声明新的物理证据。所有原条件状态保留，不把本轮通过写成整芯片物理状态机已闭合。

**14,439个保护输入全部不变**，包含前次14,341个与v39全部main payload/manifest/sandbox依赖。Harness MD5 `8cf0854d4779467bc8e472ee4fb97023`一致，正式Gold与历史分数未改。eval无辅助Python或字节码；main与sandbox分别封存。复验命令：`python -B sandbox/lm83_v40/verify_archive.py --replay`。

保护快照启动至最终字节验收完整墙钟 **12.05分钟**，含全部等待，不是净编码工时或人时；更早规划及后续报告/封存未计入。worklog记录UTC/上海时间戳和最终套件用时。11/15收口节点不变，本轮不推导全20芯片工期。

唯一下一步行动卡见NEXT_ACTION.md。
