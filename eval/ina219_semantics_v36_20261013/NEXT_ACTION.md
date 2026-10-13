# 唯一下一步行动卡

- 当前阶段：方法应用路线M4，部分通过；正式生成输入NOT_ADMITTED。
- 下一动作：在独立新版本中处理INA226的6个REPAIR字段／6个修订维度。
- 输入：`corpus/data/raw_pdf/TI/INA226.pdf`、固定`eval/independent_source_admission_20261012/field_evidence.json`与`candidate_ir/INA226_gold_ir.json`。
- 范围：CALIBRATION.UNNAMED_15、CONFIG.UNNAMED_14_12和MASK_ENABLE.UNNAMED_9_5的访问属性，CONFIG.RST的触发完成条件，以及MASK_ENABLE.AFF／CVRF的读清条件。
- 验收：先核对原页默认值、保留位与读清／锁存／转换事件的条件，再做非零状态和交叉读取见证；独立审查来源与代码、检出合成错误、拒绝伪造证据、核对旧文件不变。没有来源支持的行为继续保持未知。
- 环境：现有本地Python、pytest及PDF足够，无需SCNet或采购硬件。

可复制提示词：

> 继续M4，在独立新版本处理INA226的6个REPAIR字段／6个修订维度。按原手册核对三处保留字段访问、RST完成条件及AFF/CVRF的读清、锁存、转换完成边界，再实现明确条件的数字事件原型与非零见证。使用项目内SCI-Skills独立审查来源与实现，检出合成错误、拒绝伪造证据并校验旧IR、冻结测试、历史成绩和所有已归档材料不变。保留未知与实物时序边界，完成有界验收和归档后，只给一个下一步行动卡。
