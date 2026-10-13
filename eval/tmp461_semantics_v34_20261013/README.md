# TMP461 v3.4 有界事件语义

从项目根目录运行 `python _setup/run_tmp461_v34.py` 生成实际事件见证和有界准入账本；`python _setup/package_tmp461_v34.py` 验收专家返回契约、复跑独立测试并更新本轮状态；`python _setup/archive_tmp461_v34.py` 校验签审字节并生成档案清单。需要本地 Python、pytest 和现有手册，无需 SCNet、模型或实物。

接口：`Semantics(profile='common_source')`、`write(reg,byte)`、`read(reg)`、`read_masked(reg,mask)`；`conversion_started`、`conversion_completed(local_code=uint12,remote_code=uint12或None,remote_open=bool)`、`qualified_remote_open_detected`、`qualified_alert_service_completed`、`general_call_reset_completed(second_byte=byte)` 事件。`alert_pin()`/`therm_pin()` 为逻辑0/1，不模拟上拉、电压或真实 SMBus 服务事务。

输入数字为12位寄存器编码，正常范围解释为有符号数/16°C；扩展范围解释为无符号数/16−64°C。事件是已资格化的数字转换/故障/服务，不是模拟温度测量。ONE_SHOT 在 SD1 下写任意 byte 直接开始转换，写值不保存、不提供读回；STATUS 复位知识掩码为0，不能读取为零。内部占位值不构成设备可见事实。

建立已知正常基线的方法：完成双方通道的受控中间温度转换，再读取已知 BUSY 位 `read_masked('STATUS',0x80)`；此操作是整个 STATUS 寄存器读取，清除原因已消失的锁存位，后续字段才可被观测。温度高低字节观察必须完成配对，或读其他寄存器结束配对；本原型不模拟转换跨越未完成配对时的真实快照锁定机制，会限制该完成事件。

共用范围只实现两通道、DF00、CONAL01、零offset/η校正；`therm2_candidate` 另行验证高温迟滞和 OPEN 条件，低温状态数字仍未知。读清采取通道结果同时处于低高限之间的保守资格化条件，未断言所有相反越限组合的清除真值表。未规定或未实施操作的 OutsideContract 是范围限制，不是厂商统一的总线错误响应。

重新运行 producer 会更新执行耗时；若已有签审，应依次重跑 `tests/record_independent_execution.py` 和 `tests/package_code_review.py` 重新绑定记录，再 package/archive。原 IR、冻结测试、历史结果不被脚本替换。
