# 唯一下一步行动卡

- 当前阶段：方法应用路线M4，部分通过，正式生成输入NOT_ADMITTED。
- 下一动作：在独立新版本中修复并验证INA219的6个REPAIR字段／7个修订维度，包括BUS_VOLTAGE四字段的reset及RSV_2保留位策略、SHUNT_VOLTAGE.SV复位、CONFIGURATION.RST完成条件。
- 输入：`corpus/data/raw_pdf/TI/INA219.pdf`、`eval/independent_source_admission_20261012/field_evidence.json`、`candidate_ir/INA219_gold_ir.json`，已冻结旧档案只作方法参考。
- 验收：核对数据/状态复位与转换完成作用域，不能把动态结果当固定存储；以明确事件和合法输入验证CNVR/OVF及复位动作。保留保留位、转换/溢出与校准的未规定行为；来源、代码、故障检出、证据重放独立验收；不修改旧IR、冻结测试或历史成绩。
- 环境：本地Python/pytest及现有PDF足够，无需SCNet或采购硬件。

可复制提示词：

> 继续M4，在新的版本目录处理INA219的6个REPAIR字段和7个修订维度。先按原手册核对BUS/SHUNT结果复位、CNVR/OVF及RSV_2、RST的触发和完成边界，再实现数字事件原型与非零见证。使用项目内SCI-Skills独立核对来源与实现，检出合成错误、拒绝伪造证据并校验旧文件不变。保留未知和实际硬件时序边界，归档有界结论，最后只给一个下一步行动卡。
