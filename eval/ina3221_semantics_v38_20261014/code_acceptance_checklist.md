# INA3221 v38 独立预实现验收清单

制定依据：仅原 PDF 完整相关页；制定时没有读取候选实现。所有条目是后续验收要求，当前并未执行。以 source_review.json claim IDs 为绑定依据。

## 范围和来源锁

- exactly CONFIG.RST/trigger_completion, MASK_ENABLE.CVRF/read_clear, MASK_ENABLE.TCF/read_clear；任何支撑字段不增加晋升范围。
- 原 PDF SHA256 = 6ef5bf2263e34332fce7ea2547d9824ff5d3900418d51d59e5e3b711dcdc98d0，50页。
- 保存八冲突；TCF literal11h、statusR/W 不做无来源修正；0Eh 支撑值与访问隔离。
- 所有事件协议推断单列；不得写物理验证、芯片时延认证或整字段晋升。

## RST 请求/完成

- 写 RST1 接受复位请求；请求/完成边界明确。若原子实现必须明说事件完成抽象。
- RST0 普通配置写不假装硬件复位；等值重复 RST1 也有新请求代际。
- 待完成区间不认证任意瞬时 RST读0、即时全默认或最大延迟。
- 完成后 RST0、CONFIG7127h等有无冲突的已定义默认恢复；0Eh、TCF reset冲突及未知支撑bit排除。
- 修改非默认无冲突配置/支撑值后恢复，否则全默认断言是空测试。
- 旧转换/TC事件在新reset代际不可污染。重复完成/旧完成不能再次恢复当前已变配置。
- p15 PV引脚保持直到检测序列完成；不写成所有外设引脚同POR。若接口不建模PV须显式排除。

## CVRF 完成与读清

- 构造当前非空启用集合全部选定信号完成再置CVRF1；部分通道/仅shunt或bus子集完成不行。
- 禁用通道不等待；模式1/5只shunt，2/6只bus，3/7两者；全部禁用不能空集自动置位，这是协议选择而非硅保证。
- 事件校验epoch/sequence/config、启用集合、模式、AVG身份；非法/旧/重复/不完整事件拒绝。无事件寄存器读不产生完成。
- AVG非默认至少检查当前身份及处理完整性；拒绝不同AVG配置的旧事件；不能要求N轮/时长乘N并宣称制造商规则（p16递归更新）。
- 单次1/2/3同MODE再写启动新的请求；完成一次进入内部powerdown且不虚构新的完成。连续5/6/7允许新sequence完成。
- CVRF1 后 MASK读返回前状态并清该位为0；同次返回前后顺序若选定为协议假设必须标明；重复读维持0。
- CONFIG读及其他地址读不清CVRF；写MASK不能宣称普通RW清/任意持久化；须保持R/W来源标签与访问排除。
- 活动CONFIG写按清除规则清CVRF并换epoch。MODE0/4写为共同powerdown例外，原有CVRF1保持；不能由powerdown收到新completion。
- all-channel-disable CONFIG写后的CVRF清/保持明确UNKNOWN，或命名候选分支并排除manufactureroracle；不能把MODE4称新增disable-only编码。
- 在未清前值为1而不是只测试0->0；read-clear与set重新发生有序隔离。

## TCF 生命周期、引脚和未知

- flag和TCpin分别表示；TCpin默认high/faultlow来源p14Fig7-4；不得复用activehighfaultflag推TCF。
- TCF候选default1需保留reset11h冲突，不能整字段晋升。
- 未完成 TC 序列的普通 CONFIG 写禁用监控；后来完成/失败事件拒绝，直到powercycle/softwareRST新代际rearm。
- 单独读取MASK不能清TCF；单独写MASK无clear事实；其他读无凭空clear；在非平凡状态及known/unknown状态检查不被读重置。
- fault后的TCF值commonoracle为UNKNOWN；若实现PIN_LEVEL1->0候选，明确未认证；fault=1不可标manufacturerfact。
- 已终止监控不自动再次启动；powercycle及softwareRST都建立新序列。RST与普通CONFIG早写优先顺序明确为协议，避免reset先重启再被同写意外禁用。
- CH1阈值事件在前，随后默认all3channels四周期CH2未达阈值才构造pinlow候选事件；无默认条件/任意timeout不能当原文事实。
- TC默认时间28.6ms和1.2V不作物理测量oracle；注入事件仅验证状态机。陈旧epoch、错配置、序列错序、disabled/terminal事件检出。

## 报告约束

- 三维度有界通过、未知/排除、整字段晋升零分别统计。
- 变异至少覆盖RST不自清/错误默认或陈旧恢复，CVRF未完成早置/错误readclear/MODE例外/旧配置/AVG身份，TCF错误readclear/遗漏software-resetrearm/early-write未禁用/极性错误认证。
- 测试执行日志、命令、被测文件hash与独立清单hash留存；输入来源不得用候选实现自证。

下一步：主控冻结测试公共子集及排除范围，然后独立验收实现。
