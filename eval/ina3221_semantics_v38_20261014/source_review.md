# INA3221 v38 独立来源精读卡

范围：仅 CONFIG.RST/trigger_completion、MASK_ENABLE.CVRF/read_clear、MASK_ENABLE.TCF/read_clear 三字段三原始待修维度。来源为用户已有 TI 完整 50 页 PDF，SHA256 `6ef5bf2263e34332fce7ea2547d9824ff5d3900418d51d59e5e3b711dcdc98d0`。精读及完整页视觉检查：11-16、18、24、26-27、33-35。台账仅用于范围库存，不作为事实来源。未读、运行候选实现。

修订记录：2026-10-14 04:21:06（Asia/Shanghai）作来源澄清；此时主控已有实现，专家仍未读或运行实现。此前仅排除全部禁用的建议偏窄，现明确包含部分禁用／子集选择。原预实现清单原始字节另存 `preimplementation_checklist_original.md`；修订清单为后续来源补充，不倒签为完整预实现证据。

## 1. Bibliographic position

原文事实：TI INA3221，SBOS576C，May 2012，revised September 2026。器件数据手册而非研究论文；以下十六节适配为可审计字段语义精读。来源版本、页码、位图及正文全部保留，不认证整字段。

## 2. Research question

AI分析：如何将复位请求/完成、转换完成/读清、TC 监控/非读清拆成来源约束的有界接口，并保留未知与矛盾，而不是凭自然语言生成完整器件保证？

## 3. Background route

原文事实：p.11 §7.3.1，测量跳过禁用通道；模式选择分流/总线/两者；单次或连续。p.26 §8.2.1，配置写中止进行中的转换并使用新配置重启；配置读不影响设置和转换。

## 4. Unresolved pain point

AI分析：主要风险是将 self-clears 写成任意时刻读零；将所有通道理解成固定三路；将 AVG 推成 N 次完成等待；将 TC 低有效引脚与 TCF 常规高有效故障位混同；将泛化读清正文覆盖字段例外；将同样 POR 表述覆盖 PV 引脚保持例外。

## 5. Core insight

AI分析：可信性来自明确的可验证公共子集及排除集。必须声明哪些是制造商事实、哪些是协议选择。事件可信不等于物理时间可信，字段局部验收不等于整字段晋升。

## 6. Method overview

执行事实：核对 PDF 50 页和哈希；pypdf 提取相关完整页，Poppler 120 dpi 渲染；人工视觉检查完整页面，包括表格、页脚、图注及 Figures 7-4、7-5。额外读取 p.16/18/24，防止 AVG 和支撑寄存器的误读。所有文件只写来源审阅 sandbox。

## 7. Module or mechanism logic

- RST：写 1 请求系统复位，完成后寄存器恢复已定义默认且 RST 自清（p.26 Table 8-4）。p.15 §7.3.3 限定 PV 输出保持直到 power-valid sequence 完成。等待期的读值/最大时延不明确。
- CVRF：所有启用通道及选定信号转换完成后置位，读 MASK 清除（pp.11/35）。配置写清具有 powerdown 例外；p.35 还加入未明确映射的 disable-mode。MODE 0/4 是 powerdown（p.27）。disable-mode 不能按来源擅自限制成全部禁用；部分禁用／子集选择的精确配置写清同样未确定。普通 CONFIG 写：活动 MODE 且三通道全启用可清为 0；活动 MODE 且 CHen!=0b111（含部分、全部禁用）将 CVRF 已知性标 UNKNOWN，不认证清0或保留1；MODE0/4保留此前已知／未知状态。随后合格的非空启用通道全转换完成可重新确定1，MASK读取确定0。UNKNOWN 是保守准入边界而非芯片产生未知值的宣称。
- TCF：TC 引脚 p.14 Fig.7-4 明确正常高、失败低；p.34 TCF 默认高、对应引脚且 asserted 后不清除至断电/软件 reset，表述存在极性/锁存歧义。TC 监控只在上电/软件复位开始，序列未完成前写 CONFIG 会禁用至新 cycle/reset（p.15）。MASK 读取不可独立清 TCF；不能因此认证故障后位值。

## 8. Essential formulas and assumptions

原文事实：p.16 §7.4.1/Fig.7-5 可写为 `y_new = y_old + (x_new - y_old)/N`。x_new 为相应通道本次新测量，y_old/y_new 为更新前后输出，N 为 AVG 对应 1/4/16/64/128/256/512/1024。原文是每次转换递归更新，并未定义 CVRF 等待 N 完整通道轮次。整数舍入、内部精度及噪声结果不在本任务确定范围。

协议假设：completion event 带当前 epoch、sequence、配置、启用通道集合、选择信号及 AVG 身份；确认全部必要测量与该配置的平均处理完成。此元数据防止陈旧/重复/部分事件，并不认证 N 个样本或物理时间。禁用集合不得空集真值自动完成；此为保守协议选择，精确 silicon 全禁用状态仍未知。复位请求/完成两个边界；等待态读回未知。

## 9. Data, cohort, material, or benchmark

来源材料只有原 PDF 与范围库存。没有板级观测、时序仪器、仿真硅模型或制造商澄清。哈希及文本/图片 manifest 留档。目标三字段三维度为固定范围；其他寄存器仅作依赖约束。

## 10. Experimental design, metrics, and baselines

未执行候选实现或硬件实验。独立核验设计在 checklist 中预先固定：正/负事件、相同模式重复触发、连续序列、读操作作用域、复位阶段、TC 默认条件/取消/重启、源冲突隔离。不得使用旧金标作为来源裁决。将来报告协议检查结果与排除数，不把 API 事件验证标成芯片物理测量。

## 11. Experiment-to-claim evidence table

| 来源声明 | 精确定位 | claim ID | 可验收边界 |
|---|---|---|---|
| RST=1 请求复位，默认0且自清 | p.26 Tables8-3/4 | INA3221-RST-01 | 完成边界，等待期排除 |
| 软件复位保持 PV 引脚 | p.15 §7.3.3 | INA3221-RST-02 | 不承诺引脚立即 POR 等价 |
| 0Eh 支撑默认/访问矛盾 | pp.24/33 Tables8-1/31/32 | INA3221-RST-04 | 排除 0Eh 全默认/可写断言 |
| CVRF 所有转换完成、MASK读清 | pp.11/35 | INA3221-CVRF-01/02/03 | 启用集合及所选信号 |
| CONFIG重启、MODE0/4停机 | pp.26/27 | INA3221-CVRF-04 | 当前配置身份，停机无完成 |
| disable-mode 额外例外未定义 | pp.11/35 | INA3221-CVRF-05 | 活动MODE的部分／子集及全部禁用写清未知 |
| AVG递归滤波 | pp.16/18/26 Fig.7-5 | INA3221-CVRF-06 | 不推 N-cycle CVRF |
| TC引脚高/故障低 | p.14 Figs7-3/4 | INA3221-TCF-02 | 默认条件约束，引脚与位分离 |
| 早期 CONFIG 禁用 TC | p.15 | INA3221-TCF-03 | cycle/reset 重启 |
| TCF特例非读清 | p.34 Table8-34 | INA3221-TCF-04 | MASK读不可单独清TCF |
| 默认11h、极性和访问争议 | p.34 | INA3221-TCF-01/05/06 | 保留冲突与未知，不整字段晋升 |

## 12. Conclusion boundary

可作为三维度有界协议的来源审阅输入；不可宣布 M4 通过、正式输入准入、全寄存器 reset、整字段 RO/RW、故障 TCF 位值或物理延迟已验证。TCF 数值冲突、访问语义、部分／子集及全部禁用配置写清、AVG 解释保留。专家总建议 REPAIR，由主控冻结排除边界后做实现验收。

## 13. Author-stated limitations

原文没有本任务研究式 limitations 节，不能伪造。p.11 26 V 输入限制不是本任务试验结果。p.14 的 28.6 ms 是默认配置序列示意的近似时间；p.15 明确改写配置会禁用 TC。来源并未给 RST 任意时刻读零或 CVRF N 轮平均的承诺。

## 14. Critical assessment

已记录八项未解决冲突：TCF reset11h；TCF 位/引脚/非清除极性；一般读清与字段特例；disable-mode 未定义（不限制为全部禁用，覆盖部分／子集）；状态 R/W 未给持久化；软件 POR 与 PV 例外；0Eh reset/access；AVG 样本表与递归描述解释风险。不可暗称官方 errata。以特定规则建立公共子集属于有界分析，不能删除竞争原文。

## 15. Reusable knowledge and connections

AI分析：复位/转换/TC 都需要 epoch 边界，但作用不同；reset 是全局再初始化，CVRF read-clear 是局部消费状态，TC 非读清是监控状态生命周期。保存三者独立接口使后续论文能审计每条主张的事实、假设、未知与执行证据。

## 16. Testable follow-up ideas

研究假设一：加入当前 epoch/config 身份可检出错误接收陈旧 CVRF 完成。区别于原文：软件协议防护而非新器件行为。需要配对正确/错误实现，证伪结果为不能检出陈旧事件；最小版本为改写配置后旧 completion 注入；风险为测试元数据来自同实现自证。

研究假设二：显式 unknown TCF 极性可降低来源冲突被错误晋升。区别于原文：可审计准入策略。需要独立审阅及含未知的评分排除；证伪结果为未知仍被统计成通过；最小版本为 fault 后 TCF known_mask 失效且 read 保持未知；风险为减少覆盖率必须如实报告。

研究假设三：TC early-write 取消及 reset 重启可检出永久禁用/迟到故障污染。需要状态独立 oracle；证伪结果为变异实现通过；最小版本为 early CONFIG、late event、software reset、新 sequence；风险为物理时序未测，因此只能报告协议证据。未做更广文献搜索，不宣称新颖性。

下一步：主控在准入前重新复制修订 contract，保留原预实现清单及后续补充的时间顺序，冻结扩大后的未知边界并独立验收实现。
