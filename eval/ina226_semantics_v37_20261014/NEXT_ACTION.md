# 唯一下一步行动卡

- 当前阶段：方法应用路线 M4，部分通过；正式生成输入 NOT_ADMITTED。
- 下一动作：在独立新版本处理 INA3221 的 3 个 REPAIR 字段／3 个修订维度。
- 输入：`corpus/data/raw_pdf/TI/INA3221.pdf`、固定来源账本 `eval/independent_source_admission_20261012/field_evidence.json` 和对应 candidate IR。
- 范围：CONFIG.RST.trigger_completion；MASK_ENABLE.CVRF.read_clear；MASK_ENABLE.TCF.read_clear。
- 验收：原页核对复位完成、已使能通道转换／平均的完成条件、CVRF 的读取／写入清除条件，以及 TCF 的非读清、power-cycle／software-reset 重初始化边界。不能把同族 INA226／INA219 实现当来源，也不能将数字事件当实际时序；保留原手册矛盾与未知。独立来源、代码、故障检出、证据拒绝与旧文件保全均需执行。
- 协作：Codex 单写入者；专家／外部辅助代码只在独立 sandbox，主任务整合。11/15 仍是有界范围收口目标。

可复制提示词：

> 继续 M4，在新的独立版本处理 INA3221 的 CONFIG.RST、MASK_ENABLE.CVRF、MASK_ENABLE.TCF 三个 REPAIR 字段／三个维度。先按原手册核对复位请求与完成、已使能通道转换及平均过程、CVRF 清除和 TCF 的非读清及断电／软件复位重初始化条件，再实施明确范围的数字事件原型与非零见证。使用 SCI-Skills 独立审阅来源和代码，检出合成错误、拒绝伪造证据，并核对旧 IR、冻结 Harness、历史成绩和全部先前归档材料不变。保持主任务单写入者，辅助代码只写独立 sandbox，保留未知和物理边界，记录实际工时，最后给一个下一步行动卡。
