# v41 实现审阅前固定验收清单

1. 八原字段overall REPAIR/0逐维REPAIR；本轮8条CONDITIONAL trigger_completion，另8条conditional_write不动。v39 read_clear/v40 access和C01–C04/U01–U02不自动关闭，不晋升Gold或历史分数。
2. 固定L→D2→D1→D3连续轮询，按对应通道采样→转换完成更新该通道数字结果、告警及pin。单采样不更新，不能设整轮完成屏障。早于末通道即可断言Local/D2/D1告警；只有对应通道合法完成可重置读清后标志。
3. 显式sample_id/round_index/slot_index为数字审计资格，不是硅片寄存器或物理转换信号证明。sample类型/位置/新身份及completion匹配先验证，错序/过期/重复/未采样/类型混淆原子拒绝；合法commit恰好一次。
4. 样本温度在sample时保存，只在commit更新values/completed/status/pin。commit不能携带新温度覆盖sample；last_completion记录当前样本与对应已提交值。快照资格/pending都保持可审计，失败事件不部分改变。
5. 同地址读清、field读取消费与软件writeguard仍沿用冻结v39/v40；读/拒绝写不充当转换。读取可以发生在sample与complete间，clear/unknown及引脚保持按原profile继承，不擅自闭合read-before-recovery历史。
6. common_source持续CRIT读取后unknown，只有对应明确超温completion重新已知；另一通道completion/仅sample不解析该位。HIGH>与CRIT>断言，HIGH<=退役后读、CRIT<退役后读；CRIT等值与ack历史继续来源边界。
7. 保留SR1 A8、SR2 48。多通道故障pin聚合不因读消失；OPEN、动态屏蔽/配置、停转换/复位、主机trigger寄存器、ADC/物理总线/失败读不实现也不声称认证。
8. 时间仅来源元数据：460typ TA25 /600max额定TA/TJ VCC3.0–3.6；正文approx480round/120channel/60从采样到完成更新，local与remote均纳入原文。无elapsed_ms运行、无最短重置高间隔/无普适0..600ms保证；Note10lastconverteddata可读不等于host资格令牌。
9. 全部代码/测试/专家资料在sandbox/lm83_v41；旧v39/v40哈希校验后同一字节buffer编译，禁旧目录字节码；eval仅证据。执行-B/PYTHONDONTWRITEBYTECODE/no pytestcache，源/依赖/清单/库存前后哈希一致。
10. 独立行为来源预期、实执行变异探针、精确源字节与typed事件回放准入分开；缺真实见证PARTIAL，伪造来源/旧依赖/源意见/身份/温度/phase/profile/timing/trace/类型REJECTED，确定回放不替代行为oracle。
