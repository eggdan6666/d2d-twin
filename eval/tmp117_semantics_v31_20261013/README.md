# TMP117 3.1 来源限定语义

本版本单独实现TMP117；原v3、来源审校包、正式IR、冻结测试与历史模型数据保持原样。输入仍为SNOSD82D原PDF及20芯片独立来源草案，本轮范围是15个TMP117 REPAIR字段所涉及的16个修订维度。

实施计划：核对原页约束→区分易失/NVM与操作模式→建立受控转换/加载事件→验证非默认状态与反例→生成逐条有限闭环台账。数据资料SUFFICIENT，现有Python/pytest与CPU足够，没有实物/SCNet步骤。

## 原型功能清单

- CONFIG、THIGH、TLOW、TEMP_OFFSET的锁定易失写、解锁编程、Busy镜像、general-call/POR重载；CONFIG后备掩码0x07fc，MOD1不持久。
- 编程过程和完成后、重载前的即时配置激活/读回不编造oracle。Busy可用掩码读取；编程期间写入不评分。POR明确忽略CONFIG/limits写，其余地址响应排除。
- AVG=00/01/10/11对应1/8/32/64样本。受控开始与样本完成分开，只有第N次更新TEMP/DR；OS完成进入操作shutdown，MOD数值读回仍未知。MOD01明确中止，其他活跃改写/重触发排除。
- 有符号、精确整除的累计平均；AVG00下offset的有符号加法与端点饱和；非整数平均舍入、AVG>0加非零offset的管线先后排除。
- CONFIG/TEMP读取清DR、Alert/THERM条件读清、严格有符号门限与滞回。POL与DR_ALERT选择逻辑ALERT电平，属于抽象数字观察，不证明电气或响应时间。
- Table7-7的全部32项CONV/AVG值作为名义周期元数据；不是物理计时或事件完成期限。

## 接口与流程文档

```python
from tmp117 import Semantics

d = Semantics()  # 明确工厂EEPROM情景；也可传四地址完整eeprom_image
d.write('CONFIG', 0x0c20)  # OS、8次平均
d.event('conversion_started')
for _ in range(8):
    d.event('conversion_sample_completed', temperature_code=0x1940)
assert d.operating_mode == 'shutdown'
assert d.read_masked('CONFIG', 0x2000) == 0x2000  # 返回preclear DR，再清零
assert d.read('TEMP') == 0x1940
```

read_masked执行对应整个寄存器的读副作用，只对已知且请求的位提供值；零掩码拒绝。普通read遇未知MOD/revision等位拒绝。OutsideContract表示基准范围限制，不能外推成真实芯片会抛异常/忽略所有非法输入。输入样本声明为已线性化数字结果，未模拟ADC、模拟温度、真实I2C帧或物理毫秒等待。

CONFIG逐位EEPROM场景验证符号化后备位布局和重载结果；EUN1写后的即时模式激活未知，不在解锁状态注入转换。因此这些结果不是物理编程流程安全性或即时读回证明。TNA改写带既有非零/未知告警历史时排除，不能凭LOW在THERM恒零推断完整模式切换转移。

运行：

```powershell
python _setup/run_tmp117_v31.py
python -m pytest eval/tmp117_semantics_v31_20261013/tests -q -p no:cacheprovider
```

scenario_execution保存实际条款检查和事件轨迹。admission在本地重新执行确定性场景，逐字节规范化比较记录，再匹配原572账本中的准确15字段/16维度，拒绝假PASS、删改检查/事件和伪造身份。这是本地重现检查，不是远程执行可信证明；独立代码审查和原页证据仍不可替代。

closure_ledger里的BOUNDED_CLAUSES_VERIFIED仅针对声明场景及明确排除。来源REPAIR标签保留，whole_dimension_closed和whole_field_promoted保持false；全20芯片正式生成仍NOT_ADMITTED。没有新的模型成绩或旧720次重评。
