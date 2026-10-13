"""Independent primary-source review. Only writes to this partition, never executes models."""
from pathlib import Path
import json, hashlib, collections, copy, re

HERE=Path(__file__).resolve().parent
OUT=HERE.parents[1]
ROOT=OUT.parents[1]
BASE=ROOT/'eval/protocol_v2_20261012'
CHIPS=['HDC2021','LM83','TMP461','TPS23861']
INPUTS=['REPORT.md','SOURCE_POLICY_REVIEW.md','LEGAL_DOMAIN_SUPPLEMENT.md','INDEPENDENT_REPAIR_REVIEW.md','source_policy.json','field_policy_inventory.json','protocol_manifest.json']
review={c:json.loads((OUT/'review_inputs'/f'{c}.json').read_text(encoding='utf-8')) for c in CHIPS}
documents={n:(BASE/n).read_text(encoding='utf-8') for n in INPUTS}
for n in INPUTS[4:]: json.loads(documents[n])

def dump(name,data):
    (HERE/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
versions={'HDC2021':'SNAS773A, December 2019, revised June 2020','TMP461':'SBOS722B, June 2015, revised August 2016','TPS23861':'SLUSBX9I, March 2014, revised July 2019','LM83':'SNIS111A wrapper; National DS101058, November 1999, copyright 2000; local file includes 2025 packaging addendum'}
def loc(c,p,sec,excerpt):
    # Locators retain actual raw-PDF text rather than an IR-name paraphrase.
    source=(OUT/'source_extracts'/c/f'p{p:03d}.txt').read_text(encoding='utf-8')
    norm=lambda s:re.sub(r'\s+',' ',s).strip()
    lines=[norm(x) for x in source.splitlines() if x.strip()]
    fixes={
      'The ALERT interrupt latch ... is not reset by reading the status register.':'is not reset by reading the status register.',
      'ALERT_THERM2':'ALERT/THERM2',
      '01h 1 (default); 03h 2; 07h 3; 0Fh 4':'01h 1 (default)',
      'Status Register flags are updated at the completion of a conversion.':'Register flags are updated at the completion of a conversion,',
      'so long as a temperature comparison does not signal a fault':'INT, so long as a temperature comparison does not signal a',
      'Before each external conversion ... external diode fault detection sequence.':'Before each external conversion the LM83 goes through an',
      'its OPEN bit in the Status Register will be set.':'its OPEN bit in the Status Register will be',
      'Temperature data is represented by an 8-bit, two’s complement byte':'an 8-bit, two’s complement byte',
      'VDUV and VPUV bits ... follow the state of VDD and VPWR supply rails.':'supply rails.',
      'ensure that port power good status ... is also set':'ensure that port power good status in',
      'provided that the condition ... is not present anymore':'provided that the condition that caused the setting of the flags is not present',
      '0 = Clear-on-read mode; 1 = Comparator mode':'1 = Comparator mode',
      'RESET or POR ... Reserved':'Reserved',
      'RESAL: ... equivalent to a power-up reset.':'equivalent to a power-up reset.',
      'Command = 41h':'Command = 41h with 1 Data Byte, Read Only',
      '41 Firmware Revision':'Firmware',
      'POR N/A':'N/A',
      '3.5 ms':'3.5',
      'Writing a “1” at POFFn and PWONn ... powers off the port.':'off the port.',
      'Pushbutton power on ignored. Port follows Auto Mode rules':'Pushbutton power on ignored. Port follows Auto Mode',
      'automatically locks the access ... stores permanently':'automatically locks',
      'AA AA AA AA':'RESET or POR VALUE AA AA AA AA',
      'VDUV and VPUV bits ... follow the state of VDD and VPWR supply rails.':'supply rails.',
    }
    if c=='TPS23861' and p==56 and excerpt=='Represents the most recent classification and detection results':
        excerpt='The value of CLASS Pn is the most recent classification'
    excerpt=fixes.get(excerpt,excerpt)
    if ': POR ' in excerpt and c=='TMP461' and p==17:
        ir_name=excerpt.split(':')[0]
        addr=next(x['addr'] for x in review[c]['ir']['registers'] if x['name']==ir_name)[2:]
        excerpt=next(x for x in lines if (x.startswith(addr+' ') and 'Register' in x) or (ir_name=='ONE_SHOT' and 'One-Shot Start Register' in x))
    if ' power up default ' in excerpt and c=='LM83':
        if p==15 and 'MID' in excerpt:excerpt='(Read Address FEh) Default value 01h.'
        elif p==16 and 'TCS' in excerpt:excerpt='Power up default is T_CRIT = 127˚C.'
        elif p==16:excerpt='Power up default is LHIGH = RD1HIGH=RD2HIGH=RD3HIGH = 127˚C.'
        elif 'TEMP_' in excerpt:excerpt='D7–D0: Temperature Data. One LSB = 1˚C. Two’s complement format.'
        else:excerpt='Power up default is with all bits “0” (zero).'
    if c=='LM83' and p==14 and excerpt.startswith('TEMP_'):
        name={'TEMP_LOCAL':'Read Local Temperature','TEMP_D2':'Read D2 Remote','TEMP_D1':'Read D1 Remote','TEMP_D3':'Read D3 Remote'}[excerpt]
        excerpt=next(x for x in lines if name in x)
    if c=='LM83' and p==14 and excerpt=='CONFIG':
        excerpt=next(x for x in lines if 'Read Configuration' in x)
    if c=='TPS23861' and excerpt.endswith('RESET or POR VALUE'):
        excerpt=next(x for x in lines if ('POR VALUE' in x) and (x.startswith('RESET') or x.startswith('POR')))
    if norm(excerpt) not in norm(source):
        raise ValueError(f'Unmatched excerpt {c} p{p} {excerpt!r}')
    return {'pdf_page':p,'printed_page':p-1 if c=='LM83' else p,'table_or_section':sec,'excerpt':norm(excerpt)}
def dim(status,fact,rule,locators,cls='MANUFACTURER_FACT',applicable=True):
    return {'status':status,'fact':fact,'candidate_rule':rule,'evidence_class':cls,'applicable':applicable,'locators':locators}
FIELDS=[]; FINDINGS=[]; PATCHES=[]; GAPS=[]
def finding(fid,c,targets,problem,old,candidate,locators,severity='MAJOR'):
    FINDINGS.append({'id':fid,'chip':c,'targets':targets,'problem':problem,'old':old,'candidate_rule':candidate,'locators':locators,'severity':severity})
def patch(c,r,f,prop,old,new,locators,certainty='MANUFACTURER_FACT',op='replace'):
    PATCHES.append({'chip':c,'register':r,'field':f,'property':prop,'old':old,'new':new,'certainty':certainty,'locators':locators,'op':op})
def gap(c,r,addr,problem,rule,locators):
    GAPS.append({'chip':c,'register':r,'address':addr,'problem':problem,'candidate_rule':rule,'status':'REPAIR','locators':locators})
def mask(bits):
    b=str(bits).split(':');hi=int(b[0]);lo=int(b[-1]);return ((1<<(hi-lo+1))-1)<<lo,lo
def base_field(c,row,reg,field,p,sec,reset,access,quote):
    m,lo=mask(row['bits']); width=m.bit_count(); ev=[loc(c,p,sec,quote)]
    dimensions={
      'reset':dim('PASS',f'原始手册在所列位置给出寄存器初值 0x{reset:02X}；本字段初值为 {(reset&m)>>lo}。',{'known_mask':hex(m),'expected_register':hex(reset),'expected_field':(reset&m)>>lo,'scope':'POR immediately after reset and before any new measurement/event'},ev),
      'access':dim('PASS',f'原始手册定义本字段所属寄存器/行访问为 {access}。',{'access':access,'read_address':reg['addr'],'storage_scope':'direct register only, with legal surrounding bits'},ev),
      'legal_encoding':dim('PASS',f'位宽为 {width}，数据/位图为完整字段；未列出独立保留编码。',{'legal_values':list(range(1<<width)),'scope':'encoding/storage; no claim of physical measurement reachability'},ev,'ABSTRACTION_ASSUMPTION'),
      'read_clear':dim('PASS','此配置/数据字段的所列来源未定义读取清除动作。',{'applicable':False,'absence_of_action_is_scope_annotation':True,'never_synthesize_a_clear_side_effect':True},ev,'ABSTRACTION_ASSUMPTION',False),
      'trigger_completion':dim('PASS','该字段在所列来源中不是启动/完成状态字段。',{'applicable':False,'do_not_infer_timing':True},ev,'ABSTRACTION_ASSUMPTION',False),
      'conditional_write':dim('PASS','来源未给此字段独立的写入门控；限直接寄存器合法输入范围。',{'applicable':access=='RW','no_concurrent_events':True,'no_inference_from_passing_reference':True},ev,'ABSTRACTION_ASSUMPTION',access=='RW'),
      'reserved_policy':dim('PASS','该字段是已命名功能/数据字段。',{'applicable':False,'surrounding_reserved_bits_obey_separate_rules':True},ev,'ABSTRACTION_ASSUMPTION',False)
    }
    out={'chip':c,'register':row['register'],'field':row['field'],'bits':row['bits'],'source_path':review[c]['source']['path'],'source_sha256':review[c]['source']['sha256'],'manual_version':versions[c],'overall_status':'PASS','old_inventory':row,'dimensions':dimensions}
    return out
def dynamic(out,ev,reason,mask_value=None):
    out['overall_status']='CONDITIONAL'
    m,_=mask(out['bits']);m=m if mask_value is None else mask_value
    out['dimensions']['access']=dim('CONDITIONAL',reason,{'access':'RO','dynamic_mask':hex(m),'reject_snapshot_equality_without_event_freeze':True,'write_protection_means_no_software_storage_write':True,'event_injection_required_for_nonzero_behavior':True},ev)
    out['dimensions']['conditional_write']=dim('CONDITIONAL','对只读动态字段，写入保护不等于两次读回必须一致。',{'reject_software_write_as_event_injection':True,'compare_with_matched_event_schedule_or_mask_dynamic_bits':True},ev,'ABSTRACTION_ASSUMPTION')
def reserved(out,ev,known=True,value=0,access_defined=False,hard_zero=False):
    out['overall_status']='CONDITIONAL' if hard_zero else 'EXCLUDE'
    m,lo=mask(out['bits'])
    out['dimensions']['legal_encoding']=dim('CONDITIONAL','保留位不提供任意编码的功能保证；有明确硬连值时仅该值适用。',{'fixed_write_field':value,'exclude_nondefault_stimuli':not hard_zero},ev,'MANUFACTURER_FACT' if hard_zero else 'ABSTRACTION_ASSUMPTION')
    out['dimensions']['reserved_policy']=dim('PASS' if hard_zero else 'CONDITIONAL','原文明确恒零/写1读0。' if hard_zero else '初值和访问/非法写后行为须分开；保留位标签不能自动证明硬连0或ROM。',{'reset_known':known,'fixed_write_field':value,'exclude_nondefault_oracle':not hard_zero,'hardware_constant':hard_zero},ev,'MANUFACTURER_FACT' if hard_zero else 'ABSTRACTION_ASSUMPTION')
    out['dimensions']['access']=dim('PASS' if hard_zero else 'EXCLUDE','原文明示写1读0。' if hard_zero else ('仅寄存器级访问标签已知，保留位无功能/翻转行为定义。' if access_defined else '逐位TYPE/access未定义，不能继承IR的RO常零。'),{'exclude_protection_assertion':not hard_zero,'read_as':0 if hard_zero else None,'preserve_or_fixed_legal_write':True},ev,'MANUFACTURER_FACT' if hard_zero else 'UNDEFINED_BEHAVIOR')
    out['dimensions']['conditional_write']=dim('CONDITIONAL','保留位写入仅使用规定/保守默认值。',{'fixed_write_field':value,'nondefault_write_behavior':'unscored'},ev,'ABSTRACTION_ASSUMPTION')

# HDC2021: every reviewed register has an explicit per-field table.
hdc_map={
 'TEMP_LOW':(21,'Table 7-8',0,'R','Temperature data- lower byte'),
 'TEMP_HIGH':(21,'Table 7-10',0,'R','Temperature data- higher byte'),
 'HUM_LOW':(22,'Table 7-12',0,'R','Humidity data- lower byte'),
 'HUM_HIGH':(22,'Table 7-14',0,'R','Humidity data- higher byte'),
 'STATUS':(23,'Table 7-16 / §7.6.5',0,'R','DRDY_STATUS TH_STATUS TL_STATUS HH_STATUS HL_STATUS'),
 'TEMP_MAX':(24,'Table 7-18 / §7.6.6',0,'R','Maximum temperature measurement data (one-shot mode only)'),
 'HUM_MAX':(24,'Table 7-20 / §7.6.7',0,'R','Maximum humidity measurement data (one-shot mode only)'),
 'INTERRUPT_ENABLE':(25,'Table 7-22 / §7.6.8',0,'R/W','DRDY_ENABLE TH_ENABLE TL_ENABLE HH_ENABLE HL_ENABLE'),
 'TEMP_OFFSET':(26,'Table 7-24 / §7.6.9',0,'R/W','Temperature offset adjustment value.'),
 'HUM_OFFSET':(27,'Table 7-26 / §7.6.10',0,'R/W','Humidity offset adjustment value.'),
 'TEMP_THR_L':(28,'Table 7-28',1,'R/W','Temperature threshold LOW value'),
 'TEMP_THR_H':(28,'Table 7-30',255,'R/W','Temperature threshold HIGH value'),
 'RH_THR_L':(29,'Table 7-32',0,'R/W','Humidity threshold LOW value'),
 'RH_THR_H':(29,'Table 7-34',255,'R/W','Humidity threshold HIGH value'),
 'DEVICE_CONFIG':(30,'Table 7-36',0,'R/W','SOFT_RES CC[2:0] HEAT_EN DRDY/INT_EN INT_POL INT_MODE'),
 'MEAS_CONFIG':(31,'Table 7-38',0,'R/W','TACC[1:0] HACC[1:0] RES MEAS_CONF[1:0] MEAS_TRIG'),
 'MANUF_ID_L':(31,'Table 7-40',73,'R','Manufacturer ID- lower byte value'),
 'MANUF_ID_H':(32,'Table 7-42',84,'R','Manufacturer ID- higher byte value'),
 'DEVICE_ID_L':(32,'Table 7-44',208,'R','Device ID - lower byte value'),
 'DEVICE_ID_H':(32,'Table 7-46',7,'R','Device ID - higher byte value')}

for row in review['HDC2021']['inventory']:
    c='HDC2021';r=row['register'];f=row['field'];reg=next(x for x in review[c]['ir']['registers'] if x['name']==r);field=next(x for x in reg['fields'] if x['name']==f)
    p,sec,rst,ac,q=hdc_map[r]; o=base_field(c,row,reg,field,p,sec,rst,{'R':'RO','R/W':'RW'}[ac],q);ev=o['dimensions']['reset']['locators']
    if r in ['TEMP_LOW','TEMP_HIGH','HUM_LOW','HUM_HIGH','TEMP_MAX','HUM_MAX']:
        dynamic(o,ev+[loc(c,11,'§7.3.3','After the measurement is completed, the device goes back to the sleep mode automatically')],'只读转换结果/峰值随真实转换更新；复位0仅在未触发测量状态断言。')
        if r in ['TEMP_MAX','HUM_MAX']:
            o['dimensions']['trigger_completion']=dim('CONDITIONAL','最高测量值只在one-shot模式定义，保存最后复位后的最高已转换值。',{'maximum_update_mode':'CC=0','event':'conversion_complete','continuous_mode_oracle':'exclude'},ev)
    if r=='STATUS' and f!='UNUSED':
        dynamic(o,ev,'状态随conversion/threshold事件变化，并有读回副作用。')
        if f=='DRDY_STATUS':
            clr=[loc(c,23,'§7.6.5','This bit is cleared when the any of the following registers is read')]
            o['dimensions']['read_clear']=dim('REPAIR','DRDY_STATUS由读0x00/01/02/03/04中任一地址清除，也由reset清除。',{'clear_on_reads':['0x00','0x01','0x02','0x03','0x04'],'event_injection':'completed_conversion','returned_value':'preclear register data','prevent_new_conversion_between_reads':True},clr)
            o['dimensions']['trigger_completion']=dim('CONDITIONAL','DRDY_STATUS表示温度和/或湿度转换完成。',{'event':'conversion_complete','do_not_confuse_MEAS_TRIG_clear_with_completion':True},[loc(c,23,'§7.6.5','temperature and/or humidity conversion is completed')])
        else:
            modepage={'TH_STATUS':14,'TL_STATUS':15,'HH_STATUS':16,'HL_STATUS':17}[f]
            me=[loc(c,modepage,'§7.3.5.2 / Figures 7-3–7-6','When the INT_MODE bit is set to 1')]+ev
            o['dimensions']['read_clear']=dim('REPAIR','INT_MODE=0时门限状态保持至读STATUS；INT_MODE=1时反映当前转换比较结果。§7.6.5读清简述需与模式正文联合读取。',{'clear_on_reads':['0x04'],'condition':'INT_MODE=0','comparator_mode':'current_conversion_threshold_result','event_injection':'threshold_violation_then_controlled_reads','no_unconditional_zero_oracle_in_comparator_mode':True},me)
            o['dimensions']['trigger_completion']=dim('CONDITIONAL','门限状态由有效转换结果与门限比较产生。',{'event':'conversion_complete','mode':'read_clear or comparator','signal_assertion_requires':'DRDY_INT_EN and corresponding interrupt enable'},me)
        o['overall_status']='REPAIR'
    if f=='UNUSED' and r in ['STATUS','INTERRUPT_ENABLE']:
        reserved(o,ev,access_defined=False)
        o['dimensions']['reset']['fact']='Table逐位RESET为0，TYPE列为空；reset可检查。'
    if r=='INTERRUPT_ENABLE' and f!='UNUSED':
        o['dimensions']['conditional_write']=dim('CONDITIONAL','使能影响DRDY/INT脚输出，状态内容不受此寄存器影响；pin门控要求DRDY/INT_EN=1。',{'write_storage':True,'pin_effect_requires':'DEVICE_CONFIG.DRDY_INT_EN=1','status_flags_not_masked':True},[loc(c,25,'§7.6.8','The Status register (address 0x04) content is unaffected by this register.')])
    if r=='DEVICE_CONFIG':
        if f=='SOFT_RES':
            e=[loc(c,30,'Table 7-36','This bit self-clears after RESET.'),loc(c,7,'§6.6 tPOR','Power-On Reset or Software Reset Duration')]
            o['overall_status']='REPAIR';o['dimensions']['access']=dim('CONDITIONAL','R/W动作位；写1触发软复位，复位之后才自清。',{'access':'RW_ACTION','read_as_zero_only_after':'reset_complete','not_instantaneous_constant_zero':True},e)
            o['dimensions']['trigger_completion']=dim('REPAIR','SOFT_RES在RESET之后自清；tPOR最大3.5 ms列为设计/特征化参数。',{'trigger':'SOFT_RES=1','completion':'software_reset_complete','reset_duration_max_ms':3.5,'timing_hardware_verified':False,'atomic_completed_reset_allowed_only_as_abstraction':True},e)
            o['dimensions']['conditional_write']=dim('CONDITIONAL','写1具有整器件复位副作用。',{'ordinary_persistence_values':[0],'action_values':[1],'reinitialize_sourced_known_bits_only':True},e)
        elif f=='CC':
            o['dimensions']['legal_encoding']=dim('PASS','Table 7-36完整定义CC=0–7；0 one-shot，1–7 periodic rates。',{'legal_values':list(range(8)),'rates_hz':[0,1/120,1/60,0.1,0.2,1,2,5]},ev)
            o['dimensions']['conditional_write']=dim('CONDITIONAL','CC选择测量模式；MEAS_TRIG在该模式下启动测量，不能用静态位存储证明转换启动/停止。',{'freeze_CC_for_storage_tests':True,'functional_start_gate':'MEAS_TRIG=1','no_analog_claim':True},ev+[loc(c,31,'Table 7-38','continuous measurements in continuous conversion mode.')])
        elif f=='INT_MODE':
            o['overall_status']='REPAIR';o['dimensions']['legal_encoding']=dim('REPAIR','原文0=Clear-on-read mode，1=Comparator mode；旧IR描述成数据就绪/中断模式。',{'legal_values':[0,1],'meanings':{'0':'clear-on-read','1':'comparator'}},ev)
            o['dimensions']['conditional_write']=dim('CONDITIONAL','INT_MODE改变门限状态和引脚行为；DRDY硬件中断要求0。',{'mode_side_effects':'status latching vs conversion comparator','DRDY_pin_requires':'INT_MODE=0 and DRDY_INT_EN=1 and DRDY_ENABLE=1'},ev+[loc(c,13,'§7.3.5.1','the INT_MODE bit must be set to 0')])
        elif f=='HEAT_EN':
            o['dimensions']['conditional_write']=dim('CONDITIONAL','heater会改变测量环境，功能示例建议激活后继续测量。',{'storage_scope':True,'conversion_schedule_and_measurement_values_not_fixed':True,'heater_temperature_limit_C':100},ev+[loc(c,11,'§7.3.4','operating temperature of the device shall be limited to below 100°C.')])
    if r=='MEAS_CONFIG':
        if f in ['TACC','HACC','MEAS_CONF']:
            lv=[0,1] if f=='MEAS_CONF' else [0,1,2]
            o['dimensions']['legal_encoding']=dim('PASS','Table 7-38明列有效编码，其余标NA。',{'legal_values':lv,'excluded_values':[x for x in range(4) if x not in lv],'illegal_encoding_behavior':'undefined/unscored'},ev)
            o['dimensions']['conditional_write']=dim('CONDITIONAL','测量配置字段改变精度/通道；纯存储刺激避免MEAS_TRIG和reserved位副作用。',{'baseline_MEAS_TRIG':0,'baseline_RSVD3':0,'functional_effect_requires_started_measurement':True},ev)
        elif f=='RSVD3': reserved(o,ev,access_defined=True)
        elif f=='MEAS_TRIG':
            e=[loc(c,31,'Table 7-38','This bit self-clears to 0 once the measurement starts.')]
            o['overall_status']='REPAIR';o['dimensions']['access']=dim('CONDITIONAL','R/W trigger；1启动测量，不属于任意值持久存储。',{'access':'RW_ACTION','persistence_values':[0],'self_clear_value':0},e)
            o['dimensions']['trigger_completion']=dim('REPAIR','MEAS_TRIG在测量开始时自清，而非转换完成时；数据就绪状态才表示conversion complete。',{'trigger':'write1','self_clear_event':'measurement_start','completion_event':'DRDY_STATUS=1 after conversion','atomic_start_is_abstraction':True},e+[loc(c,23,'§7.6.5','temperature and/or humidity conversion is completed')])
            o['dimensions']['conditional_write']=dim('CONDITIONAL','CC=0启动单次，CC非零启动连续测量。',{'one_shot':'CC=0','continuous':'CC=1..7','legal_resolution_and_channels_required':True,'ordinary_RW_persistence_excluded_for_value1':True},e)
    FIELDS.append(o)

# TMP461 register map POR independently transcribed from Table 4, not inherited from IR.
tmp_rst={'TEMP_LOCAL_HIGH':0,'TEMP_REMOTE_HIGH':0,'STATUS':None,'CONFIG':0,'CONV_RATE':8,'LOCAL_HIGH_LIMIT':127,'LOCAL_LOW_LIMIT':128,'REMOTE_HIGH_LIMIT_HIGH':127,'REMOTE_LOW_LIMIT_HIGH':128,'ONE_SHOT':None,'TEMP_REMOTE_LOW':0,'REMOTE_OFFSET_HIGH':0,'REMOTE_OFFSET_LOW':0,'REMOTE_HIGH_LIMIT_LOW':240,'REMOTE_LOW_LIMIT_LOW':0,'TEMP_LOCAL_LOW':0,'CHANNEL_ENABLE':3,'REMOTE_THERM_LIMIT':127,'LOCAL_THERM_LIMIT':127,'THERM_HYSTERESIS':10,'CONSECUTIVE_ALERT':1,'N_FACTOR':0,'DIGITAL_FILTER':0,'MANUFACTURER_ID':85}
tmp_readonly={'TEMP_LOCAL_HIGH','TEMP_REMOTE_HIGH','TEMP_REMOTE_LOW','TEMP_LOCAL_LOW','STATUS','MANUFACTURER_ID'}
tmp_alias={'CONFIG':'0x09','CONV_RATE':'0x0A','LOCAL_HIGH_LIMIT':'0x0B','LOCAL_LOW_LIMIT':'0x0C','REMOTE_HIGH_LIMIT_HIGH':'0x0D','REMOTE_LOW_LIMIT_HIGH':'0x0E'}
for row in review['TMP461']['inventory']:
    c='TMP461';r=row['register'];f=row['field'];reg=next(x for x in review[c]['ir']['registers'] if x['name']==r);field=next(x for x in reg['fields'] if x['name']==f); ac='W' if r=='ONE_SHOT' else 'RO' if r in tmp_readonly else 'RW'
    o=base_field(c,row,reg,field,17,'Table 4',tmp_rst[r] or 0,ac,f'{r}: POR '+('N/A' if tmp_rst[r] is None else f'{tmp_rst[r]:02X}h'));ev=o['dimensions']['reset']['locators']
    if r in tmp_alias: o['dimensions']['access']['candidate_rule']['write_address']=tmp_alias[r]
    if tmp_rst[r] is None:
        o['dimensions']['reset']=dim('REPAIR','Table 4该行POR为N/A；没有数值00的厂商证据。',{'known_mask':'0x00','remove_field_reset':True,'remove_register_reset':True,'runtime_value':r=='STATUS','do_not_turn_NA_into_zero':True},ev,'UNDEFINED_BEHAVIOR')
        o['overall_status']='REPAIR';patch(c,r,f,'reset',field.get('reset'),None,ev,op='remove')
    if r.startswith('TEMP_'):
        dynamic(o,ev+[loc(c,18,'§8.6.1.2','updated by the ADC each time a temperature measurement is completed.')],'温度只读数据随ADC完成而变；读高字节先锁低字节，下一条读低字节保持同次转换。')
        o['dimensions']['trigger_completion']=dim('CONDITIONAL','任一温度字节先读会锁另一个字节；读其它寄存器会终止配对保证。',{'pair_latch':True,'preferred_order':'high then low','next_read_must_be_pair':True,'conversion_complete_updates':True},[loc(c,18,'§8.6.1.2','This assurance remains valid only until another register is read.')])
    if f.startswith('RSV_'):
        reserved(o,ev+[loc(c,20 if r=='CONFIG' else 17,'§8.6.1.4' if r=='CONFIG' else 'Table 4','reserved and must always be set to 0' if r=='CONFIG' else '0')],access_defined=False)
        if r.startswith('TEMP_'): o['dimensions']['trigger_completion']['applicable']=False
    if r=='STATUS':
        e=[loc(c,19,'§8.6.1.3 / Table 5',f)]
        dynamic(o,e,'状态随ADC/比较器/外部二极管连接更新，不能以RO强制两次快照不变。');o['overall_status']='REPAIR'
        o['dimensions']['reset']=dim('REPAIR','Table 4 STATUS POR为N/A；不能将每位硬编码初始0。',{'known_mask':'0x00','runtime_reset':True},ev,'UNDEFINED_BEHAVIOR')
        if f=='BUSY':
            o['dimensions']['trigger_completion']=dim('CONDITIONAL','BUSY=1在ADC转换中；0在不转换时。SD=1要等当前cycle完成才停。',{'busy_condition':'ADC converting','completion':'ADC not converting','shutdown_wait':'current sequence completes'},e+[loc(c,20,'§8.6.1.4','stops converting when the current conversion sequence is complete')])
        elif f in ['LHIGH','LLOW','RHIGH','RLOW','OPEN']:
            o['dimensions']['read_clear']=dim('REPAIR','ALERT模式五旗读后清除的前提是致因不再存在；THERM2模式只有OPEN保持读清锁存，温度高旗遵循THERM模式。',{'read_address':'0x02','condition':'cause retired / result within limits / remote sensor functional','ALERT_mode_clear_mask':'0x7C','THERM2_latched_read_clear_mask':'0x04','cannot_clear_ALERT_pin_by_status_read':True,'event_injection_required':True},[loc(c,19,'Table 5 note (1) / §8.6.1.3','provided that the condition that caused the setting of the flags is not present anymore')])
            o['dimensions']['trigger_completion']=dim('CONDITIONAL','告警旗置位取决于有效结果、连接及模式；ALERT pin另有中断latch。',{'ALERT_pin_clear':'master reads temperature sensor address to service interrupt, flags reset and cause absent','THERM2_temperature_flags':'high-limit comparator and hysteresis; lows have no pin effect','do_not_equate_status_clear_with_pin_clear':True},[loc(c,19,'§8.6.1.3','The ALERT interrupt latch ... is not reset by reading the status register.')])
        else:
            o['dimensions']['read_clear']=dim('PASS','THERM flags在温度回到limit减hysteresis以下自动解除，不由read STATUS清除。',{'applicable':False,'auto_clear_when':'T <= THERM_limit - HYS'},[loc(c,19,'§8.6.1.3','These flags are reset automatically when the temperature returns to within the limits.')],applicable=False)
            o['dimensions']['trigger_completion']=dim('CONDITIONAL','THERM状态与温度/迟滞比较关联。',{'set':'T > THERM_limit','clear':'T <= THERM_limit - HYS','requires_controlled_measurement_events':True},e)
    if r=='CONFIG' and not f.startswith('RSV_'):
        e=[loc(c,20,'Table 6 / §8.6.1.4',f)]
        o['dimensions']['legal_encoding']=dim('PASS','Table 6每个功能位定义0/1两种模式。',{'legal_values':[0,1]},e)
        rule={'MASK1':{'pin_mask_effect_only_when':'ALERT_THERM2=0'},'SD':{'shutdown_complete':'current conversion sequence finishes','one_shot_requires':'SD=1'},'ALERT_THERM2':{'mode0':'ALERT latched/status+service','mode1':'THERM2 high thresholds with HYS'},'RANGE':{'mode0':'standard binary -40..127 C','mode1':'extended binary -64..191 C','apply_to_interpretation_of_result_and_limits':True}}[f]
        o['dimensions']['conditional_write']=dim('CONDITIONAL','CONFIG写地址09/读地址03，字段改变运行/编码/引脚功能。',rule,e)
    if r=='CONV_RATE' and f=='CR':
        o['dimensions']['legal_encoding']=dim('PASS','Table 7完整列00h–09h，08h默认16 SPS。',{'legal_values':list(range(10)),'excluded_values':list(range(10,16))},[loc(c,21,'Table 7 / §8.6.1.5','08h 16 (default)')])
    if r=='ONE_SHOT':
        e=[loc(c,21,'§8.6.1.6','The value of the data sent in the write command is irrelevant and is not stored')]
        o['overall_status']='REPAIR';o['dimensions']['access']=dim('PASS','Only pointer write0Fh,无读值；any data不是可存储寄存器字段。',{'access':'WO_ACTION','write_address':'0x0F','read_oracle':'excluded'},e)
        o['dimensions']['legal_encoding']=dim('PASS','任意8位payload均启动，payload被忽略且不存储。',{'legal_values':list(range(256)),'payload_not_stored':True},e)
        o['dimensions']['trigger_completion']=dim('CONDITIONAL','仅SD=1时启动一次选定channel的conversion+comparison cycle，结束后回shutdown。',{'start_requires':'SD=1','selected_channels':'LEN/REN','completion':'single cycle completes, then shutdown','not_software_reset':True},e)
        o['dimensions']['conditional_write']=dim('CONDITIONAL','单次启动功能以shutdown为前提；run-mode写入结果未给独立oracle。',{'required_SD':1,'run_mode_trigger_behavior':'exclude','event_model_required':True},e)
    if r=='CONSECUTIVE_ALERT' and f=='CONAL':
        o['dimensions']['legal_encoding']=dim('PASS','Table8列reg=01/03/07/0F，抽取CONAL得0/1/3/7。',{'legal_values':[0,1,3,7],'excluded_values':[2,4,5,6],'fixed_bit0':1},[loc(c,21,'Table 8','01h 1 (default); 03h 2; 07h 3; 0Fh 4')])
        o['dimensions']['trigger_completion']=dim('CONDITIONAL','告警需连续越限次数达到所定义计数。',{'violations_by_code':{'0':1,'1':2,'3':3,'7':4},'no_conversion_event_no_coverage':True},[loc(c,21,'§8.6.1.8','consecutively exceeds the high limit register value')])
    if r=='CONSECUTIVE_ALERT' and f=='FIXED_1':reserved(o,ev,known=True,value=1,access_defined=False)
    if r=='DIGITAL_FILTER' and f=='DF':
        o['dimensions']['legal_encoding']=dim('PASS','disabled/level1/level2分别0/1/2，无3定义。',{'legal_values':[0,1,2],'excluded_values':[3],'sample_averages':{'0':None,'1':4,'2':8}},[loc(c,12,'§8.3.4','Level 1 performs a moving average of four consecutive samples.')])
    if r=='N_FACTOR':
        o['dimensions']['legal_encoding']=dim('PASS','η correction twos complement数据-128..127。',{'legal_values':list(range(256)),'signed_min':-128,'signed_max':127},[loc(c,22,'§8.6.1.9','yielding an effective data range from –128 to 127.')])
    if r=='MANUFACTURER_ID':
        o['dimensions']['legal_encoding']=dim('PASS','manufacturer code明确55h。',{'read_values':[85],'write_values':[]},[loc(c,22,'§8.6.1.11','reads 55h for the manufacturer code.')])
    FIELDS.append(o)

# LM83 has a wrapper page: PDF page numbers are printed page + 1 throughout the register text.
lm_rst={'TEMP_LOCAL':0,'TEMP_D2':0,'SR1':0,'CONFIG':0,'LHS':127,'D2RHS':127,'TEMP_D1':0,'TEMP_D3':0,'SR2':0,'D1RHS':127,'D3RHS':127,'TCS':127,'MID':1}
lm_rw={'CONFIG','LHS','D2RHS','D1RHS','D3RHS','TCS'}
lm_alias={'CONFIG':'0x09','LHS':'0x0B','D2RHS':'0x0D','D1RHS':'0x50','D3RHS':'0x52','TCS':'0x5A'}
for row in review['LM83']['inventory']:
    c='LM83';r=row['register'];f=row['field'];reg=next(x for x in review[c]['ir']['registers'] if x['name']==r);field=next(x for x in reg['fields'] if x['name']==f)
    p=15 if r in ['SR1','SR2','CONFIG','MID'] or r.startswith('TEMP') else 16
    sec={'SR1':'§2.3.1','SR2':'§2.3.2','CONFIG':'§2.5','MID':'§2.4'}.get(r,'§2.2' if r.startswith('TEMP') else '§2.7' if r=='TCS' else '§2.6')
    o=base_field(c,row,reg,field,p,sec,lm_rst[r],'RW' if r in lm_rw else 'RO',f'{r} power up default '+f'{lm_rst[r]:02X}h');ev=o['dimensions']['reset']['locators']
    o['dimensions']['reset']['locators'].append(loc(c,14 if r!='MID' else 15,'§2.1 command/default table',r))
    if r in lm_alias:
        o['dimensions']['access']['candidate_rule']['write_address']=lm_alias[r]
        o['dimensions']['access']['fact']='读写指针不同但功能相同的地址镜像同一数据；只使用来源给出的写别名。'
    if r.startswith('TEMP'):
        dynamic(o,ev+[loc(c,9,'§1.1 / note10','will yield last conversion result')],'温度是last conversion的8位twos complement值；更新顺序local,D2,D1,D3，不承诺多次读取不变。')
        o['dimensions']['trigger_completion']=dim('CONDITIONAL','每通道依序转换，数据可随转换完成更新。',{'conversion_sequence':['LOCAL','D2','D1','D3'],'storage_protection_requires_frozen_schedule':True,'no_static_runtime_zero':True},[loc(c,9,'§1.1','round robin sequence takes approximately 480 ms')])
    if r in ['SR1','SR2']:
        if f.startswith('RSV'):
            reserved(o,[loc(c,15,sec,'These bits are always set to 0 and reserved for future use.')],hard_zero=True)
            o['overall_status']='PASS'
        else:
            dynamic(o,ev+[loc(c,10,'§1.2–1.3','Status Register flags are updated at the completion of a conversion.')],'状态由温度/连接事件更新；RO不保证两次读值相同。')
            if 'OPEN' in f:
                o['dimensions']['trigger_completion']=dim('CONDITIONAL','D+短到VCC/浮空令OPEN=1，短到GND/D−不会置OPEN。',{'fault_detection':'before external conversion','open_conditions':['D+ to VCC','floating D+'],'not_open_conditions':['D+ to GND','D+ to D-']},[loc(c,11,'§1.8','its OPEN bit in the Status Register will be set.')])
                o['dimensions']['read_clear']=dim('EXCLUDE','§1.8定义连接检测状态，却未明确OPEN与告警位相同的读清/恢复条件。',{'read_clear_oracle':'exclude unless separately sourced','inject_reconnection_and_conversion_for_current_status':True},[loc(c,11,'§1.8','Before each external conversion ... external diode fault detection sequence.')],'UNDEFINED_BEHAVIOR')
            else:
                e=[loc(c,10,'§1.2 / §1.3 / Figures 4–7','Status Register Bits are reset by a read of Status Register where bit is located.'),loc(c,12,'§1.9','so long as a temperature comparison does not signal a fault')]
                critical='CRIT' in f
                o['dimensions']['read_clear']=dim('CONDITIONAL','图注称所在status read清位，正文将output/flags解除与当前温度比较条件联合；重复conversion可重置位。不得把持久清零作为无条件硅事实。',{'read_address':reg['addr'],'safe_condition':'conversion below T_CRIT' if critical else 'conversion <= corresponding HIGH','read_returns_preclear_data':True,'no_new_conversion_between_reads':True,'active_fault_clear_timing':'exclude'},e,'SOURCE_CONFLICT')
                o['dimensions']['trigger_completion']=dim('CONDITIONAL','mask不阻止状态置位；只有相应报警输出被屏蔽。',{'event':'completed temperature conversion','status_not_masked':True,'output_clear_requires_read_and_retired_fault':True},[loc(c,10,'§1.3','will still be set in the Status Registers.')])
                o['overall_status']='REPAIR'
    if r=='CONFIG' and f.startswith('RSV'):
        reserved(o,[loc(c,16,'§2.5','A write of 1 will return a 0 when read.')],hard_zero=True);o['overall_status']='PASS'
    if r=='CONFIG' and not f.startswith('RSV'):
        o['dimensions']['legal_encoding']=dim('PASS','§2.5各功能位0/1定义明确。',{'legal_values':[0,1]},ev)
        o['dimensions']['conditional_write']=dim('CONDITIONAL','mask只阻止输出，不阻止温度告警status置位；INT_INV改变极性。',{'write_address':'0x09','read_address':'0x03','status_bits_not_masked':True,'signal_polarity_and_masks_separate_from_status':True},ev+[loc(c,10,'§1.3','will still be set in the Status Registers.')])
    if r in ['LHS','D2RHS','D1RHS','D3RHS','TCS']:
        o['dimensions']['legal_encoding']=dim('PASS','8位twos complement门限，1LSB=1°C；未列保留编码。',{'legal_values':list(range(256)),'format':'twos-complement 8bit, 1C/LSB'},ev+[loc(c,11,'§1.6','Temperature data is represented by an 8-bit, two’s complement byte')])
    if r=='MID':o['dimensions']['legal_encoding']=dim('PASS','厂商ID默认01h。',{'read_values':[1],'write_values':[]},ev)
    FIELDS.append(o)

# TPS23861 inventory intentionally aggregates individual port bits: preserve aggregation boundaries.
tps_meta={'INTERRUPT':(47,'§7.5.1',128),'POWER_EVENT':(50,'§7.5.3',0),'DETECT_EVENT':(51,'§7.5.4',0),'FAULT_EVENT':(52,'§7.5.5',0),'START_EVENT':(53,'§7.5.6',0),'SUPPLY_EVENT':(54,'§7.5.7',48),'PORT1_STATUS':(55,'§7.5.8.1',0),'PORT2_STATUS':(55,'§7.5.8.2',0),'PORT3_STATUS':(55,'§7.5.8.3',0),'PORT4_STATUS':(55,'§7.5.8.4',0),'POWER_STATUS':(57,'§7.5.9',0),'GENERAL_MASK':(63,'§7.5.16',128),'INTERRUPT_TIMER':(68,'§7.5.22',0),'TEMPERATURE':(71,'§7.5.25',0),'POE_PLUS':(77,'§7.5.29',0)}
tps_clear={'POWER_EVENT':'0x03','DETECT_EVENT':'0x05','FAULT_EVENT':'0x07','START_EVENT':'0x09','SUPPLY_EVENT':'0x0B'}
for row in review['TPS23861']['inventory']:
    c='TPS23861';r=row['register'];f=row['field'];reg=next(x for x in review[c]['ir']['registers'] if x['name']==r);field=next(x for x in reg['fields'] if x['name']==f)
    p,sec,rst=tps_meta[r];ac='RW' if r in ['GENERAL_MASK','INTERRUPT_TIMER','POE_PLUS'] else 'RO';o=base_field(c,row,reg,field,p,sec,rst,ac,f'{r} RESET or POR VALUE');ev=o['dimensions']['reset']['locators']
    if r in ['INTERRUPT','POWER_EVENT','DETECT_EVENT','FAULT_EVENT','START_EVENT','SUPPLY_EVENT','POWER_STATUS','TEMPERATURE'] or r.startswith('PORT'):
        dynamic(o,ev,'事件/端口/ADC数据有异步硬件来源；仅写权限保护不足以要求快照不变。')
    if r=='INTERRUPT':
        o['dimensions']['read_clear']=dim('CONDITIONAL','00h读本身非CoR；summary位按相关事件读清地址或RESET.CLRAIN清。',{'direct_read_clear':False,'clear_dependencies':list(tps_clear.values()),'global_clear':'0x1A bit7 CLRAIN','recompute_summary_from_remaining_event_latches':True},ev+[loc(c,66,'§7.5.19','CLRAIN clears all event registers and all bits in the Interrupt Register.')])
        o['dimensions']['trigger_completion']=dim('CONDITIONAL','各summary是对应事件OR，不是写入存储值。',{'event_sources':{'SUPF':'TSD|VDUV|VPUV','STRTF':'STRTn','IFAULT':'ICUTn|ILIMn','CLASC':'CLSCn','DETC':'DETCn','DISF':'DISFn','PGC':'PGCn','PEC':'PECn'},'event_injection_required':True},ev)
    if r in tps_clear:
        e=[loc(c,p,sec,'Clear-on-Read command clears all bits of the register.')]
        o['dimensions']['read_clear']=dim('CONDITIONAL','非CoR与CoR地址返回同一preclear数据，只有CoR地址清全寄存器；无受控事件不能把0→0当覆盖。',{'read_address':reg['addr'],'clear_on_read_alias':tps_clear[r],'clear_mask':'0xFF','return':'preclear value','postclear_expected':0,'new_events_blocked_between_reads':True,'event_injection_required':True,'clear_not_reset_to_POR':True},e)
        effects={'POWER_EVENT':'PGC/PEC status changes', 'DETECT_EVENT':'CLSC/DETC completed cycles; port off clears', 'FAULT_EVENT':'DISF/ICUT; POFFn or RESPn clears', 'START_EVENT':'ILIM/STRT; POFFn or RESPn clears','SUPPLY_EVENT':'TSD/VDUV/VPUV supply events'}
        o['dimensions']['trigger_completion']=dim('CONDITIONAL','来源定义事件而非任意可写flag。',{'event_source':effects[r],'global_clear':'CLRAIN','inject_events_separately_from_register_writes':True},ev)
        if r=='SUPPLY_EVENT':
            if f in ['RSV6','RSV3_0']:reserved(o,ev,access_defined=True);o['overall_status']='CONDITIONAL'
            else:
                o['dimensions']['reset']=dim('CONDITIONAL','p54只称POR VALUE=30h；RESET输入期间VPUV按VPWR阈值、VDUV在VDD保持时无影响，RESAL遵循供电轨。',{'POR_expected':'0x30','field_POR':0 if f=='TSD' else 1,'hardware_reset_not_identical_to_POR':True,'supply_conditions_explicit':True},ev+[loc(c,54,'§7.5.7 note','There is no impact on VDUV since VDD is maintained.'),loc(c,66,'§7.5.19','VDUV and VPUV bits ... follow the state of VDD and VPWR supply rails.')])
                if f in ['VDUV','VPUV']:
                    o['overall_status']='REPAIR';o['dimensions']['legal_encoding']=dim('REPAIR','VDUV是VDD UVLO事件、VPUV是VPWR UVLO事件；旧说明的检测未启用非原文。',{'read_values':[0,1],'meaning':'VDD UVLO' if f=='VDUV' else 'VPWR UVLO'},ev)
    if r.startswith('PORT'):
        e=ev+[loc(c,56,'§7.5.8 bit descriptions','Represents the most recent classification and detection results')]
        o['dimensions']['legal_encoding']=dim('CONDITIONAL','聚合ST包含CLASS[7:4]/DETECT[3:0]；CLASS5 reserved read as class0，DETECT2/7 reserved，9–12仅legacy。',{'read_encoding_subfields':{'CLASS':{'defined_values':[0,1,2,3,4,6,7,8],'reserved':{'5':'read as class0'},'unlisted':list(range(9,16))},'DETECT':{'defined_values':[0,1,3,4,5,6,8,9,10,11,12],'reserved':[2,7],'legacy_only':[9,10,11,12],'unlisted':[13,14,15]}},'write_values':[],'split_for_next_gold_ir':True},e)
        o['dimensions']['trigger_completion']=dim('CONDITIONAL','最近一次detect/class完成结果；port off清状态。',{'event':'detection/classification completes','clear_on_port_off':True,'no_direct_read_clear':True},ev)
    if r=='POWER_STATUS':
        o['dimensions']['trigger_completion']=dim('CONDITIONAL','PG表示DRAIN低于VPGT且turn-on完成后锁存；PE是port on/off。',{'PG':'latched after completed turn on, clears on port off/reset','PE':'actual port on/off','turn_off_precondition':'if PE=1 ensure PG=1 before POFF/RESP/off-mode'},ev+[loc(c,65,'§7.5.18 note','ensure that port power good status ... is also set')])
        o['dimensions']['read_clear']=dim('PASS','Power Status由关断/reset清除，不由普通读清除。',{'applicable':False,'clear_events':['port off','reset']},ev,applicable=False)
    if r=='GENERAL_MASK':
        if f in ['RSV3','RSV2','ROM1']:
            e=[loc(c,45,'Table 10','1000,0000'),loc(c,63,'§7.5.16 reset/POR row','Reserved')]
            reserved(o,e,known=False)
            o['overall_status']='EXCLUDE';o['dimensions']['reset']=dim('EXCLUDE','Table10整字节80h与详细R17[3:1] Reserved初值粒度冲突保留。',{'known_mask':'0x00','preserve_fresh_observed_value':True,'do_not_assign_numeric_reset':True},e,'SOURCE_CONFLICT')
            o['dimensions']['reserved_policy']=dim('CONDITIONAL','R17[3:1] reserved不可改初值；R不是ROM，更无器件version功能。',{'preserve_write':True,'exclude_fixed_reset_and_access_oracle':True,'conflict_id':'TPS23861_R17_SOURCE_GRANULARITY_CONFLICT'},e,'SOURCE_CONFLICT')
        elif f in ['RSV6','RSV5']:
            reserved(o,ev,access_defined=True);o['overall_status']='EXCLUDE'
        elif f=='M250':
            o['overall_status']='REPAIR';o['dimensions']['legal_encoding']=dim('REPAIR','M250选择current sense resistor；1=250mΩ、0=255mΩ，不是250ms定时。',{'legal_values':[0,1],'meanings':{'0':'255 milliohm','1':'250 milliohm'}},[loc(c,63,'§7.5.16 M250','Current-sense-resistor-selection bit.')])
            o['dimensions']['conditional_write']=dim('CONDITIONAL','M250应与外部sense resistor一致，影响ICUT/classification lookups。',{'storage_only':True,'physical_effect_requires_known_resistor':True},ev)
        elif f=='INTEN':
            o['dimensions']['conditional_write']=dim('CONDITIONAL','INTEN门控INT脚，不影响Event registers；还需要对应InterruptEnable。',{'event_registers_unaffected':True,'pin_assertion_requires':'INTEN & event enable & active summary'},[loc(c,63,'§7.5.16 note','Activating INTEN has no impact on the Event Registers.')])
        elif f=='MAINS':
            o['dimensions']['conditional_write']=dim('CONDITIONAL','MAINS影响检测电压ADC时间：0 800/s (50Hz),1 960/s (60Hz)，16采样平均。',{'storage_scope':True,'detection_duration_function_requires_ADC_events':True},ev)
    if r=='INTERRUPT_TIMER':
        if f=='ROM':reserved(o,[loc(c,68,'§7.5.22','Reserved: Bits R27[7:4] are reserved for future use.')],access_defined=True)
        else:
            o['dimensions']['legal_encoding']=dim('PASS','完整4bit N定义周期10ms*N且读回firmware最后写值。',{'legal_values':list(range(16)),'period_ms':'10*N','readback':'last_written_value, not current countdown'},[loc(c,68,'§7.5.22','the contents will be the contents last written by firmware.')])
            o['dimensions']['trigger_completion']=dim('CONDITIONAL','非零timer连续倒数、零时递交noncritical interrupts并reload；0禁用延迟。',{'critical_interrupts':'not deferred','noncritical_delivery':'counter zero','timer_countdown_not_exposed_as_readback':True,'no_physical_timing_claim':True},ev)
    if r=='TEMPERATURE':
        o['dimensions']['legal_encoding']=dim('CONDITIONAL','8bit ADC N，T=20−N*TSTEP；performance仅typical。',{'read_values':list(range(256)),'TSTEP_C':0.7,'physical_accuracy_verified':False},[loc(c,71,'§7.5.25','Temperature sensor performance is only typical')])
    if r=='POE_PLUS':
        if f=='RSVD_LO':
            e=[loc(c,46,'Table 10','0000,----'),loc(c,77,'§7.5.29','RESET or POR VALUE')]
            reserved(o,e,known=False);o['dimensions']['reset']=dim('EXCLUDE','低4位RESET为---- / 详细位表空白，不是数值0。',{'known_mask':'0x00','remove_field_reset':True,'do_not_set_zero_as_fact':True},e,'UNDEFINED_BEHAVIOR');o['overall_status']='EXCLUDE'
            patch(c,r,f,'reset',field.get('reset'),None,e,op='remove')
        else:
            o['overall_status']='CONDITIONAL';o['dimensions']['conditional_write']=dim('CONDITIONAL','host可写，Auto模式在power-on前根据PD class自动置/清；纯RW持久性必须禁止Auto分类事件。',{'static_persistence_requires':'ports in Manual/Semi-Auto, no automatic classification update','Auto_class4':'sets PoEP','Auto_class0_to3':'clears PoEP','match_ICUT_to_PoEP':'required for functional behavior'},[loc(c,77,'§7.5.29','Additionally, the bit is set when in Auto Mode'),loc(c,42,'§7.4.4','ICUT and PoEP fields are set automatically')])
            o['dimensions']['trigger_completion']=dim('CONDITIONAL','PoEP是classification完成/power-on准备产生的模式副作用之一。',{'event':'recognized PD class before power on','Auto_mutation_is_sourced_fact':True},ev)
    FIELDS.append(o)

# Differences are candidates only. No protected tree is modified.
for r in ['STATUS','ONE_SHOT']:
    reg=next(x for x in review['TMP461']['ir']['registers'] if x['name']==r)
    e=[loc('TMP461',17,'Table 4','POR N/A')]
    patch('TMP461',r,None,'reset',reg.get('reset'),None,e,op='remove')
    patch('TMP461',r,None,'runtime_value',reg.get('runtime_value'),True,e,certainty='ABSTRACTION_ASSUMPTION',op='add')
def field_desc_patch(c,r,f,new,e):
    reg=next(x for x in review[c]['ir']['registers'] if x['name']==r);fd=next(x for x in reg['fields'] if x['name']==f);patch(c,r,f,'desc',fd.get('desc'),new,e)
field_desc_patch('HDC2021','MEAS_CONFIG','MEAS_TRIG','写1在CC模式下启动测量；测量开始时自清0；转换完成由DRDY_STATUS表示。',[loc('HDC2021',31,'Table 7-38','self-clears to 0 once the measurement starts.')])
field_desc_patch('HDC2021','DEVICE_CONFIG','INT_MODE','0=Clear-on-read mode；1=Comparator mode，改变threshold status与DRDY/INT输出。',[loc('HDC2021',30,'Table 7-36','0 = Clear-on-read mode; 1 = Comparator mode')])
field_desc_patch('HDC2021','DEVICE_CONFIG','SOFT_RES','写1触发软复位，在RESET完成后自清0；完成前读值不能视为恒0。',[loc('HDC2021',30,'Table 7-36','This bit self-clears after RESET.')])
hdc_soft=next(f for r in review['HDC2021']['ir']['registers'] if r['name']=='DEVICE_CONFIG' for f in r['fields'] if f['name']=='SOFT_RES')
patch('HDC2021','DEVICE_CONFIG','SOFT_RES','read_as',hdc_soft.get('read_as'),None,[loc('HDC2021',30,'Table 7-36','This bit self-clears after RESET.')],op='remove')
for f in ['LHIGH','LLOW','RHIGH','RLOW','OPEN']:
    field_desc_patch('TMP461','STATUS',f,'动态RO告警旗：ALERT模式读STATUS且致因已消失后清；THERM2模式仅OPEN保持读清，温度告警模式依正文。',[loc('TMP461',19,'§8.6.1.3 / Table5 note1','provided that the condition ... is not present anymore')])
field_desc_patch('TPS23861','GENERAL_MASK','M250','Current-sense-resistor-selection：1=250mΩ，0=255mΩ；选择ICUT/classification look-up tables。',[loc('TPS23861',63,'§7.5.16','Current-sense-resistor-selection bit.')])
field_desc_patch('TPS23861','GENERAL_MASK','ROM1','R17[1] reserved，详细初值Reserved与总览80h粒度冲突；保持新实例观测初值，不解释为ROM/revision。',[loc('TPS23861',45,'Table10 note1','Bits labeled "R" are reserved.'),loc('TPS23861',63,'§7.5.16','R17[1]')])
field_desc_patch('TPS23861','INTERRUPT_TIMER','ROM','R27[7:4] reserved，RESET/POR明确0，写入保持0；非ROM，无非法写后行为保证。',[loc('TPS23861',68,'§7.5.22','Reserved: Bits R27[7:4]')])
field_desc_patch('TPS23861','SUPPLY_EVENT','VDUV','VDD UVLO事件；POR置1，VDD低于VUVDD_F置1；CoR地址0Bh清。',[loc('TPS23861',54,'§7.5.7','VDUV: Indicates that a VDD UVLO occurred.')])
field_desc_patch('TPS23861','SUPPLY_EVENT','VPUV','VPWR UVLO事件；POR置1，VPWR低于VPUV_F置1；RESET输入行为需按供电轨。',[loc('TPS23861',54,'§7.5.7','VPUV: Indicates that a VPWR UVLO occurred.')])
reg=next(x for x in review['TPS23861']['ir']['registers'] if x['name']=='FIRMWARE_REV');patch('TPS23861','FIRMWARE_REV',None,'addr',reg['addr'],'0x41',[loc('TPS23861',77,'§7.5.30','Command = 41h with 1 Data Byte, Read Only')])

finding('PT-HDC-TRIGGER-START','HDC2021',['MEAS_CONFIG.MEAS_TRIG'],'旧注释把开始自清写成完成自清，v2无触发完成模型时仍可能按RW持久性错判。','self-clear on conversion complete / ordinary RW',{'self_clear_event':'measurement starts','completion':'DRDY_STATUS conversion complete','exclude_trigger1_from_storage_persistence':True},[loc('HDC2021',31,'Table7-38','self-clears to 0 once the measurement starts.')])
finding('PT-HDC-STATUS-MODES','HDC2021',['STATUS.DRDY_STATUS','STATUS.TH_STATUS','STATUS.TL_STATUS','STATUS.HH_STATUS','STATUS.HL_STATUS','DEVICE_CONFIG.INT_MODE'],'漏掉DRDY多读地址清零和threshold comparator模式，旧INT_MODE描述错误。','no read_action; 0 data-ready/1 interrupt',{'DRDY_clear_reads':['0x00','0x01','0x02','0x03','0x04'],'threshold_clear':'readSTATUS with INT_MODE0','comparator':'INT_MODE1 current result','pin_gate':'DRDY_INT_EN and interrupt enable; DRDY pin also INT_MODE0'},[loc('HDC2021',23,'§7.6.5','The bit is cleared when the Status Register (0x04) is read.'),loc('HDC2021',30,'Table7-36','1 = Comparator mode'),loc('HDC2021',14,'§7.3.5.2.1','reflects the current temperature conversion result.')])
finding('PT-HDC-SOFTRESET','HDC2021',['DEVICE_CONFIG.SOFT_RES'],'self clear after RESET不能推出每次读恒0；旧read_as=0隐藏动作区间。',{'read_as':0},{'read_zero_condition':'reset_complete','reset_latency_max_ms':3.5,'atomic_reset':'explicit benchmark abstraction only'},[loc('HDC2021',30,'Table7-36','self-clears after RESET.'),loc('HDC2021',7,'tPOR','3.5 ms')])
finding('PT-TMP461-NO-POR','TMP461',['STATUS.*','ONE_SHOT.START'],'Table4 STATUS与ONE_SHOT POR=N/A，候选reset=00及各字段0缺来源。',{'register_reset':'0x00','field_reset':0},{'remove_resets':True,'runtime_status':True,'one_shot_not_stored':True},[loc('TMP461',17,'Table4','N/A')])
finding('PT-TMP461-CONDITIONAL-CLEAR','TMP461',['STATUS.LHIGH','STATUS.LLOW','STATUS.RHIGH','STATUS.RLOW','STATUS.OPEN','CONFIG.ALERT_THERM2'],'read-clear遗漏cause-retired和模式条件；读STATUS不清ALERT interrupt latch。','read_action=clear unconditional',{'mode_dependent_clear':True,'cause_absent_required':True,'ALERT_service':'master reads sensor address only when flags reset and condition absent','THERM2_mask':'0x04 latched read-clear only'},[loc('TMP461',19,'§8.6.1.3 / Table5 note1','Only bit 2 (OPEN) stays high'),loc('TMP461',19,'§8.6.1.3','is not reset by reading the status register.')])
finding('PT-TMP461-PAIR-LATCH','TMP461',['TEMP_LOCAL_HIGH.*','TEMP_LOCAL_LOW.*','TEMP_REMOTE_HIGH.*','TEMP_REMOTE_LOW.*'],'单次RO读回比较不能验证conversion动态或跨字节配对锁存。','no paired conversion model',{'dynamic_masks':True,'event_injection':True,'high_then_low_next_read':True,'third_register_read_breaks_pair_guarantee':True},[loc('TMP461',18,'§8.6.1.2','only until another register is read.')])
finding('PT-LM83-STATUS-READ','LM83',['SR1.*','SR2.*'],'温度告警读清/输出解除条件与Figure图注粒度存在差异；OPEN缺独立read-clear定义。','no read action / RO snapshots',{'safe_read_clear':'inject alarm, retire fault, freeze conversion, read containing status','active_fault_postclear_timing':'exclude','OPEN_readclear':'exclude absent explicit source'},[loc('LM83',10,'§1.2 / §1.3 / Figures4–7','Status Register Bits are reset by a read'),loc('LM83',12,'§1.9','so long as a temperature comparison does not signal a fault')])
finding('PT-TPS-ALIAS-EVENTS','TPS23861',['POWER_EVENT.EV','DETECT_EVENT.EV','FAULT_EVENT.EV','START_EVENT.EV','SUPPLY_EVENT.*','INTERRUPT.FLAGS'],'CoR返回/清零需区分五个alias与完整summary依赖；默认0的事件读0再读0没有非零覆盖。','all reset snapshots or empty readclear evidence',{'alias_map':tps_clear,'nonzero_event_injection':True,'clear_returns_preclear_data':True,'summary_recompute':True,'port_off_and_RESP_side_effects':True},[loc('TPS23861',50,'§7.5.3','Clear-on-Read command clears all bits'),loc('TPS23861',66,'§7.5.19','CLRAIN clears all event registers')])
finding('PT-TPS-SUPPLY-RESET','TPS23861',['SUPPLY_EVENT.VDUV','SUPPLY_EVENT.VPUV','SUPPLY_EVENT.TSD'],'原IR把UVLO说成检测未启用，且POR30h不可推广为任何RESET/RESAL都同值。','VDUV/VPUV detection not enabled; reset30h',{'POR':'0x30','UVLO':'supply events','RESET_pin_and_RESAL':'supply rails explicit'},[loc('TPS23861',54,'§7.5.7','VDUV: Indicates that a VDD UVLO occurred.'),loc('TPS23861',66,'§7.5.19','follow the state of VDD and VPWR supply rails.')])
finding('TPS23861_R17_SOURCE_GRANULARITY_CONFLICT','TPS23861',['GENERAL_MASK.RSV3','GENERAL_MASK.RSV2','GENERAL_MASK.ROM1'],'总览80h与详细Reserved初值粒度冲突保持；ROM1功能是误释。','numeric0 / RO / ROM revision',{'known_reset_mask':'0xF1','preserve_write_mask':'0x0E','exclude_access_mask':'0x0E','source_conflict':'UNRESOLVED','not_official_erratum':True},[loc('TPS23861',45,'Table10','1000,0000'),loc('TPS23861',63,'§7.5.16','RESET or POR ... Reserved')],'BLOCKER')
finding('PT-TPS-M250-RESERVED','TPS23861',['GENERAL_MASK.M250','INTERRUPT_TIMER.ROM'],'M250是250mΩ电阻选择，R27高位Reserved非ROM；名称错误可误导生成。','M250 250ms timer / ROM',{'M250':'250/255mohm sense resistor selector','R27':'reserved reset0 fixed-write0 no illegal-write oracle'},[loc('TPS23861',63,'§7.5.16','Current-sense-resistor-selection bit.'),loc('TPS23861',68,'§7.5.22','reserved for future use.')])
finding('PT-TPS-POEP-AUTO','TPS23861',['POE_PLUS.POEP'],'Auto class识别在power-on前改POEP；普通RW恒持久oracle可能误判正确硬件。','unconditional RW persistence',{'freeze_manual_or_semi_auto_for_storage':True,'Auto_class4_set':True,'Auto_class0_to3_clear':True,'match_ICUT':'functional prerequisite'},[loc('TPS23861',77,'§7.5.29','the bit is set when in Auto Mode'),loc('TPS23861',42,'§7.4.4','PoEP fields are set automatically')])
finding('PT-TPS-FIRMWARE-ADDRESS','TPS23861',['FIRMWARE_REV (no inventory field)'],'候选IR地址FEh，原始手册Table10与§7.5.30为41h。','0xFE',{'address':'0x41','runtime_revision':True,'do_not_fabricate_default':True},[loc('TPS23861',46,'Table10','41 Firmware Revision'),loc('TPS23861',77,'§7.5.30','Command = 41h')])

# Registers absent from the 572-field inventory still govern inventoried field behavior.
gap('TPS23861','RESTART','0x18','IR有寄存器但无fields，因而572-field清单不含8个pushbuttons。',{'split_fields':['RCL4','RCL3','RCL2','RCL1','RDET4','RDET3','RDET2','RDET1'],'write1':'trigger','write0':'no effect','Manual':'single cycle','SemiAuto_Auto':'set corresponding Detect/Class Enable','cooldown':'accepted action delayed','next_0x14_write_delay_ms':1.2,'no_numeric_reset':True},[loc('TPS23861',64,'§7.5.17','Push button register.')])
gap('TPS23861','POWER_ENABLE','0x19','8个POFF/PWON command无字段，漏掉事件清/置、status变更与模式前提。',{'split_fields':['POFF4..1','PWON4..1'],'same_port_POFF_PWON':'off wins','Off_or_SHTDWN':'on prohibited','SemiAuto_Auto_cooldown':'PWON ignored','Manual':'immediate','before_off_if_PE1':'PG must1','POFF_effects':'clear detect,fault,start,status,enables; if previously on setPGC/PEC and clearPG/PE','next_0x14_write_delay_ms':1.2,'no_numeric_reset':True},[loc('TPS23861',65,'§7.5.18','Writing a “1” at POFFn and PWONn ... powers off the port.'),loc('TPS23861',43,'Table8','Pushbutton power on ignored. Port follows Auto Mode rules')])
gap('TPS23861','RESET_CMD','0x1A','旧desc把RESAL当all-alarm、CLINP/CLRAIN当classification clear；实际为不同全局/port动作，无字段。',{'fields':{'CLRAIN7':'clear all event/interrupt bits and releaseINT','CLINP6':'releaseINT only, no event/interrupt mutation','RESAL4':'power-up equivalent reset with supply conditions','RESP3..0':'immediate port off; clear flags/status/enables; if on setPGC/PEC and clearPG/PE; cancelcooldown'},'bit5':'reserved unscored keep0','write0':'no effect','before_RESP_if_PE1':'PG must1','next_0x14_write_delay_ms':1.2,'no_numeric_reset':True},[loc('TPS23861',66,'§7.5.19','RESAL: ... equivalent to a power-up reset.')])
gap('TPS23861','FIRMWARE_REV','IR0xFE / source0x41','无field且地址错误；不能将FEh硬当映射的revision寄存器。',{'source_address':'0x41','runtime_value':True,'no_numeric_reset':True,'do_not_assert_default0':True},[loc('TPS23861',77,'§7.5.30','Command = 41h')])
gap('TPS23861','I2C_SLAVE_ADDRESS','0x11','EEPROM AUTO/SLA未列当前IR/572 inventory，但决定AUTO、reset初值及准入上下文。',{'EEPROM_factory_initial':'0xA0','write_gate':['global broadcast0x30 unlock0xAA with temporary address','selected AIN high','then register0x11 write','auto-lock and permanent EEPROM store'],'invalid_addresses':['0x00','0x30','0x0C'],'SLA3':'A3 input overrides','AUTO_sampled_at':['POR','RESET pin','RESAL'],'program_timeout_ms_approx':100,'post_program_read_delay_ms':100,'post_reset_min_wait_ms':22,'endurance_cycles':25,'no_model_EEPROM_claim_without_gate_state':True},[loc('TPS23861',35,'§7.3.13','unlock code (AAh)'),loc('TPS23861',37,'§7.3.13','automatically locks the access ... stores permanently'),loc('TPS23861',57,'§7.5.10','Initial EEPROM VALUE')])
gap('TPS23861','OPERATING_MODE / DETECT_CLASS_ENABLE','0x12 / 0x14','关键模式寄存器未列IR/inventory，无法宣称独立事件/POEP持久性或完成前提完整覆盖。',{'mode_values':{'0':'Off','1':'Manual','2':'Semi-Auto','3':'Auto'},'Off':'clears port events/status/enables; writesDETE/CLE do not stick','Manual_DETE_CLE':'one cycle then auto-clear','Auto_POEP':'hardware mutable','reset_values':'depend EEPROM AUTO','processing_delay_to_0x14_ms':1.2},[loc('TPS23861',58,'§7.5.11','AA AA AA AA'),loc('TPS23861',59,'§7.5.13','automatically cleared when the cycle has been completed.'),loc('TPS23861',42,'§7.4.4','will not stick if the port is in Off Mode')])
gap('TPS23861','RESERVED_REGISTERS','0x1B,1D,1E,1F,22–25,59','手册定义reserved manufacturing/future-use地址；不能把所有未列IR地址作为非法访问自由oracle。',{'exclude_writes_to_reserved_addresses':True,'undefined_address_policy':'separate abstraction assumption, no manufacturer promise of return0/ignore'},[loc('TPS23861',84,'§7.5.36','Undesirable behavior may result if these registers are written to.')])
gap('LM83','STEP_ID','0xFF','IR列runtime寄存器但无fields，572-field清单完全未计此硬件修订值；source未给数字默认。',{'add_runtime_readonly_field':'revision','known_reset_mask':'0x00','no_fabricated_zero':True},[loc('LM83',15,'§2.1 continued','Read Stepping or Die Revision Code')])

# Source binding, mechanical completeness, and immutable inputs checks.
expected={(c,x['register'],x['field'],x['bits']) for c in CHIPS for x in review[c]['inventory']}
actual={(x['chip'],x['register'],x['field'],x['bits']) for x in FIELDS}
assert expected==actual and len(FIELDS)==len(expected)==149
assert all(set(x['dimensions'])=={'reset','access','legal_encoding','read_clear','trigger_completion','conditional_write','reserved_policy'} for x in FIELDS)
assert all(d['locators'] for x in FIELDS for d in x['dimensions'].values())
for c in CHIPS: assert sha(ROOT/review[c]['source']['path'])==review[c]['source']['sha256']
for p in PATCHES:
    for e in p['locators']: assert 1<=e['pdf_page']<=review[p['chip']]['source']['pdf_pages']
counts=dict(collections.Counter(x['overall_status'] for x in FIELDS))
per_chip={c:dict(collections.Counter(x['overall_status'] for x in FIELDS if x['chip']==c)) for c in CHIPS}
sources=[]
for c in CHIPS:
    pages=sorted({e['pdf_page'] for x in FIELDS if x['chip']==c for d in x['dimensions'].values() for e in d['locators']}|{e['pdf_page'] for g in GAPS if g['chip']==c for e in g['locators']})
    sources.append({'chip':c,'path':review[c]['source']['path'],'sha256':review[c]['source']['sha256'],'manual_version':versions[c],'pdf_pages':review[c]['source']['pdf_pages'],'printed_page_rule':'pdf_page - 1 (wrapper precedes National document)' if c=='LM83' else 'pdf_page = printed_page for reviewed technical pages','reviewed_technical_pages':pages,'visual_pages':{'HDC2021':[31],'TMP461':[17,19],'TPS23861':[63,66],'LM83':[10]}[c],'source_status':'VERIFIED_SOURCE (local original PDF, no current website comparison)'})
dump('fields.json',FIELDS);dump('findings.json',FINDINGS);dump('register_gaps.json',GAPS);dump('sources.json',sources);dump('ir_patches.json',PATCHES)
dump('quality_checks.json',{'inventory_count':149,'per_chip_inventory':{c:len(review[c]['inventory']) for c in CHIPS},'unique_keys':len(actual),'dimension_objects':len(FIELDS)*7,'no_missing_locators':True,'source_hashes_match':True,'counts':counts,'per_chip_status':per_chip,'patch_count':len(PATCHES),'gap_count':len(GAPS),'seven_input_sha256':{n:sha(BASE/n) for n in INPUTS},'models_reference_tests_hardware':'NOT_EXECUTED'})
conflicts=[{'conflict_id':'TPS23861_R17_SOURCE_GRANULARITY_CONFLICT','type':'SOURCE_CONFLICT','claim':'R17[3:1] reset/access','competing_values':['Table10 full80h','§7.5.16 perbit Reserved'],'locators':[loc('TPS23861',45,'Table10','1000,0000'),loc('TPS23861',63,'§7.5.16','Reserved')],'recommended_resolution':'preserve observed bits; exclude numeric/reset and access oracles; do not label erratum'}, {'conflict_id':'LM83_STATUS_CLEAR_TIMING_SCOPE','type':'SOURCE_CONFLICT','claim':'status latch read reset vs conditional output/flag reset','competing_values':['Figures4/6 note: read clears bits','§1.2/1.3/1.9 condition clearance on retired comparator cause'],'locators':[loc('LM83',10,'Figures4/6 / §1.2/1.3','Status Register Bits are reset by a read'),loc('LM83',12,'§1.9','so long as a temperature comparison does not signal a fault')],'recommended_resolution':'only deterministic cause-retired/frozen-conversion case; active cause timing excluded'}]
expert={'contract_version':'1.0','expert_skill':'sci-skills-presubmission-review','project_id':'d2d-twin','paper_family':'M','stage_id':'M4','task_id':'source_power_thermal','task_status':'COMPLETE','inputs_reviewed':[f'eval/protocol_v2_20261012/{n}' for n in INPUTS]+[x['path'] for x in sources]+['four candidate IR files read-only'],'outputs':[str((HERE/n).relative_to(ROOT)).replace('\\','/') for n in ['fields.json','findings.json','register_gaps.json','sources.json','ir_patches.json','quality_checks.json','REVIEW.md','expert_return.json']],'evidence_status':['VERIFIED_USER_MATERIAL: seven named protocol files, inventory and candidate IR','VERIFIED_SOURCE: four raw manufacturer PDFs, field-level locators, six critical page renders inspected','EXECUTED_LOCAL: SHA-256, 149-key/1043-dimension completeness check, candidate artifact generation','AI_INFERENCE: direct-register storage scope, fixed default reserved inputs, event-free atomic actions','NOT_EXECUTED: reference/model tests, new generation, SCNet, hardware, external APIs','PENDING_VERIFICATION: manufacturer conflict silicon behavior and any omitted functional models'],'assumptions':['PASS denotes bounded reviewed field facts/storage scope, not all hardware behavior','Reset facts apply to POR/explicit completion before new events','Unknown/default-free bits remain excluded','LM83 printed page is physical page minus1','Future harness must gate all CONDITIONAL cases before scored admission'],'author_input_needed':[],'manual_actions':[],'quality_checks':['149 inventory entries and unique keys match','1043 dimension objects all carry source locator(s)','four PDF SHA-256 values recomputed and match prepare manifest','seven protocol input files read and fingerprints recomputed','all writes limited to this new partition','six PDF pages rendered and visually inspected','no model/reference/hardware executed'],'conflicts':conflicts,'conflict_resolution_status':'UNRESOLVED','merge_permission':'orchestrator_only','recommended_next_action':'主编排任务汇总本分区候选，建立有事件/模式/完成条件门控的新输入与新harness冻结候选；保留冲突并独立编号后再批准正式生成。','stage_acceptance_recommendation':'REPAIR'}
dump('expert_return.json',expert)

report='''# 独立来源签审：power / thermal 分区

日期：2026-10-12。身份：独立 AI 来源审校子任务 `source_power_thermal`，SCI-Skills presubmission-review。审查范围：HDC2021、LM83、TMP461、TPS23861；阶段为M4有界来源准入，不推进或宣告阶段通过。只写本次新目录分区。

已逐项生成149个inventory字段、每字段7维共1043对象。判定计数：COUNTS。分芯片：PERCHIP。每条保留原始PDF路径、SHA-256、版本、物理页/印刷页、表号或节号及短原文；部分字段共用同一真实表，但结论单列。PASS仅指明示来源事实及明确抽象范围可接受；CONDITIONAL须未来harness落实门控，EXCLUDE可能仍保留已知reset，不是整体删字段。此审查不以20/20参考通过、模型得分或内部reset一致代替来源证据。

## 重大修订候选

1. TMP461 Table4(p17)将STATUS、ONE_SHOT的POR列为N/A；既有00及8个状态位/START的0不能冻结为厂商事实。状态位随ADC/连接/比较器变化；温度register 00/01/10/15的POR00可保留，但只在新测量前。读温度字节锁配对字节的保证仅到另一寄存器被读之前。
2. TMP461 p19的LHIGH/LLOW/RHIGH/RLOW/OPEN在ALERT模式读清必须致因消失。THERM2模式仅OPEN保持该读清锁存；温度高flag/引脚用THERM和HYS行为，low flags无THERM2输出效应。读STATUS不清ALERT interrupt latch；master服务sensor address且状态/致因解除才清脚。ONE_SHOT须SD=1、按LEN/REN选通道，payload任意且不存储，结束回shutdown。
3. HDC2021 MEAS_TRIG在measurement **starts**时自清，不是完成时；完成由DRDY_STATUS表示。SOFT_RES在RESET之后清0，旧read_as0不能作为时序恒定事实。INT_MODE真实含义为0 clear-on-read、1 comparator。DRDY经读00/01/02/03/04任一地址清；threshold flags在模式0锁存至STATUS读，模式1反映当前转换；输出enable和状态本身分开。MAX仅one-shot模式、最后reset后的峰值。
4. TPS23861五组CoR地址03/05/07/09/0B返回preclear整字节并清0，不能写成restore POR；事件注入必须非零并冻结新事件窗口。Interrupt summary由剩余event latches重算。POFF/RESP/Off mode对detect/fault/start/status/enables的清除、对power-event的置位均须建模。RESET命令CLRAIN清事件+interrupt+释放INT，CLINP仅释放INT，RESAL是power-up-equivalent，RESP是port reset；旧desc混淆三者。
5. TPS23861 Supply p54只列POR30h；RESET输入/RESAL的VDUV/VPUV取决于供电轨，不能把30h无条件推广。VDUV/VPUV是VDD/VPWR UVLO事件，不是未启用检测。M250表示250/255mΩ sense resistor而非250ms。R27 Reserved非ROM。FIRMWARE_REV为0x41，IR0xFE是可确定地址错误但无inventory字段；保留runtime未知值。
6. TPS23861 POEP在Auto分类完成/power-on前由硬件自动改写，任意RW持久性须隔离Auto事件；功能上需ICUT匹配。原手册完整register set远超当前inventory，尤其0x11 EEPROM AUTO/SLA、0x12 mode、0x14 enables未列，但控制当前字段前提。EEPROM要求broadcast30h unlockAA、临时地址、AIN selection、寄存器11h写、自动锁定永久保存；约100ms timeout；reset后至少22ms，program后读验证建议100ms；25次endurance。只读标签在unlock期间变RW，不能按常规RO翻转测试替代。
7. LM83全正文印刷页=PDF物理页−1。状态HIGH/CRIT的图注称read清flag、正文将flags/output解除与温度比较联合，必须保存解释粒度/时序不确定性；仅退休致因且冻结conversion的窗口作候选确定oracle，active fault重置位行为排除。OPEN由外部conversion前的连接检测决定，缺单独读清证据，不能沿用HIGH/CRIT clear。CONFIG reserved6/0有明文“write1 returns0”，可保留硬证据，与其它器件保留字段分开。

## 冲突与范围

TPS23861 R17[3:1]保留`SOURCE_CONFLICT`：Table10总览80h、详细表Reserved。只保留非冲突位数值初值，R17[3:1]保持新实例观测值、排除访问/固定数值断言；R17[1]不是ROM/revision。此分区没有裁定TMP117/INA3221的冲突，主任务须维持原冲突状态；本报告没有厂商勘误来源，不称任何候选为官方勘误。

读取源/输出源事实、R/W静态寄存器抽象、NA/undefined行为、内部冲突分别用MANUFACTURER_FACT、ABSTRACTION_ASSUMPTION、UNDEFINED_BEHAVIOR、SOURCE_CONFLICT。默认无read-clear/trigger的对象是明确`applicable=false`的范围标注，不是证明手册不存在任何副作用。动态RO只保护software write权限；无法保证时间推进后读值不变。

## 新输入冻结建议

`ir_patches.json`只列可定位的候选属性修改；不得原位覆盖旧IR、旧v2或历史生成材料。新IR必须去除无来源数值reset，保留掩码/来源冲突/EEPROM条件，修正错误desc和TPS revision地址，扩展缺字段commands或明确排除。这些候选未经新harness兑现，不能把静态IR先冻结成全面Gold。

新harness候选门控：独立reset事件类型及供电/EEPROM状态；事件注入与conversion scheduler；preclear read值和postclear状态；读取alias依赖；MEAS_TRIG开始与DRDY完成分离；ALERT/THERM/comparator模式；POEP自动改写及POFF/RESP副作用；任意受保护动态位用匹配事件窗口或dynamic mask，而非整快照相等。没有门控能力的维度必须CONDITIONAL/EXCLUDE，0→0不能记动态功能覆盖；atomic action只可写明completed-event抽象，不能宣称实际时序验证。

将源SHA、候选IR/policy/harness、版本、命名冲突、适用掩码、被排除值/地址、抽象范围、generation prompt模板完整哈希，再允许新一轮生成。原始历史成绩与旧提示词事实继续独立保存。

## 证据与交付

`fields.json`149条、`findings.json`13项、`register_gaps.json`8项、`sources.json`4份、`ir_patches.json`属性候选、`quality_checks.json`机械核验及七输入指纹、`expert_return.json`1.0完整契约。技术页完整文本逐页读取，TMP461 p17/19、HDC2021 p31、TPS23861 p63/66、LM83 PDF10/印刷9已渲染目视；其它页用完整原始页文本核对。版本与source hash均以本地文件身份冻结，不声称当前官网下载字节核验。没有运行模型、reference tests、SCNet、外部API或实物；没有需要用户账号/购买的动作。

Contribution视角：改进来源准入与测试有效性，不能称为模型学习能力提高。Methods视角：事件、版本、未知reset与模式门控仍需新协议实施。Communication视角：149条ledger与硬件功能覆盖是不同计数，冲突不能修辞抹平。独立签审为 **REPAIR / NOT_READY for unconditional hardware-faithful admission**；阶段裁决权仅属于主编排。

唯一下一步：由主编排汇总分区，建立上述事件/模式/完成门控的新输入与新harness冻结候选，保留命名冲突后再审批正式生成。
'''.replace('COUNTS',json.dumps(counts,ensure_ascii=False)).replace('PERCHIP',json.dumps(per_chip,ensure_ascii=False))
(HERE/'REVIEW.md').write_text(report,encoding='utf-8')
print(json.dumps({'fields':149,'dimensions':1043,'counts':counts,'per_chip':per_chip,'findings':len(FINDINGS),'patches':len(PATCHES),'register_gaps':len(GAPS)},ensure_ascii=False))
