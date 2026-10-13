# INA219 v3.6 有界语义原型

本目录针对固定来源账本的6个REPAIR字段、7个修订维度。它使用明确的未知掩码、资格化数字事件和来源冲突分支；正式生成输入仍NOT_ADMITTED，不能代替完整芯片或实物验证。目录名称保留20261013，最终验收记录日期为2026-10-14。

## 输入与实施计划

输入为TI INA219原手册SBOS448G、固定`field_evidence.json`及只供寄存器布局的候选IR。原型继承先前冻结版本的字段工具；启动时验证工具和布局哈希。

实施顺序：独立原页审校→未知掩码及两阶段转换状态机→来源条款绑定的实际场景→独立故障与损坏证据测试→闭包账本→旧文件哈希核对及归档。来源矛盾采用未知保护或明确候选分支，不用猜测填补手册空白。

## 原型功能清单与接口

- `Semantics(profile='common_source')`为主范围；`register_detail_candidate`为寄存器详细页候选策略。
- `write('CONFIGURATION', word)`和`write('CALIBRATION', word)`接收16位整数。MODE3写入启动单次转换；MODE7使用显式启动事件；MODE0/4为关闭模式。其余模式编码合法，但对应历史尚未实现。
- `read`／`read_masked`只观察已知位。BUS位2始终未知；冷启动和已完成复位时BUS/SHUNT测量值不填零。
- `event('conversion_started')`→`event('voltage_results_completed', shunt_word=..., bus_code=...)`→`event('whole_sequence_completed')`分别表示开始、资格化电压结果和资格化全序列完成。CNVR不得只因电压结果到达而置位。
- `event('qualified_math_overflow')`只在非零校准的计算阶段接受已资格化的正向溢出。它不执行或判定校准算术，也不提供溢出清零规则。
- CONFIG.RST写1进入`reset_pending`，阻止所有数字读取；`event('reset_completed')`恢复已明确默认值及未知测量掩码。没有模拟复位耗时。
- `nominal_adc_settings('BADC'|'SADC')`返回16种合法编码对应的分辨率、平均次数和名义时间；4..7是有效别名。该接口不是计时实验。

源文描述“首次编程校准之前CURRENT/POWER保持0”；本实现只在这一历史边界及已完成复位后使用零值保证。曾编程非零校准再写零仍保持结果未知，不能把写校准当作即时结果复位。

## 流程文档与来源限制

主范围在BUS／POWER读取后使CNVR知识失效；同一个活跃MODE重写也使其未知。详细页候选单列POWER读清、BUS不清及活跃CONFIG写清的策略。候选及混合场景有独立标签，测试通过不代表来源矛盾解决。

SHUNT是声明范围内已编码的有符号码；BUS是4mV单位的数字码，左移3位。32V量程元数据不授权芯片物理输入超过26V。真实ADC、平均调度、整数舍入、负功率、溢出结果表示、I2C电气／帧／指针时序、活跃重触发舍弃历史及复位中间值均在范围外。

## 测试准备材料与操作

本地Python和pytest、项目内现有手册足够，本轮不调用SCNet。执行命令均在项目根目录运行：

```powershell
python -B _setup/run_ina219_v36.py
python -B eval/ina219_semantics_v36_20261013/tests/record_independent_execution.py
python -B eval/ina219_semantics_v36_20261013/tests/package_code_review.py
python -B _setup/package_ina219_v36.py
python -B _setup/archive_ina219_v36.py
```

`run`会重新生成执行记录；完整重跑后应按上述顺序刷新审校签审和归档。只核查现有档案时运行`archive`，它校验已有签审字节而不重写已签署的执行输入。不要用生成器脚本覆盖已签审代码后沿用旧签名。

独立验收清单、测试源码、故障夹具、两套JUnit／日志、输入输出哈希、来源证据、闭包和原始文件保全记录均随本目录保存。场景和检查数是本地验证数量，不是模型样本或实物测量数。
