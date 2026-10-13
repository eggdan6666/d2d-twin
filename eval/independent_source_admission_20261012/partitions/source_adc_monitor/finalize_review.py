"""Create source review documentation and candidate-only changes; no protected writes."""
import json, hashlib
from pathlib import Path
from collections import Counter
O=Path(__file__).resolve().parent
B=O.parents[1]
F=json.loads((O/'fields.json').read_text(encoding='utf-8'))
K={(x['chip'],x['register'],x['field']):x for x in F}
S=json.loads((O/'sources.json').read_text(encoding='utf-8'))
G=json.loads((O/'register_gaps.json').read_text(encoding='utf-8'))
Find=json.loads((O/'findings.json').read_text(encoding='utf-8'))
I={c:json.loads((B/'review_inputs'/f'{c}.json').read_text(encoding='utf-8')) for c in sorted({x['chip'] for x in F})}
def dump(n,x):(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
PATCHES=[]
def patch(c,r,f,prop,new,dim='access',certainty='MANUFACTURER_FACT'):
    reg=next(z for z in I[c]['ir']['registers'] if z['name']==r)
    oldobj=reg if f is None else next(z for z in reg['fields'] if z['name']==f)
    ll=K[(c,r,f)]['dimensions'][dim]['locators'] if f is not None else list({json.dumps(t,sort_keys=True):t for z in F if z['chip']==c and z['register']==r for t in z['locators']}.values())
    if c=='INA3221' and r=='CONFIG' and f=='RST' and prop=='desc':
        ll=ll+K[('INA3221','MASK_ENABLE','PVF')]['dimensions']['read_clear']['locators']
    PATCHES.append({'chip':c,'register':r,'field':f,'property':prop,'old':oldobj.get(prop),'new':new,'certainty':certainty,'locators':ll,'application_scope':'candidate input only; never apply to old IR or historical model prompts'})
patch('TMP117','CONFIG','HIGH_ALERT','desc','R, reset 0. In Alert mode (T/nA=0), read CONFIG clears HIGH_Alert; in Therm mode (T/nA=1), CONFIG read does not clear, temperature conversion > high limit sets and < low limit clears. Dynamic event model required.','read_clear')
patch('TMP117','CONFIG','LOW_ALERT','desc','R, reset 0. In Alert mode (T/nA=0), read CONFIG clears LOW_Alert; in Therm mode (T/nA=1), always reads 0. No unconditional read-clear annotation.','read_clear')
patch('TMP117','CONFIG','HIGH_ALERT','read_action','conditional_clear','read_clear')
patch('TMP117','CONFIG','LOW_ALERT','read_action','conditional_clear','read_clear')
patch('TMP117','CONFIG','CONV','desc','CONV codes 000..111 all defined. Table7-7 continuous cycle time depends on AVG: default CONV=100 gives 1s for all AVG settings; 101/110/111 give4/8/16s. One-shot duration depends on AVG and is independent of CONV.','legal_encoding')
patch('TMP117','CONFIG','EEPROM_BUSY','desc','R status, mirror of EEPROM_UL[14]. Busy=1 while POR EEPROM loading or programming;0 means ready. POR loading approximately1.5ms; programming a cell typically7ms. Reads do not clear Busy; wait Busy=0 before next programming write.','trigger_completion')
patch('TMP117','EEPROM_UL','EEPROM_BUSY','desc','R status, mirror of CONFIG[12]. Busy=1 while POR reset load or programming;0 means ready. Not a read-clear field. Reset0 applies after POR load complete.','trigger_completion')
patch('TMP117','EEPROM_UL','EUN','desc','EUN0: writes to EEPROM mapped addresses update volatile digital registers but do not program EEPROM. EUN1: writes to programmable registers program backing EEPROM only when ready. Wait Busy0 before further writes; general-call reset clears EUN and reloads EEPROM.','conditional_write')
patch('TMP117','EEPROM_UL',None,'desc','EEPROM unlock: EUN[15] R/W0; Busy[14] R0 and mirror CONFIG[12]; Reserved[13:0] R0. Locked writes to EEPROM addresses still update volatile digital registers; EUN1 permits NVM programming when Busy0. Programming typical7ms, no writes until Busy0.','conditional_write')
patch('TMP117','CONFIG','SOFT_RESET','desc','Same-file unresolved source conflict: Figure7-14 bit1 is R0, Table7-6 continued is R/W0 and says write1 triggers2ms software reset and always reads0. Any table-text-priority action profile is explicitly conditional; no official erratum established.','access',certainty='SOURCE_CONFLICT')
patch('TMP117','DEVICE_ID','ID','desc','RO aggregate ID contains revision[15:12] and DID[11:0]. DID117h is consistent; revision reset is Figure7-22 R-x versus Table7-15 0h. Main comparison mask0FFF across reset/snapshots; retain source conflict.','reset',certainty='SOURCE_CONFLICT')
patch('TMP117','DEVICE_ID',None,'desc','RO device ID register: low12 DID117h known; upper4 revision bits unresolved R-x/0h source conflict. Full0117h is conditional revision0 profile, not an unconditional cross-revision reset value.','reset',certainty='SOURCE_CONFLICT')
patch('TMP117','CONFIG',None,'desc','Factory CONFIG0220h with EEPROM-backed mask07FC; MOD1 is nonpersistent. HIGH/LOW read clear only in Alert mode T/nA0; Therm mode has threshold/hysteresis HIGH and LOW0, CONFIG read does not clear alert flags. DATA_READY clears on CONFIG or TEMP reads; Busy mirrors unlock Busy and is temporal. Soft_Reset Figure/table access conflict retained.','read_clear')
patch('TMP117','TEMP_OFFSET','OFF','desc','16-bit signed temperature offset; saturates result at temperature output range limits. Factory reset0 is EEPROM-backed per Table7-3 note1, so programmed EEPROM can change its reset.','reset')
for gap in G:
    reg=next(z for z in I['TMP117']['ir']['registers'] if z['name']==gap['register'])
    PATCHES.append({'chip':'TMP117','register':gap['register'],'field':None,'property':'desc','old':reg.get('desc'),'new':'16-bit R/W volatile scratch register backed by programmable EEPROM. Locked(EUN0) writes update volatile register and are readable but do not burn EEPROM; unlocked(EUN1) writes program backing memory. Reset loads persistent manufacturing/user contents, numerical value unknown. No writes during Busy. EEPROM2 additionally has conflicting reset0000 title vs detailedxxxx/diagramR/W-x, retained unresolved.','certainty':gap['evidence_class'],'locators':gap['locators'],'application_scope':'candidate input only; old IR remains preserved'})
for c,r in [('INA219','CONFIGURATION'),('INA226','CONFIG'),('INA3221','CONFIG')]:
    patch(c,r,'RST','desc','Write1 requests system reset and the bit self-clears. Compare default registers and RST0 only after reset completion; instantaneous always0 is an explicit atomic-model assumption. INA3221 software reset holds PV output until power-valid detection finishes.' if c=='INA3221' else 'Write1 requests system reset and the bit self-clears. Compare default registers and RST0 only after reset completion; instantaneous always0 is an explicit atomic-model assumption.','trigger_completion')
    patch(c,r,'RST','read_as',None,'trigger_completion',certainty='ABSTRACTION_ASSUMPTION')
for r,f in [('SHUNT_VOLTAGE','SV'),('BUS_VOLTAGE','BD'),('BUS_VOLTAGE','RSV_2'),('BUS_VOLTAGE','CNVR'),('BUS_VOLTAGE','OVF')]:
    patch('INA219',r,f,'reset',None,'reset',certainty='UNDEFINED_BEHAVIOR')
for r in ['SHUNT_VOLTAGE','BUS_VOLTAGE']:
    patch('INA219',r,None,'reset',None,'reset',certainty='UNDEFINED_BEHAVIOR')
patch('INA219','BUS_VOLTAGE','RSV_2','desc','Unlabeled bit2 of read-only BUS_VOLTAGE. Numeric POR and always-zero behavior are not specified in Table2/Figure24; exclude these oracles.','reserved_policy',certainty='UNDEFINED_BEHAVIOR')
patch('INA219','BUS_VOLTAGE','CNVR','desc','Hardware conversion-ready after conversions/averaging/multiplication. Register detail p23 says POWER read clears and active new MODE write clears; p10 instead says Status read/convert pin and any CONFIG write. Preserve unresolved source conflict; select no single unconditional read-clear oracle.','read_clear',certainty='SOURCE_CONFLICT')
for r,f in [('CONFIG','UNNAMED_14_12'),('CALIBRATION','UNNAMED_15'),('MASK_ENABLE','UNNAMED_9_5')]:
    patch('INA226',r,f,'access','UNSPEC','access',certainty='UNDEFINED_BEHAVIOR')
    patch('INA226',r,f,'desc','Unlabeled reserved positions with defined POR bits in a register-level R/W table. No per-bit RO or hardwired read constant is specified. Preserve reset values in legal writes; exclude nondefault access assertions.','access',certainty='UNDEFINED_BEHAVIOR')
patch('INA226','MASK_ENABLE','CVRF','desc','Hardware managed. Set after all conversions/averaging/multiplications complete; reading MASK_ENABLE clears, CONFIG write clears except MODE0/4 powerdown. No ordinary RW persistence.','read_clear')
patch('INA226','MASK_ENABLE','AFF','desc','Hardware managed. LEN1: MASK_ENABLE read clears latched AFF. LEN0: next no-alert conversion clears. CONFIG-write clear conflicts between p13 and p27; quarantine that action pending explicit profile.','conditional_write',certainty='SOURCE_CONFLICT')
patch('INA226','DIE_ID','ID','desc','RO identification. Table7-1 gives2260/2261 by country-of-origin; Table7-15 POR row is all0. Preserve source conflict and exclude fixed numeric reset in main profile. Do not treat source-table selection as official erratum.','reset',certainty='SOURCE_CONFLICT')
patch('INA3221','MASK_ENABLE','TCF','desc','Hardware timing-control status with original R/W source label. Not read-clear; reinitialized on power cycle or software reset. Default high/RW1/register0002 support bit1, but detailed reset literal11h is inconsistent and retained as a source representation conflict.','reset',certainty='SOURCE_CONFLICT')
patch('INA3221','MASK_ENABLE','CVRF','desc','Hardware conversion-ready, original source R/W label. Set when all enabled channel conversions complete. MASK_ENABLE read clears; CONFIG write clears except powerdown/disable MODE0/4. No ordinary software-written status persistence.','read_clear')
patch('INA3221','SHUNT_SUM_LIMIT','SVL','desc','Inventory aggregate[15:1] contains source SIGN[15] plus SVL[14:1]. Table8-31 RW/reset7FFE conflicts with Table8-32 R/reset0. Main profile reset checks only registermask8001; all0E write/protection oracles excluded. Retain source conflict.','access',certainty='SOURCE_CONFLICT')
patch('ADS1115','CONFIG','OS','desc','Operational status/action, not ordinary storedRW. Write0 no effect; write1 in powerdown starts one conversion, write1 while converting no effect. Read0=converting/read1=idle. Use MODE1 idle prerequisite and completion event, not write-equals-read persistence.','access')
patch('ADS1115','CONFIG','COMP_LAT','desc','0 nonlatching,1 latching comparator. Reading CONVERSION or successful SMBus alert response clears asserted latched ALERT/RDY output; COMP_LAT configuration field does not itself read-clear.','read_clear')
patch('ADS1220','CONFIG2','PSW','desc','Low-side switch control:0 open,1 closes on START/SYNC and opens on POWERDOWN. In single-shot mode switch remains closed between conversions if PSW1; single conversion completion does not open it.','trigger_completion')
for r in ['CONFIG0','CONFIG1','CONFIG2','CONFIG3']:
    patch('ADS1220',r,None,'conversion_write_side_effect',{'single_shot_write':'starts/restarts one conversion','write_during_conversion':'restarts current conversion','write_from_powerdown':'wakes and starts one conversion irrespective CM','continuous_start':'CM1 followed by START/SYNC'},'trigger_completion')
dump('ir_patches.json',PATCHES)

PREHANDLED={'TMP117_REV_RESET_CONFLICT':'existing v2 DEVICE_ID known_mask0FFF already handles bounded reset','TMP117_MOD_ONE_SHOT_BOUNDARY':'existing v2 normalizes2->0 and excludes3 persistence; completion/event remains conditional','INA3221_0E_SOURCE_CONFLICT':'existing v2 knownmask8001/exclude_writes already handles central conflict','ADS1220_RESERVED_ALWAYS_WRITE_ZERO':'existing v2 fixedwrite0/only0 already handles illegal bit1 write','RESERVED_NONDEFAULT_WRITE_UNDEFINED':'existing v2 quarantines MASK.RSVD15; six limit Reserved fields newly require separation'}
for x in Find:
    x['prior_policy_handling']=PREHANDLED.get(x['id'],'NEW_OR_MORE_PRECISE_SOURCE_REVIEW_CANDIDATE')
dump('findings.json',Find)

conflicts=[]
for cid,c,r,f,d in [('TMP117_REV_RESET_CONFLICT','TMP117','DEVICE_ID','ID','reset'),('TMP117_SOFT_RESET_SOURCE_CONFLICT','TMP117','CONFIG','SOFT_RESET','access'),('TMP117_EEPROM2_RESET_SOURCE_CONFLICT','TMP117','EEPROM2',None,None),('INA219_CNVR_CLEAR_SOURCE_CONFLICT','INA219','BUS_VOLTAGE','CNVR','read_clear'),('INA226_AFF_CONFIG_CLEAR_SOURCE_CONFLICT','INA226','MASK_ENABLE','AFF','conditional_write'),('INA226_DIE_ID_RESET_SOURCE_CONFLICT','INA226','DIE_ID','ID','reset'),('INA3221_0E_SOURCE_CONFLICT','INA3221','SHUNT_SUM_LIMIT','SVL','access'),('INA3221_TCF_RESET_LITERAL_CONFLICT','INA3221','MASK_ENABLE','TCF','reset')]:
    z=G[1] if f is None else K[(c,r,f)]['dimensions'][d]
    conflicts.append({'conflict_id':cid,'conflict_type':'INTERNAL_MANUFACTURER_PDF_INCONSISTENCY','claim':z['fact'],'source_or_locator':z['locators'],'competing_values_or_interpretations':z['candidate_rule'],'recommended_resolution':'retain unresolved; main-profile mask or exclude disputed action; any alternate source-priority profile explicitly named and never described as official erratum'})
dump('conflicts.json',conflicts)
tot=Counter(x['overall_status'] for x in F)
qc=json.loads((O/'quality_checks.json').read_text(encoding='utf-8'))
qc['total_status_counts']=dict(tot)
qc['ir_patch_count']=len(PATCHES)
qc['unresolved_conflict_count']=len(conflicts)
qc['locator_roundtrip']='Each excerpt generated directly from separately opened original PDF and exact normalized phrase; table anchor used when present.'
dump('quality_checks.json',qc)

report='''# 6器件独立来源审校签审候选

日期：2026-10-12。任务：source_adc_monitor。审校者为独立 AI 专家子任务；本文不代表人类签字，不推进M4，也不证明实物行为。遵循项目 sci-skills-paper-deep-reading 与PDF阅读工作流。

已审154/154个inventory字段，每字段七维，共1078条维度记录，并覆盖TMP117的三个空字段EEPROM寄存器。输入中的报告、policy、inventory、manifest均为待审对象；不以参考通过、历史分数或原IR自述作证据。证据限于6份本地完整原始厂商PDF的实际相关全页，使用独立SHA-256、PDF原生提取与9张关键冲突页面渲染目视核对。

| 器件 | 字段 | PASS | REPAIR | CONDITIONAL | EXCLUDE |
|---|---:|---:|---:|---:|---:|
'''
for c in I:
    t=Counter(x['overall_status'] for x in F if x['chip']==c)
    report+=f"| {c} | {sum(t.values())} | {t['PASS']} | {t['REPAIR']} | {t['CONDITIONAL']} | {t['EXCLUDE']} |\n"
report+='''
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
'''
(O/'REVIEW.md').write_text(report,encoding='utf-8')
result={'contract_version':'1.0','expert_skill':'sci-skills-paper-deep-reading','project_id':'d2d-twin','paper_family':'M','stage_id':'M4','task_id':'source_adc_monitor','task_status':'COMPLETE','inputs_reviewed':['eval/protocol_v2_20261012/REPORT.md','eval/protocol_v2_20261012/SOURCE_POLICY_REVIEW.md','eval/protocol_v2_20261012/LEGAL_DOMAIN_SUPPLEMENT.md','eval/protocol_v2_20261012/INDEPENDENT_REPAIR_REVIEW.md','eval/protocol_v2_20261012/source_policy.json (common rules + all six chip policies)','eval/protocol_v2_20261012/field_policy_inventory.json (all154 assigned identities)','eval/protocol_v2_20261012/protocol_manifest.json']+[s['source_path'] for s in S],'outputs':[str((O/n).relative_to(O.parents[3])).replace('\\','/') for n in ['fields.json','findings.json','register_gaps.json','ir_patches.json','sources.json','conflicts.json','quality_checks.json','REVIEW.md','expert_return.json']],'evidence_status':['VERIFIED_USER_MATERIAL: input reports, inventory, candidate IR/policy/manifest read as audit objects','VERIFIED_SOURCE: local original PDF relevant pages and semantic sections; eight conflicts retained','EXECUTED_LOCAL: independent SHA, PDF extraction,9 source-page renders visually inspected,154identity/1078dimension structured validation','NOT_EXECUTED: harness/reference/model/SCNet/hardware, external source download or official erratum verification'],'assumptions':['Local exact PDF byte versions define current source boundary','Nonapplicable dimensions are reviewer scope judgements, explicitly marked abstraction','Completed reset can be atomic only in a named abstract profile','No new mode register numerical normalization inferred from operating-state powerdown','EEPROM factory profile distinct from user-programmed persistent image'],'author_input_needed':[],'manual_actions':[],'quality_checks':['154 inventory identities covered exactly once; all seven dimensions present','six rawPDF independent hashes match reviewed input metadata','source locator excerpts are exact normalized primaryPDF extracts','separate correct-existing-policy versus new findings','source conflicts preserved without fixed disputed numerical patches','only new task partition written'],'conflicts':conflicts,'conflict_resolution_status':'UNRESOLVED','merge_permission':'orchestrator_only','recommended_next_action':'Orchestrator merges evidence into an independently versioned candidate frozen generation input package and lists all new-harness conditions/exclusions; do not promote existing v2.','stage_acceptance_recommendation':'REPAIR'}
dump('expert_return.json',result)
print(json.dumps({'patches':len(PATCHES),'status':dict(tot),'conflicts':len(conflicts)},ensure_ascii=True))
