# INA226 v37 独立来源验收清单（实现审阅之前制定）

角色：sci-skills-paper-deep-reading；任务 ina226-v37/source_review；M4。此文件仅描述来源准入门槛，未阅览或运行候选实现。源 PDF SHA256 c9b67f886d4a5241a5e070723f7b61867409eeb27eed768b9cdd9cb17e03ca2d，41 页；账本 SHA256 0905059f5f981f89137533d8b6f34d33cde5b673a05707c6b7141d521bb54711。

## 范围和来源

- 精确六个原始 REPAIR 字段 / 六个维度：CALIBRATION.UNNAMED_15.access；CONFIG.RST.trigger_completion；CONFIG.UNNAMED_14_12.access；MASK_ENABLE.AFF.read_clear；MASK_ENABLE.CVRF.read_clear；MASK_ENABLE.UNNAMED_9_5.access。
- 从原始 PDF 完整相关页与表、脚注制定；旧来源账本仅作范围清单。全文提取已执行，重点 11-13、22-28 页已渲染和目视。
- 候选实现、现有 d2d/ir 与旧 Harness 均未阅览或执行。本清单不接受整字段晋升或实测硅片结论。

## 保留 / 未命名位

- CONFIG[14:12] POR=100（二进制），掩码 0x7000，值 0x4000；CALIBRATION[15] POR=0，掩码 0x8000；MASK_ENABLE[9:5] POR=00000，掩码 0x03e0。
- 表中破折号是未命名位；三个所在寄存器均整寄存器 R/W，但无逐位 RO、写保护或始终读常量保证。
- 合法激励把这些位固定为 POR 值；非默认写入排除判定，不返回伪造硬件的 ignore/error/constant 结论。已知 POR 和运行读回 knownness 独立。
- 对 nondefault write 的 rejected/undefined 响应只能标为验证协议策略，不能称厂商行为；不能把排除的访问维度宣告全面 PASS。

## RST

- 来源 p23：写 1 产生等同 POR 的系统复位，全寄存器回默认且 RST 自清。只在复位完成边界认定默认，未给 RST 完成时长或复位期间读值。
- 将请求与完成分开，或明确标注原子完成的抽象假设。若保持 pending 状态，其读值 unknown；不得强断言写后每次立即读为 0。
- 暂存配置写后的同字低位与 reset-default 的优先关系必须由 reset completion 事件保证，不把事件先后说成物理总线保证。

## AFF 与 LEN

- 初态 POR=0；使用真正非零 AFF 故障事件。p12-13 / p26-27 支持选择告警函数的故障置位；不能空白循环读零来验证清除。
- LEN=1 锁存：无故障下一转换仍保持；完整 MASK_ENABLE 读清；重新 fault conversion 可以重置位。
- LEN=0 透明：下一次相关转换没有告警条件才清。单纯 fault stimulus 撤销或读取 MASK_ENABLE 不能替代这一转换边界。
- 共通 profile：对 LEN=1 的 CONFIG 写后 AFF knownness=unknown（p13 清 / p27 only MASK read 冲突未解决）；禁止自动选一段厂商文字作为唯一事实。
- 可选 named profiles 分别说明采用 p13 或 p27；必须保留 C_AFF_CONFIG_WRITE 冲突，不能让默认 / 共通 profile 隐式采用任一 profile。
- MASK_ENABLE 自清读回的原始报告值有功能用途的来源支持（p12、p27），但“清除前快照”与确切清除时点并未逐字规定。如返回旧值再清，应显式列为协议抽象假设，完整 16-bit 事务/无并发重新置位的边界也要写明。

## CVRF

- p11 / p27：必须全部 conversions + averaging + multiplication operations 完成才置位；普通结果写入、单个样本、尚未平均或未完成计算不等价。
- 事件应携带当前模式 / 配置代际、全部所需转换完成、平均完成、计算完成语义。一个未限定的“result ready”事件不能支撑独立完成断言。
- 先置非零 CVRF，再读 MASK_ENABLE 清；不读相关输出寄存器清；CFG 写 MODE=1/2/3/5/6/7 清。
- p24 Table 7-6：MODE=0 和 MODE=4 均 powerdown；RST=0 的这两种 CFG 写不因该写动作清 CVRF（若混入 reset，须独立走 reset-default 逻辑）。
- CNVR 是输出告警使能，不是 CVRF 是否会置位的前提；AFF 与 CVRF 的事件与清除条件分开。
- read returns preclear 的顺序同 AFF，仅可声明协议抽象，无总线字节时刻或原子硅片保证。

## 缺失保证 / 交付

- 无物理测量、模拟阈值误差、真实 ADC 精度、I2C 电气/时序、温度电源变化、并发读与转换重置位竞态验证。
- 非法编码、保留位非默认写、partial byte read 的 flag-clear 时点、CONFIG 写清 AFF 冲突、RST completion 时间仍不可补造。
- Table 6-3 p21 脚注明示其总线时序 min/max 并非保证且未生产测试；数字事件模型不能升级为这些硬件保证。
- 主写入者应检查六维度的有界 disposition、来源 ID、冲突 ID、unknown / exclusion 与实际测试门槛一致，才能形成建议验收；阶段仍由 orchestrator 决定。

下一步：由主写入者按本清单构建并独立验收六个维度的有界规则，保留厂商冲突与排除项。
