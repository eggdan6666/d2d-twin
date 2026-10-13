# HDC2021 v3.3 有界事件语义

从项目根目录运行 `python _setup/run_hdc2021_v33.py`，产生实际场景记录与有界闭包。`python _setup/package_hdc2021_v33.py` 验收两项专家返回契约、运行独立测试并更新本轮状态；`python _setup/archive_hdc2021_v33.py` 校验签审字节并生成档案清单。重新运行 producer 会重写执行耗时；若已签审，应重新运行 `tests/record_independent_execution.py` 和 `tests/package_code_review.py` 绑定新的 producer 记录，再 package/archive。

需要已有 Python、pytest 和本地 PDF，无需 SCNet、API 或实物。`hdc2021.py` 是有界逻辑模型，`scenarios.py` 产生非零执行见证，`admission.py` 绑定原字段身份并确定性重放。完整记录及哈希见 scenario_execution、execution_manifest、两套 JUnit 和 artifact_manifest。

接口为 `Semantics(profile='common_source')`、`write(reg,byte)`、`read(reg)`、`read_masked(reg,mask)`，以及 `measurement_started`、`measurement_completed(temperature_code=word, humidity_code=word或None)`、`reset_completed` 事件。`phase` 明确请求、转换、复位待完成等边界。`interrupt_pin()` 返回逻辑0/1或 `HIGH_Z`；名义周期和复位时限方法仅返回手册元数据。

STATUS/INTERRUPT_ENABLE 的低三位不被认证为动态恒零，使用 `read_masked('STATUS',0xF8)` 观察已知字段。所有数据读取仍具有真实寄存器语义所需的逻辑读清副作用，mask 仅限制观察位，不表示物理按位读取总线。未知字段、无范围依据的操作会得到 OutsideContract；它是基准范围限制，不是统一的芯片异常响应。

`common_source` 只表示有共同依据的读清和事件边界；数值阈值预条件仍使用明确标注的表格/图示候选。`table_figure_candidate` 进一步允许争议比较器读策略及禁用使能时的状态解释。六处来源冲突没有被测试结果解决，所有字段和维度整体准入仍为 false。

不实施真实 I2C、ADC、精度量化、峰值检测、模拟迟滞、非零 offset、加热器、实际转换周期或复位耗时。模型样本和历史成绩没有重算。
