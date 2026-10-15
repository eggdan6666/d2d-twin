# v40 实现审阅前固定验收清单

1. 固定八原字段、overall REPAIR、0逐维REPAIR；本轮仅8条CONDITIONAL access，另外16条 trigger_completion/conditional_write未闭环。v39八条read_clear仍CONDITIONAL，C01–C04继承，不晋升整字段/整维度，不改Gold/分数。
2. 原厂02/35是Read Only，无状态data-write别名；§1.9的写command byte可用于选择读取地址，不等同写状态存储。动态RO不意味重复读取相同，停止转换也不取消读清副作用。
3. write_status是有界软件存储保护接口：typed address02/35与typed byte0..255，拒绝存储写且所有状态保持（包括flags/unknown/qualified temperatures/pins/pending sample/usedids/counter）。这是软件策略，不代表物理写ACK/NACK/ignore事实；后者UNKNOWN。
4. Linux lm83_temp_read每次读whole SRx再mask字段；alarm属性0444、lm83_temp_write只允许max/crit，其他EOPNOTSUPP。lm83_regmap_config无writable_reg统一保护；底层write default透传，因此不能声称任意regmap/I2C写都被驱动拒绝。
5. read_field一次调用整体读且消费所在SR；同地址其他告警受影响，另一地址保持。八字段映射明确，nonzero→消费后再读，qualified conversion→再置位可变；不使用“RO连续读相等”oracle。
6. common_source持续CRIT位UNKNOWN时read_field返回known=false/value=null，不能把未知投影为0；HIGH及保留位仍可知。已知字段的raw_preclear_read应保留全字节与knownmask。
7. 保留v39状态机（SHA256钉住旧实现再导入）；仅对应通道完成重置位，采样/拒绝写/另一地址读不替代转换；错序失配和重复事件仍拒绝。SR1 A8/SR2 48保持0，OPEN不计入八字段。
8. 双地址读取为两个操作，可在间隙插入转换，禁止原子快照或事件丢失率推断。真实总线失败/并发/ACK/采样时间不模拟；已知驱动第一读成功第二失败不回滚的代码边界记录，失败读物理侧效未知。
9. 所有辅助代码与测试只在sandbox/lm83_v40；eval只证据整合。执行-B、禁字节码和pytest缓存；源码、旧依赖、来源意见、冻结清单、target/scope输入前后哈希保持，记录JUnit实际结果。
10. 独立来源预期、实执行代码变异、非零见证与准入伪造拒绝分开。缺失真实见证PARTIAL；类型/内容/profile/事件/元数据伪造或来源/旧依赖/独立意见字节改动REJECTED。回放只验证证据一致性，不能替代行为验收。
