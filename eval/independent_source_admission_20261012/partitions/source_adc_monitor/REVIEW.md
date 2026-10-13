# 6器件独立来源审校签审候选

日期：2026-10-12。任务：source_adc_monitor。审校者为独立 AI 专家子任务；本文不代表人类签字，不推进M4，也不证明实物行为。遵循项目 sci-skills-paper-deep-reading 与PDF阅读工作流。

已审154/154个inventory字段，每字段七维，共1078条维度记录，并覆盖TMP117的三个空字段EEPROM寄存器。输入中的报告、policy、inventory、manifest均为待审对象；不以参考通过、历史分数或原IR自述作证据。证据限于6份本地完整原始厂商PDF的实际相关全页，使用独立SHA-256、PDF原生提取与9张关键冲突页面渲染目视核对。

| 器件 | 字段 | PASS | REPAIR | CONDITIONAL | EXCLUDE |
|---|---:|---:|---:|---:|---:|
| ADS1115 | 12 | 0 | 1 | 11 | 0 |
| ADS1220 | 16 | 0 | 0 | 16 | 0 |
| INA219 | 16 | 6 | 6 | 3 | 1 |
| INA226 | 29 | 6 | 6 | 17 | 0 |
| INA3221 | 61 | 13 | 3 | 38 | 7 |
| TMP117 | 20 | 2 | 15 | 3 | 0 |

PASS仅说明当前声明范围内已核对的寄存器事实可保留。REPAIR说明待审输入或策略有可修订缺口；CONDITIONAL保留明确前置条件、动态事件或来源冲突；EXCLUDE只隔离非默认/未定义操作，仍保留维度中有来源的reset事实。七维内applicable=false的PASS是范围判断，不能算实际行为通过。全部记录可追溯手册版本、原PDF SHA、物理/印刷页码、表/章节及短原文。非适用维度用ABSTRACTION_ASSUMPTION明确区分，无事后补造厂商保证。

TMP117最重要修订是HIGH/LOW读清只适用于T/nA0；Therm模式HIGH由转换阈值置清且LOW恒0，读CONFIG不清。DATA_READY既由CONFIG也由TEMP读清。所有EEPROM后备reset需要条件化，含CONFIG位(持久mask07FC)、THIGH、TLOW以及TEMP_OFFSET；MOD1不持久。表给的Busy0是ready阶段，POR加载中为1。编程单位置典型7ms，POR加载约1.5ms，2ms是soft reset描述，不能混用。EUN0仍允许volatile scratch写，EUN1才烧录EEPROM；编程时禁止写入的结果未定义，不能评分忽略/保存。EEPROM1/2/3空字段不等于没有契约。EEPROM2标题0000与图/表xxxx冲突新增登记。

INA219原Table2没有SHUNT/BUS的数值reset，因此旧0断言需要隔离；未命名bit2也无恒零保证。CNVR在完成转换/平均/乘法后置位，但p10的Status/convert pin与p23的POWER读取清除、新MODE写清表述不同；本审校保留来源冲突。另Power/Current只有Calibration0时保持0。INA219/INA226/INA3221的self-clearing RST支持完成后归零，不证明任意瞬时读总0；原子复位仅能是已命名抽象。

INA226 CVRF读MASK清、CONFIG非powerdown写清；AFF清除受LEN模式限制。AFF的CONFIG写清在p13与p27冲突。DIE_ID不仅是2260/2261产地变体：p28 Table7-15全0POR与p22汇总不一致，应加入冲突。三组未命名保留位未有逐位RO依据；维持POR值、排除非默认访问oracle，不能将整表R/W或空名字倒推成硅只读。告警使能多个置1是最高bit优先，非保留编码。

INA3221 0E冲突继续未解决：只保留registermask8001的reset一致位，所有0E写/保护oracle隔离，并区分SIGN与SVL。MASK flags的source标签仍为R/W，软件不可写是抽象策略；普通RW持久性不适用。CF/SF/WF读MASK清，PVF/TCF不读清；TCF原文还有software reset重新初始化。TCF reset列11h与单比特位图/0002/文字high另有表达冲突，保留而不称官方勘误。CONFIG早写会禁用尚未完成的timing-control序列；power-valid功能依赖bus模式和周期测量。

ADS1115 OS是写动作/读状态，powerdown时写1启动、busy时写1无作用。连续模式CONFIG写不打断旧转换，新配置下一转换才生效。CONVERSION读清的是锁存ALERT/RDY输出，不是COMP_LAT字段或数据。比较器门限要求补码HI>LO且PGA变化更新；HI MSB1/LO MSB0另用于ready模式。全部MUX/PGA/DR编码有定义，包括PGA5/6/7别名，未把别名强行读回归一。

ADS1220任意CONFIG写启动或重启单次转换；powerdown写CONFIG只启动一次，不论CM。连续开始需CM1后START/SYNC，寄存器存储读回不能代替该命令/事件协议。TS1屏蔽CONFIG0功能并强制实际internal reference，但无数值读回改写承诺。IDAC先设电流再routing，启动最长200us；single-shot完成后IDAC及PSW可以继续有效，POWERDOWN才关闭/打开相关器件。Reserved bit0只允许写0，不能以R/W码认证写1持久性。既有合法域与fixed0策略已处理的项在findings内单独标识。

交付：fields.json为逐字段账本，findings.json为37项差异候选，register_gaps.json为3项空字段门控证据，ir_patches.json为候选输入属性/描述更正，sources.json为6来源指纹及核对页面，conflicts.json为8项保留冲突，quality_checks.json为完整性检查，expert_return.json为精确1.0专家返回。仅新分区写入；原d2d/ir、冻结黑盒、v2已有输入和历史模型结果未写。

输入冻结建议：以这些记录生成独立候选包，将源摘要、每字段合法域、known-mask、EEPROM图像、事件前置、非适用项、冲突版本全部写入生成输入与harness契约，并冻结完整提示词/IR/policy/PDF SHA。主存储profile可以保守排除动态未实现事件，但不能把事件字段恒0及读0再读0算覆盖；另一事件profile需有可控非零生成、完成推进及返回清前状态。默认厂商给的时间、典型时间与抽象原子完成必须分开。旧模型分数只代表旧输入，任何新包需新生成队列；本审校没有运行模型或参考harness，无SCNet或实体操作。

签审建议：REPAIR，merge_permission=orchestrator_only。来源冲突共8项UNRESOLVED，不做多数表决，不称官方勘误；新候选包在对应新harness落实全部条件之前不可成为无条件Gold。物理输出/模拟采样/时序功能仍未实测。

唯一下一步：由主编排整合本分区证据，生成独立候选冻结输入包并显式列出新harness尚需兑现的条件与排除。
