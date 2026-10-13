"""Bounded independent audit. Writes only this new partition; never executes a model or harness.
Rows below are transcriptions/interpretations of original local PDF pages read by reviewer,
not derivations from the old IR reset/access fields. Inventory supplies identities only.
"""
import copy, hashlib, json, re
from collections import Counter
from pathlib import Path
import pymupdf as fitz

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'eval/independent_source_admission_20261012'
OUT=Path(__file__).resolve().parent
CHIPS=['TMP117','INA219','INA226','INA3221','ADS1115','ADS1220']
INPUTS={c:json.loads((BASE/'review_inputs'/f'{c}.json').read_text(encoding='utf-8')) for c in CHIPS}
DOCS={c:fitz.open(ROOT/f'corpus/data/raw_pdf/TI/{c}.pdf') for c in CHIPS}
VERSIONS={'TMP117':'SNOSD82D, June 2018, revised September 2022','INA219':'SBOS448G, August 2008, revised December 2015','INA226':'SBOS547C, June 2011, revised August 2026','INA3221':'SBOS576C, May 2012, revised September 2026','ADS1115':'SBAS444E (ADS1113/ADS1114/ADS1115), May 2009, revised December 2024','ADS1220':'SBAS501D, May 2013, revised May 2026'}
SHA={c:hashlib.sha256((ROOT/f'corpus/data/raw_pdf/TI/{c}.pdf').read_bytes()).hexdigest() for c in CHIPS}
TEXT={c:[re.sub(r'\s+',' ',p.get_text(sort=True)).strip() for p in DOCS[c]] for c in CHIPS}

def loc(c,p,table=None,section=None,needle=None):
    t=TEXT[c][p-1]
    nd=re.sub(r'\s+',' ',needle or table or section).strip()
    anchor=re.search(r'(?:Table|Figure) \d+(?:-\d+)?',table or '')
    anchor_at=t.lower().find(anchor[0].lower()) if anchor else -1
    at=t.lower().find(nd.lower(),max(anchor_at,0))
    if at<0 and anchor_at>=0:
        at=t.lower().find(nd.lower()) # Context prose before its register table.
    if at<0:
        raise ValueError(f'Missing exact PDF locator needle {c} p{p}: {nd}')
    ex=t[at:at+min(220,len(t)-at)]
    return {'pdf_page':p,'printed_page':str(p),'table':table,'section':section,'excerpt':ex}

def dim(status,fact,rule,locs,evidence='MANUFACTURER_FACT',applicable=True):
    return {'status':status,'applicable':applicable,'fact':fact,'candidate_rule':rule,'evidence_class':evidence,'locators':locs}

ROWS={}
def source(c,r,f,reset,access,p,table,needle=None,section=None,domain=None,kind='configuration'):
    ROWS[(c,r,f)]={'reset':reset,'access':access,'locs':[loc(c,p,table,section,needle)],'domain':domain,'kind':kind}

# TMP117, Figures 7-13..7-22 and Tables 7-5..7-15.
source('TMP117','TEMP','T',0x8000,'RO',26,'Table 7-5','T[15:0]',kind='measurement')
for f,v,a,nd in [('HIGH_ALERT',0,'RO','HIGH_Alert'),('LOW_ALERT',0,'RO','LOW_Alert'),('DATA_READY',0,'RO','Data_Ready'),('EEPROM_BUSY',0,'RO','EEPROM_Busy'),('MOD',0,'RW','MOD[1:0]'),('CONV',4,'RW','CONV[2:0]'),('AVG',1,'RW','AVG[1:0]'),('TNA',0,'RW','T/nA'),('POL',0,'RW','POL'),('DR_ALERT',0,'RW','DR/Alert')]:
    source('TMP117','CONFIG',f,v,a,27,'Table 7-6',nd,domain={'HIGH_ALERT':[0,1],'LOW_ALERT':[0,1],'DATA_READY':[0,1],'EEPROM_BUSY':[0,1],'MOD':list(range(4)),'CONV':list(range(8)),'AVG':list(range(4)),'TNA':[0,1],'POL':[0,1],'DR_ALERT':[0,1]}[f],kind='status' if a=='RO' else 'configuration')
source('TMP117','CONFIG','SOFT_RESET',0,'RW',28,'Table 7-6 (continued)','Software reset bit.',domain=[0,1],kind='command')
source('TMP117','CONFIG','UNUSED',0,'RO',28,'Table 7-6 (continued)','Not used',kind='reserved')
source('TMP117','THIGH','H',0x6000,'RW',29,'Table 7-8','H[15:0]',domain={'range':[0,65535]},kind='threshold')
source('TMP117','TLOW','L',0x8000,'RW',29,'Table 7-9','L[15:0]',domain={'range':[0,65535]},kind='threshold')
source('TMP117','EEPROM_UL','EUN',0,'RW',30,'Table 7-10','EEPROM unlock.',domain=[0,1])
source('TMP117','EEPROM_UL','EEPROM_BUSY',0,'RO',30,'Table 7-10','EEPROM busy.',domain=[0,1],kind='status')
source('TMP117','EEPROM_UL','UNUSED',0,'RO',30,'Table 7-10','13:0',kind='reserved')
source('TMP117','TEMP_OFFSET','OFF',0,'RW',31,'Table 7-13','Temperature offset data',domain={'range':[0,65535]})
source('TMP117','DEVICE_ID','ID',0x0117,'RO',32,'Table 7-15','DID[11:0]',kind='identity')

# INA219. Table 2 explicitly has nonnumeric measurement POR for registers 01/02.
for f,v in [('RST',0),('RSV_14',0),('BRNG',1),('PG',3),('BADC',3),('SADC',3),('MODE',7)]:
    p,ta,nd= {'RST':(19,'Table 3 / Figure 19','Reset Bit'),'RSV_14':(19,'Figure 19','R/W-0'),'BRNG':(19,'Table 3','Bus Voltage Range'),'PG':(19,'Table 4','PG Bit Settings'),'BADC':(20,'Table 5','ADC Settings'),'SADC':(20,'Table 5','ADC Settings'),'MODE':(20,'Table 6','Mode Settings')}[f]
    source('INA219','CONFIGURATION',f,v,'RW',p,ta,nd,domain={'RST':[0,1],'RSV_14':None,'BRNG':[0,1],'PG':list(range(4)),'BADC':list(range(16)),'SADC':list(range(16)),'MODE':list(range(8))}[f],kind='reserved' if f=='RSV_14' else ('command' if f=='RST' else 'configuration'))
source('INA219','SHUNT_VOLTAGE','SV',None,'RO',18,'Table 2','Shunt voltage',kind='measurement')
for f in ['BD','RSV_2','CNVR','OVF']:
    source('INA219','BUS_VOLTAGE',f,None,'RO',23,'Figure 24 / §8.6.3.2',{'BD':'Bus Voltage register stores','RSV_2':'Figure 24.','CNVR':'CNVR:','OVF':'OVF:'}[f],kind='reserved' if f=='RSV_2' else ('measurement' if f=='BD' else 'status'))
source('INA219','POWER','PWR',0,'RO',23,'Figure 25','Power Register',kind='measurement')
source('INA219','CURRENT','CURR',0,'RO',23,'Figure 26','Current Register',kind='measurement')
source('INA219','CALIBRATION','FS',0,'RW',24,'Figure 27','FS15',domain={'range':[0,32767]})
source('INA219','CALIBRATION','FS0',0,'RO',24,'Figure 27 note (1)','FS0 is a void bit',domain=[0],kind='constant')

# INA226. Unnamed bits have POR values but no per-bit RO/immutable semantics.
for f,v in [('RST',0),('UNNAMED_14_12',4),('AVG',0),('VBUSCT',4),('VSHCT',4),('MODE',7)]:
    p,ta,nd={'RST':(23,'§7.1.1 RST','Reset Bit'),'UNNAMED_14_12':(22,'Table 7-2','Configuration Register (00h) (Read/Write) Descriptions'),'AVG':(23,'Table 7-3','AVG Bit Settings'),'VBUSCT':(23,'Table 7-4','VBUSCT Bit Settings'),'VSHCT':(23,'Table 7-5','VSHCT Bit Settings'),'MODE':(24,'Table 7-6','Mode Settings')}[f]
    source('INA226','CONFIG',f,v,'UNKNOWN' if f.startswith('UNNAMED') else 'RW',p,ta,nd,domain=list(range(8)) if f in ['AVG','VBUSCT','VSHCT','MODE'] else ([0,1] if f=='RST' else None),kind='reserved' if f.startswith('UNNAMED') else ('command' if f=='RST' else 'configuration'))
source('INA226','SHUNT_VOLTAGE','SV',0,'RO',24,'Table 7-7','Shunt Voltage Register (01h) (Read-Only) Description',kind='measurement')
source('INA226','BUS_VOLTAGE','RESERVED_15',0,'RO',25,'Table 7-8 continued note (1)','D15 is always zero',domain=[0],kind='constant')
source('INA226','BUS_VOLTAGE','BV',0,'RO',24,'Table 7-8','Bus Voltage Register (02h) (Read-Only) Description',kind='measurement')
source('INA226','POWER','PD',0,'RO',26,'Table 7-9','Power Register (03h) (Read-Only) Description',kind='measurement')
for f in ['CSIGN','CD']:
    source('INA226','CURRENT',f,0,'RO',26,'Table 7-10','CSIGN' if f=='CSIGN' else 'CD14',kind='measurement')
source('INA226','CALIBRATION','UNNAMED_15',0,'UNKNOWN',26,'Table 7-11','Calibration Register (05h) (Read/Write) Description',kind='reserved')
source('INA226','CALIBRATION','FS',0,'RW',26,'Table 7-11','FS14',domain={'range':[0,32767]})
for f in ['SOL','SUL','BOL','BUL','POL','CNVR','UNNAMED_9_5','AFF','CVRF','OVF','APOL','LEN']:
    p=26 if f in ['SOL','SUL','UNNAMED_9_5'] else 27
    needle={'SOL':'Shunt Voltage Over-Voltage','SUL':'Shunt Voltage Under-Voltage','BOL':'Bus Voltage Over-Voltage','BUL':'Bus Voltage Under-Voltage','POL':'Power Over-Limit','CNVR':'Conversion Ready','UNNAMED_9_5':'Mask/Enable Register (06h) (Read/Write)','AFF':'Alert Function Flag','CVRF':'Conversion Ready Flag','OVF':'Math Overflow Flag','APOL':'Alert Polarity bit','LEN':'Alert Latch Enable'}[f]
    a='UNKNOWN' if f.startswith('UNNAMED') else ('HARDWARE_MANAGED' if f in ['AFF','CVRF','OVF'] else 'RW')
    source('INA226','MASK_ENABLE',f,0,a,p,'Table 7-12 / §7.1.7',needle,domain=None if f.startswith('UNNAMED') else [0,1],kind='reserved' if f.startswith('UNNAMED') else ('status' if a=='HARDWARE_MANAGED' else 'configuration'))
source('INA226','ALERT_LIMIT','AUL',0,'RW',28,'Table 7-13','AUL15',domain={'range':[0,65535]},kind='threshold')
source('INA226','MANUFACTURER_ID','ID',0x5449,'RO',28,'Table 7-14','Manufacturer ID Register (FEh) (Read-Only)',kind='identity')
source('INA226','DIE_ID','ID',None,'RO',28,'Table 7-15','Die ID Register (FFh) (Read-Only)',kind='identity')

# INA3221: transcribe separate specific row tables, not a single source for all fields.
for f,v in [('RST',0),('CH1en',1),('CH2en',1),('CH3en',1),('AVG',0),('VBUSCT',4),('VSHCT',4),('MODE',7)]:
    p=27 if f=='MODE' else 26
    source('INA3221','CONFIG',f,v,'RW',p,'Table 8-4 (continued)' if p==27 else 'Table 8-4',{'RST':'Reset bit.','CH1en':'Channel enable mode.','CH2en':'Channel enable mode.','CH3en':'Channel enable mode.','AVG':'Averaging mode.','VBUSCT':'Bus-voltage conversion time.','VSHCT':'Shunt-voltage conversion time.','MODE':'Operating mode.'}[f],domain=list(range(8)) if f in ['AVG','VBUSCT','VSHCT','MODE'] else [0,1],kind='command' if f=='RST' else 'configuration')
for k in range(1,4):
    p=27+k
    for r,tab,datum in [(f'SHUNT{k}',6+4*(k-1),'SD'),(f'VBUS{k}',8+4*(k-1),'BD')]:
        for f in ['SIGN',datum,'UNUSED']:
            source('INA3221',r,f,0,'RO',p,f'Table 8-{tab}',{'SIGN':'Sign bit.',datum:f'Channel-{k} '+('shunt-voltage data bits' if datum=='SD' else 'bus-voltage data bits'),'UNUSED':'Reserved'}[f],kind='reserved' if f=='UNUSED' else 'measurement')
for r,tab,p,f in [('CRIT1',18,31,'CL'),('WARN1',20,31,'WL'),('CRIT2',22,31,'CL'),('WARN2',24,32,'WL'),('CRIT3',26,32,'CL'),('WARN3',28,32,'WL')]:
    source('INA3221',r,f,0xFFF,'RW',p,f'Table 8-{tab}',f'Table 8-{tab}.',domain={'range':[0,8191]},kind='threshold')
    source('INA3221',r,'UNUSED',0,'RW',p,f'Table 8-{tab}',f'Table 8-{tab}.',kind='reserved')
for f in ['SIGN','SV','UNUSED']:
    source('INA3221','SHUNT_SUM',f,0,'RO',33,'Table 8-30',{'SIGN':'Sign bit.','SV':'Shunt-voltage sum data bits','UNUSED':'Reserved'}[f],kind='reserved' if f=='UNUSED' else 'measurement')
source('INA3221','SHUNT_SUM_LIMIT','SVL',None,'CONFLICT',33,'Tables 8-31 / 8-32','Shunt-Voltage Sum-Limit Register',kind='threshold')
source('INA3221','SHUNT_SUM_LIMIT','UNUSED',0,'CONFLICT',33,'Tables 8-31 / 8-32','Shunt-Voltage Sum-Limit Register',kind='reserved')
for f,v in [('RSVD15',0),('SCC',0),('WEN',0),('CEN',0),('CF',0),('SF',0),('WF',0),('PVF',0),('TCF',1),('CVRF',0)]:
    p=35 if f=='CVRF' else 34
    needle={'RSVD15':'Reserved','SCC':'Summation channel control.','WEN':'Warning alert latch enable.','CEN':'Critical alert latch enable.','CF':'Critical-alert flag indicator.','SF':'Summation-alert flag indicator.','WF':'Warning-alert flag indicator.','PVF':'Power-valid-alert flag indicator.','TCF':'Timing-control-alert flag indicator.','CVRF':'Conversion-ready flag.'}[f]
    source('INA3221','MASK_ENABLE',f,v,'HARDWARE_MANAGED' if f in ['CF','SF','WF','PVF','TCF','CVRF'] else 'RW',p,'Table 8-34 continued' if p==35 else 'Table 8-34',needle,domain=None if f=='RSVD15' else list(range(8)) if f in ['CF','WF','SCC'] else [0,1],kind='reserved' if f=='RSVD15' else 'status' if f in ['CF','SF','WF','PVF','TCF','CVRF'] else 'configuration')
for r,f,v,ta in [('PV_UPPER','PVU',1250,36),('PV_LOWER','PVL',1125,38)]:
    source('INA3221',r,'SIGN',0,'RO',35,f'Table 8-{ta}',f'Table 8-{ta}.',kind='constant',domain=[0])
    source('INA3221',r,f,v,'RW',35,f'Table 8-{ta}',f'Table 8-{ta}.',domain={'range':[0,4095]},kind='threshold')
    source('INA3221',r,'UNUSED',0,'RO',35 if r=='PV_UPPER' else 36,f'Table 8-{ta}'+(' continued' if r=='PV_LOWER' else ''),f'Table 8-{ta}.',kind='reserved')
source('INA3221','MANUF_ID','ID',0x5449,'RO',36,'Table 8-40','Manufacturer ID bits',kind='identity')
source('INA3221','DIE_ID','DIE',0x3220,'RO',36,'Table 8-42','Die ID bits',kind='identity')

# ADS1115 only: do not import ADS1113/1114 reserved-bit definitions.
source('ADS1115','CONVERSION','D',0,'RO',24,'Table 8-2','16-bit conversion result',kind='measurement')
for f,v in [('OS',1),('MUX',0),('PGA',2),('MODE',1),('DR',4),('COMP_MODE',0),('COMP_POL',0),('COMP_LAT',0),('COMP_QUE',3)]:
    p=25 if f in ['OS','MUX'] else 26
    needle={'OS':'Operational status or single-shot conversion start','MUX':'Input multiplexer configuration (ADS1115 only)','PGA':'Programmable gain amplifier configuration','MODE':'Device operating mode','DR':'Data rate','COMP_MODE':'Comparator mode','COMP_POL':'Comparator polarity','COMP_LAT':'Latching comparator','COMP_QUE':'Comparator queue and disable'}[f]
    source('ADS1115','CONFIG',f,v,'RW',p,'Table 8-3'+(' continued' if p==26 else ''),needle,domain=list(range(8)) if f in ['MUX','PGA','DR'] else list(range(4)) if f=='COMP_QUE' else [0,1],kind='command' if f=='OS' else 'configuration')
source('ADS1115','LO_THRESH','THRESH',0x8000,'RW',27,'Table 8-5','Lo_thresh[15:0]',domain={'range':[0,65535]},kind='threshold')
source('ADS1115','HI_THRESH','THRESH',0x7FFF,'RW',27,'Table 8-5','Hi_thresh[15:0]',domain={'range':[0,65535]},kind='threshold')

# ADS1220: local May 2026 PDF, all four registers reset 00; each field R/W label.
for r,p,ta,fs in [('CONFIG0',43,'Table 8-10',['MUX','GAIN','PGA_BYPASS']),('CONFIG1',44,'Table 8-11',['DR','MODE','CM','TS','BCS']),('CONFIG2',45,'Table 8-13',['VREF','FIFTY_SIXTY','PSW','IDAC']),('CONFIG3',46,'Table 8-14',['I1MUX','I2MUX','DRDYM','RESERVED'])]:
    for f in fs:
        nd={'MUX':'Input multiplexer configuration','GAIN':'Gain configuration','PGA_BYPASS':'Disables and bypasses','DR':'Data rate','MODE':'Operating mode','CM':'Conversion mode','TS':'Temperature sensor mode','BCS':'Burn-out current sources','VREF':'Voltage reference selection','FIFTY_SIXTY':'FIR filter configuration','PSW':'Low-side power switch configuration','IDAC':'IDAC current setting','I1MUX':'IDAC1 routing configuration','I2MUX':'IDAC2 routing configuration','DRDYM':'DRDY mode','RESERVED':'Always write 0b'}[f]
        domain={'MUX':list(range(15)),'GAIN':list(range(8)),'PGA_BYPASS':[0,1],'DR':list(range(7)),'MODE':[0,1,2],'CM':[0,1],'TS':[0,1],'BCS':[0,1],'VREF':list(range(4)),'FIFTY_SIXTY':list(range(4)),'PSW':[0,1],'IDAC':list(range(8)),'I1MUX':list(range(7)),'I2MUX':list(range(7)),'DRDYM':[0,1],'RESERVED':[0]}[f]
        source('ADS1220',r,f,0,'RW',p,ta,nd,domain=domain,kind='reserved' if f=='RESERVED' else 'configuration')

FIELDS=[]; BYKEY={}
for c in CHIPS:
    for inv in INPUTS[c]['inventory']:
        r,f,b=inv['register'],inv['field'],inv['bits']
        spec=ROWS[(c,r,f)]; ll=spec['locs']; a=spec['access']; k=spec['kind']
        bt=[int(x) for x in b.split(':')]; hi=bt[0]; lo=bt[-1]; mask=((1<<(hi-lo+1))-1)<<lo
        dims={}
        rv=spec['reset']
        dims['reset']=dim('PASS' if rv is not None else 'EXCLUDE', f'原始表/位图给字段上电初值 {rv:#x}。' if rv is not None else '原始相关页没有一个可无条件断言的数值复位值。', {'expected_field_value':rv,'known_mask':hex(mask) if rv is not None else '0x0','phase':'defined reset boundary, before first result/event'},ll,'MANUFACTURER_FACT' if rv is not None else 'UNDEFINED_BEHAVIOR')
        dims['access']=dim('PASS' if a not in ['UNKNOWN','CONFLICT','HARDWARE_MANAGED'] else 'CONDITIONAL',f'字段相关表/正文访问语义为 {a}；此处未把整寄存器R/W推成每一保留位可写。',{'source_access':a,'software_write_persistence':a=='RW' and k not in ['reserved','command','status'],'ro_protection_requires_no_hardware_update':k in ['measurement','status']},ll,'MANUFACTURER_FACT' if a not in ['UNKNOWN','CONFLICT','HARDWARE_MANAGED'] else 'ABSTRACTION_ASSUMPTION')
        domain=spec['domain']
        dims['legal_encoding']=dim('PASS' if domain is not None or a=='RO' else 'CONDITIONAL', '来源定义所列编码/数据位格式。' if domain is not None or a=='RO' else '该保留/未命名位没有定义非默认写值的功能域。',{'legal_values':domain,'software_encoding_test_applicable':a=='RW' and domain is not None,'exclude_unlisted_codes':isinstance(domain,list)},ll,'MANUFACTURER_FACT' if domain is not None or a=='RO' else 'UNDEFINED_BEHAVIOR',a=='RW')
        for d in ['read_clear','trigger_completion','conditional_write','reserved_policy']:
            dims[d]=dim('PASS','此字段自身在已核对的定义中未被规定为该类操作；这不是其所在寄存器无副作用的声明。',{'applicable':False,'do_not_invent_unreported_behavior':True},ll,'ABSTRACTION_ASSUMPTION',False)
        if k in ['measurement','status']:
            dims['trigger_completion']=dim('CONDITIONAL','字段为测量/硬件状态，结果可随对应测量或事件更新；只读不等于运行中恒定。',{'event_driven_model_required':True,'exclude_analog_event_claims_from_static_register_contract':True,'test_nonzero_event_before_clear':k=='status'},ll,'MANUFACTURER_FACT')
        if k=='reserved':
            dims['reserved_policy']=dim('CONDITIONAL','原始表标为保留/未命名；已知reset与访问标签不说明非法/非默认写入的后果。',{'keep_default_in_legal_stimuli':True,'fixed_write':rv if a!='RO' else None,'exclude_nondefault_write_oracle':True,'do_not_infer_read_constant_from_reset':True},ll,'UNDEFINED_BEHAVIOR')
            if a in ['RW','UNKNOWN']:
                dims['access']=dim('EXCLUDE','仅有保留/未命名标签或整寄存器访问码；不据此认证非默认软件写入语义。',{'source_label':a,'exclude_software_write_persistence':True,'exclude_ro_protection':a=='UNKNOWN'},ll,'UNDEFINED_BEHAVIOR')
                dims['legal_encoding']=dim('EXCLUDE','未定义非默认写值的保证。',{'legal_baseline_only':rv,'exclude_nondefault_values':True},ll,'UNDEFINED_BEHAVIOR')
        record={'chip':c,'register':r,'field':f,'bits':b,'source_path':f'corpus/data/raw_pdf/TI/{c}.pdf','source_sha256':SHA[c],'manual_version':VERSIONS[c],'overall_status':'PASS','dimensions':dims,'locators':ll,'old_inventory':inv,'fact_scope':'local manufacturer PDF; source admission only; independent AI review, not hardware validation'}
        FIELDS.append(record);BYKEY[(c,r,f)]=record

def change(c,r,f,d,status,fact,rule,ll,evidence='MANUFACTURER_FACT'):
    x=BYKEY[(c,r,f)];x['dimensions'][d]=dim(status,fact,rule,ll,evidence)
    x['locators']=list({json.dumps(z,sort_keys=True):z for z in x['locators']+ll}.values())

# TMP117: POR/EEPROM conditions apply beyond the two threshold registers.
ep=[loc('TMP117',18,section='§7.5.1.1-2',needle='Any I2C writes performed'),loc('TMP117',30,'Table 7-10',needle='EEPROM is locked for programming')]
for r,f in [('CONFIG','MOD'),('CONFIG','CONV'),('CONFIG','AVG'),('CONFIG','TNA'),('CONFIG','POL'),('CONFIG','DR_ALERT'),('THIGH','H'),('TLOW','L'),('TEMP_OFFSET','OFF')]:
    x=BYKEY[('TMP117',r,f)];reset=x['dimensions']['reset']['candidate_rule']['expected_field_value']
    ll=x['locators']+[loc('TMP117',25,'Table 7-3 note (1)',needle='This value is stored'),loc('TMP117',28,'Figure 7-14 notes (1)-(2)',needle='These bits can be stored')]
    change('TMP117',r,f,'reset','CONDITIONAL','这些地址/配置子位有EEPROM后备；表列为出厂值，用户EEPROM可改变reset。MOD1不能存EEPROM，MOD0可以；不要把整个MOD同等处理。',{'factory_eeprom_profile_expected':reset,'general_reset_rule':'reload EEPROM image','wait_for_por_load_complete':True,'por_busy_reset_is_temporal':True,'eeprom_configuration_mask':'0x07fc','MOD1_nonpersistent':True},ll)
    change('TMP117',r,f,'conditional_write','REPAIR','POR加载约1.5ms期间写CONFIG/limits被忽略；EEPROM锁定时写易失寄存器，解锁后可编程对应EEPROM。编程典型7ms；期间禁止I2C写。',{'preconditions':['POR complete','EEPROM_Busy=0'],'EUN0':'volatile register only','EUN1':'program nonvolatile backing, await Busy=0 before next write','avoid_conversion_while_unlocked':True,'separate_typical_time_from_completion_predicate':True},ep)
change('TMP117','TEMP','T','reset','PASS','复位后0x8000，直到首次转换包括平均完成；此值不是运行时温度。',{'expected_field_value':32768,'known_mask':'0xffff','before_first_conversion_complete':True},[loc('TMP117',26,'Table 7-5',needle='Following a reset')])
for f in ['HIGH_ALERT','LOW_ALERT']:
    change('TMP117','CONFIG',f,'read_clear','REPAIR','T/nA=0 Alert模式读CONFIG清对应标志；T/nA=1 Therm模式CONFIG读不清。Therm的HIGH由转换阈值/滞回置清，LOW一直0。',{'on_read':'CONFIG','only_if':{'CONFIG.TNA':0},'THERM_HIGH':'set/clear at conversion completion by high/low limits','THERM_LOW':'always zero','require_controlled_asserted_event':True},[loc('TMP117',27,'Table 7-6',needle='HIGH_Alert' if f=='HIGH_ALERT' else 'LOW_Alert'),loc('TMP117',17,section='§7.4.4.2',needle='I2C reads of the configuration register do not affect')])
change('TMP117','CONFIG','DATA_READY','read_clear','REPAIR','Data_Ready在温度更新/转换含平均完成时置1；读TEMP或CONFIG均清，不限定T/nA。',{'on_read':['TEMP','CONFIG'],'return_preclear_data':True,'require_controlled_asserted_event':True,'exclude_zero_then_zero_as_coverage':True},[loc('TMP117',27,'Table 7-6',needle='Data ready flag.')])
for r,f in [('CONFIG','EEPROM_BUSY'),('EEPROM_UL','EEPROM_BUSY')]:
    change('TMP117',r,f,'reset','CONDITIONAL','表给0为ready；POR load与编程期间Busy=1，初始POR窗口不能无条件断言0。',{'expected_after_busy_complete':0,'during_por_load':1},[loc('TMP117',18,section='§7.5.1.1',needle='While the POR sequence is being executed'),loc('TMP117',30,'Table 7-10',needle='performing power-up on reset load')])
    change('TMP117',r,f,'trigger_completion','REPAIR','两个Busy镜像相同状态；0表示ready，1表示编程/POR加载；读取不是清除事件。',{'mirror':['CONFIG[12]','EEPROM_UL[14]'],'complete_when':'Busy=0','program_time_typical_ms':7,'por_load_approx_ms':1.5,'no_read_clear':True},[loc('TMP117',30,'Table 7-10',needle='mirror of the EEPROM busy flag'),loc('TMP117',18,section='§7.5.1.2',needle='Programming a single location typically takes')])
change('TMP117','EEPROM_UL','EUN','conditional_write','REPAIR','EUN0不编程EEPROM但仍写数字逻辑寄存器；EUN1写可编程寄存器对应EEPROM。general-call reset清EUN重新锁定。',{'EUN0':'volatile writes allowed','EUN1':'nonvolatile programming allowed only when not busy','lock_after_general_call_reset':True,'busy_write_behavior':'EXCLUDE prohibited write oracle'},ep+[loc('TMP117',18,section='§7.5.1.2',needle='This command also clears')])
change('TMP117','CONFIG','MOD','trigger_completion','CONDITIONAL','编码2读回0有明确来源；编码3启动one-shot，转换含平均完成后进入shutdown。CONV不影响one-shot时长；不将进入shutdown自动推成MOD=1读回。',{'legal_values':[0,1,2,3],'readback_values':{'2':0},'completion_event':'temperature update / Data_Ready','post_completion_operating_state':'shutdown','post_completion_MOD_readback':'not explicitly established; exclude numerical oracle','exclude_unbounded_persistence_for_3':True},[loc('TMP117',27,'Table 7-6',needle='reads back = 00'),loc('TMP117',15,section='§7.4.3',needle='After the device completes')])
change('TMP117','CONFIG','CONV','legal_encoding','REPAIR','8个CONV编码全有定义；默认100=1s而不是旧注释0.25Hz。CONV与AVG共同决定连续周期，one-shot不受CONV影响。',{'legal_values':list(range(8)),'cycle_ms_by_avg':[[15.5,125,500,1000],[125,125,500,1000],[250,250,500,1000],[500,500,500,1000],[1000]*4,[4000]*4,[8000]*4,[16000]*4]},[loc('TMP117',28,'Table 7-7',needle='Conversion Cycle Time in CC Mode'),loc('TMP117',15,section='§7.4.3',needle='CONV bits do not affect')])
change('TMP117','CONFIG','AVG','legal_encoding','PASS','编码0/1/2/3为不平均/8/32/64次累加平均，不是移动平均。',{'legal_values':[0,1,2,3],'averaging_counts':[1,8,32,64]},[loc('TMP117',27,'Table 7-6',needle='accumulated average')])
change('TMP117','CONFIG','SOFT_RESET','access','CONDITIONAL','图7-14 bit1为R-0，表7-6续表为R/W并写明写1复位；属于同文件来源冲突。',{'diagram_access':'R','table_access':'R/W','recommended_separate_exploratory_profile':'table_text_priority','main_claim':'retain conflict; no official erratum asserted'},[loc('TMP117',27,'Figure 7-14',needle='Soft_Reset'),loc('TMP117',28,'Table 7-6 continued',needle='Software reset bit.')],'SOURCE_CONFLICT')
change('TMP117','CONFIG','SOFT_RESET','trigger_completion','CONDITIONAL','表述写1触发2ms software reset且该位always读0；动作证据存在，但图访问冲突未解决。',{'table_text_profile':{'write_value':1,'duration_ms':2,'read_as':0},'main_profile':'conditional text interpretation; retain reset completion phase'},[loc('TMP117',28,'Table 7-6 continued',needle='When set to 1')],'SOURCE_CONFLICT')
change('TMP117','DEVICE_ID','ID','reset','CONDITIONAL','低12位DID=0x117一致；高4位Rev图R-x、表reset0且是器件修订号。',{'known_mask':'0x0fff','expected_register':'0x0117','exclude_mask':'0xf000','apply_mask_to_all_reset_and_snapshot_oracles':True},[loc('TMP117',32,'Figure 7-22',needle='Rev3'),loc('TMP117',32,'Table 7-15',needle='Indicates the revision number')],'SOURCE_CONFLICT')
for r in ['CONFIG','EEPROM_UL']:
    change('TMP117',r,'UNUSED','reserved_policy','PASS','详细表明确R、reset0且Not used；源未承诺所有时点硬连零，保留POR与软件只读保护。',{'reset_known':True,'access':'RO','keep_zero_in_stimuli':True,'runtime_constant_zero_claim':False},BYKEY[('TMP117',r,'UNUSED')]['locators'])

# System reset self-clearing != always-zero reads without a completion boundary.
for c,r in [('INA219','CONFIGURATION'),('INA226','CONFIG'),('INA3221','CONFIG')]:
    x=BYKEY[(c,r,'RST')]
    change(c,r,'RST','trigger_completion','REPAIR','原文定义写1产生系统复位且该位self-clears；未给此位任意瞬时读必为0的承诺。',{'write_value':1,'after_reset_completed':'all defined defaults restored and RST=0','atomic_reset_abstraction':'explicit protocol assumption; no silicon timing proof','exclude_during_reset_readback_oracle':True},x['locators'])

# INA219 measurement reset and CNVR source inconsistency.
for r,f in [('SHUNT_VOLTAGE','SV'),('BUS_VOLTAGE','BD'),('BUS_VOLTAGE','RSV_2'),('BUS_VOLTAGE','CNVR'),('BUS_VOLTAGE','OVF')]:
    change('INA219',r,f,'reset','REPAIR','Table2为01/02的POR列写测量值Shunt voltage/Bus voltage，HEX为横线；详细图没有R-0 reset行。旧数值0无独立来源支持。',{'known_reset_mask':'0x0','exclude_fixed_numeric_reset':True,'zero_analog_input_if_used':'an external input assumption, not POR fact'},[loc('INA219',18,'Table 2',needle='Shunt voltage'),loc('INA219',23,'Figure 24',needle='Figure 24. Bus Voltage Register')],'UNDEFINED_BEHAVIOR')
change('INA219','BUS_VOLTAGE','RSV_2','reserved_policy','REPAIR','总表只规定寄存器R、图bit2未命名，未规定此位恒零或固定数值reset。',{'source_access':'register-level RO','exclude_constant_zero_oracle':True,'do_not_write_nondefault_reserved_bits':True},[loc('INA219',23,'Figure 24',needle='Figure 24. Bus Voltage Register'),loc('INA219',18,'Table 2',needle='Bus voltage')],'UNDEFINED_BEHAVIOR')
change('INA219','BUS_VOLTAGE','CNVR','read_clear','CONDITIONAL','p23规定POWER读清CNVR；p10却写Status读清且提convert pin，而寄存器表/引脚没有对应对象。章节表述冲突，不能 silently修成同一语义。',{'main_profile':'source conflict retained; read-clear excluded until policy interpretation frozen','optional_register_detail_priority':'reading POWER clears BUS_VOLTAGE.CNVR','not_same_register_read_clear':True,'require_asserted_CNVR_event':True},[loc('INA219',23,section='§8.6.3.2',needle='Reading the Power Register'),loc('INA219',10,section='§8.3.1',needle='Reading the Status register')],'SOURCE_CONFLICT')
change('INA219','BUS_VOLTAGE','CNVR','trigger_completion','CONDITIONAL','CNVR在所有转换/平均/乘法完成置1；CONFIG写清的措辞p10为任意CONFIG写(除模式0/4)、p23为new mode写(除0/4)。',{'set_event':'all conversions, averaging, multiplications complete','common_clear':'CONFIG write selecting active different mode','same_mode_CONFIG_write_clear':'quarantine source wording ambiguity','no_timing_or_event_model':'exclude CNVR dynamic assertions'},[loc('INA219',23,section='§8.6.3.2',needle='Writing a new mode'),loc('INA219',10,section='§8.3.1',needle='Writing to the Configuration register')],'SOURCE_CONFLICT')
change('INA219','BUS_VOLTAGE','OVF','trigger_completion','CONDITIONAL','功率/电流计算超范围置OVF，源未给无条件读清动作。',{'set_event':'Power or Current calculations out of range','read_clear':'not defined; do not fabricate','static_fixed_zero_runtime':'abstraction only'},[loc('INA219',23,section='§8.6.3.2 OVF',needle='Power or Current calculations')])
for c in ['INA219','INA226']:
    for r,f in [('POWER','PWR' if c=='INA219' else 'PD'),('CURRENT','CURR' if c=='INA219' else 'CD')]+([('CURRENT','CSIGN')] if c=='INA226' else []):
        change(c,r,f,'trigger_completion','CONDITIONAL','Calibration=0时Current/Power保持0；编程校准后随测量及计算更新，不能把0运行值推广到任意校准。',{'zero_output_if':'Calibration=0','after_programming_calibration':'derived from measured shunt/bus quantities','exclude_analog_math_claims_without_input_model':True},[loc(c,12 if c=='INA219' else 15,section='§8.5 / §6.5 Programming',needle='Until the Calibration')])
for c,r,f,p,sec in [('INA219','CONFIGURATION','MODE',9,'§8.3.1'),('INA226','CONFIG','MODE',11,'§6.3.1'),('INA3221','CONFIG','MODE',11,'§7.3.1')]:
    change(c,r,f,'trigger_completion','CONDITIONAL','写入triggered编码1/2/3触发一次，重复写相同模式也重触发。进入低功耗/等待态不证明MODE字段自行改成0/4。',{'trigger_values':[1,2,3],'same_value_write_retriggers':True,'mode_storage_after_completion':'no numerical normalization explicitly established; do not invent','completion_event':'CNVR' if c=='INA219' else 'CVRF','timing_model_required':True},[loc(c,p,section=sec,needle='Writing any' if c=='INA219' else 'In triggered mode' if c=='INA226' else 'In single-shot (triggered) mode')])

# INA226 flags, reserved access, and ID/AFF conflicts.
for f in ['AVG','VBUSCT','VSHCT','MODE']:
    change('INA226','CONFIG',f,'conditional_write','CONDITIONAL','CONFIG读不影响转换；CONFIG写中止当前转换，写完按新配置启动。',{'configuration_write_restarts_conversion':True,'clear_CVRF_unless_powerdown':True,'register_storage_only_may_be_scored_separately':True},[loc('INA226',22,section='§7.1.1',needle='Writing to the Configuration Register halts')])
for r,f in [('CONFIG','UNNAMED_14_12'),('CALIBRATION','UNNAMED_15'),('MASK_ENABLE','UNNAMED_9_5')]:
    change('INA226',r,f,'access','REPAIR','逐位表给未命名位与POR，整寄存器为R/W；无逐位RO码或写保护文字。旧RO分类不能称厂商事实。',{'exclude_access_oracle':True,'keep_reset_value_in_all_legal_writes':True,'retain_known_por':True},BYKEY[('INA226',r,f)]['locators'],'UNDEFINED_BEHAVIOR')
change('INA226','MASK_ENABLE','CVRF','read_clear','REPAIR','读MASK_ENABLE清CVRF；写CONFIG除powerdown也清；转换/平均/乘法全部完成置1。',{'on_read':'MASK_ENABLE','on_write':'CONFIG with MODE not 0 or 4','set_event':'all conversions, averaging, multiplications complete','require_nonzero_event':True},[loc('INA226',27,section='§7.1.7 CVRF',needle='Conversion Ready Flag bit clears'),loc('INA226',11,section='§6.3.1',needle='Conversion Ready flag (CVRF) bit is set')])
change('INA226','MASK_ENABLE','AFF','read_clear','REPAIR','LEN=1锁存时MASK读清AFF；LEN=0透明模式由下一次无告警转换清。不能无条件读清。',{'if_LEN1_on_read':'MASK_ENABLE','if_LEN0_clear':'next conversion without alert','require_controlled_alert':True},[loc('INA226',27,section='§7.1.7 AFF',needle='When the Alert Latch Enable bit is set to Latch mode')])
change('INA226','MASK_ENABLE','AFF','conditional_write','CONDITIONAL','p13说锁存AFF/ALERT直到CONFIG写或MASK读；p27说AFF锁存only MASK读清。CONFIG写清AFF保持来源冲突。',{'CONFIG_write_clear_AFF':'excluded main profile; text disagreement retained','MASK_read_clear_AFF':'supported when LEN=1'},[loc('INA226',13,section='§6.3.1.2',needle='until either the Configuration'),loc('INA226',27,section='§7.1.7 AFF',needle='clears only when')],'SOURCE_CONFLICT')
for f in ['SOL','SUL','BOL','BUL','POL','CNVR']:
    change('INA226','MASK_ENABLE',f,'trigger_completion','CONDITIONAL','D15..11只同时选择最高有效位告警；CNVR可与一种阈值告警并行。这是功能优先级而非非法编码。',{'multiple_alert_enables':'highest D15..D11 has priority','CNVR':'may coexist with one threshold alert','storage_domain':[0,1],'exclude_physical_ALERT_function_without_model':True},[loc('INA226',12,section='§6.3.1.2',needle='Only one of these alert functions'),loc('INA226',26,'Table 7-12',needle='highest significant bit position')])
change('INA226','DIE_ID','ID','reset','CONDITIONAL','Table7-1给2260/2261按产地；Table7-15却全部POR=0。两处不同，不能仅用runtime跳过后声称无冲突。',{'main_reset_known_mask':'0x0','exclude_fixed_ID_reset':True,'optional_summary_priority_expected_set':['0x2260','0x2261'],'split_device_and_revision_fields':True},[loc('INA226',22,'Table 7-1 note (3)',needle='Die COO'),loc('INA226',28,'Table 7-15',needle='POR')],'SOURCE_CONFLICT')

# INA3221 flags are hardware managed despite R/W labels; table labels retained.
for f in ['CH1en','CH2en','CH3en','AVG','VBUSCT','VSHCT','MODE']:
    change('INA3221','CONFIG',f,'conditional_write','CONDITIONAL','CONFIG写中止进行中转换并按新值重启；完成timing-control序列前写CONFIG会禁用TC功能直至power cycle或RST。',{'on_write':'halt/restart conversion','CVRF_clear_unless_powerdown':True,'TC_sequence_early_CONFIG_write':'disables timing control until power cycle/software reset'},[loc('INA3221',26,section='§8.2.1',needle='Writing to this register halts'),loc('INA3221',15,section='§7.3.2.4',needle='Writing to the Configuration register before')])
for f in ['CF','SF','WF','PVF','TCF','CVRF']:
    change('INA3221','MASK_ENABLE',f,'access','CONDITIONAL','Table8-34明确R/W标签；正文定义硬件状态，写MASK不清状态，不给任意写值持久化规则。现RO编码是抽象的软件保护选择。',{'source_label':'R/W','effective_role':'hardware managed status','exclude_ordinary_RW_persistence':True,'software_ignores_write_to_status':'abstraction assumption, not a quoted RO code'},[loc('INA3221',34,'Table 8-34',needle='Writing to this register does not clear'),BYKEY[('INA3221','MASK_ENABLE',f)]['locators'][0]],'ABSTRACTION_ASSUMPTION')
for f in ['CF','SF','WF']:
    change('INA3221','MASK_ENABLE',f,'read_clear','PASS','详细字段说明明确读MASK_ENABLE清CF/SF/WF；写MASK不清。事件生成是必要前置条件。',{'on_read':'MASK_ENABLE','writes_do_not_clear_flags':True,'require_nonzero_event':True,'return_old_flag_before_clear':'explicit protocol convention'},[loc('INA3221',34,'Table 8-34',needle={'CF':'critical alert flag bits are cleared','SF':'Summation Alert Flag bit is cleared','WF':'Warning Alert Flag bits clear'}[f])])
change('INA3221','MASK_ENABLE','CVRF','read_clear','REPAIR','CVRF在所有转换完成置1；MASK读清、CONFIG写清除powerdown/disable选择。旧无条件CONFIG写清说明不精确。',{'on_read':'MASK_ENABLE','on_CONFIG_write_clear_if_MODE_not':[0,4],'set_event':'all enabled channel conversions complete','require_nonzero_event':True},[loc('INA3221',35,'Table 8-34 continued',needle='Conversion ready clears')])
change('INA3221','MASK_ENABLE','PVF','read_clear','PASS','PVF不会由MASK读清；直到造成条件消失且PV pin清。',{'no_read_clear':True,'clear_condition':'fault removed and PV pin cleared','software_reset_PV_output':'hold until power-valid sequence completes'},[loc('INA3221',34,'Table 8-34',needle='This bit does not clear until'),loc('INA3221',15,section='§7.3.3',needle='holds the output of the PV pin')])
change('INA3221','MASK_ENABLE','TCF','read_clear','REPAIR','TCF不由读取清除；原文明确power recycled或software reset，旧注释只断电遗漏software reset。',{'no_read_clear':True,'reinitialize_event':['power cycle','software reset'],'do_not_keep_forever_constant_1':True},[loc('INA3221',34,'Table 8-34',needle='unless the power is recycled or a software reset')])
change('INA3221','MASK_ENABLE','TCF','reset','CONDITIONAL','位图RW-1、寄存器0002及正文default high支持1；同一单比特的Table8-34 reset列却为11h，超范围。保留数值表达冲突。',{'main_por_expected_bit':1,'support':'register header, bitmap, default-high prose','table_literal':'11h','classification':'source representation conflict, not official erratum'},[loc('INA3221',34,'Table 8-33',needle='RW-1'),loc('INA3221',34,'Table 8-34',needle='11h')],'SOURCE_CONFLICT')
for f in ['SVL','UNUSED']:
    change('INA3221','SHUNT_SUM_LIMIT',f,'access','CONDITIONAL','Table8-31全位RW；Table8-32同位R。整个0E的访问oracle隔离。SVL[15:1]还合并独立SIGN与SVL[14:1]。',{'exclude_all_write_and_ro_protection_oracles':True,'mapped_address_still_valid':True,'candidate_split_fields':['SIGN[15]','SVL[14:1]','Reserved[0]']},[loc('INA3221',33,'Table 8-31',needle='Table 8-31.'),loc('INA3221',33,'Table 8-32',needle='Table 8-32.')],'SOURCE_CONFLICT')
change('INA3221','SHUNT_SUM_LIMIT','SVL','reset','CONDITIONAL','标题/位图7FFE与表数据reset0冲突；仅SIGN15与Reserved0的0一致。',{'register_known_mask':'0x8001','expected_register':'0x0000','field_known_mask':'0x8000','exclude_register_mask':'0x7ffe','do_not_promote_16383_to_unconditional_fact':True},BYKEY[('INA3221','SHUNT_SUM_LIMIT','SVL')]['locators'],'SOURCE_CONFLICT')
change('INA3221','SHUNT_SUM_LIMIT','UNUSED','reset','PASS','bit0数值reset0在两表一致，尽管access冲突；可保留此单维事实。',{'expected_field_value':0,'known_mask':'0x0001'},BYKEY[('INA3221','SHUNT_SUM_LIMIT','UNUSED')]['locators'])
for r,f in [('PV_UPPER','PVU'),('PV_LOWER','PVL')]:
    change('INA3221',r,f,'trigger_completion','CONDITIONAL','power-valid监测要求MODE启用bus测量并周期更新；PV Upper为所有bus超过阈值，PV Lower为任意bus跌破阈值。纯门限存储不证明PV序列。',{'require_bus_measurement_modes':[2,3,6,7],'upper_rule':'all relevant bus channels above upper','lower_rule':'any bus channel below lower','exclude_functional_assertions_without_controlled_bus_inputs':True},[loc('INA3221',35,section='§8.2.17-18',needle='For the power-valid conditions to be monitored')])

# ADS1115 status and configuration application timing / comparator side effects.
change('ADS1115','CONFIG','OS','access','REPAIR','OS写0无作用，powerdown写1启动；转换中写1无作用。读值报告busy/idle，不能按普通RW恒等读回。',{'write0':'no effect','write1_when_powerdown':'start one conversion','write1_while_busy':'no effect','read0':'conversion in progress','read1':'idle','exclude_storage_persistence':True},[loc('ADS1115',25,'Table 8-3',needle='OS can only be written')])
change('ADS1115','CONFIG','OS','trigger_completion','REPAIR','单次启动约25us后OS=0并转换，数据完成后powerdown；OS读1=未在转换。连续模式在完成后立即新转换。',{'precondition':'MODE=1 and idle','on_trigger':'power up, OS=0, start','complete_when':'conversion data available, OS=1 and powerdown','powerup_typical_us':25,'no_unqualified_immediate_OS1_after_write':True},[loc('ADS1115',18,section='§7.4.2.1',needle='When the OS bit is asserted'),loc('ADS1115',25,'Table 8-3',needle='When reading')])
for f in ['MUX','PGA','MODE','DR','COMP_MODE','COMP_POL','COMP_LAT','COMP_QUE']:
    change('ADS1115','CONFIG',f,'conditional_write','CONDITIONAL','连续模式CONFIG更新不打断当前conversion；当前按旧配置完成，之后才用新配置。读回配置存储不证明采样立即切换。',{'storage_readback_vs_effective_conversion_configuration':'separate','continuous_update_applies':'after current old-config conversion completes','OS_stimulus':'0 for ordinary field persistence baseline'},[loc('ADS1115',18,section='§7.4.2.2',needle='When writing new configuration settings')])
change('ADS1115','CONFIG','COMP_LAT','read_clear','CONDITIONAL','读CONVERSION清锁存ALERT/RDY输出，不清COMP_LAT字段或转换数据；SMBus响应可清输出。不要误编码字段read_action=clear。',{'field_read_action':'none declared','cross_register_side_effect':'CONVERSION read clears latched ALERT output','condition':'COMP_LAT=1, comparator enabled and asserted','need_alert_state_model':True},[loc('ADS1115',16,section='§7.3.7',needle='This latched assertion can only be cleared'),loc('ADS1115',26,'Table 8-3 continued',needle='remains latched until')])
for r in ['LO_THRESH','HI_THRESH']:
    change('ADS1115',r,'THRESH','conditional_write','CONDITIONAL','比较器使用时HI必须大于LO(补码比较)，PGA变化需更新阈值。HI MSB=1/LO MSB=0选择conversion-ready功能。不把这个独立RDY组合误称非法门限。',{'storage_data_domain':'all 16-bit patterns','comparator_function_precondition':'signed HI > signed LO','pga_changed':'update thresholds for desired analog limits','RDY_mode_condition':{'HI_THRESH.MSB':1,'LO_THRESH.MSB':0},'storage_only_precondition':'disable comparator (COMP_QUE=3)'},[loc('ADS1115',27,section='§8.1.4',needle='Hi_thresh register value must always be greater'),loc('ADS1115',27,section='§8.1.4',needle='conversion-ready function')])

# ADS1220: writes themselves trigger/restart conversions; command plane omitted by IR.
for (c,r,f),x in BYKEY.items():
    if c=='ADS1220':
        change(c,r,f,'trigger_completion','CONDITIONAL','单次模式任意CONFIG写均开始/重启转换；powerdown写CONFIG唤醒仅单次，不论CM。连续转换开始需CM1后START/SYNC。所有寄存器写均为潜在事件。',{'CONFIG_write_single_shot':'start/restart one conversion','CONFIG_write_ongoing':'restart current conversion','CONFIG_write_from_powerdown':'wake and one conversion regardless CM','continuous_start':'CM=1 then START/SYNC','completion':'DRDY high-to-low / new output available','config_readback_is_not_conversion_validation':True},[loc(c,34,section='§8.4.2.1-2',needle='every write access to any'),loc(c,35,section='§8.4.3.4',needle='Writing to any configuration register wakes')])
change('ADS1220','CONFIG0','MUX','conditional_write','PASS','MUX8..11单端AINN=AVSS要求bypass1且gain仅1/2/4；MUX12/13内部监测为PGA bypassed。',{'when_MUX_8_to_11':{'PGA_BYPASS':1,'GAIN_codes':[0,1,2]},'when_MUX_12_13':'PGA bypassed in function; explicit safe baseline PGA_BYPASS=1,GAIN=0 is protocol choice','safe_baseline_for_other_MUX':{'GAIN':0,'PGA_BYPASS':0}},[loc('ADS1220',43,'Table 8-10',needle='For settings where AINN'),loc('ADS1220',43,'Table 8-10',needle='VREFPx')])
change('ADS1220','CONFIG0','PGA_BYPASS','conditional_write','PASS','GAIN8..128时PGA总开，不论bypass字段；只gain1/2/4可关闭。读回bit不证明PGA功能。',{'test_bypass1_baseline_GAIN':0,'GAIN_codes_3_to_7':'PGA enabled regardless bypass','do_not_normalize_readback_without_source':True},[loc('ADS1220',43,'Table 8-10',needle='PGA is always enabled')])
change('ADS1220','CONFIG2','FIFTY_SIXTY','conditional_write','PASS','非0 filter只能normal20SPS或duty5SPS；其他组合必须00。',{'nonzero_allowed_if':{'CONFIG1.DR':0,'CONFIG1.MODE':[0,1]},'otherwise_fixed_write':0,'all_four_codes_defined':True},[loc('ADS1220',45,'Table 8-13',needle='Only use these bits together')])
for r,f in [('CONFIG0','MUX'),('CONFIG0','GAIN'),('CONFIG0','PGA_BYPASS'),('CONFIG2','VREF')]:
    change('ADS1220',r,f,'trigger_completion','CONDITIONAL','TS=1时CONFIG0所有设置对测温无效且internal reference覆盖VREF；原寄存器配置字段仍是R/W，没有数值改写承诺。另任何CONFIG写都有转换开始/重启副作用。',{'temperature_sensor_override_if':'CONFIG1.TS=1','CONFIG0_effect':'none on temperature conversion','effective_VREF':'internal reference regardless selection','storage_fields':'do not fabricate readback normalization','any_CONFIG_write':'start/restart as §8.4.2; separate command/event profile'},[loc('ADS1220',33,section='§8.3.13',needle='settings of configuration register 0 have no effect')])
for f in ['IDAC']:
    change('ADS1220','CONFIG2',f,'conditional_write','CONDITIONAL','IDAC电流设置后启动最长200us；先设电流再设I1MUX/I2MUX。单次转换之间IDAC保持开，POWERDOWN关闭，不能把单次完成等同IDAC关闭。',{'program_sequence':['IDAC current','wait startup if claiming stable current','I1MUX/I2MUX routing'],'startup_max_us':200,'single_shot_complete':'IDAC stays active','POWERDOWN':'IDAC off, stored register retained'},[loc('ADS1220',31,section='§8.3.8',needle='IDACs require up to 200'),loc('ADS1220',31,section='§8.3.8',needle='IDACs remain active')])
for f in ['I1MUX','I2MUX']:
    change('ADS1220','CONFIG3',f,'conditional_write','CONDITIONAL','手册要求先设IDAC电流再选routing；合法存储0..6不能证明模拟IDAC符合compliance。',{'functional_preconditions':['set current first','await startup','routing pin voltage <= AVDD - 0.9V'],'storage_baseline':'IDAC=0 or explicit current sequence; no analog validation'},[loc('ADS1220',31,section='§8.3.8',needle='Set the IDAC current'),loc('ADS1220',31,section='§8.3.8',needle='compliance voltage')])
change('ADS1220','CONFIG2','PSW','trigger_completion','CONDITIONAL','PSW1在START/SYNC后闭合，POWERDOWN打开；单次转换之间保持闭合。PSW0可随时打开；不是单次完成自动关闭。',{'PSW0':'open','PSW1_START_SYNC':'close','POWERDOWN':'open','single_shot_completion':'retain closed if PSW1','config_write_side_effect':'separate conversion restart'},[loc('ADS1220',31,section='§8.3.9',needle='switch stays closed between conversions')])
change('ADS1220','CONFIG3','RESERVED','reserved_policy','PASS','R/W-0标签旁明确Always write0b，只有默认0合法；写1之后的存储/钳位/忽略未定义。',{'fixed_write':0,'known_reset':True,'exclude_nonzero_write_oracle':True,'skip_writability_due_to_no_legal_alternative':True},[loc('ADS1220',46,'Table 8-14',needle='Always write 0b')])
change('ADS1220','CONFIG3','RESERVED','access','PASS','厂家标签R/W，但非零写被明文禁止；仅证明合法0刺激，不能对1作可写性oracle。',{'source_access':'R/W','allowed_stimulus':[0],'nonzero_write_assertions':'EXCLUDE'},[loc('ADS1220',46,'Table 8-14',needle='Always write 0b')])
change('ADS1220','CONFIG3','RESERVED','legal_encoding','PASS','仅0合法，1的结果未规定。',{'legal_values':[0],'excluded_values':[1]},[loc('ADS1220',46,'Table 8-14',needle='Always write 0b')])

# Nonapplicable dimensions do not force whole-field exclusion.
for x in FIELDS:
    d=x['dimensions'];a=ROWS[(x['chip'],x['register'],x['field'])]['access'];k=ROWS[(x['chip'],x['register'],x['field'])]['kind']
    if any(v['status']=='REPAIR' for v in d.values()): x['overall_status']='REPAIR'
    elif a=='UNKNOWN' or (k=='reserved' and a=='RW' and x['chip']!='ADS1220'): x['overall_status']='EXCLUDE'
    elif any(v['status']=='CONDITIONAL' and v['applicable'] for v in d.values()): x['overall_status']='CONDITIONAL'
    elif d['reset']['status']=='EXCLUDE':x['overall_status']='EXCLUDE'
    else:x['overall_status']='PASS'
    x['conclusion']='仅按对应维度条件准入；N/A维度不表示实现或实物验证。' if x['overall_status'] in ['PASS','CONDITIONAL'] else '修订/隔离待审输入后再冻结；保留已明确维度事实。'

GAPS=[]
for r,p,ta in [('EEPROM1',30,'Table 7-11'),('EEPROM2',31,'Table 7-12'),('EEPROM3',32,'Table 7-14')]:
    ll=[loc('TMP117',p,ta,needle=ta+'.'),loc('TMP117',30,section='§7.6.7',needle='Writes to this address when the EEPROM is locked'),loc('TMP117',18,section='§7.5.1.2',needle='Programming a single location typically takes')]
    if r=='EEPROM2':ll+=[loc('TMP117',31,section='§7.6.8 title',needle='[reset = 0000h]'),loc('TMP117',25,'Table 7-3',needle='EEPROM2')]
    GAPS.append({'chip':'TMP117','register':r,'existing_fields':[],'overall_status':'CONDITIONAL','source_path':'corpus/data/raw_pdf/TI/TMP117.pdf','source_sha256':SHA['TMP117'],'manual_version':VERSIONS['TMP117'],'fact':'完整16位R/W scratch register，有EEPROM后备；locked写volatile，unlocked编程。reset xxxx由工厂唯一ID或用户EEPROM决定。EEPROM2标题0000h与图表xxxxh冲突。','candidate_rule':{'candidate_field':{'name':'D','bits':'15:0','source_access':'R/W'},'reset_known_mask':'0x0','EUN0':'volatile write persists until reset, not EEPROM programming','EUN1':'program backing cell only when Busy=0; wait completion before next write','reset':'reload persistent contents','program_typical_ms':7,'busy_mirrors':['CONFIG[12]','EEPROM_UL[14]'],'no_assertion_on_prohibited_busy_writes':True},'evidence_class':'SOURCE_CONFLICT' if r=='EEPROM2' else 'MANUFACTURER_FACT','locators':ll})

FINDINGS=[]
def finding(fid,c,targets,problem,old,rule,ll,severity='P1',evidence='MANUFACTURER_FACT'):
    FINDINGS.append({'id':fid,'chip':c,'targets':targets,'problem':problem,'old':old,'candidate_rule':rule,'locators':ll,'severity':severity,'evidence_class':evidence,'source_path':f'corpus/data/raw_pdf/TI/{c}.pdf','source_sha256':SHA[c],'manual_version':VERSIONS[c]})
def ff(fid,c,r,f,d,problem,old,severity='P1'):
    a=BYKEY[(c,r,f)]['dimensions'][d];finding(fid,c,[r+'.'+f],problem,old,a['candidate_rule'],a['locators'],severity,a['evidence_class'])
ff('TMP117_ALERT_MODE_QUALIFIED_READ_CLEAR','TMP117','CONFIG','HIGH_ALERT','read_clear','无条件清HIGH/LOW与Therm模式不符','HIGH_ALERT/LOW_ALERT read_action=clear unconditional')
ff('TMP117_DATA_READY_CROSS_REGISTER_CLEAR','TMP117','CONFIG','DATA_READY','read_clear','TEMP读也清DATA_READY必须纳入事件策略','field-only CONFIG CoR metadata')
ff('TMP117_EEPROM_VOLATILE_AND_NVM_GATE','TMP117','EEPROM_UL','EUN','conditional_write','锁定不等同全部写被忽略；EEPROM空字段隐藏有效scratch行为','旧Q1称EEPROM1-3写仅EUN1有效')
ff('TMP117_ALL_EEPROM_BACKED_RESETS','TMP117','TEMP_OFFSET','OFF','reset','不止门限，offset和多个CONFIG位也EEPROM后备','factory condition only described in report for THIGH/TLOW')
ff('TMP117_BUSY_MIRROR_AND_COMPLETION','TMP117','CONFIG','EEPROM_BUSY','trigger_completion','Busy镜像、POR1.5ms及编程7ms尚未模型化','EEPROM excluded block says 2ms busy')
ff('TMP117_CONV_PERIOD_DESCRIPTION','TMP117','CONFIG','CONV','legal_encoding','默认CONV100/AVG01周期1s，旧0.25Hz不符','CONV desc default100 T/nA0 0.25Hz')
ff('TMP117_MOD_ONE_SHOT_BOUNDARY','TMP117','CONFIG','MOD','trigger_completion','shutdown operating state不支持自创MOD读回1','MOD3 omitted persistence but completion readback not defined')
ff('TMP117_SOFT_RESET_SOURCE_CONFLICT','TMP117','CONFIG','SOFT_RESET','access','图R/tableR/W冲突不得称已官方确认勘误','proofread_record erratum_found says manual erratum')
ff('TMP117_REV_RESET_CONFLICT','TMP117','DEVICE_ID','ID','reset','保留既有高4bit来源冲突和统一mask','candidate ID fullreset0117')
finding('TMP117_EEPROM2_RESET_SOURCE_CONFLICT','TMP117',['EEPROM2'],'标题0000 vs 总表/详细表xxxx及图R/W-x','runtime0 placeholder hides conflicting header',GAPS[1]['candidate_rule'],GAPS[1]['locators'],'P1','SOURCE_CONFLICT')
ff('INA219_VOLTAGE_NUMERIC_RESET_UNSUPPORTED','INA219','SHUNT_VOLTAGE','SV','reset','Table2测量值/HEX横线不是0reset','SHUNT/BUS all fields reset0')
ff('INA219_CNVR_CLEAR_SOURCE_CONFLICT','INA219','BUS_VOLTAGE','CNVR','read_clear','p10Status/convert pin vs p23Power/newMODE应登记冲突','CNVR no read_action and static0')
ff('INA219_RSV2_CONSTANT_ZERO_UNSUPPORTED','INA219','BUS_VOLTAGE','RSV_2','reserved_policy','未命名图位不能推出恒零','RSV_2 RO reset0 and description恒读0')
for c,r in [('INA219','CONFIGURATION'),('INA226','CONFIG'),('INA3221','CONFIG')]:ff(c+'_RST_COMPLETION_SCOPE',c,r,'RST','trigger_completion','self-clears不是任意瞬时always0','read_as0 / desc reads always0')
ff('INA226_UNNAMED_ACCESS_UNDEFINED','INA226','CONFIG','UNNAMED_14_12','access','三组未命名位逐位RO未在来源定义','CONFIG14:12/CAL15/MASK9:5 all RO')
ff('INA226_CVRF_CLEAR_EVENTS','INA226','MASK_ENABLE','CVRF','read_clear','必须控制完成事件后检验MASK读清和CONFIG例外','CVRF no read_action static0')
ff('INA226_AFF_LATCH_CLEAR','INA226','MASK_ENABLE','AFF','read_clear','AFF清除受LEN模式限制','AFF no read_action static0')
ff('INA226_AFF_CONFIG_CLEAR_SOURCE_CONFLICT','INA226','MASK_ENABLE','AFF','conditional_write','p13CONFIG写清 vs p27onlyMASK读清未解决','not registered')
ff('INA226_DIE_ID_RESET_SOURCE_CONFLICT','INA226','DIE_ID','ID','reset','Table7-15零POR与Table7-1 2260/61不一致','runtime2260 variants only')
ff('INA3221_0E_SOURCE_CONFLICT','INA3221','SHUNT_SUM_LIMIT','SVL','reset','维持0E reset/access来源冲突，不用图优先当事实','SVL candidate16383')
ff('INA3221_CVRF_CONFIG_POWERDOWN_EXCEPTION','INA3221','MASK_ENABLE','CVRF','read_clear','CONFIG写清CVRF有powerdown/disable例外','writeCONFIG clears unconditionally desc')
ff('INA3221_TCF_SOFT_RESET_AND_LITERAL','INA3221','MASK_ENABLE','TCF','read_clear','soft reset重新初始化遗漏；reset列11h另有单比特表达冲突','TCF desc only powercycle clear')
ff('INA3221_TCF_RESET_LITERAL_CONFLICT','INA3221','MASK_ENABLE','TCF','reset','11h超字段范围与RW1/0002冲突','not registered')
ff('INA3221_EARLY_CONFIG_DISABLES_TIMING','INA3221','CONFIG','MODE','conditional_write','CONFIG写不止换模式/重启，还会提前停止timing功能','CONFIG write halts conversion only')
ff('INA3221_FLAGS_RW_LABEL_ABSTRACTION','INA3221','MASK_ENABLE','CF','access','硬件标志的RO是抽象；保留原表RW码及写不清状态','CF/SF/WF/PVF/TCF/CVRF codedRO')
ff('ADS1115_OS_TRIGGER_STATUS_GATE','ADS1115','CONFIG','OS','access','OS不是可持久写的普通RW','OS ordinary RW, no field special policy')
ff('ADS1115_CONFIG_APPLIES_AFTER_OLD_CONVERSION','ADS1115','CONFIG','MUX','conditional_write','CONFIG写不中止旧转换，新配置下一次才生效','no condition policy')
ff('ADS1115_COMPARATOR_READ_CONVERSION_EFFECT','ADS1115','CONFIG','COMP_LAT','read_clear','CONVERSION读取解除锁存输出，不是CONFIG bit读清','no external alert state in register contract')
ff('ADS1115_THRESHOLDS_FUNCTION_CONSTRAINT','ADS1115','LO_THRESH','THRESH','conditional_write','补码HI>LO/PGA变化更新及RDY组合必须分开','threshold unrestricted storage only')
ff('ADS1220_ANY_CONFIG_WRITE_RESTARTS','ADS1220','CONFIG1','CM','trigger_completion','任意配置写都有conversion事件，CM1并不代替START/SYNC','only static register interface, commands excluded')
ff('ADS1220_TEMP_MODE_OVERRIDES_CONFIG0_VREF','ADS1220','CONFIG2','VREF','trigger_completion','TS1使CONFIG0无效且实际内部reference，不证明读回位改写','no mode override policy')
ff('ADS1220_IDAC_STARTUP_AND_POWERDOWN','ADS1220','CONFIG2','IDAC','conditional_write','IDAC先设置后routing，单次完成不自动关','only legal codes defined')
ff('ADS1220_PSW_STATE_PERSISTENCE','ADS1220','CONFIG2','PSW','trigger_completion','PSW1单次完成后保持关合，POWERDOWN才开','PSW desc says power switch/powerdown mode')
ff('ADS1220_RESERVED_ALWAYS_WRITE_ZERO','ADS1220','CONFIG3','RESERVED','reserved_policy','0-only合法刺激没有可写性对照','existing policy correct fixed0; prior IR desc reserved却可写 should not imply1')
finding('RESERVED_NONDEFAULT_WRITE_UNDEFINED','INA3221',['CRIT1.UNUSED','WARN1.UNUSED','CRIT2.UNUSED','WARN2.UNUSED','CRIT3.UNUSED','WARN3.UNUSED','MASK_ENABLE.RSVD15'],'Reserved/RW0仅访问码与reset，不定义非零存储功能；分开保留事实与undefined操作','6 limit RESERVED fields unrestricted ordinaryRW; RSVD15 policy already excludes',{'retain_source_RW_label':True,'retain_reset0':True,'main_profile_default_only':True,'exclude_nondefault_write_oracle':True},[loc('INA3221',31,'Table 8-18',needle='Table 8-18.'),loc('INA3221',32,'Table 8-24',needle='Table 8-24.'),loc('INA3221',34,'Table 8-34',needle='Reserved')],'P2','UNDEFINED_BEHAVIOR')

SOURCES=[]
for c in CHIPS:
    reviewed=sorted({z['pdf_page'] for x in FIELDS if x['chip']==c for z in x['locators']}|{z['pdf_page'] for x in GAPS if x['chip']==c for z in x['locators']})
    SOURCES.append({'device':c,'source_path':f'corpus/data/raw_pdf/TI/{c}.pdf','sha256':SHA[c],'manual_version':VERSIONS[c],'pdf_pages':len(DOCS[c]),'source_depth':'full local original manufacturer PDF available; full relevant register and functional sections reviewed','reviewed_pdf_pages':reviewed,'printed_page_mapping':'physical PDF pages reviewed equal printed pages','independent_hash_matches_review_input':SHA[c]==INPUTS[c]['source']['sha256'],'visual_pages':{'TMP117':[27,31,32],'INA219':[10,23],'INA226':[28],'INA3221':[33,34],'ADS1220':[46],'ADS1115':[]}[c],'mutable_web_source_checked':False})

def save(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert len(FIELDS)==154
assert len(BYKEY)==154
assert all(set(x['dimensions'])=={'reset','access','legal_encoding','read_clear','trigger_completion','conditional_write','reserved_policy'} for x in FIELDS)
expected={(x['chip'],x['register'],x['field'],x['bits']) for c in CHIPS for x in INPUTS[c]['inventory']}
assert expected=={(x['chip'],x['register'],x['field'],x['bits']) for x in FIELDS}
assert all(s['independent_hash_matches_review_input'] for s in SOURCES)
for x in FIELDS:
    for d in x['dimensions'].values():
        assert d['locators']
        assert all(isinstance(z,dict) for z in d['locators'])
save('fields.json',FIELDS);save('findings.json',FINDINGS);save('register_gaps.json',GAPS);save('sources.json',SOURCES)
counts={c:dict(Counter(x['overall_status'] for x in FIELDS if x['chip']==c)) for c in CHIPS}
save('quality_checks.json',{'identity_coverage_count':154,'seven_dimension_count':1078,'missing_fields':[],'duplicate_fields':[],'counts':counts,'source_hashes_match':True,'findings_count':len(FINDINGS),'register_gaps_count':len(GAPS),'execution_scope':'hash/extraction/render/structured-source review only; no harness/model/hardware'})
print(json.dumps({'counts':counts,'findings':len(FINDINGS),'gaps':len(GAPS)},ensure_ascii=True))
