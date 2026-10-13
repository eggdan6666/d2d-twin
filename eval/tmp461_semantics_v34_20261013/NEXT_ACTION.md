# 唯一下一步行动卡

- 当前阶段：方法应用路线M4，部分通过，正式生成输入NOT_ADMITTED。
- 下一动作：在独立新版本中实现并验证LIS3DH的8个REPAIR字段／8个修订维度，其中CTRL_REG4.ST为access，其余7个STATUS_REG字段为reset。
- 输入：`eval/independent_source_admission_20261012/field_evidence.json`、`candidate_ir/LIS3DH_gold_ir.json`、原审校记录指向的LIS3DH官方本地手册；原始IR与此前独立审校材料只作历史背景。
- 验收：核对自检位访问与非法编码、上电/输出数据准备状态及未知值，实施资格化新样本、受控数据读取、ready/overrun条件；不可通过改写冻结测试或填零制造通过。来源、实现、合成故障和证据重放分别独立验收，整字段晋升保持受准入门控制。
- 环境：本地Python/pytest和现有文件足够，不需要SCNet或购买传感器。

可复制提示词：

> 继续M4，在新版本目录处理LIS3DH的8个REPAIR字段和8个修订维度。按原手册核对CTRL_REG4.ST访问和STATUS_REG的ready/overrun复位作用域，建立数字事件模型及非零见证，使用项目内SCI-Skills独立核对来源与实现，检出合成错误并拒绝损坏证据。保留未知、非法编码和未实施硬件行为，不修改旧IR、冻结测试或历史成绩。归档有界验收结果，最后只给一个下一步行动卡。
