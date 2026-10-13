import copy, hashlib, json, re
from pathlib import Path
from collections import Counter
import fitz

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
PREP = ROOT / 'eval/independent_source_admission_20261012'
CHIPS = ['AD5592R', 'LIS3DH', 'LIS2DW12', 'MPU6050']
INPUT_NAMES = ['REPORT.md','SOURCE_POLICY_REVIEW.md','LEGAL_DOMAIN_SUPPLEMENT.md','INDEPENDENT_REPAIR_REVIEW.md','source_policy.json','field_policy_inventory.json','protocol_manifest.json']
inputs = {c:json.loads((PREP/'review_inputs'/f'{c}.json').read_text(encoding='utf-8')) for c in CHIPS}
audited_inputs = []
for n in INPUT_NAMES:
    p=ROOT/'eval/protocol_v2_20261012'/n
    data=p.read_bytes()
    txt=data.decode('utf-8-sig')
    if n.endswith('.json'): json.loads(txt)
    audited_inputs.append({'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(data).hexdigest(),'role':'OBJECT_UNDER_REVIEW_NOT_MANUFACTURER_EVIDENCE','review_scope':'four assigned chip slices and global claims of certification'})
source_specs = {
 'AD5592R':('corpus/data/raw_pdf/ADI/ad5592r.pdf','AD5592R/AD5592R-1 Data Sheet Rev. H'),
 'LIS3DH':('corpus/data/raw_pdf/ST/LIS3DH.pdf','DocID17530 Rev 2'),
 'LIS2DW12':('corpus/data/raw_pdf/ST/lis2dw12.pdf','DS11811 Rev 9'),
 'MPU6050':('corpus/data/raw_pdf/InvenSense/MPU-6000-Register-Map1_mirror.pdf','RM-MPU-6000A-00 Revision 4.2; 08/19/2013'),
}
docs={}; source_records=[]
for chip,(path,version) in source_specs.items():
    p=ROOT/path; d=fitz.open(p); docs[chip]=[pg.get_text(sort=False)+'\n'+pg.get_text(sort=True) for pg in d]
    source_records.append({'chip':chip,'path':path,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'manual_version':version,'pdf_pages':len(d),'source_role':'PRIMARY_REGISTER_MAP_SOURCE','source_depth':'full local manufacturer PDF; relevant original pages text-read; selected original pages visually inspected','official_current_download_verified':False})
p=ROOT/'corpus/data/raw_pdf/InvenSense/MPU6050.pdf'
source_records.append({'chip':'MPU6050','path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'manual_version':'PS-MPU-6000A-00 Revision 3.4; 08/19/2013','pdf_pages':len(fitz.open(p)),'source_role':'SUPPLEMENTARY_PRODUCT_SPECIFICATION','source_depth':'full local PDF available; scope and electrical characteristics read','official_current_download_verified':False,'note':'prepare.py initial device-name match was supplementary PS, not RM. RM p.40 and PS p.40 are different sections; never exchange their locators.'})
src={r['chip']:r for r in source_records if r['source_role']=='PRIMARY_REGISTER_MAP_SOURCE'}

def norm(t): return re.sub(r'\s+',' ',t).strip()
def loc(c,p,section,needle=None):
    t=norm(docs[c][p-1])
    if needle:
        needle=norm(needle)
        i=t.lower().find(needle.lower())
        if i<0: raise ValueError(f'locator missing {c} p{p}: {needle}')
        excerpt=t[i:i+len(needle)]
    else: excerpt=t[:100]
    return {'pdf_page':p,'printed_page':str(p),'table_or_section':section,'excerpt':excerpt,'source_path':src[c]['path']}

def dim(status,fact,rule,locators,eclass='MANUFACTURER_FACT'):
    return {'status':status,'fact':fact,'candidate_rule':rule,'evidence_class':eclass,'locators':copy.deepcopy(locators)}

register_locs={
 'AD5592R':{
  'DAC_RD':[(36,'Table 15','DAC_RD_EN'),(37,'Table 15 continued','111: DAC7')],
  'ADC_SEQ':[(37,'Table 16','ADC sequence repetition'),(38,'Table 16 continued','Include the ADC0 channel')],
  'GEN_CTRL_REG':[(38,'Table 17','ADC buffer precharge'),(39,'Table 17 continued','changed')],
  'ADC_CONFIG':[(39,'Table 18','Select the I/O7 pin as ADC input'),(40,'Table 18 continued','Select the I/O0 pin as ADC input')],
  'DAC_CONFIG':[(40,'Table 19','Select the I/O7 pin as DAC output'),(41,'Table 19 continued','Select the I/O0 pin as DAC output')],
  'PULLDWN_CONFIG':[(41,'Table 20','PULL_DWN_7'),(42,'Table 20 continued','PULL_DWN_0')],
  'SW_RESET':[(50,'Table 28','10110101100: Reset')],
 },
 'LIS3DH':{
  'WHO_AM_I':[(34,'Table 24; §8.5','Device identification register')],
  'CTRL_REG0':[(34,'Tables 25–26; §8.6','Leave bits 0 through 6')],
  'TEMP_CFG_REG':[(34,'Tables 27–28; §8.7','ADC_EN')],
  'CTRL_REG1':[(35,'Tables 29–31; §8.8','Data rate configuration')],
  'CTRL_REG4':[(37,'Tables 37–39; §8.11','Block data update')],
  'STATUS_REG':[(39,'Tables 46–47; §8.15','ZYXOR')],
  **{f'OUT_{a}_{b}':[(40,'§8.16–8.18','two’s complement left-justified')] for a in 'XYZ' for b in ['L','H']},
 },
 'LIS2DW12':{
  'OUT_T_L':[(35,'Tables 22–23; §8.1','TEMP3')],
  'OUT_T_H':[(35,'Tables 24–25; §8.2','TEMP11')],
  'WHO_AM_I':[(35,'Table 26; §8.3','fixed at 44h')],
  'CTRL1':[(36,'Tables 27–31; §8.4','Data rate configuration')],
  'CTRL2':[(37,'Table 32; §8.5','Control register 2 (R/W)')],
  'CTRL4_INT1_PAD_CTRL':[(39,'Tables 36–37; §8.7','Control register 4 (R/W)')],
  'CTRL5_INT2_PAD_CTRL':[(40,'Tables 38–39; §8.8','Control register 5 (R/W)')],
  'OUT_T':[(42,'Tables 43–44; §8.10','1°C/LSB')],
  'STATUS':[(42,'Tables 45–46; §8.11','Status register (R)')],
  'FIFO_CTRL':[(44,'Tables 53–55; §8.18','FIFO control register (R/W)')],
  'FIFO_SAMPLES':[(45,'Tables 56–57; §8.19','number of unread samples')],
  'WAKE_UP_SRC':[(50,'Tables 77–78; §8.28','Wake-up source register (R)')],
  **{f'{a}_OFS_USR':[(54,f'Tables {85+2*i}–{86+2*i}; §8.{32+i}',f"Two's complement user offset value on {a}-axis")] for i,a in enumerate('XYZ')},
 },
 'MPU6050':{
  'SMPLRT_DIV':[(11,'§4.2 divider bit table','Type: Read/Write'),(12,'§4.2 divider formula','8-bit unsigned value')],
  'CONFIG':[(13,'§4.3 CONFIG bit/encoding tables','Type: Read/Write')],
  'GYRO_CONFIG':[(14,'§4.4 GYRO_CONFIG bit/encoding tables','Type: Read/Write')],
  'ACCEL_CONFIG':[(15,'§4.5 ACCEL_CONFIG bit/encoding tables','Type: Read/Write'),(16,'§4.5 parameters','2-bit unsigned value')],
  **{f'ACCEL_{a}OUT_{b}':[(29,'§4.17 acceleration measurements','Type: Read Only')] for a in 'XYZ' for b in ['H','L']},
  'PWR_MGMT_1':[(40,'§4.28 bit/encoding tables','Type: Read/Write'),(41,'§4.28 parameters','The bit automatically clears to 0')],
  'WHO_AM_I':[(45,'§4.32 WHO_AM_I','Type: Read Only')],
 }
}

def rl(c,r): return [loc(c,*v) for v in register_locs[c][r]]
def width(bits):
    n=[int(x) for x in bits.split(':')]; return n[0]-n[-1]+1
fields=[]; bykey={}
for c in CHIPS:
    regmap={r['name']:r for r in inputs[c]['ir']['registers']}
    for f in inputs[c]['inventory']:
        r=regmap[f['register']]; old=next(v for v in r['fields'] if v['name']==f['field']); l=rl(c,r['name'])
        reserved=old['access']=='UNSPEC' or old['name'].startswith(('ZERO','MUST_BE_ZERO','FIXED','RESERVED'))
        reset=old.get('reset'); access=old.get('access')
        rec={'chip':c,'register':r['name'],'field':old['name'],'bits':old['bits'],'source_path':src[c]['path'],'source_sha256':src[c]['sha256'],'manual_version':src[c]['manual_version'],'overall_status':'PASS','old':{'register_addr':r['addr'],'register_reset':r.get('reset'),'access':access,'reset':reset,'desc':old.get('desc'),'field_policy':f.get('field_policy',{}),'known_reset_bit_mask':f.get('known_reset_bit_mask')},'review_scope':'source admission for frozen inventory identity; no model or reference execution','dimensions':{}}
        D=rec['dimensions']
        D['reset']=dim('PASS',f'字段默认值 {reset} 由原始复位/默认表按位提取；仅上电或规定复位完成边界。',{'known_reset':True,'expected':reset,'scope':'specified default boundary, not perpetual output'},l)
        D['access']=dim('PASS',f'原页寄存器类型为 {"R/W" if access in ["RW","UNSPEC"] else "R" if access=="RO" else "write command"}；细位未定义策略另列。',{'verified_access':access,'scope':'legal direct-register access'},l)
        D['legal_encoding']=dim('PASS',f'位图/描述定义 {width(old["bits"])} 位字段；二进制/数字域具体意义见同页。',{'legal_range':[0,2**width(old['bits'])-1]},l)
        D['read_clear']=dim('EXCLUDE','本字段审查页未给自读清零或数据读清零条件；无动作声明不能推导读不变或读清零。',{'assertion':'none','reason':'no field-specific read-clear guarantee in reviewed scope'},l,'ABSTRACTION_ASSUMPTION')
        D['trigger_completion']=dim('EXCLUDE','本字段未有独立触发完成说明；不把配置存储通过解释为模拟或事件功能完成。',{'assertion':'none'},l,'ABSTRACTION_ASSUMPTION')
        D['conditional_write']=dim('PASS','原页配置位/存储值的定义在合法器件模式及接口条件下适用；字段特殊前置条件见具体覆盖。',{'scope':'legal mode/interface, device idle where specified','unconditional_hardware_guarantee':False},l,'ABSTRACTION_ASSUMPTION')
        D['reserved_policy']=dim('EXCLUDE','该命名字段没有独立保留位；同寄存器保留位须由各自记录约束。',{'assertion':'none','not_applicable':True},l,'ABSTRACTION_ASSUMPTION')
        if reserved:
            rec['overall_status']='CONDITIONAL'
            D['access']=dim('EXCLUDE','保留/固定输入位不能仅因所在寄存器R/W或原IR访问标签认定非零写回行为。',{'exclude':['nondefault write persistence','RO flip/write-protection assertions']},l,'UNDEFINED_BEHAVIOR')
            D['legal_encoding']=dim('CONDITIONAL','仅维持文档默认/规定值；其它输入行为不作硅保证。',{'legal_values':[reset],'fixed_write':reset},l,'ABSTRACTION_ASSUMPTION')
            D['conditional_write']=dim('CONDITIONAL','正常操作采用规定/保守默认输入；非法写后的结果不由本审查定义。',{'fixed_write':reset,'exclude_illegal_write_oracle':True},l,'ABSTRACTION_ASSUMPTION')
            D['reserved_policy']=dim('CONDITIONAL','逐位保留和固定零/一策略应按具体原文区别，不外推写保护。',{'fixed_write':reset,'known_reset':True,'access_unknown':True},l,'ABSTRACTION_ASSUMPTION')
        fields.append(rec); bykey[(c,r['name'],old['name'])]=rec

def setd(c,r,f,d,status,fact,rule,ls,eclass='MANUFACTURER_FACT',overall=None):
    rec=bykey[c,r,f]; rec['dimensions'][d]=dim(status,fact,rule,ls,eclass)
    if overall: rec['overall_status']=overall
def many(c,r,fs,d,*args,**kwargs):
    for f in fs: setd(c,r,f,d,*args,**kwargs)
def targetfields(c,r): return [f['field'] for f in fields if f['chip']==c and f['register']==r]

# AD5592R: source framing, readback and lock are real constraints, not a raw memory bus.
AD='AD5592R'; al=[loc(AD,35,'Table 13','Default Value'),loc(AD,27,'POWER-UP TIME','The configuration process takes 250')]
for rec in fields:
    if rec['chip']==AD:
        rec['dimensions']['reset']['locators']+=copy.deepcopy(al)
        rec['dimensions']['access']['fact']='控制字selector由bits14:11编码，MSB=0；厂商允许经指定readback流程读取控制寄存器，不存在本IR式独立总线地址读。'
        rec['dimensions']['access']['candidate_rule']={'abstraction':'selector-to-register adapter','readback':'write CONFIG_READ_AND_LDAC selector and REG_RD_EN then next SPI transfer','exclude':'raw direct-address read as silicon fact'}
        rec['dimensions']['access']['evidence_class']='ABSTRACTION_ASSUMPTION'
        rec['dimensions']['access']['status']='CONDITIONAL'
        rec['dimensions']['access']['locators'] += [loc(AD,27,'READ MODE','Reading from a register first requires a write'),loc(AD,33,'READBACK AND LDAC MODE','on the next SPI transfer')]
        rec['overall_status']='CONDITIONAL'
for r in ['DAC_RD','ADC_SEQ','GEN_CTRL_REG','ADC_CONFIG','DAC_CONFIG','PULLDWN_CONFIG']:
    for f in targetfields(AD,r):
        if f.startswith('RESERVED'):
            ls=rl(AD,r)
            setd(AD,r,f,'reserved_policy','PASS','逐位表明确Reserved及set to0，默认0；禁止把写1的行为定义为忽略、钳位或可存储。',{'fixed_write':0,'known_reset':True,'exclude_illegal_write_oracle':True},ls)
            setd(AD,r,f,'legal_encoding','PASS','厂商要求该保留域写0。',{'legal_values':[0]},ls)
readback_l=[loc(AD,29,'DAC READBACK','Set the Bits[4:3] to 11'),loc(AD,36,'Table 15','1: DAC register readback enabled')]
setd(AD,'DAC_RD','DAC_RD_EN','legal_encoding','CONDITIONAL','正文写bits4:3=11使能；两位组表仅写0/1描述，01/10行为未明确。',{'legal_values':[0,3],'excluded_values':[1,2],'reason':'conservative specified combinations; not official erratum'},readback_l,'SOURCE_CONFLICT')
many(AD,'DAC_RD',['DAC_RD_EN','DAC_CH_SEL'],'trigger_completion','CONDITIONAL','写DAC_RD选择后下一次SPI操作输出DAC数据；只有无ADC转换序列时可读取DAC。',{'completion':'subsequent SPI operation','requires':['no ADC sequence','selected DAC configured'],'exclude':'perpetual readback enable storage inferred from function'},[loc(AD,29,'DAC READBACK','Data can only be read back from a DAC when there is no ADC'),loc(AD,29,'DAC READBACK','on the subsequent SPI operation')],overall='CONDITIONAL')
for r in ['ADC_CONFIG','DAC_CONFIG','PULLDWN_CONFIG']:
    many(AD,r,[f for f in targetfields(AD,r) if not f.startswith('RESERVED')],'conditional_write','REPAIR','I/O pin配置仅在idle、无ADC转换、无register readback且IO_LOCK=0时可重配；IO_LOCK=1写配置被忽略。v2未列这些前置条件。',{'requires':{'GEN_CTRL_REG.IO_LOCK':0,'adc_conversion_active':False,'readback_active':False},'when_locked':'configuration writes ignored','scope':'I/O pin configuration, not all control registers'},[loc(AD,27,'CONFIGURING THE AD5592R','The I/Ox pins can be reconfigured at any time'),loc(AD,27,'CONFIGURING THE AD5592R','pin configuration registers are ignored')],overall='REPAIR')
setd(AD,'GEN_CTRL_REG','IO_LOCK','conditional_write','REPAIR','IO_LOCK=1忽略I/O pin配置写，0允许变更；原始字段动作需跨寄存器状态，不能当普通独立RW数据。',{'cross_register_effect':'lock I/O configuration writes','must_test':'unlocked write / locked ignored write separately','not_claimed':'irreversible lock or all-control lock'},[loc(AD,38,'Table 17','IO_LOCK'),loc(AD,39,'Table 17 continued','changed'),loc(AD,27,'CONFIGURING','pin configuration registers are ignored')],overall='REPAIR')
for f in ['REP','TEMP','ADC_CH_MASK']:
    setd(AD,'ADC_SEQ',f,'trigger_completion','CONDITIONAL','写sequence先track第一通道500ns；后续SYNC下降沿转换并一周期延迟输出；REP=1重复，0序列完成后ADC输出three-state。',{'requires':'enabled ADC pin configuration where selected','start':'next SYNC falling edge after tracking','completion':'sequence converted; serial read cycle latency','simulation':'explicit event/transaction adapter or exclude function'},[loc(AD,29,'ADC OPERATION','Tracking takes 500 ns'),loc(AD,29,'ADC OPERATION','The ADC operates with one cycle latency'),loc(AD,29,'ADC OPERATION','If the REP bit is clear')],overall='CONDITIONAL')
setd(AD,'GEN_CTRL_REG','ALL_DAC','trigger_completion','CONDITIONAL','1使后续DAC地址忽略，将同数据写全部已配置DAC；无此写事务不能声称广播更新验证。',{'event':'future DAC write','target':'all channels configured as DACs'},[loc(AD,39,'Table 17 continued','all channels configured as DACs')],overall='CONDITIONAL')
setd(AD,'GEN_CTRL_REG','ADC_BUF_PRECH','trigger_completion','CONDITIONAL','precharge效果以ADC_BUF_EN为条件，转换时上电，间隙掉电；它不宣称该配置位自清。',{'requires':{'ADC_BUF_EN':1},'excluded':'buffer electrical behavior without ADC model'},[loc(AD,38,'Table 17','If the ADC buffer is enabled, it is powered up while')],overall='CONDITIONAL')
setd(AD,'ADC_SEQ','REP','reserved_policy','CONDITIONAL','通用SPI格式p.26将bits10:9称保留，但Table16明确bit9 REP；逐寄存器解释需显式源冲突策略。',{'interpretation':'per-register detail for REP bit9; preserve generic-format discrepancy','official_erratum':False},[loc(AD,26,'SERIAL INTERFACE; Table 10','Bits[10:9] are reserved'),loc(AD,37,'Table 16','REP')],'SOURCE_CONFLICT')
setd(AD,'SW_RESET','SW_RESET_CODE','access','PASS','Table28为写复位命令，不赋予普通存储RW持久性。',{'verified_access':'W_COMMAND','exclude':'command value persistence'},rl(AD,'SW_RESET'))
setd(AD,'SW_RESET','SW_RESET_CODE','legal_encoding','CONDITIONAL','仅0x5AC明确复位作用；其它11位word未定义该作用，不声称错误key必定无副作用。',{'recognized_reset_key':1452,'wrong_key_behavior':'not specified; exclude hardware oracle'},rl(AD,'SW_RESET'),'UNDEFINED_BEHAVIOR')
setd(AD,'SW_RESET','SW_RESET_CODE','trigger_completion','CONDITIONAL','0x5AC复位所有寄存器和I/O默认；250µs最大，期间禁止新数据写。原子完成为寄存器MVP假设。',{'write_key':'0x5AC','completion':'after reset completed, up to250us','atomic_completed_reset':'ABSTRACTION_ASSUMPTION','no_write_during_reset':True},[loc(AD,50,'Table 28','10110101100: Reset'),loc(AD,33,'RESET FUNCTION','takes 250 µs maximum')],overall='CONDITIONAL')
setd(AD,'SW_RESET','SW_RESET_CODE','reserved_policy','CONDITIONAL','p.26通用bits10:9保留规则与Table28整域key不兼容；不得先强制清零而破坏0x5AC。',{'selector_exception':'SW_RESET key uses bits10:0','preserve_conflict':True},[loc(AD,26,'Table10','Bits[10:9] are reserved'),loc(AD,50,'Table28','10110101100: Reset')],'SOURCE_CONFLICT')

# LIS3DH: seven explicit status defaults; neither Output label nor symmetry may replace source.
LI='LIS3DH'
for rec in fields:
    if rec['chip']==LI and rec['register'] not in ['STATUS_REG'] and not rec['register'].startswith('OUT_'):
        rec['dimensions']['reset']['locators'].append(loc(LI,31,'Table21 register address map',rec['register']))
for f in ['FIXED_6','FIXED_5','FIXED_4','FIXED_3_0']:
    v=1 if f=='FIXED_4' else 0
    setd(LI,'CTRL_REG0',f,'reserved_policy','PASS','Table25脚注及Note要求低7位保留default 0x10，bit4=1其它=0。',{'fixed_write':v,'known_reset':True,'illegal_write_behavior':'excluded'},rl(LI,'CTRL_REG0'))
    setd(LI,'CTRL_REG0',f,'legal_encoding','PASS','原文规定正常操作输入。',{'legal_values':[v]},rl(LI,'CTRL_REG0'))
setd(LI,'TEMP_CFG_REG','FIXED_5_0','reserved_policy','CONDITIONAL','Table27位图直接标0但未给该组access/非法写动作；保持0，已知默认仍保留。',{'fixed_write':0,'known_reset':True,'exclude_illegal_write_oracle':True},rl(LI,'TEMP_CFG_REG'),'ABSTRACTION_ASSUMPTION')
setd(LI,'CTRL_REG1','ODR','legal_encoding','PASS','Table31列0–9，其中8仅Low-power1.60kHz；A–F未列定义。',{'legal_values':list(range(10)),'excluded_values':list(range(10,16))},rl(LI,'CTRL_REG1'))
setd(LI,'CTRL_REG1','ODR','conditional_write','CONDITIONAL','ODR8限LPen1/HR0；9在HR/normal1.344kHz、LP5.376kHz，不能同一frequency解释。',{'if_ODR_8':{'LPen':1,'HR':0},'timing_validation':'excluded'},[loc(LI,35,'Table31','Low power mode (1.60 kHz)')],overall='CONDITIONAL')
setd(LI,'CTRL_REG1','LPen','conditional_write','CONDITIONAL','Table10明确LPen1/HR1 Not allowed；合法刺激不得产生此组合。',{'when_LPen_1':{'CTRL_REG4.HR':0}},[loc(LI,16,'Table10','Not allowed')],overall='CONDITIONAL')
setd(LI,'CTRL_REG4','HR','conditional_write','CONDITIONAL','HR1时LPen需0；高分辨率输出不是普通数据稳定性。',{'when_HR_1':{'CTRL_REG1.LPen':0}},[loc(LI,16,'Table10','Not allowed')],overall='CONDITIONAL')
setd(LI,'CTRL_REG4','BLE','conditional_write','CONDITIONAL','BLE功能仅high-resolution可激活，寄存器位读回不证明字节序。',{'functional_requires':{'HR':1,'LPen':0},'byte_order_function':'separate adapter or exclude'},[loc(LI,37,'Table37 footnote','only in high-resolution mode')],overall='CONDITIONAL')
setd(LI,'CTRL_REG4','BDU','trigger_completion','CONDITIONAL','BDU1使输出MSB/LSB均读完前禁止更新；0连续更新，不能用简单双读稳定性判硬件。',{'completion':'both MSB and LSB read','sample_update_model':'required for function'},[loc(LI,37,'Table38','output registers not updated until MSB and LSB reading')],overall='CONDITIONAL')
setd(LI,'TEMP_CFG_REG','ADC_EN','conditional_write','CONDITIONAL','辅助ADC功能要求ADC_EN1且CTRL_REG4.BDU1，采样频率随ODR；不影响单纯enable位存储范围。',{'functional_requires':{'CTRL_REG4.BDU':1},'functional_sample_rate':'CTRL_REG1.ODR','exclude_without_aux_ADC_model':True},[loc(LI,19,'§3.7','the user must set the BDU bit')],overall='CONDITIONAL')
setd(LI,'TEMP_CFG_REG','TEMP_EN','trigger_completion','CONDITIONAL','TEMP_EN1将ADC通道3连接温度传感器；使用辅助ADC仍须ADC_EN1/BDU1，不能从enable位断言温度输出已生成。',{'functional_requires':{'ADC_EN':1,'BDU':1},'output':'OUT_ADC3_H/L','exclude_without_aux_ADC_model':True},[loc(LI,19,'§3.7','Channel 3 of the ADC can be connected'),loc(LI,19,'§3.7','the user must set the BDU bit')],overall='CONDITIONAL')
setd(LI,'CTRL_REG4','ST','access','REPAIR','Table21明确CTRL_REG4 rw，Table38/ST描述定义自检enable；UNSPEC是旧审查排除标签而非厂家access事实。',{'verified_access':'RW','storage_scope':'legal codes only','exclude_self_test_response':True},[loc(LI,31,'Table21','CTRL_REG4'),loc(LI,37,'Table38','Self-test enable')],overall='REPAIR')
setd(LI,'CTRL_REG4','ST','legal_encoding','PASS','Table39定义00、01、10；11为--。',{'legal_values':[0,1,2],'excluded_values':[3]},[loc(LI,37,'Table39','Self-test 0'),loc(LI,37,'Table39','Self-test 1')])
setd(LI,'CTRL_REG4','ST','reserved_policy','EXCLUDE','ST是命名自检字段；仅编码11未定义，不是整域reserved。',{'not_applicable':True,'exclude_code':3},rl(LI,'CTRL_REG4'),'ABSTRACTION_ASSUMPTION')
for f in targetfields(LI,'STATUS_REG'):
    if f=='XDA':
        setd(LI,'STATUS_REG',f,'reset','CONDITIONAL','Table46含XDA位名，但Table47在本Rev2中没有XDA描述行；Table21只写Output。不能对称补default0。',{'known_reset':False,'exclude_numeric_reset':True},[loc(LI,39,'Tables46–47','XDA'),loc(LI,31,'Table21','STATUS_REG')],'UNDEFINED_BEHAVIOR',overall='CONDITIONAL')
    else:
        setd(LI,'STATUS_REG',f,'reset','REPAIR','Table47该字段明确Default value0；v2因寄存器总表Output而全排除status reset过宽。只允许初始/复位边界0。',{'known_reset':True,'expected':0,'register_known_mask':'0xFE','scope':'default boundary before event'},[loc(LI,39,'Table47',f)],overall='REPAIR')
    setd(LI,'STATUS_REG',f,'access','PASS','Table21该寄存器r，Table46定义相应动态标志位；只读不等于运行中不变。',{'verified_access':'RO','exclude_runtime_stability':True},[loc(LI,31,'Table21','STATUS_REG'),loc(LI,39,'Table46',f)])
    setd(LI,'STATUS_REG',f,'legal_encoding','CONDITIONAL','单bit动态状态，写状态作为刺激不构成事件；XDA描述缺省不得补动作。',{'output_domain':[0,1],'write_stimulus':'none'},[loc(LI,39,'Table46',f)],'ABSTRACTION_ASSUMPTION')
    setd(LI,'STATUS_REG',f,'read_clear','EXCLUDE','该原始Rev2 STATUS描述没有状态清除条件；不能认定读STATUS清、读任一半字节清、或读完双字节清。',{'assertion':'none','requires':'additional original source for flag-clearing condition; no fabricated CoR'},[loc(LI,39,'Tables46–47',f)],'UNDEFINED_BEHAVIOR')
for r in [f'OUT_{a}_{b}' for a in 'XYZ' for b in ['L','H']]:
    f='DATA'; setd(LI,r,f,'reset','EXCLUDE','Table21为Output，无数值default；§8.16–8.18为动态两补码left-justified数据。',{'known_reset':False,'exclude_numeric_reset':True},[loc(LI,31,'Table21',r)]+rl(LI,r),'UNDEFINED_BEHAVIOR',overall='CONDITIONAL')
    setd(LI,r,f,'access','CONDITIONAL','R数据随采样变化；FIFO已启用时输出最旧样本并推进读取，BDU1需上下字节都读后更新。',{'verified_access':'RO','exclude_runtime_stability':True,'default_fixture':{'FIFO_EN':0,'BDU':0,'ODR':0}},[loc(LI,31,'Table21',r),loc(LI,23,'§5.1.5','Each time data is read from the FIFO'),loc(LI,37,'Table38','output registers not updated')])
    setd(LI,r,f,'trigger_completion','CONDITIONAL','FIFO读取按6输出寄存器数据集，地址0x2D后回0x28；32级全读192字节。读数据不是恒零read-clear。',{'fifo_model':'sample queue and burst transaction; otherwise excluded','burst_bytes_for_all_levels':192,'bdu_release':'both MSB and LSB read'},[loc(LI,23,'§5.1.5','192 bytes'),loc(LI,37,'Table38','MSB and LSB reading')])
    setd(LI,r,f,'read_clear','CONDITIONAL','FIFO读取first sample set后FIFO_SRC_REG.OVRN_FIFO清0；这是取完整样本集导致的跨寄存器状态变化，不是读任一byte使DATA清0，也不推导STATUS_REG清除条件。',{'cross_register_clear':'OVRN_FIFO clears once first sample set has been read','own_DATA_clear':'no assertion','STATUS_flag_clear':'not specified by this fact','requires':'enabled FIFO and sample-set read transaction'},[loc(LI,23,'§5.1.5','Each time data is read from the FIFO'),loc(LI,41,'Table52','The OVRN bit is set to 0')])
    setd(LI,r,f,'legal_encoding','CONDITIONAL','RO字节是8/10/12bit两补码left-justified样本的一部分，低byte有效位和BLE字节顺序随合法mode变；不把位宽全域当无条件输出域。',{'write_stimuli':'none','normal_BLE0_output_format':{'LPen1_HR0':'8bit left-justified','LPen0_HR0':'10bit left-justified','LPen0_HR1':'12bit left-justified'},'BLE1':'swapped bytes only in high-resolution','exclude_exhaustive_output_value_claim':True},[loc(LI,16,'Table10','8-bit data output'),loc(LI,40,'§8.16–8.18','two’s complement left-justified'),loc(LI,37,'Table37','only in high-resolution mode')])
setd(LI,'CTRL_REG4','SIM','conditional_write','CONDITIONAL','SIM切换SPI4wire/3wire，位存储验证不能证明切换后物理read仍按旧帧成功。',{'adapter_required':'selected SPI mode','exclude_physical_interface_guarantee':True},[loc(LI,37,'Table38','3-wire interface')],overall='CONDITIONAL')

# LIS2DW12: explicit temperature bit-order repair, mode/FIFO side effects and non-proven read-clear.
LD='LIS2DW12'
for rec in fields:
    if rec['chip']==LD:
        rp=34 if rec['register'] in ['Y_OFS_USR','Z_OFS_USR'] else 33
        rec['dimensions']['reset']['locators'].append(loc(LD,rp,'Table21 register map',rec['register']))
for f,nb in [('TEMP_3_0','7:4'),('ZERO_7_4','3:0')]:
    rec=bykey[LD,'OUT_T_L',f]; rec['overall_status']='REPAIR'; rec['candidate_bits']=nb
    setd(LD,'OUT_T_L',f,'access','REPAIR','Table22从MSB到LSB为TEMP3 TEMP2 TEMP1 TEMP0 0 0 0 0；当前字段位域上下半字节颠倒。',{'verified_access':'RO','candidate_bits':nb,'rename':'ZERO_3_0' if f=='ZERO_7_4' else f},[loc(LD,35,'Table22','TEMP3'),loc(LD,18,'§3.6','left-justified in 12-bit mode')],overall='REPAIR')
    setd(LD,'OUT_T_L',f,'legal_encoding','REPAIR','12bit温度左对齐形成16bit两补码，TEMP3:0在总线bits7:4，低4位0。',{'candidate_bits':nb,'legal_values':[0] if f=='ZERO_7_4' else list(range(16))},[loc(LD,35,'Tables22–23','TEMP3'),loc(LD,18,'§3.6','left-justified in 12-bit mode')],overall='REPAIR')
setd(LD,'OUT_T_L','ZERO_7_4','reserved_policy','REPAIR','零位属于温度输出低半字节bits3:0，来源R输出位图明示0；不是强制写0配置位。',{'candidate_bits':'3:0','rename':'ZERO_3_0','known_zero_mask':'0x0F','verified_access':'RO'},[loc(LD,35,'Table22','TEMP3')],overall='REPAIR')
for r,f in [('OUT_T_L','TEMP_3_0'),('OUT_T_H','TEMP_11_4'),('OUT_T','TEMP_7_0')]:
    setd(LD,r,f,'trigger_completion','CONDITIONAL','温度输出是采样的两补码温度，初值0不是运行时恒25°C；BDU和输出更新条件独立于只读保护。',{'dynamic_output':True,'exclude_runtime_stability':True,'bdu':'both MSB and LSB read when applicable'},rl(LD,r)+[loc(LD,37,'BDU','both MSB and LSB are read')],overall='REPAIR' if r=='OUT_T_L' else 'CONDITIONAL')
setd(LD,'CTRL1','ODR','legal_encoding','PASS','Table29只定义0–9，A–F未定义。不同MODE数据率映射不能独立当精确功能。',{'legal_values':list(range(10)),'excluded_values':list(range(10,16))},rl(LD,'CTRL1'))
setd(LD,'CTRL1','MODE','legal_encoding','PASS','Table30定义0low-power、1high-performance、2single demand，3为-。',{'legal_values':[0,1,2],'excluded_values':[3]},rl(LD,'CTRL1'))
setd(LD,'CTRL1','LP_MODE','legal_encoding','PASS','Table31四个编码均low-power模式，分别12/14bit；没有独立reserved编码。',{'legal_values':[0,1,2,3]},rl(LD,'CTRL1'))
many(LD,'CTRL1',['MODE','LP_MODE','ODR'],'trigger_completion','CONDITIONAL','MODE2单次按需转换由CTRL3 SLP_MODE_SEL/SLP_MODE_1或INT2时钟触发；输出寄存器/FIFO存入后power-down，typ.T_on不是严格完成上限。',{'when_MODE_2':'event adapter for CTRL3 or INT2; then output available and power-down','typ_T_on_ms':[1.2,1.7,2.3,3.55],'time_bound_claim':'none','exclude_unmodelled_function':True},[loc(LD,16,'§3.2.2','When output data is saved'),loc(LD,38,'Table34','this bit is set to 0 automatically')],overall='CONDITIONAL')
setd(LD,'CTRL2','BOOT','trigger_completion','CONDITIONAL','BOOT重载NVM trimming；操作完自回0；§3.5明确不影响control registers，不应当SOFT_RESET。',{'start':'write1','completion':'NVM download completed','clear_on_completion':True,'control_register_reset':False,'static_baseline':0,'exclude_unmodelled_completion':True},[loc(LD,37,'BOOT description','Once the operation is over'),loc(LD,18,'§3.5','Setting this bit has no impact on the control registers')],overall='CONDITIONAL')
setd(LD,'CTRL2','SOFT_RESET','trigger_completion','CONDITIONAL','SOFT_RESET复位所有control registers然后回0；未给动态输出/FIFO全部归默认的保证，也未给瞬时read时序。',{'start':'write1','reset_scope':'all control registers','clear_on_completion':True,'atomic_completed_reset':'ABSTRACTION_ASSUMPTION','exclude_unmodelled_completion':True},[loc(LD,37,'SOFT_RESET','Soft reset acts as reset for all control registers')],overall='CONDITIONAL')
setd(LD,'CTRL2','MUST_BE_ZERO','access','REPAIR','Table32脚注要求该位设0以正确操作，没有RO访问标签或非法写1后读回保证。',{'verified_access':None,'fixed_write':0,'exclude_protection_assertion':True},[loc(LD,37,'Table32 footnote1','This bit must be set to 0')],overall='REPAIR')
setd(LD,'CTRL2','MUST_BE_ZERO','reserved_policy','PASS','正常操作必须写0；默认0证据由Table21和位图支持。',{'fixed_write':0,'known_reset':True,'exclude_illegal_write_oracle':True},[loc(LD,37,'Table32 footnote1','This bit must be set to 0'),loc(LD,33,'Table21','CTRL2')])
setd(LD,'CTRL2','BDU','trigger_completion','CONDITIONAL','BDU1未读完MSB/LSB前禁止输出更新；避免不同sample time混读，不能声明任何两次单读稳定。',{'completion':'both MSB and LSB read','unmodelled_function':'exclude'},[loc(LD,37,'BDU','both MSB and LSB are read')],overall='CONDITIONAL')
for f,text in [('IF_ADD_INC','automatically incremented'),('I2C_DISABLE','I²C mode disabled'),('SIM','3-wire interface')]:
    setd(LD,'CTRL2',f,'conditional_write','CONDITIONAL','该配置改变后续总线可用性或读写地址递增；内存式direct-register接口省略功能只能声明抽象。',{'adapter_required':True,'exclude_physical_interface_assertion':True},[loc(LD,37,'Table32 / control definitions',text)],overall='CONDITIONAL')
for r in ['CTRL4_INT1_PAD_CTRL','CTRL5_INT2_PAD_CTRL']:
    for f in targetfields(LD,r):
        setd(LD,r,f,'trigger_completion','CONDITIONAL','该位为相关事件到INT pad的routing enable；事件配置、routing及CTRL7全局enable/CTRL3锁存共同决定输出。只验存储未验证事件。',{'event_function':'explicit event generator or excluded','requires':'source configured and interrupts enabled where required'},rl(LD,r)+[loc(LD,55,'Table92','Enables interrupts')],overall='CONDITIONAL')
for r in ['STATUS','FIFO_SAMPLES','WAKE_UP_SRC']:
    for f in targetfields(LD,r):
        if f.startswith('ZERO'):
            setd(LD,r,f,'access','PASS','Table77位图高两位0，该寄存器R；只读0定义不外推其它保留域。',{'verified_access':'RO','hard_zero_bits':'7:6'},rl(LD,r)); continue
        setd(LD,r,f,'access','CONDITIONAL','只读动态事件/FIFO状态；文档初值0与事件后的值分别处理，不以静态存储双读判硅状态。',{'verified_access':'RO','exclude_runtime_stability':True,'event_fixture_required':True},rl(LD,r),overall='CONDITIONAL')
        setd(LD,r,f,'conditional_write','EXCLUDE','R字段无写事件接口；无法用任意write模拟状态触发。',{'assertion':'none','event_injection':'explicit source event or exclude'},rl(LD,r),'ABSTRACTION_ASSUMPTION')
        setd(LD,r,f,'legal_encoding','CONDITIONAL','输出bit/domain由事件决定；不构造非法状态写入。',{'output_domain':list(range(33)) if f=='DIFF' else [0,1],'no_write_stimuli':True},rl(LD,r),'ABSTRACTION_ASSUMPTION')
for f in ['FF_IA','SLEEP_STATE_IA','WU_IA','X_WU','Y_WU','Z_WU']:
    setd(LD,'WAKE_UP_SRC',f,'read_clear','REPAIR' if f=='FF_IA' else 'CONDITIONAL','§8.28仅事件状态描述，无读WAKE_UP_SRC自动清规定；§8.31明确读ALL_INT_SRC使相关已routing到INT pads的function flags同时reset。',{'clear_operation':'read ALL_INT_SRC (0x3B)','scope':'related interrupt function flags routed to INT pads; axis-specific clearing not expressly mapped','exclude_unqualified_self_CoR':True},[loc(LD,50,'§8.28 Tables77–78',f if f not in ['SLEEP_STATE_IA'] else 'Sleep event status'),loc(LD,53,'§8.31','Reading this register, all related interrupt function flags')],overall='REPAIR' if f=='FF_IA' else 'CONDITIONAL')
setd(LD,'FIFO_CTRL','FMODE','legal_encoding','PASS','Table55合法0/1/3/4/6，2/5/7Reserved。',{'legal_values':[0,1,3,4,6],'excluded_values':[2,5,7]},[loc(LD,44,'Table55','Reserved')])
setd(LD,'FIFO_CTRL','FMODE','trigger_completion','CONDITIONAL','Table55的011写trigger deasserted，正文§5.3.4写trigger event；100表名bypass-to-continuous却终态写FIFO，而正文§5.3.5写continuous。原文歧义保留，不能称官方勘误。',{'static_legal_codes':[0,1,3,4,6],'exclude_event_mode_oracle':[3,4],'FMODE_0_effect':'bypass resets FIFO content','conflict_id':'MOTION-LIS2-FIFO-MODE-SOURCE'},[loc(LD,44,'Table55','then FIFO mode'),loc(LD,25,'§5.3.4','FIFO mode starts upon an internal trigger event'),loc(LD,26,'§5.3.5','starts in continuous mode upon an internal trigger event'),loc(LD,24,'§5.3.1','Bypass mode is also used to reset')],'SOURCE_CONFLICT',overall='CONDITIONAL')
setd(LD,'FIFO_CTRL','FTH','trigger_completion','CONDITIONAL','threshold状态通常DIFF≥FTH，但FTH0明确FIFO_FTH0；切进/出FIFO首个样本discard。',{'FIFO_FTH':'FTH!=0 and DIFF>=FTH','discard_first_sample_on_FIFO_switch':True,'event_function':'exclude without FIFO event model'},[loc(LD,23,'§5.3','If FTH[4:0] is equal to 0'),loc(LD,23,'§5.3','the first sample acquired must be discarded')],overall='CONDITIONAL')
many(LD,'FIFO_SAMPLES',['FIFO_FTH','FIFO_OVR','DIFF'],'trigger_completion','CONDITIONAL','FIFO_FTH受FTH0特例；FIFO_OVR为full且至少overwrite；DIFF0空、32满，不是6bit全域任意状态。输出读取FIFO样本影响这些状态。',{'DIFF_output_domain':[0,32],'FIFO_FTH':'FTH!=0 and DIFF>=FTH','FIFO_OVR':'full and at least one overwrite','requires':'sample queue and read transaction model'},[loc(LD,45,'Table57','at least one sample has been overwritten'),loc(LD,23,'§5.3','If FTH[4:0] is equal to 0')],overall='CONDITIONAL')
for a in 'XYZ':
    r=f'{a}_OFS_USR'
    setd(LD,r,r,'conditional_write','CONDITIONAL','two’s complement offset值存储；输出/唤醒应用依CTRL7 USR_OFF_ON_OUT/ON_WU、USR_OFF_W，输出offset还要求CTRL6 FDS0。',{'legal_range':[0,255],'function_requires':'CTRL7 offsets enabled; output path FDS=0','weight_options':['977ug/LSB','15.6mg/LSB'],'exclude_function_without_dependencies':True},rl(LD,r)+[loc(LD,55,'Table92','FDS bit in CTRL6 (25h) must be set to 0')],overall='CONDITIONAL')

# MPU6050: separate RM source from PS, preserved source-layout discrepancies and any-read clear side effects.
MP='MPU6050'; reset_l=[loc(MP,8,'§3 reset note','The reset value is 0x00 for all registers')]
for rec in fields:
    if rec['chip']==MP:
        rec['dimensions']['reset']['locators']+=copy.deepcopy(reset_l)
        if rec['register']!='WHO_AM_I':
            rec['dimensions']['read_clear']=dim('CONDITIONAL','本字段数据无自身read-clear说明；INT_PIN_CFG.INT_RD_CLEAR=1时任何read operation清interrupt status，读取本地址也有跨寄存器副作用。',{'own_data_read_clear':'no assertion','cross_register_effect':'any read clears interrupt status only if INT_RD_CLEAR=1','default_fixture_INT_RD_CLEAR':0},[loc(MP,26,'§4.14 INT_RD_CLEAR','interrupt status bits are cleared on any read')])
setd(MP,'SMPLRT_DIV','SMPLRT_DIV','trigger_completion','CONDITIONAL','divider改变FIFO、DMP、输出的sample rate；accel1kHz使更高sample rate可能重复相同样本。',{'formula':'gyro output rate/(1+SMPLRT_DIV)','unmodelled_rate_function':'exclude'},[loc(MP,12,'§4.2','Sample Rate = Gyroscope Output Rate'),loc(MP,12,'§4.2','same accelerometer sample may be output')],overall='CONDITIONAL')
setd(MP,'CONFIG','DLPF_CFG','legal_encoding','CONDITIONAL','§4.3表7列Reserved（带Fs8kHz），§4.2却明确0 or7禁用DLPF。先只0–6，保留文档7含义冲突，不能宣称7无任何定义。',{'legal_values':list(range(7)),'excluded_values':[7],'exclusion_reason':'source internally ambiguous','conflict_id':'MOTION-MPU-DLPF7-SOURCE'},[loc(MP,13,'§4.3 DLPF table','RESERVED'),loc(MP,12,'§4.2','DLPF_CFG = 0 or 7')],'SOURCE_CONFLICT',overall='CONDITIONAL')
setd(MP,'CONFIG','EXT_SYNC_SET','trigger_completion','CONDITIONAL','FSYNC采样值取代所选sensor data LSB；5/6/7直接影响ACCEL X/Y/Z低byte bit0，采样后latch重设当前FSYNC。',{'output_replacement':{'5':'ACCEL_XOUT_L[0]','6':'ACCEL_YOUT_L[0]','7':'ACCEL_ZOUT_L[0]'},'requires':'FSYNC signal event model or exclude function'},[loc(MP,13,'§4.3','in place of the least significant bit'),loc(MP,13,'§4.3','latch will reset')],overall='CONDITIONAL')
for f in ['XG_ST','YG_ST','ZG_ST']:
    setd(MP,'GYRO_CONFIG',f,'access','CONDITIONAL','§3 overview p.6对应high3bits为-，但§4.4 p.14具体位表/正文命名XG/YG/ZG_ST可写自检；须记录布局差异，不默认为官方勘误。',{'verified_access':'RW under detailed-register interpretation','interpretation':'detail-first provisional','conflict_id':'MOTION-MPU-GYRO-ST-LAYOUT'},[loc(MP,6,'§3 overview GYRO_CONFIG','GYRO_CONFIG'),loc(MP,14,'§4.4','XG_ST')],'SOURCE_CONFLICT',overall='CONDITIONAL')
    setd(MP,'GYRO_CONFIG',f,'trigger_completion','CONDITIONAL','bit1启用对应gyro轴自检，允许独立/同时；结果应比较enable与disable响应，不是自清脉冲，完成时间未给。',{'legal_values':[0,1],'self_test':'enabled state, not automatic clear','exclude_analog_response':True},[loc(MP,14,'§4.4','independently or all at the same time')])
for f in ['XA_ST','YA_ST','ZA_ST']:
    setd(MP,'ACCEL_CONFIG',f,'trigger_completion','CONDITIONAL','1启用对应accel轴自检；§4.1要求自检fullscale±8g，功能验收依PS响应范围。普通读写不证明自检。',{'requires_for_self_test':{'AFS_SEL':2},'exclude_analog_response':True},[loc(MP,15,'§4.5','independently or all at the same time'),loc(MP,11,'§4.1','full-scale range should be set to ±8g')],overall='CONDITIONAL')
for r,f in [('CONFIG','RESERVED_7_6'),('GYRO_CONFIG','RESERVED_2_0'),('PWR_MGMT_1','RESERVED_4')]:
    setd(MP,r,f,'reserved_policy','CONDITIONAL','原文Reserved且总复位note0；未写mandatory0或非法写行为。保守只写0属于协议选域。',{'fixed_write':0,'known_reset':True,'exclude_illegal_write_oracle':True},rl(MP,r)+reset_l,'ABSTRACTION_ASSUMPTION')
setd(MP,'ACCEL_CONFIG','RESERVED_2_0','reserved_policy','CONDITIONAL','p.15表低3bit标-，正文提及DHPF却不给位域/编码；无set0或明确RO保证。只保持复位0，访问不评分。',{'fixed_write':0,'known_reset':True,'exclude_access_oracle':True,'no_invented_DHPF_encoding':True},[loc(MP,15,'§4.5','Digital High Pass Filter')]+reset_l,'UNDEFINED_BEHAVIOR',overall='CONDITIONAL')
for a in 'XYZ':
    for b in ['H','L']:
        r=f'ACCEL_{a}OUT_{b}'; f=targetfields(MP,r)[0]
        setd(MP,r,f,'access','CONDITIONAL','RO最近测量；内部sample-rate更新，serial idle时user-facing复制；burst同一采样保证，单byte读取需检查DRDY，不保证运行双读值相同。',{'verified_access':'RO','exclude_runtime_stability':True,'same_sample_guarantee':'burst read only; single reads check data ready'},[loc(MP,29,'§4.17','whenever the serial interface is idle'),loc(MP,29,'§4.17','a burst read of sensor registers')],overall='CONDITIONAL')
        setd(MP,r,f,'trigger_completion','CONDITIONAL','测量sample-rate更新；LSB可被FSYNC替代，clockstop/sleep/cycle改变更新过程。reset0仅复位边界。',{'requires':'sample model and config mode events or excluded','EXT_SYNC_SET':'5/6/7 alters corresponding low byte bit0'},[loc(MP,29,'§4.17','written to these registers at the Sample Rate'),loc(MP,13,'§4.3','in place of the least significant bit')])
setd(MP,'PWR_MGMT_1','DEVICE_RESET','access','PASS','命名RW reset control；写1为reset action，完成自清0，不能一般持久存储。',{'verified_access':'RW_ACTION','exclude_write1_persistence':True},rl(MP,'PWR_MGMT_1'))
setd(MP,'PWR_MGMT_1','DEVICE_RESET','trigger_completion','CONDITIONAL','写1复位所有internal registers到§3默认，reset完自清0；100ms+signal_path_reset+100ms备注只适用于SPI设备情形，MPU6050为I²C。',{'completed_reset_scope':'all internal registers to section3 defaults','clear_on_completion':True,'atomic_completed_reset':'ABSTRACTION_ASSUMPTION','do_not_apply_SPI_wait_as_I2C_guarantee':True},[loc(MP,41,'§4.28 DEVICE_RESET','resets all internal registers to their default values'),loc(MP,41,'§4.28 SPI note','When using SPI interface')],overall='CONDITIONAL')
setd(MP,'PWR_MGMT_1','CLKSEL','legal_encoding','PASS','0–5及7定义，6Reserved；7停clock并保持timing generator reset，不能叫非法7。',{'legal_values':[0,1,2,3,4,5,7],'excluded_values':[6]},[loc(MP,40,'§4.28 CLKSEL table','Stops the clock and keeps the timing generator')])
setd(MP,'PWR_MGMT_1','CLKSEL','trigger_completion','CONDITIONAL','7停止clock；4/5依external clock；gyro PLL reference1–3与gyro状态有关。位存储测试未验clock功能。',{'clock_stop_value':7,'external_source_required_values':[4,5],'exclude_unmodelled_clock_behavior':True},[loc(MP,40,'§4.28 CLKSEL table','Stops the clock')],overall='CONDITIONAL')
setd(MP,'PWR_MGMT_1','SLEEP','trigger_completion','CONDITIONAL','1 low-power sleep，不以输出永久0推导sleep；初始化SLEEP1为明确default。',{'when_1':'sleep mode','runtime_updates':'explicit sleep model or excluded'},[loc(MP,40,'§4.28','By setting SLEEP to 1')],overall='CONDITIONAL')
setd(MP,'PWR_MGMT_1','CYCLE','conditional_write','CONDITIONAL','Cycle功能只在CYCLE1且SLEEP disabled生效；速率依PWR_MGMT_2 LP_WAKE_CTRL，未映射。',{'functional_requires':{'SLEEP':0},'dependency':'PWR_MGMT_2.LP_WAKE_CTRL','exclude_unmodelled_function':True},[loc(MP,40,'§4.28','When CYCLE is set to 1 while SLEEP is disabled')],overall='CONDITIONAL')
setd(MP,'PWR_MGMT_1','TEMP_DIS','trigger_completion','CONDITIONAL','1 disable temperature sensor；未给单独sensor output复位/读值保证。',{'when_1':'temperature sensor disabled','exclude_temperature_output_oracle':True},[loc(MP,41,'§4.28','disables the temperature sensor')],overall='CONDITIONAL')
for f in ['WHO_AM_I','ZERO_7','ZERO_0']:
    setd(MP,'WHO_AM_I',f,'read_clear','CONDITIONAL','WHO_AM_I自身为固定ID；任何read清interrupt规则仍在INT_RD_CLEAR1成立，固定ID不能代表无读副作用。',{'own_data':'fixed identifier / hard zero bits','cross_register_effect':'interrupt clear when INT_RD_CLEAR=1'},[loc(MP,45,'§4.32','Hard coded to 0'),loc(MP,26,'§4.14','on any read')])
for f in ['ZERO_7','ZERO_0']:
    setd(MP,'WHO_AM_I',f,'access','PASS','§4.32明确reserved hardcoded0，RO register，与普通reserved位不同。',{'verified_access':'RO','hard_zero':True},[loc(MP,45,'§4.32','Hard coded to 0')])
    setd(MP,'WHO_AM_I',f,'legal_encoding','PASS','输出明确定义为0。',{'output_values':[0]},[loc(MP,45,'§4.32','Hard coded to 0')])
    setd(MP,'WHO_AM_I',f,'reserved_policy','PASS','硬编码0事实支持读恒0；不可外推其余Reserved。',{'hard_zero':True,'verified_access':'RO','known_reset':True},[loc(MP,45,'§4.32','Hard coded to 0')])
    bykey[MP,'WHO_AM_I',f]['overall_status']='PASS'
for c,r,f,value in [(LI,'WHO_AM_I','ID',51),(LD,'WHO_AM_I','ID',68),(MP,'WHO_AM_I','WHO_AM_I',52)]:
    setd(c,r,f,'legal_encoding','PASS','器件标识的来源给定值；没有可写刺激，不把字段位宽范围当有效设备ID域。',{'output_values':[value],'write_stimuli':'none'},rl(c,r))
for a in 'XYZ':
    for b in ['H','L']:
        r=f'ACCEL_{a}OUT_{b}'; f=targetfields(MP,r)[0]
        setd(MP,r,f,'legal_encoding','CONDITIONAL','只读字节是16bit两补码测量切片；具体可观测值受物理输入、fullscale及FSYNC LSB替换影响，无任意写事件刺激。',{'write_stimuli':'none','format':'16bit two\'s complement high/low byte','exclude_exhaustive_output_value_claim':True},[loc(MP,29,'§4.17','16-bit 2’s complement value'),loc(MP,13,'§4.3','in place of the least significant bit')])

# All concrete findings are review candidates; no protected file is mutated.
findings=[]
def finding(id,c,targets,problem,old,candidate,ls,severity='P1'):
    findings.append({'id':id,'chip':c,'targets':targets,'problem':problem,'old':old,'candidate_rule':candidate,'locators':ls,'severity':severity,'official_erratum':False})
finding('MOTION-LIS2-TEMP-NIBBLE',LD,['OUT_T_L.TEMP_3_0','OUT_T_L.ZERO_7_4'],'温度低byte数据/零域上下半字节颠倒，来源图与12bit左对齐一致。',{'TEMP_3_0.bits':'3:0','ZERO_7_4.bits':'7:4'},{'TEMP_3_0.bits':'7:4','ZERO_7_4.rename':'ZERO_3_0','ZERO_3_0.bits':'3:0','known_zero_mask':'0x0F'},[loc(LD,35,'Table22; visually verified','TEMP3'),loc(LD,18,'§3.6','left-justified in 12-bit mode')])
finding('MOTION-LIS3-STATUS-DEFAULT',LI,['STATUS_REG.'+f for f in ['ZYXOR','ZOR','YOR','XOR','ZYXDA','ZDA','YDA']],'Output总表不能覆盖Table47七个明确default0；14动态字段reset全排除措辞不准确。',{'v2_status_known_reset_mask':'0x00','report':'14 nonstatic reset fields'},{'known_reset_mask':'0xFE','expected':0,'scope':'initial default before measurement/event','XDA_unknown':True},[loc(LI,39,'Table47; visually verified','Default value: 0'),loc(LI,31,'Table21','STATUS_REG')])
finding('MOTION-LIS3-XDA-NO-DESCRIPTION',LI,['STATUS_REG.XDA'],'Table46有XDA，Table47实际缺XDA行；缺少默认和clear动作不能补全。',{'field_reset':0},{'known_reset':False,'exclude_CoR':True,'do_not_infer_by_symmetry':True},[loc(LI,39,'Tables46–47; visually verified','XDA')],'P2')
finding('MOTION-LIS3-FIFO-READ-EFFECT',LI,['OUT_X/Y/Z','FIFO_SRC_REG.OVRN_FIFO'],'输出读取FIFO样本集会推进FIFO并在first sample set读完后清OVRN_FIFO；不等于DATA读清0或STATUS_REG旗标的清除规则。',{'v2':'no FIFO/read transaction model'},{'cross_register_clear':'OVRN_FIFO after first sample set read','sample_pop':True,'exclude_unmodelled_FIFO_function':True},[loc(LI,23,'§5.1.5','Each time data is read from the FIFO'),loc(LI,41,'Table52','The OVRN bit is set to 0')],'P2')
finding('MOTION-LIS3-ST-ACCESS',LI,['CTRL_REG4.ST'],'UNSPEC是旧IR排除标记，不能当厂商访问事实。原始rw表和合法自检编码支持限定RW。',{'ir_access':'UNSPEC'},{'access':'RW','legal_values':[0,1,2],'exclude_values':[3],'exclude_analog_response':True},[loc(LI,31,'Table21','CTRL_REG4'),loc(LI,37,'Tables38–39','Self-test enable')],'P2')
finding('MOTION-LIS3-AUX-ADC-BDU',LI,['TEMP_CFG_REG.ADC_EN','TEMP_CFG_REG.TEMP_EN','CTRL_REG4.BDU'],'辅助ADC/温度功能必须BDU1/ADC_EN1，现policy未列功能前置条件。',{'v2':'no auxiliary ADC condition'},{'ADC_function_requires':{'BDU':1,'ADC_EN':1},'TEMP_function':'ADC channel3 selected with TEMP_EN1; output OUT_ADC3','function_without_dependencies':'EXCLUDE'},[loc(LI,19,'§3.7','the user must set the BDU bit'),loc(LI,19,'§3.7','Channel 3 of the ADC can be connected')],'P2')
finding('MOTION-LIS2-MBZ-ACCESS',LD,['CTRL2.MUST_BE_ZERO'],'脚注must0不证明RO hardwire；现policy虽排除非法写但IR未来生成仍误导。',{'ir_access':'RO'},{'access':'UNSPEC','fixed_write':0,'known_reset':True,'exclude_illegal_write_oracle':True},[loc(LD,37,'Table32 footnote','This bit must be set to 0')],'P2')
finding('MOTION-LIS2-WAKE-CLEAR',LD,['WAKE_UP_SRC.FF_IA','WAKE_UP_SRC','ALL_INT_SRC'],'FF_IA“自读清”未在§8.28规定；明确可核的clear操作是ALL_INT_SRC对related routed interrupt flags。',{'FF_IA.desc':'自由落体事件标志，读清除'},{'desc':'Free-fall event status. ALL_INT_SRC read resets related routed interrupt function flags; no unqualified self-CoR guarantee','CoR_assertion':'exclude unless relevant mapped clear semantics and fixture'},[loc(LD,50,'§8.28','Free-fall event detection status'),loc(LD,53,'§8.31','Reading this register, all related interrupt function flags')])
finding('MOTION-LIS2-FIFO-MODE-SOURCE',LD,['FIFO_CTRL.FMODE'],'§5.3.4/5.3.5的trigger event/continuous终态与Table55的deasserted/FIFO终态不一致。',{'Table55.FMODE_4':'then FIFO mode','body_FMODE_4':'continuous upon trigger event'},{'legal_codes':[0,1,3,4,6],'source_conflict':'UNRESOLVED','exclude_FMODE3_4_event_oracles':True},bykey[LD,'FIFO_CTRL','FMODE']['dimensions']['trigger_completion']['locators'])
finding('MOTION-LIS2-FTH0',LD,['FIFO_CTRL.FTH','FIFO_SAMPLES.FIFO_FTH','STATUS.FIFO_THS'],'FTH0时明确FIFO_FTH0，不能无条件DIFF≥FTH公式；FIFO切换首样discard。',{'v2':'no functional FIFO rule'},{'FIFO_FTH':'FTH!=0 and DIFF>=FTH','discard_first_sample_on_switch':True,'functional_scope':'requires FIFO events'},[loc(LD,23,'§5.3','If FTH[4:0] is equal to 0')],'P2')
finding('MOTION-AD-LOCK-IDLE',AD,['GEN_CTRL_REG.IO_LOCK','ADC_CONFIG.ADC_PIN_MASK','DAC_CONFIG.DAC_PIN_MASK','PULLDWN_CONFIG.PULL_DWN_MASK'],'缺跨寄存器IO_LOCK及idle无转换/无readback前置条件。',{'source_policy_constraints':[]},{'requires_IO_LOCK':0,'requires_idle':True,'locked_pin_config_writes':'ignored'},[loc(AD,27,'CONFIGURING','pin configuration registers are ignored'),loc(AD,27,'CONFIGURING','The I/Ox pins can be reconfigured at any time')])
finding('MOTION-AD-READBACK-ADAPTER',AD,['all mapped control registers','CONFIG_READ_AND_LDAC.REG_RD_EN'],'direct memory read抽象缺厂商readback流程：selector/REG_RD_EN/next SPI，REG_RD_EN完成自清；ADC转换时其它read request ignored。',{'register_model':'direct address read'},{'scope':'declared selector abstraction, not physical SPI guarantee','adapter_requires':['readback selector','REG_RD_EN','next SPI','no active ADC for other reads'],'REG_RD_EN_clear':'read complete'},[loc(AD,27,'READ MODE','all other read requests are ignored'),loc(AD,43,'Table21','REG_RD_EN automatically clears')])
finding('MOTION-AD-RESET-WRONGKEY',AD,['SW_RESET.SW_RESET_CODE'],'0x5AC有明确reset动作，但任意错key必须不复位的硬件oracle不由原文直接支持。',{'v2':'wrong key must not reset'},{'recognized_key':'0x5AC','wrong_key_oracle':'EXCLUDE as manufacturer fact; optionally separately labelled abstraction','completion':'250us max, no write during reset'},[loc(AD,50,'Table28','10110101100: Reset'),loc(AD,33,'RESET FUNCTION','takes 250 µs maximum')])
finding('MOTION-AD-COMMAND-FORMAT-SOURCE',AD,['ADC_SEQ.REP','SW_RESET.SW_RESET_CODE','address_encoding.reserved_command_data_bits'],'p.26通用bits10:9保留与逐寄存器REPbit9、SWkeybits10:0不兼容。',{'generic_format':'bits10:9 reserved for control writes'},{'interpretation':'per-register-specific command bits; retain generic-format discrepancy','official_erratum':False},[loc(AD,26,'Table10','Bits[10:9] are reserved'),loc(AD,37,'Table16','REP'),loc(AD,50,'Table28','10110101100: Reset')])
finding('MOTION-MPU-SOURCE-IDENTITY',MP,['source_manifest.MPU6050'],'产品规格Rev3.4与寄存器地图Rev4.2必须分别锁源，不能混用页码。',{'initial_source':'corpus/data/raw_pdf/InvenSense/MPU6050.pdf'},{'primary_source':src[MP],'supplementary_source':source_records[-1]},[loc(MP,1,'title page','Revision: 4.2')],'P2')
finding('MOTION-MPU-DLPF7-SOURCE',MP,['CONFIG.DLPF_CFG'],'§4.2 DLPF_CFG0 or7 disabled与§4.3表7 Reserved不同粒度；排除7可保守但不能说其毫无定义。',{'v2_legal_values':list(range(7))},{'legal_values':list(range(7)),'excluded_value7':'UNRESOLVED_SOURCE_AMBIGUITY'},bykey[MP,'CONFIG','DLPF_CFG']['dimensions']['legal_encoding']['locators'],'P2')
finding('MOTION-MPU-GYRO-ST-LAYOUT',MP,['GYRO_CONFIG.XG_ST','GYRO_CONFIG.YG_ST','GYRO_CONFIG.ZG_ST'],'总map high3bits“-”与detail named ST位的布局差异，应保留detail-first解读条件。',{'overview':'- - -','detail':'XG_ST YG_ST ZG_ST'},{'access':'RW detail-first provisional','source_conflict':'UNRESOLVED_LAYOUT_DISCREPANCY','no_official_erratum':True},bykey[MP,'GYRO_CONFIG','XG_ST']['dimensions']['access']['locators'],'P2')
finding('MOTION-MPU-ANY-READ-CLEAR',MP,['all mapped reads','INT_PIN_CFG.INT_RD_CLEAR','INT_STATUS'],'INT_RD_CLEAR1时任意read清interrupt；未映射中断block使当前测试无法覆盖。',{'v2':'no interrupt register mapping in IR'},{'scope_baseline':{'INT_RD_CLEAR':0},'dynamic_extension':['INT_PIN_CFG','INT_ENABLE','INT_STATUS'],'clear_rules':{'0':'INT_STATUS read only','1':'any read'}},[loc(MP,26,'§4.14','interrupt status bits are cleared on any read'),loc(MP,28,'§4.16','Each bit will clear')])
finding('MOTION-MPU-CLOCK-CYCLE',MP,['PWR_MGMT_1.CLKSEL','PWR_MGMT_1.CYCLE','PWR_MGMT_1.SLEEP'],'CLKSEL7合法但clockstop，cycle依SLEEP0及LP_WAKE_CTRL；静态RW不能证明mode更新。',{'legal_values':[0,1,2,3,4,5,7]},{'keep_legal7':True,'exclude_clockstop_function_without_clock_model':True,'CYCLE_requires_SLEEP':0,'dependency':'PWR_MGMT_2.LP_WAKE_CTRL'},[loc(MP,40,'§4.28','Stops the clock'),loc(MP,40,'§4.28','When CYCLE is set to 1 while SLEEP is disabled')],'P2')

gaps=[
 {'chip':AD,'registers':['CONFIG_READ_AND_LDAC','DAC_WR','ADC_RESULT','GPIO/power/reference registers'],'status':'CONDITIONAL','why':'IR inventories only22 fields, does not include native SPI readback enable completion, ADC data/clock sequence, GPIO, LDAC or reference mode dependencies.','candidate_rule':'Freeze current abstraction with explicit omissions; source-expanded adapter is separate generation/evaluation scope.','locators':[loc(AD,27,'READ MODE','Reading from a register first requires a write'),loc(AD,43,'Table21','REG_RD_EN automatically clears'),loc(AD,29,'ADC OPERATION','The ADC operates with one cycle latency')]},
 {'chip':LI,'registers':['CTRL_REG2','CTRL_REG3','CTRL_REG5','CTRL_REG6','REFERENCE','FIFO_CTRL_REG','FIFO_SRC_REG','INT1/2 source/configuration registers'],'status':'CONDITIONAL','why':'Output/FIFO/status interactions and interrupt clear are beyond34-field subset; native Rev2 source lacks explicit STATUS_REG flag-clearing map.','candidate_rule':'Output reset excluded; seven source-defined status defaults admitted only default boundary; no fabricated statusCoR; include FIFO/sample/read adapter before event assertions.','locators':[loc(LI,23,'§5.1.5','Each time data is read from the FIFO'),loc(LI,38,'CTRL_REG5','cleared by reading INT1_SRC'),loc(LI,42,'INT1_SRC','Reading at this address clears')]},
 {'chip':LD,'registers':['CTRL3','CTRL6','CTRL7','OUT_X/Y/Z','STATUS_DUP','ALL_INT_SRC','TAP/SIXD registers'],'status':'CONDITIONAL','why':'Single-shot trigger completion, global enable, latching, FIFO readouts, offset weighting/filter prerequisites unavailable in55-field subset.','candidate_rule':'Declare controlled fixtures or exclude event functionality; do not claim read-clear coverage from WAKE_UP_SRC.FF_IA alone.','locators':[loc(LD,38,'Table34','this bit is set to 0 automatically'),loc(LD,53,'§8.31','Reading this register'),loc(LD,55,'Table92','FDS bit in CTRL6 (25h) must be set to 0')]},
 {'chip':MP,'registers':['INT_PIN_CFG','INT_ENABLE','INT_STATUS','PWR_MGMT_2','USER_CTRL','SIGNAL_PATH_RESET','FIFO controls/count/data'],'status':'CONDITIONAL','why':'Any-read interrupt clear, sleep/cycle/clock effects and measurement snapshot/FIFO excluded from29-field subset.','candidate_rule':'Default interrupt fixture0 may support static subset; expanded event-aware generation must map dependencies. DEVICE_RESET atomic-complete is abstraction, not actual100ms validation.','locators':[loc(MP,26,'§4.14','interrupt status bits are cleared on any read'),loc(MP,29,'§4.17','whenever the serial interface is idle'),loc(MP,41,'§4.28','When using SPI interface')]},
]

patches=[
 {'chip':LD,'register':'OUT_T_L','field':'TEMP_3_0','attribute':'bits','old':'3:0','candidate':'7:4','finding_id':'MOTION-LIS2-TEMP-NIBBLE'},
 {'chip':LD,'register':'OUT_T_L','field':'ZERO_7_4','attribute':'bits','old':'7:4','candidate':'3:0','finding_id':'MOTION-LIS2-TEMP-NIBBLE'},
 {'chip':LD,'register':'OUT_T_L','field':'ZERO_7_4','attribute':'name','old':'ZERO_7_4','candidate':'ZERO_3_0','finding_id':'MOTION-LIS2-TEMP-NIBBLE'},
 {'chip':LD,'register':'CTRL2','field':'MUST_BE_ZERO','attribute':'access','old':'RO','candidate':'UNSPEC','finding_id':'MOTION-LIS2-MBZ-ACCESS'},
 {'chip':LD,'register':'WAKE_UP_SRC','field':'FF_IA','attribute':'desc','old':'自由落体事件标志，读清除','candidate':'Free-fall event status. Reading ALL_INT_SRC resets related interrupt function flags routed to INT pads; unqualified self read-clear is not specified in reviewed source.','finding_id':'MOTION-LIS2-WAKE-CLEAR'},
 {'chip':LI,'register':'CTRL_REG4','field':'ST','attribute':'access','old':'UNSPEC','candidate':'RW','finding_id':'MOTION-LIS3-ST-ACCESS'},
 {'chip':AD,'attribute':'address_encoding.reserved_command_data_bits','old':inputs[AD]['ir']['address_encoding']['reserved_command_data_bits'],'candidate':'Per-register command definitions prevail provisionally; Table10 generic bits10:9 statement conflicts with REP9 and SW_RESET key10:0. No official erratum verified.','finding_id':'MOTION-AD-COMMAND-FORMAT-SOURCE'},
]
candidate_policy={'status':'CANDIDATE_NOT_FROZEN_NOT_MERGED','applies_to_inventory_count':len(fields),'source_records':source_records,'field_dimensions':[{k:r[k] for k in ['chip','register','field','bits','overall_status','dimensions']} for r in fields],'default_rules':['Pure static register-state storage is explicitly an abstraction.','Read-only protection must not imply dynamic read stability.','CoR coverage requires controlled nonzero event and a source-defined clear operation, not read0/read0.','Known default and known access are independent.','EXCLUDE dimension means no assertion, not device unsupported or a passed test.','Preserve source-conflicting semantics unresolved.'],'prospective_freeze_requirements':['Accept/reject each finding before building corrected input IR under a fresh version.','Repair LIS2 OUT_T_L bits and names in a new candidate.','Freeze raw PDF hashes plus RM-vs-PS identities, printed-page locators, inputIR hashes and source_policy.','Carry seven LIS3 status defaults mask0xFE only; XDA and6 measurement defaults unknown.','Bound native SPI/readback, BDU/FIFO, any-read clear and action completion dependencies in prompt and evaluation contracts.','Keep prior model output/harness/scores as historical; new input semantics require new generation cohort.']}

def dump(name,obj):
    (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for rec in fields:
    applicable_statuses=[v['status'] for v in rec['dimensions'].values() if not (isinstance(v['candidate_rule'],dict) and v['candidate_rule'].get('not_applicable'))]
    if 'REPAIR' in applicable_statuses: rec['overall_status']='REPAIR'
    elif 'CONDITIONAL' in applicable_statuses: rec['overall_status']='CONDITIONAL'
# candidate_policy contains references to field dimensions but a copied overall string; synchronize after aggregation.
for pr,rec in zip(candidate_policy['field_dimensions'],fields): pr['overall_status']=rec['overall_status']
counts=Counter(r['overall_status'] for r in fields)
chip_counts={c:dict(Counter(r['overall_status'] for r in fields if r['chip']==c)) for c in CHIPS}
assert len(fields)==140, len(fields)
assert len(bykey)==len(fields)
assert set(bykey)=={(c,f['register'],f['field']) for c in CHIPS for f in inputs[c]['inventory']}
assert all(set(r['dimensions'])=={'reset','access','legal_encoding','read_clear','trigger_completion','conditional_write','reserved_policy'} for r in fields)
checked_quotes=0
for rec in fields:
    for di in rec['dimensions'].values():
        assert di['status'] in ['PASS','REPAIR','CONDITIONAL','EXCLUDE']
        assert di['evidence_class'] in ['MANUFACTURER_FACT','ABSTRACTION_ASSUMPTION','UNDEFINED_BEHAVIOR','SOURCE_CONFLICT']
        assert di['locators']
        for q in di['locators']:
            assert norm(q['excerpt']).lower() in norm(docs[rec['chip']][q['pdf_page']-1]).lower()
            checked_quotes+=1
quality={'inventory_fields':len(fields),'exact_inventory_keys_preserved':True,'dimensions_per_field':7,'dimension_records':len(fields)*7,'overall_counts':dict(counts),'per_chip_counts':chip_counts,'locator_excerpt_occurrences_verified_in_original_PDF_text':checked_quotes,'visually_reviewed_pages':['LIS2DW12 p.35 Table22','LIS3DH p.39 Tables46–47','MPU6050 RM p.6 overview'],'baseline_mutations':'none; build writes partition directory only','no_model_or_reference_execution':True,'no_hardware_or_external_API':True}
dump('fields.json',fields); dump('findings.json',findings); dump('register_gaps.json',gaps)
dump('sources.json',{'sources':source_records,'inputs_reviewed':audited_inputs,'read_scope':'full local source available; assigned register detail/default and dependency pages reviewed, not every analog spec claim certified','source_manifest_initial_match_repair':'MPU6050 source selected by device filename is supplementary PS; RM mirror used for source locators','visually_reviewed_pages':quality['visually_reviewed_pages']})
dump('candidate_ir_annotation_patch.json',patches); dump('candidate_policy.json',candidate_policy); dump('quality_checks.json',quality)
ir_patches=[]
for pa in patches:
    fid=pa['finding_id']; fd=next(f for f in findings if f['id']==fid)
    if fid=='MOTION-AD-COMMAND-FORMAT-SOURCE':
        # Retain only a conflict annotation, not a uniquely resolved command assignment.
        certainty='SOURCE_CONFLICT_PRESERVED_NO_UNIQUE_ASSIGNMENT'
    elif fid=='MOTION-LIS2-MBZ-ACCESS': certainty='ABSTRACTION_ASSUMPTION_FOR_UNDEFINED_ACCESS'
    else: certainty='MANUFACTURER_FACT'
    ir_patches.append({'chip':pa['chip'],'register':pa.get('register'),'field':pa.get('field'),'property':pa['attribute'],'old':pa['old'],'new':pa['candidate'],'certainty':certainty,'locators':fd['locators']})
for f in ['ZYXOR','ZOR','YOR','XOR','ZYXDA','ZDA','YDA']:
    # The numeric field.reset was already0; the missing fact was admission/knownness.
    ir_patches.append({'chip':LI,'register':'STATUS_REG','field':f,'property':'source_default_admission','old':{'field_reset':0,'known_reset':False,'register_reset':None},'new':{'field_reset':0,'known_reset':True,'scope':'default boundary before events','register_known_mask':'0xFE'},'certainty':'MANUFACTURER_FACT_WITH_DEFAULT_BOUNDARY','locators':[loc(LI,39,'Table47',f)],'note':'No field numeric reset change. Do not invent a whole-register numeric reset including XDA. Candidate generator must support masked/reset per-field source metadata.'})
ir_patches.append({'chip':LD,'register':'OUT_T_L','field':'TEMP_3_0','property':'desc','old':bykey[LD,'OUT_T_L','TEMP_3_0']['old']['desc'],'new':'Temperature bitsTEMP3:0 occupy bus bits7:4. OUT_T_H/OUT_T_L form left-justified12bit two\'s complement output; low4 bits read0.','certainty':'MANUFACTURER_FACT','locators':[loc(LD,35,'Table22','TEMP3'),loc(LD,18,'§3.6','left-justified in 12-bit mode')]})
dump('ir_patches.json',ir_patches)
conflict_ids=['MOTION-LIS2-FIFO-MODE-SOURCE','MOTION-AD-COMMAND-FORMAT-SOURCE','MOTION-MPU-DLPF7-SOURCE','MOTION-MPU-GYRO-ST-LAYOUT']
expert={'contract_version':'1.0','expert_skill':'sci-skills-paper-deep-reading','project_id':'d2d-twin','paper_family':'M','stage_id':'M4','task_id':'source_motion_io','task_status':'COMPLETE','inputs_reviewed':audited_inputs+[{'chip':r['chip'],'path':r['path'],'sha256':r['sha256'],'manual_version':r['manual_version']} for r in source_records],'outputs':['fields.json','findings.json','register_gaps.json','sources.json','candidate_ir_annotation_patch.json','ir_patches.json','candidate_policy.json','quality_checks.json','REVIEW.md'],'evidence_status':['VERIFIED_USER_MATERIAL: assigned inventory and seven named review inputs','VERIFIED_SOURCE: local manufacturer originalPDF pages with locator+SHA, limitations retained','EXECUTED_LOCAL: PDF extraction/hashes and schema/quote validation','AI_INFERENCE: bounded abstraction and conservative exclusions','NOT_EXECUTED: reference/model/hardware/new officialdownload or erratum verification'],'assumptions':['Direct-register storage subset is an explicitly labelled abstraction.','Source admission is bounded to assigned140 inventory fields, no unrestricted full-device signoff.','Source PDF mirror carries manufacturer document content; official-current download identity not checked.'],'author_input_needed':[],'manual_actions':[],'quality_checks':[quality],'conflicts':[{'conflict_id':i,'conflict_type':'SOURCE_INTERNAL_AMBIGUITY_OR_LAYOUT_DISCREPANCY','claim':next(f['problem'] for f in findings if f['id']==i),'source_or_locator':next(f['locators'] for f in findings if f['id']==i),'competing_values_or_interpretations':next(f['old'] for f in findings if f['id']==i),'recommended_resolution':'preserve both source statements; exclude ambiguous functional assertion or declare provisional interpretation; not an official erratum'} for i in conflict_ids],'conflict_resolution_status':'UNRESOLVED','merge_permission':'orchestrator_only','recommended_next_action':'主编排逐项接受候选修订和条件/排除规则，冻结新的来源与输入版本后才用于新一轮生成。','stage_acceptance_recommendation':'REPAIR'}
dump('expert_return.json',expert)
review=f'''# 四器件独立来源审校签审候选

日期：2026-10-12。任务：source_motion_io；SCI-Skills paper-deep-reading 有界 M4 REVIEW。此为独立 AI 审校意见，不是人类签字或硬件认证；不推进或改变阶段。

结论：**REPAIR**。已覆盖 AD5592R 22、LIS3DH 34、LIS2DW12 55、MPU6050 29，共 **140 字段、980 维度记录**。逐项记录见 fields.json；总体 {dict(counts)}。PASS仅表示所列来源事实与适用范围，无动作定义的维度仍明确 EXCLUDE，不能读为整芯片功能通过。

## 范围与输入

用户指定七份文档/JSON是待审对象，相关chip字段及全局认证表述已读；厂商证据只来自 corpus/data/raw_pdf 的五份本地PDF。sources.json保留器件、版本、SHA-256、来源角色。MPU6050字段以RM镜像Rev4.2为主；同名MPU6050.pdf是PS Rev3.4，仅补充产品规格，不互换物理/印刷页码。所有新输出仅本目录，未改d2d/ir、v2、冻结harness或历史模型记录。

## 关键差异

- **LIS2DW12 OUT_T_L位域颠倒**：p.35 Table22实际bits7:4为TEMP3:0、bits3:0为0，p.18明确12bit left-justified。已渲染目视确认，候选将TEMP_3_0改7:4、ZERO_7_4改3:0并重命名ZERO_3_0。
- **LIS3DH STATUS默认排除过宽**：p.39 Table47明确七位Default0（mask0xFE）；p.31的Output标签不覆盖这些事实。XDA在Table46有位名但Table47无描述行；仍不推补初值。六个OUT字段仍无数值默认。初值已知不等于运行时不变，也没有来源指定STATUS的各项清除条件。
- **动态清除边界**：LIS2 WAKE_UP_SRC §8.28未规定FF_IA自读清；p.53 §8.31明确读ALL_INT_SRC reset相关已routing到INT pads的function flags，轴标志具体映射不补推。MPU RM p.26/28明确INT_RD_CLEAR0只读INT_STATUS清、1任意read清；当前29字段未映射中断block，读已映射地址的跨寄存器副作用也尚未建模。
- **AD配置门控与SPI抽象**：IO_LOCK和idle/noADC/noReadback前置条件缺失；CONFIG_READ_AND_LDAC selector、REG_RD_EN、next SPI read及完成自清未映射。0x5AC复位动作有出处，但任意错误key无副作用不是本地原文保证。250µs期间不写为厂商事实，atomic completed reset为模型假设。
- **模式副作用**：LIS2 BOOT只重载trimming且不影响control，SOFT_RESET仅原文all control registers；BDU在双byte读完前禁止更新。MODE2单次完成依CTRL3 trigger与输出可用，typ.T_on不能当严格上界。FIFO FTH0时FIFO_FTH0；切换首样discard；offset功能依CTRL7 enable/weight和FDS0。

## 来源冲突与来源未定义

保留AD Table10通用bits10:9保留与REP9/SWkey10:0的不同表述；DAC_RD_EN正文11使能与两位组表0/1文字歧义继续只用00/11。保留LIS2 Table55的trigger deasserted/100终态FIFO与§5.3.4–5.3.5正文trigger event/continuous差异。保留MPU DLPF7在divider正文有disabled解释、filter表为Reserved的歧义；GYRO总表high3bits“-”与细表named ST布局差异仅detail-first条件解释。均无官方勘误核验，不能改称厂家勘误。

MUST_BE_ZERO的must0不是RO；普通Reserved的默认0也不是硬编码0。MPU WHO_AM_I bit0/7有hardcoded0独立证据，可保留该特例。LIS3 ST的旧UNSPEC是基准排除而不是厂商类型，候选可改合法0/1/2的RW并独立排除analog selftest。

## 证据与执行

原始PDF相关页实际抽取，三个关键图页实际渲染/目视。全部{checked_quotes}个字段维度locator摘录出现位置已在原PDF文本中验证；这验证引用存在，不自动证明每项推理。json字段身份和七维覆盖已经本地检查。未跑参考或模型、未用SCNet、未购硬件、无外部API、未搜厂商现时勘误。没有把参考通过或模型高分用作来源证据。

## 交付与冻结建议

fields.json逐inventory键保留原identity、原bits、旧值和候选dimensions；findings.json为差异清单；candidate_ir_annotation_patch.json为可审的输入属性候选，candidate_policy.json为可冻结策略建议；register_gaps.json防止把子集称全器件coverage。不得直接merge或重写历史结果。先选择候选修订、条件范围和排除项，再用新编号冻结PDF/IR/policy/完整prompt与模型版本；新一轮生成单独队列。当前来源冲突继续UNRESOLVED，原模型代码是旧输入产生，不据此推断修正输入后的能力。

唯一下一步：主编排逐项接受候选修订和条件/排除规则，冻结新的来源与输入版本后才用于新一轮生成。
'''
(OUT/'REVIEW.md').write_text(review,encoding='utf-8')
print(json.dumps(quality,ensure_ascii=False,indent=2))
