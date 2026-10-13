# TMP126 v3.2 原始来源复核

任务：`tmp126-v32/source_review`；项目：`d2d-twin`；路线/阶段：`M/M4`。
本报告是来源专家建议，不能宣告 M4 或全项目正式生成输入通过。

直接阅读的是本地完整 TI TMP126 数据手册，SNIS209C，July 2021 / revised June 2022，共 49 PDF 页。印刷页 1–39 与 PDF 页对应。SHA-256：`6d9bab59b2814422d7bc1dff8fbd203df26e92ee40075b613c1f1fbb59eddfef`。复核正文 pp. 12–17、19–24、26–33，以及 p. 2 版本履历。对 pp. 2、17、27、29 的渲染图进行了人工视觉检查，确认冲突不是纯文本提取造成。

## 八字段关闭建议

“可关闭”仅指实现和独立验证满足以下限定条件后，可关闭原审校 REPAIR；并不将动态字段改为无条件静态 PASS。

| 字段 | 原文与位置 | 必须验证的非空状态与事件 | 关闭建议 |
| --- | --- | --- | --- |
| ALERT_STATUS.CRC_FLAG | p. 27 Table 8-7，bit 7 RC；p. 22 §8.5.2.5，失败写被丢弃并报 CRC fault | 注入已验证失败写事件后非零；合法单寄存器、无增量读先返回旧值，再清该位；其他 live 位保持 | 有条件关闭；真实 SPI/CRC 运算仍排除，其他事务清除行为保留来源冲突 |
| ALERT_STATUS.DATA_READY_FLAG | p. 28 Table 8-7，bit 0 RC；pp. 14–15 转换完成 | 完成转换后 DR=1，Status 限定读取后 0；Temp_Result 读取也跨清 DR | 有条件关闭 |
| ALERT_STATUS.SLEW_FLAG | p. 27 Table 8-7，bit 5 RC；pp. 12–13 §8.3.2/Fig. 8-3 | 连续模式两次已完成测量，正温差越过门限后 flag 非零；读清 flag，保留 live slew status | 有条件关闭；负 slew 数值、物理采样时间不评分 |
| ALERT_STATUS.THIGH_FLAG | p. 28 Table 8-7；p. 16 §8.4.4.1 | 已完成结果越过 high，flag/status 非零；读清 flag 而不清 live status；迟滞回落再产生事件 | 有条件关闭；门限边界取严格不等，避免等号歧义 |
| ALERT_STATUS.TLOW_FLAG | p. 28 Table 8-7；p. 16 §8.4.4.1 | 低于 low 后非零；读清 flag 而不清 live status；迟滞回升再产生事件 | 有条件关闭；p. 27 TLow_Status 描述误写 THigh_Limit 保留为冲突 |
| CONFIG.INT_COMP | p. 16 §8.4.4.1，Comparator→Interrupt 清整个 Status 并复位 ALERT；p. 29 Table 8-8，0 interrupt、1 comparator | 先有非零 RC 与 live bits，再执行 1→0，整个 Status=0、ALERT deassert；同值写不能代替转换验证 | 有条件关闭；编码依据 p. 29/p. 16，p. 17 首句相反编码保持未解决 |
| CONFIG.ONE_SHOT | p. 15 §8.4.3/Figs. 8-5/8-6；p. 29 Table 8-8 | 写 1 后 pending；读回始终 0；完成后新 TEMP、MODE=1、DR=1；pending 时重触发丢弃部分；AVG=1 等 8 次采样完成 | 有条件关闭；read-as-zero 本身不能当完成证据 |
| TEMP_RESULT.TEMP | p. 28 Table 8-7 Data_Ready_Flag；p. 26 Table 8-5 | DR 非零时读 TEMP，返回结果且仅跨清 DR，其他 RC/live bits 不应被该读清 | 有条件关闭；重复无增量 Temp_Result 多字读不支持，p. 21 §8.5.2.4 |

## 清除与事务条件

原文事实：Alert_Status 的 RC 位是 7、5、2、1、0，即 `0x00A7`。live R 位是 6、4、3，即 `0x0058`（pp. 27–28 Table 8-7）。合法读必须先返回清除前的值，再进行 RC 效果；不能把所有非零值直接当已读零。

原文事实：p. 27 §8.6.3 写明目前只有 single register read without auto increment 会清除。p. 19 §8.5.2.1 定义 CRC-enable、数据长度、auto-increment 等命令位，p. 21 区别重复单寄存器读与 burst。CRC 长度 1–10 有效；0 或 11–15 会忽略 CRC-enable。

限定抽象：保守安全评分范围为单字、无增量、显式事务元数据读取。将 burst/no-clear 用作本次候选策略的防越界测试可行，但不能将其升级为 SNIS209C 所有实际器件的无争议事实，因为版本履历与正文冲突。CRC 校验可以独立按 p. 23 Table 8-2 实现：poly `0x1021`、seed `0xFFFF`、无反射、xor `0`，command word 与 data block 都参与。但仅注入 `crc_valid=false` 是事件抽象，不是 CRC 算法或电气 SPI 测试。p. 13 仍禁止 CRC-enabled Configuration 写；保守排除，不能悄悄支持并称来源已证。

## 转换、温度与报警

原文事实：温度及 high/low limits 都是 bits 15:2 的 14-bit 二补码，LSB=1/32°C（pp. 26、31 Tables 8-5/8-10/8-11）。有符号整数 `q` 的寄存器编码为 `(q & 0x3FFF) << 2`。门限启用条件是 signed(high)>signed(low)；不满足时 temperature limits 被忽略，存储权限与告警功能仍应区分。Hysteresis 的每个字节是 unsigned，LSB=0.5°C（p. 32 Table 8-12）。可用整数温度单位：high 回落阈值=`high_q - 16*high_hyst_byte`，low 回升阈值=`low_q + 16*low_hyst_byte`。

原文事实：AVG=1 要把每次 measurement、包括 one-shot，平均八次 conversions（p. 29 Table 8-8）。来源未给最终编码在非整数格点上的舍入方法。验证应使用均值恰落在 1/32°C 格点的八个有符号样本；若实现用整数截断、四舍五入或其他策略，均须标为抽象选择而非厂家事实。不能仅验证“次数到了”却把最后一条样本当平均结果。

原文事实：shutdown 立即终止转换并丢弃 partial，不清已有 Alert_Status/ALERT（p. 14 §8.4.2）。SLEW_RESULT 非连续模式回到默认 0；计算需连续模式的连续两次测量（p. 26 §8.6.2）。正 slew 的比较需要固定间隔（p. 12）。本次手动输入采样事件与固定间隔属于逻辑层条件，不能声称验证了器件响应时间、模拟精度、供电或 0.5 ms reset 的真实计时。

原文事实：Interrupt 的 ALERT 由启用 flags 驱动；读 Status 清 flags 后 deassert，live statuses 可保持（p. 16）。Comparator 的温度/slew ALERT 对应启用 live statuses，读清 flags 不应让仍成立的 live limit 自动失效（p. 17、p. 30 Table 8-9）。DR 与 CRC 仍由对应 flags 驱动。对 enable-disable 的立即效果，不作无争议判定，详见冲突。

## 未解决来源冲突

1. `TMP126-C-REV-CLEAR`：p. 2 Revision C 履历声称移除 auto-increment not clearing status 限制，但 p. 27 正文仍明确 only single/no-increment clear。安全共同范围是单字无增量读确实清；其余分支保持候选策略/排除，不宣称官方勘误。
2. `TMP126-C-REV-CRC`：p. 2 称移除 CRC Configuration 写限制，p. 13 仍明文禁止。排除 CRC Configuration 写，不把正文选择解释成所有实际硬件确定事实。
3. `TMP126-C-REV-SLEW`：p. 2 称移除 negative slew limitation，p. 26 仍说负值不保证。只评分正 slew 和非连续归零；不评分负值数值。
4. `TMP126-C-INT-COMP-CODE`：p. 17 §8.4.4.2 首句把 comparator 写为 INT_COMP=0；p. 29 Table 8-8 明确 comparator=1，且 p. 16 interrupt=0。候选采用表格/p. 16 一致编码，保留冲突而非标官方更正。
5. `TMP126-C-ENABLE-DEASSERT`：p. 17 comparator prose 称 disable 立即 deassert；p. 30 §8.6.5 称当前已有 ALERT 需 status read 或新 conversion 才 deassert。仅验证这些事件后的稳定行为；不以立即边界为来源 PASS。p. 17 Figure 8-8 的线条也不能覆盖这项文字冲突。
6. `TMP126-C-TLOW-NAME`：p. 27 TLow_Status=1 描述写 below THigh_Limit，与字段标题、p. 16/p. 31 low 限制语义不一致。候选可采用低门限，明确推断修补而非官方勘误。

## 结论与唯一下一步

来源复核完成。八项 REPAIR 已给出可执行的限定关闭条件，尚未读取本轮最终实现及独立执行结果，不签署无条件通过，不修改原 IR、冻结测试或历史结果。唯一下一步：由编排器对上述八字段执行非零状态、事务/模式条件与事件重放验证，保留六项来源冲突，再决定限定准入。
