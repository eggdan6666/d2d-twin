# 第三版语义原型

本目录是 `3.0-semantic-prototype-20261012.1`，用于将独立来源审校中的部分规则落实为可执行事件和故障夹具。原目录日期保留版本身份，本轮验收日期为2026-10-13（Asia/Shanghai）。这是有界原型，不能直接替换第一版/第二版评分，也不是20芯片全面参考实现。

来源输入为 `../independent_source_admission_20261012/` 的独立不可变审校包。109项来源补丁已在该包候选IR中应用；本版本通过哈希和20芯片/572字段映射读取它们，不重新修改旧目录。compiler先核对全部1252个审校材料哈希、21份PDF身份、572字段几何与策略，任一输入变动即拒绝执行。

runtime实现五种芯片的有限数字语义：TMP117的THIGH易失写/EEPROM编程与显式POR加载、Busy镜像及告警读清；TMP126事务受限读清、跨TEMP读清、单次平均转换完成；HDC2021单次测量开始/完成和DRDY跨地址清除；BME280湿度配置commit及Bosch两种forced编码完成。只实现文档所列操作，其余操作用OutsideContract拒绝；该异常是基准刺激范围限制，不声称真实硬件会抛异常。

原始候选规则仍是来源证据，不能由任意文字直接“编译成通过”。repair_closure_ledger逐条保留4004个字段维度的来源裁决、规则哈希和实施状态。执行过部分条款也不代表整个字段或整个维度通过。本版production_gate始终NOT_ADMITTED，明确要求未来完成全部准入机制后新建版本，不提供绕过开关。

事件接口是抽象数字模型：不推进物理时间，不保证典型毫秒时长，不模拟真实I2C/SPI帧、模拟温度/湿度或引脚电平。TMP117 qualifying_conversion_completed输入已完成转换的16位数字温度码，按已配置的有符号高低门限计算阈值关系并更新TEMP；场景使用非默认合法门限，不把旧TEMP默认值当新转换结果。这不验证模拟温度转换、offset补偿或AVG调度；输入被声明为已完成数字结果。TMP126 qualifying_flag_event表示致因已满足，不验证CRC计算/模拟slew。BME280 active_humidity是抽象观察接口，不是厂商寄存器。forced写入在本原型原子进入测量阶段，不声称硅片即时转移。未知ID高位、空字段EEPROM寄存器和争议soft-reset不提供伪造零oracle。

运行：

```powershell
python _setup/build_semantic_v3.py
python -m pytest eval/semantic_protocol_v3_20261012/tests -q -p no:cacheprovider
```

build在本目录更新scenario_execution、repair_closure_ledger、admission_gate和execution_manifest。pytest包含独立编写的负向故障夹具。预期通过只证明本版本有限契约与夹具的一致，不能改变来源135 PASS/96 REPAIR/302 CONDITIONAL/39 EXCLUDE，也不生成模型性能分数。

对旧720样本未执行任何重复评分，本步没有SCNet、外部模型API或实物操作。正式IR、冻结测试和历史分数保留。
