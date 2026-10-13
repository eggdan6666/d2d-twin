"""Write human-readable signoff and prospective generation freeze recommendations."""
from pathlib import Path
import json,hashlib,collections
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,x):p.write_text(x,encoding='utf-8')
def dump(p,x):write(p,json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
q=read(OUT/'quality_checks.json'); rows=read(OUT/'field_evidence.json');sources=read(OUT/'reviewed_source_manifest.json')['sources']
assert q['field_count']==572 and q['dimension_count']==4004 and q['excerpt_mismatch_count']==0
assert not q['preservation']['changed_or_missing'] and not q['preservation']['v2_manifest_mismatches']
counts=q['verdict_counts']
source_md=['# 本轮来源身份冻结','','本地原始厂商PDF锁定；SHA-256绑定实际审查字节，不声称当前官网最新版本、实体芯片revision或官方勘误已核验。MPU6050原始产品规格和原厂Register Map本地镜像分别记录，字段审查引用RM，不能把PS的相同页码当RM页码。LM83技术正文印刷页为物理页−1。BME280封面/正文版本标识差异保留。','','|器件|版本/来源角色|文件SHA-256|路径|','|---|---|---|---|']
for s in sources:
 c=s.get('chip',s.get('device'));v=s.get('manual_version','')
 source_md.append(f"|{c}|{v}; {s.get('source_role','reviewed local manufacturer source')}|`{s['sha256']}`|`{s['source_path']}`|")
write(OUT/'SOURCE_IDENTITIES.md','\n'.join(source_md)+'\n')

report=f'''# 独立来源签审：20芯片 / 572字段

审校日期：2026-10-12（Asia/Shanghai）。签审身份：Codex 独立AI来源审校主任务，配合三个项目SCI-Skills独立审查子任务；非人类专家签字、非厂商认证、非实物验证。待审对象为用户指定的七份v2报告/政策/manifest，实际证据来自 corpus/data/raw_pdf 的原始厂商PDF。未使用参考通过或模型得分裁决来源。

**签审结论：审校与候选交付完成；当前输入全面准入为 REPAIR，正式新一轮生成冻结为 NOT_ADMITTED。** M4保持部分通过，未推进阶段。

## 逐项审查结果

20芯片572个既有inventory字段全部对应一条独立账本，无缺项、重复或分母扩大；每字段审查reset、access、合法编码、读清零、触发完成、条件写入、保留位七维，共4004条维度记录。额外空字段EEPROM/命令/范围缺口在register_scope_gaps.json单列，不计入572分母，也不外推当前selected register set为全芯片认证。

|逐字段结论|数量|含义|
|---|---:|---|
|PASS|{counts['PASS']}|所引原页与限定的字段事实/契约可接受；不代表全部动态功能已执行验证|
|REPAIR|{counts['REPAIR']}|现输入/政策需修订，或遗漏副作用/域/门控；候选尚未在新harness兑现|
|CONDITIONAL|{counts['CONDITIONAL']}|事实有来源，但断言必须附具体版本、模式、复位边界、事件或抽象前提|
|EXCLUDE|{counts['EXCLUDE']}|该字段相关主oracle缺定义或有不可裁决冲突；可分别保留已知reset等其他事实|

每条维度同时保留MANUFACTURER_FACT、ABSTRACTION_ASSUMPTION、UNDEFINED_BEHAVIOR、SOURCE_CONFLICT分类。无独立读清/触发规定的维度标EXCLUDE及适用范围；不把手册未给动作证明为“没有任何副作用”。status是对旧inventory的审查结论，候选几何位置与新字段名在candidate_source_policy的inventory_field_id/candidate_bit_mask中显式映射。

## 本轮决定性差异

- TMP117：T/nA=0才对HIGH/LOW读CONFIG清零；THERM模式HIGH依阈值更新、LOW恒0，CONFIG读不清。EUN=0仍更新易失scratch/config/limits寄存器，只是不编程EEPROM。典型编程7ms，Busy需完成后再写；CONFIG的EEPROM-backed位、门限、TEMP_OFFSET复位不能无条件固定出厂值。三个无字段EEPROM寄存器另列门控；EEPROM2标题与图表reset冲突新增保留。
- 动态转换与告警：TMP100 OS受POL和比较器迟滞影响，不能恒read_as1；TMP102 OS是转换状态、AL受POL反相，EM=1改变TEMP/门限位格式。TMP1075限非N，OS触发需SD1；写TM清fault count/alert history。INA219/INA226/INA3221转换标志的读/写清条件、单次完成及校准副作用单列，权限不等于恒定快照。
- 读清零范围：TMP126 Alert_Status要求single-register read且无auto increment；TEMP_RESULT还清DATA_READY，ONE_SHOT完成置MODE1，Comparator→Interrupt清状态。LM83、TMP461清flag需模式/致因/转换窗口；ALERT引脚解除与寄存器flag清除分开。HDC2021 MEAS_TRIG在测量开始自清，DRDY完成另判，多输出读址可清DRDY，INT_MODE编码说明需修复。
- 确定输入错误：LIS2DW12 OUT_T_L数据在bits7:4、零位在3:0，旧位域颠倒；TMP100用12位完整TEMP寄存器格式并按分辨率置未用LSB。TMP461 STATUS与ONE_SHOT的POR为N/A，移除旧0候选。TPS23861 FIRMWARE_REV地址应0x41而非0xFE；GENERAL_MASK.M250是sense resistor选择，非250ms。
- 模式与门控：Bosch config写需sleep；BME ctrl_hum需后续ctrl_meas写commit，模式切换存在等待/忽略窗口。BMP280的10同01都是forced；XLSB高半字节承载数据。LIS3DH七个STATUS字段Table47有Default0，不宜全部以“14动态字段无默认”排除；XDA该版缺描述行及输出数值未定义分别保留。AD5592R IO_LOCK与readback使能、MPU睡眠/中断清条件、TPS EEPROM解锁/Auto改写/端口动作都作为条件规则。

## 不裁决的来源冲突

TMP117 DEVICE_ID高四位Rev及Soft_Reset图/表、INA3221 0Eh图/表、TPS23861 R17[3:1]总览/详细粒度冲突保持UNRESOLVED。主oracle仍用TMP117 DID低12位、INA3221仅0x8001一致reset位并排除0Eh写/保护裁决、TPS歧义位保留首次观测值而不固定0。新增INA226 DIE_ID/AFF、INA219 CNVR章节、TMP117 EEPROM2、INA3221 TCF单比特11h、AD通用命令位布局、LIS2 FIFO/MPU描述等内部冲突也未择多数为真。

完整逐项 competing_evidence 与locator在conflict_ledger.json；分区额外冲突卡保留。所有冲突、推断和策略都不称官方勘误。候选输入的历史审校话语移到legacy_ir_annotations.json，避免把旧“Gold/已通过/erratum”注释当下一轮厂商事实。

## 证据与完整性

本轮21份本地PDF身份（包含MPU的RM与PS）已复核SHA-256；4356处短原文引用在原PDF文本读取/排序读取中精确匹配，关键位图已渲染目视。文本匹配证明引用存在，不代替事实支持性判断；逐字段判断见账本，分区签审记录其所读页与视觉边界。不是4356条独立来源事实。

{q['candidate_ir_attribute_patches']}条候选属性补丁仅应用到新目录的20份candidate_ir；结构检查无位域重叠/越界，candidate policy逐字段映射对齐。另有{q['findings_entries']}条差异记录，同一机制可能跨多个字段，不当作互异硅缺陷数。candidate_ir保留572字段，空字段补建建议另存，未来若扩充须重新冻结分母。

受保护的{q['preservation']['protected_file_count']}个既有文件SHA-256复核全部不变，包括d2d/ir、所有现有test_d2d_blackbox.py、完整v2目录和历史模型结果清单；v2 manifest的44项匹配。未运行模型/参考测试、SCNet、外部API、实物或总线时序。本轮评分计数来自来源审查分类，不是重新评分。

## 交付与输入冻结

field_evidence.json与dimension_evidence.csv提供572字段/4004维度证据；field_verdicts.csv、per_chip_verdicts.csv提供快速筛查。revision_candidates.json、applied_candidate_patches.json、DIFFERENCES.md提供修订候选和差异。candidate_ir与candidate_source_policy.json为来源约束输入草案，schema刻意与旧v2区分，**不能作为旧harness的替换输入**。

audit_bundle_manifest.json冻结本次审校材料；input_freeze_candidate_manifest.json仅冻结可评审输入候选字节，production_generation_ready=false。INPUT_FREEZE_RECOMMENDATION.md列出准入门控、事件定义与新生成上下文应保存的指纹，GENERATION_PROMPT.zh.md提供后续可复制模板。冲突被排除的方面必须仍在新一轮报告中显式披露。

唯一下一步行动卡：在独立新版本中落实候选IR/policy与事件/完成/模式门控的harness，先验证实际适用掩码、合法刺激、非零事件与负向故障夹具，再冻结精确生成提示词和模型revision；通过后才启动新一轮生成。本步材料齐全，无需SCNet或购买实物。
'''
write(OUT/'INDEPENDENT_SIGNOFF.md',report)

freeze='''# 新一轮生成的输入冻结建议

当前建议：**审校证据可以冻结归档；正式生成输入暂不准入。** 本包提供20份已应用来源补丁的IR草案、572字段七维规则与具体冲突/排除，完成本步独立来源审查。candidate schema不是旧v2接口；未经配套新harness实施不要把候选改名成全面Gold。

## 1. 固定来源与科学范围

锁定reviewed_source_manifest的全部本地原PDF字节、器件orderable/手册版本、PDF物理页/印刷页与表号。TMP1075范围non-N；TMP117固定factory EEPROM仅作为显式情景，而非任意器件复位保证；TPS必须区分POR、输入RESET、RESAL/RESP以及供电轨。MPU使用RM作寄存器主要证据，产品规格作补充。572是既有inventory单位，空字段EEPROM及未映射命令保持另列，若新增字段/地址要重新确定分母。

保留所有SOURCE_CONFLICT项，主评分只使用无冲突方面。TMP117 DEVICE_ID reset用0x0FFF；INA3221 0Eh reset只用0x8001且写/保护排除；TPS R17[3:1]首次观测保持，reset/access不确定位不得填0。任何diagram/text优先模型要用命名exploratory profile单列，不写官方勘误。未定义非法编码输入不给钳位、忽略、异常或读零oracle。

## 2. 修订候选与生成输入分开冻结

candidate_ir为新目录中的来源草案，candidate_source_policy每条以inventory_field_id追踪原572身份，同时field/bits/candidate_bit_mask指向修复后的实际几何。LIS2 ZERO_7_4→ZERO_3_0与TMP100位宽改变已经对齐。未确认reset移除/置null/标runtime，来源冲突保留，不直接推全字段恒值。历史审校注释保存在legacy_ir_annotations，生成时不得把其过去的Gold、通过或erratum表述作为事实。

准入前必须实际验证新schema的IR、policy、harness三者共享相同字段名/地址/掩码、动作属性与范围。CONDITIONAL规则是输入契约的一部分，不能只写在报告里让harness忽略。每一REPAIR必须有闭环项：已应用的输入修订、是否需harness变更、验证证据、剩余排除；未闭环不得改PASS。记录每个使用的合法值与被排除值/组合，默认或未知保留位只作输入约束，不当RW/RO实证。

## 3. 明确静态与事件两套范围

可在新协议定义“已完成复位、初次转换完成前、无外部状态变化”的静态契约，但必须明说它是寄存器抽象。RO仅表示软件写权限，不能在时间推进、读清或MODE/POL副作用发生时做整快照相等。动态mask、相同事件窗口及逐字段保护必须实际执行。没有可观察非默认刺激的对象skip而不是通过。

动态契约若纳入，须先声明受控事件接口/调度：conversion_started、conversion_completed（含AVG次数）、NVM/POR_load_completed、EEPROM_program_completed、threshold/hysteresis/fault-count、CRC_fail、FIFO读/溢出、power/classification等。事件名是基准抽象约定，不是实测厂商时间；典型时间不能当保证超时。完成归一化与即时读回必须分开：LIS2 BOOT/reset完成自清、HDC MEAS_TRIG开始自清、TMP102 OS转换状态、TMP126 ONE_SHOT读恒0但完成MODE1等不能共享一个read_as0裁决。

读清必须构造非零flag，核对read返回的preclear数据、postclear状态、受保护未清位、重触发条件和跨地址clear。TMP117 TNA限定、TMP126 single read/no auto increment+TEMP清DR、HDC多读地址、LM83/TMP461致因解除、INA配置写清、TPS CoR清0与summary重算都需落实。没有事件接口的方面保留CONDITIONAL/EXCLUDE，读0→0不算该功能覆盖。

EEPROM须区分易失写与持久编程：TMP117 EUN0可写scratch，EUN1且Busy0才编程，Busy两位置镜像，完成后再允许下一写，reset加载持久副本；TPS需unlock/地址/AIN/自动锁定等条件。I/O锁、Bosch commit/sleep、MPU/LIS模式条件、校准有效与阈值关系均须按规则执行。若暂不实现，排除对应功能，不能让独立普通RW存储代替门控。

## 4. 准入验收与生成溯源

在新目录运行source/schema对齐、适用分母、合法刺激和掩码检查；用有区别的故障夹具验证“错误readback、无条件清除、从不清除、无条件复位、不复位、忽略门控、过早完成、非法刺激”等确实被抓住。参考通过只证明harness与参考的一致，不能改来源标签；完整来源账本继续作为事实权威。避免重复无意义的全量历史重评。

通过后再创建production_generation_manifest，哈希锁定原PDF索引、修复IR、policy、精确harness、test-values/known-masks/exclusion清单、base simulator、完整system/user提示词、模板展开后的每芯片prompt、依赖/运行命令与模型revision/参数/seed（不可得项明确缺失）。生成前计划分母与分组关系，生成后保存逐次代码SHA、响应/解析/重试轨迹。新生成与旧720次历史队列分别报告，不能后补哈希重建旧提示词或把重评分变化称学习进步。

input_freeze_candidate_manifest的哈希是本轮可评审材料快照；harness_hash=null是未实施门控的明确信号，不代表通过冻结。任何输入字节变动都产生新版本manifest，不覆盖本包或历史。

唯一下一步：在独立新目录实现并验证候选契约/harness，关闭96项REPAIR对应的准入缺口及条件规则，再冻结正式生成上下文。所需资料本地已齐，无需账号、SCNet或实物采购。
'''
write(OUT/'INPUT_FREEZE_RECOMMENDATION.md',freeze)
prompt='''# 后续新输入实施与生成提示词模板

使用条件：仅在INPUT_FREEZE_RECOMMENDATION的harness准入门控通过后用于正式生成；当前可用于新版本实施/评审。不得把本包状态改写成无条件Gold。

请根据指定芯片的candidate_ir与candidate_source_policy.field_rules实现约定接口的寄存器模型。原始厂商事实以field_evidence七维事实及原PDF定位为准；source conflicts、undefined input和未实施事件方面必须按policy排除，不能猜测硬件行为。inventory_field_id仅作追踪，字段位置使用候选field/bits/candidate_bit_mask。数字reset必须应用known mask、epoch、EEPROM/orderable/模式前提；未知位不补零。

严格区分直接软件存储、动作触发、动态读状态、读清、完成时刻及条件写入。RO不能自动写成恒值；写触发不能写成普通RW镜像；EEPROM锁定不等于TMP117 volatile write无效；read_as0不自动意味着操作完成。按冻结的事件接口和调度实现已纳入事件，未纳入功能保留排除。每个案例使用独立合法基线，并保持保留位输入/锁/模式/commit前置条件。

请只以本轮完整展开且SHA锁定的prompt、IR、policy、harness、接口为输入生成代码；不要读取历史模型得分或参考源码来构造答案。输出代码与实现的范围/排除说明；所有响应、重试、参数和版本由运行者原样归档。调用不在本步执行。
'''
write(OUT/'GENERATION_PROMPT.zh.md',prompt)
template={'status':'TEMPLATE_NOT_EXECUTED','production_generation_ready':False,'protocol_id':'TO_BE_ASSIGNED_AFTER_ADMISSION','model_name':None,'model_revision':None,'provider_or_local_runtime':None,'sampling_parameters':None,'seed_or_explicit_unavailable':None,'system_prompt_verbatim':None,'user_prompt_expanded_per_chip_sha256':None,'policy_sha256':sha(OUT/'candidate_source_policy.json'),'candidate_ir_files':{p.name:sha(p) for p in sorted((OUT/'candidate_ir').glob('*.json'))},'harness_sha256':None,'source_manifest_sha256':sha(OUT/'reviewed_source_manifest.json'),'interface_and_event_contract_sha256':None,'dependencies_and_command_sha256':None,'coverage_plan_sha256':None,'exclusion_inventory_sha256':None,'grouping_unit':'chip -> model -> repeat, predeclared','historical_results_as_input':False,'gate':'all required hashes and exact prompt supplied only after new admission'}
dump(OUT/'generation_context_template.json',template)
signoff={'review_id':'independent-source-admission-20261012.1','signed_date':'2026-10-12','timezone':'Asia/Shanghai','signer':'Codex independent AI source-review orchestrator','human_signature':False,'task_completion':'COMPLETE_REVIEW_AND_CANDIDATE_DELIVERY','source_admission_verdict':'REPAIR','production_generation_ready':False,'scope':{'chips':20,'inventory_fields':572,'dimensions':4004,'source_pdfs':21},'counts':counts,'source_classes':['MANUFACTURER_FACT','ABSTRACTION_ASSUMPTION','UNDEFINED_BEHAVIOR','SOURCE_CONFLICT'],'unresolved_named_conflicts':['TMP117','INA3221','TPS23861'],'all_discovered_conflicts':'conflict_ledger.json','official_manufacturer_errata_claimed':False,'field_evidence_sha256':sha(OUT/'field_evidence.json'),'expert_returns_sha256':sha(OUT/'expert_returns.json'),'preservation_verification_sha256':sha(OUT/'preservation_verification.json'),'performed':['local original PDF text review','selected critical page visual review','field-by-field evidence disposition','candidate-only attribute repairs','source excerpt and structural/hash verification'],'not_performed':['models','reference admission','hardware','SCNet','external API','current vendor website byte verification'],'stage':'M4 PARTIALLY_PASSED; unchanged','recommendation':'new source-scoped harness admission then exact new generation input freeze'}
dump(OUT/'independent_signoff.json',signoff)
candidate_inputs=['candidate_source_policy.json','reviewed_source_manifest.json','field_evidence.json','revision_candidates.json','applied_candidate_patches.json','conflict_ledger.json','register_scope_gaps.json','INPUT_FREEZE_RECOMMENDATION.md','GENERATION_PROMPT.zh.md','generation_context_template.json']
paths=[OUT/x for x in candidate_inputs]+sorted((OUT/'candidate_ir').glob('*.json'))
dump(OUT/'input_freeze_candidate_manifest.json',{'version':'independent-source-admission-20261012.1','status':'REVIEWABLE_SNAPSHOT_ONLY','production_generation_ready':False,'reason':'New harness and event/interface contract not implemented; conditional and repair gates open','source_certification':'572 fields reviewed and classified, not all PASS','files':{str(p.relative_to(OUT)).replace('\\','/'):sha(p) for p in paths},'prospective_harness_sha256':None,'source_pdfs':{s['source_path']:s['sha256'] for s in sources},'do_not_modify':['d2d/ir','test_d2d_blackbox.py','historical model results','existing protocol_v2 tree']})
write(OUT/'README.md','# 独立来源审校交付索引\n\n主结论与签审：[INDEPENDENT_SIGNOFF.md](INDEPENDENT_SIGNOFF.md)。\n\n- 输入冻结建议：[INPUT_FREEZE_RECOMMENDATION.md](INPUT_FREEZE_RECOMMENDATION.md)；当前正式冻结不准入。\n- 572字段快速结论：field_verdicts.csv；4004维度原文证据：dimension_evidence.csv / field_evidence.json。\n- 84差异记录：DIFFERENCES.md / revision_candidates.json；候选输入：candidate_ir/、candidate_source_policy.json。\n- 来源身份：SOURCE_IDENTITIES.md / reviewed_source_manifest.json；未解决冲突：conflict_ledger.json。\n- 审校材料冻结：audit_bundle_manifest.json；输入候选字节快照：input_freeze_candidate_manifest.json。\n- 保护证明：preservation_verification.json；分区签审与契约：partitions/、expert_returns.json。\n\n复现仅需现有Python与PyMuPDF：prepare.py是仅首次提取/建立baseline用，不要覆盖本轮before基线；consolidate.py整合与保护复核，finalize.py写签审/冻结候选。所有脚本只写新目录。\n\n唯一下一步：在独立新目录落实契约与新harness、验证门控后再冻结正式生成。\n')
# Freeze all present audit artifacts after the reports are written. Self-hash intentionally excluded.
files=[p for p in OUT.rglob('*') if p.is_file() and p.name!='audit_bundle_manifest.json' and '__pycache__' not in p.parts]
dump(OUT/'audit_bundle_manifest.json',{'review_id':'independent-source-admission-20261012.1','date':'2026-10-12','status':'REVIEW_COMPLETE_SOURCE_ADMISSION_REPAIR','production_generation_ready':False,'files':{str(p.relative_to(OUT)).replace('\\','/'):sha(p) for p in sorted(files)},'source_files':{s['source_path']:s['sha256'] for s in sources},'scope_count':{'chips':20,'fields':572,'dimensions':4004}})
print(json.dumps({'signed':signoff['source_admission_verdict'],'counts':counts,'candidate_patches':q['candidate_ir_attribute_patches'],'frozen_audit_files':len(files),'final_report':str(OUT/'INDEPENDENT_SIGNOFF.md')},ensure_ascii=False))
