# 唯一下一步行动卡

- 当前站：M4部分通过；正式生成输入NOT_ADMITTED。
- 下一动作：独立新版本推进LM83八个告警字段的条件read_clear规则。
- 范围库存：SR1.D2CRIT、D2RHIGH、LCRIT、LHIGH；SR2.D1CRIT、D1RHIGH、D3CRIT、D3RHIGH。
- 重要身份：冻结账本将这些字段overall标REPAIR，但其逐维没有REPAIR；access/read_clear/trigger_completion/conditional_write各标CONDITIONAL，其余为PASS。下一任务不得声称“八个REPAIR维度”；先固定原字段身份及选择的8条read_clear条件规则，其他24条条件规则仍保留未闭环。
- 输入：corpus/data/raw_pdf/TI/LM83.pdf、固定field_evidence.json与candidate IR。旧来源只限定库存，原手册重新作为事实依据。
- 验收：核对各状态地址读清的作用域、阈值／临界／高温故障仍存在时的保持或重触发、告警引脚与状态关系、复位及无来源行为；构造非零状态、跨地址读取及实际资格化事件，独立来源／实现／故障／证据拒绝／归档保全。不能从TMP461等同族／类似实现推断事实。
- 协作：Codex主任务单写入者；所有辅助代码与专家材料在独立sandbox。记录墙钟并保持11/15收口节点，不改Gold、旧Harness或历史分数。

可复制提示词：

> 继续M4，在新版本处理LM83的八个告警字段。先核对overall REPAIR与逐维CONDITIONAL的层级，固定原库存身份及8条read_clear条件规则，不创造REPAIR维度或更改旧账本。按原手册核对SR1/SR2各自读清、持续故障/解除后的条件、临界与高温状态及告警输出，再实现有界数字事件与非零见证；源内冲突和未知保留。使用SCI-Skills独立来源和实现审阅、合成错误检出、证据伪造拒绝，核对全部先前归档和sandbox依赖不变。辅助代码只写sandbox，由Codex单写入者整合，记录实际耗时，最后给一个下一步行动卡。
