# INA226 v37 有界语义任务

协议 `3.7-ina226-20261014`，M4。仅覆盖原账本六个 REPAIR 字段／六个维度；正式生成上下文尚未准入。所有辅助工具、独立专家代码、PDF 材料和测试在 `sandbox/ina226_v37/`；当前任务目录由主写入者整合。

## 运行与材料

归档前从仓库根目录执行 `python sandbox/ina226_v37/run_task.py` 产生数字事件见证、有界闭包和旧文件保全记录。归档后保持该目录只读，使用 `python sandbox/ina226_v37/verify_archive.py` 校验哈希；加 `--replay` 可仅在内存重放场景，不覆盖归档。独立测试命令及最终测试文件哈希见 `independent_code_execution.json`。Python/pytest 为现有本地环境，无模型推理或硬件采购。

`ina226.py` 提供 `Semantics`、`OutsideContract` 和 read/read_masked/write/event 接口；`scenarios.py` 是实际执行场景；`admission.py` 将接受的独立来源合同、原 PDF、原字段账本及重放记录绑定。`source_review.json` 为事实、遗漏、冲突及协议假设的完整来源账本；`code_acceptance_checklist.md` 在实现审阅之前制定。

## 读取与未知

`read_masked(register, mask)` 是一次**完整 16 位寄存器读取之后的数值投影**，不是局部 bit/byte 读取。清除前快照→读清采用不可穿插事件的线性化协议约定，支持 flag 诊断用途；不证明 I2C 哪个字节／时钟清除或真实并发重置位。包含未知位的数值观察被范围入口拒绝；未知 mask bit=0 不是物理 bit value=0。

保留字段仅在明确 POR 边界赋值已知。合法写把其输入维持 POR 图案，但写后保留字段 knownness 失效；非默认访问刺激排除，而非宣称硅片 RO、忽略写或抛异常。未选择 2260/2261 die variant，所以 DIE_ID 数值观察排除。

## 事件与排除

- RST=1 的合法输入采用 CONFIG 保留位基线；请求进入 pending，显式 `reset_completed` 才恢复默认。无 pending 读回或实际完成时长保证。
- `qualified_results_staged` 只暂存已资格化数字结果；`whole_sequence_completed` 必须同时声明 conversions_complete、averaging_complete、multiplication_complete 为严格布尔 true，并绑定当前 configuration_epoch 与 sequence_id。结果供给是外部资格化刺激，不是执行 ADC、平均、乘法或物理电压测量。
- 实施 MODE3/7 的双通道场景，以及 MODE0/4 的关断输入；原文存在 MODE1/2/5/6，但它们不在当前实现范围，不静默归入已验证。
- 资格化相关告警转换携带最高优先级已选择告警函数及真实 boolean fault，验证 AFF 条件规则；不计算模拟阈值或证明真实电气告警。LEN=1 在无故障下一转换保持，MASK 读清；LEN=0 到下一无故障相关转换才清。
- CONFIG 写除 MODE0/4 会清 CVRF，含相同 active-mode 重写；CNVR 控制通知使能，不是 CVRF 置位前提。读取其他数据寄存器不替代 MASK 清除。
- 锁存 AFF 的 CONFIG 写清除存在 p13／p27 冲突：common_source 标未知；config_clear_candidate／register_detail_candidate 分列两种来源条件假设，均不认证为无冲突厂商行为。
- 软件写非零状态 bit、带告警历史修改 alert 控制、未实现单通道、复位中访问、失配／过期序列及非法类型在当前范围拒绝。OutsideContract 是评测契约响应，不是芯片异常模型。
- 校准算术、OVF 清除、带历史的 CAL 清零即时结果、真实总线、精度、转换／恢复时序和并发竞态未证明；非零校准后的 CURRENT/POWER 保持未知至资格化复位。全完成后 OVF knownness 也不会凭缺少事件推成 0。

## 解释执行结果

六行闭包由三项访问排除门禁与三项条件事件规则组成。`BOUNDED_CLAUSES_VERIFIED` 表示该有界 disposition 的执行证据满足当前要求，不把三项排除解释为访问成功或六个完整字段认证。所有 `whole_field_promoted`／`whole_dimension_closed` 均为 false。元数据表、候选策略和来源冲突均单列；检查数、测试函数数、合成故障种数不能作为大模型新增样本或硬件测量数。
