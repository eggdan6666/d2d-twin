# TMP126 v3.2 有界语义验证

从项目根目录运行 `python _setup/run_tmp126_v32.py`，重建执行见证和有界准入账本。`python _setup/package_tmp126_v32.py` 运行独立测试、专家契约验收及本轮状态更新。需要本地 Python 和 pytest，无需 SCNet、模型服务或实物。

`tmp126.py` 使用冻结 v3 基类但实现独立状态机；`scenarios.py` 是执行见证；`admission.py` 校验来源身份、冻结字段分母，并确定性重放记录。`source_review.json` 保存独立原页裁决，`code_review.json` 保存独立实现审校。所有输入与结果哈希见各 execution/manifest JSON。

本轮对应原账本 8 个 REPAIR 字段、8 个 REPAIR 维度。10 个执行场景包含一个探索性 body_candidate 场景和一个名义周期表；不将这些检查数作为新增模型样本或独立来源事实。OutsideContract 表示基准范围限制，不是硬件异常响应规范。

全局正式生成输入仍为 NOT_ADMITTED。6 个手册内部冲突保持未解决。SPI 帧、CRC 算法、实际模拟转换、电气时序及非整除平均舍入不在此实现范围；限定事件由调用方预先资格化。
