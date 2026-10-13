"""Encode the primary reviewer's manually inspected register contracts, not model output."""
from pathlib import Path
import json, copy
OUT=Path(__file__).resolve().parents[2]
DEST=Path(__file__).resolve().parent
SOURCE=json.loads((OUT/'source_manifest.json').read_text(encoding='utf-8'))
CHIPS=['BME280','BMP280','TMP100','TMP102','TMP1075','TMP126']
VERSIONS={'BME280':'BST-BME280-DS001-24, cover revision 1.24 February 2024; body footer DS001-23 Revision_1.23_012022 (retained mismatch)', 'BMP280':'BST-BMP280-DS001-26 revision 1.26 October 2021','TMP100':'SBOS231I revised November 2015','TMP102':'SBOS397I revised June 2024','TMP1075':'SBOS854F revised June 2024; non-N orderables only','TMP126':'SNIS209C revised June 2022'}
ROWS=[]; FINDINGS=[]; PATCHES=[]

def write(name,data):
    (DEST/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def loc(p,table,excerpt=''):
    return {'pdf_page':p,'printed_page':str(p),'table':table,'excerpt':excerpt}

def dim(status,fact,rule,locators,cls='MANUFACTURER_FACT',applicable=True,**kw):
    return dict(status=status,fact=fact,candidate_rule=rule,evidence_class=cls,locators=locators,applicable=applicable,**kw)

def setdim(row,key,status,fact,rule,ls,cls='MANUFACTURER_FACT',**kw):
    row['dimensions'][key]=dim(status,fact,rule,ls,cls,**kw)

def finding(id,chip,targets,problem,old,rule,ls,severity='major',**kw):
    FINDINGS.append(dict(id=id,chip=chip,targets=targets,problem=problem,old=old,candidate_rule=rule,locators=ls,severity=severity,**kw))

def patch(chip,r,f,prop,old,new,ls,certainty='MANUFACTURER_FACT'):
    PATCHES.append(dict(chip=chip,register=r,field=f,property=prop,old=old,new=new,certainty=certainty,locators=ls))

REGS={
'BME280':{'id':(27,'Table 18 / §5.4.1',0x60),'reset':(27,'Table 18 / §5.4.2',0),'ctrl_hum':(28,'Tables 19–20 / Table 18 p.27',0),'status':(28,'Table 21 / Table 18 p.27',0),'ctrl_meas':(29,'Tables 22–25 / Table 18 p.27',0),'config':(30,'Tables 26–28 / Table 18 p.27',0),'press_msb':(31,'Table 29 / Table 18 p.27',0x80),'press_lsb':(31,'Table 29 / Table 18 p.27',0),'press_xlsb':(31,'Table 29 / Table 18 p.27',0),'temp_msb':(31,'Table 30 / Table 18 p.27',0x80),'temp_lsb':(31,'Table 30 / Table 18 p.27',0),'temp_xlsb':(31,'Table 30 / Table 18 p.27',0),'hum_msb':(31,'Table 31 / Table 18 p.27',0x80),'hum_lsb':(31,'Table 31 / Table 18 p.27',0)},
'BMP280':{'id':(24,'Table 18 / §4.3.1',0x58),'reset':(24,'Table 18 / §4.3.2',0),'status':(25,'Table 19 / Table 18 p.24',0),'ctrl_meas':(25,'Tables 20–22 pp.25–26 / Table 18 p.24',0),'config':(26,'Table 23 / Table 18 p.24',0),'press_msb':(26,'Table 24 / Table 18 p.24',0x80),'press_lsb':(26,'Table 24 / Table 18 p.24',0),'press_xlsb':(26,'Table 24 / Table 18 p.24',0),'temp_msb':(27,'Table 25 / Table 18 p.24',0x80),'temp_lsb':(27,'Table 25 / Table 18 p.24',0),'temp_xlsb':(27,'Table 25 / Table 18 p.24',0)},
'TMP100':{'TEMP':(16,'Tables 6–7 / §7.3.1 p.9',0),'CONFIG':(16,'Table 8 / §§7.4.2,7.5.3 / Tables 9–10 p.17',0x80),'TLOW':(18,'Tables 13–14 / §7.5.4 / Table 1 p.9',0x4b00),'THIGH':(18,'Tables 11–12 / §7.5.4 / Table 1 p.9',0x5000)},
'TMP102':{'TEMP':(17,'Tables 6-8–6-9 / §6.3.1 p.8',0),'CONFIG':(17,'Tables 6-10–6-11 / §§6.5.3.1–6.5.3.9 pp.17–19',0x60a0),'TLOW':(19,'Tables 6-15–6-16 pp.19–20 / §6.5.4',0x4b00),'THIGH':(19,'Tables 6-13–6-14 / §6.5.4',0x5000)},
'TMP1075':{'TEMP':(21,'Table 7-7 / Figure 7-11',0),'CFGR':(22,'Table 7-8 / Figures 7-12–7-13',0x00ff),'LLIM':(23,'Table 7-9 / Figure 7-14',0x4b00),'HLIM':(23,'Table 7-10 / Figure 7-15',0x5000),'DIEID':(24,'Table 7-11 / Figure 7-16 / Table 7-5 p.21',0x7500)},
'TMP126':{'TEMP_RESULT':(26,'Table 8-5 / Figure 8-19',0),'SLEW_RESULT':(26,'Table 8-6 / Figure 8-20',0),'ALERT_STATUS':(27,'Table 8-7 pp.27–28 / Figure 8-21',0),'CONFIG':(29,'Table 8-8 / Figure 8-22',6),'ALERT_ENABLE':(30,'Table 8-9 / Figure 8-23',0x16),'TLOW_LIMIT':(31,'Table 8-10 / Figure 8-24',0xf380),'THIGH_LIMIT':(31,'Table 8-11 / Figure 8-25',0x2a80),'HYSTERESIS':(32,'Table 8-12 / Figure 8-26',0x0a0a),'SLEW_LIMIT':(33,'Table 8-13 / Figure 8-27',0x0500)}
}

for chip in CHIPS:
    inp=json.loads((OUT/'review_inputs'/f'{chip}.json').read_text(encoding='utf-8'))
    for reg in inp['ir']['registers']:
        rn=reg['name']; p,t,rr=REGS[chip][rn]
        ls=[loc(p,t)]
        resetls=ls
        if chip in ['BME280','BMP280']:
            resetls=[loc(27 if chip=='BME280' else 24,'Table 18','Reset')]
            ls=resetls+[loc(p,t)]
        for f in reg.get('fields',[]):
            fn=f['name']; q=rn+'.'+fn; hi,*tail=map(int,f['bits'].split(':')); lo=tail[-1] if tail else hi
            mask=((1<<(hi-lo+1))-1)<<lo; exp=(rr&mask)>>lo; width=hi-lo+1
            record={'chip':chip,'register':rn,'field':fn,'bits':f['bits'],'source_path':SOURCE[chip]['path'],'source_sha256':SOURCE[chip]['sha256'],'manual_version':VERSIONS[chip],'reviewer':'source_root','ir_reset':f.get('reset'),'ir_access':f.get('access'),'dimensions':{}}
            ds=record['dimensions']
            ds['reset']=dim('PASS' if exp==f.get('reset') else 'REPAIR',f'原页复位读回寄存器=0x{rr:X}；本字段位位置{f["bits"]}，提取值={exp}。',{'expected':exp,'mask':hex(mask),'epoch':'completed_reset_before_first_conversion_completed'},resetls)
            ds['access']=dim('PASS',f'来源寄存器/字段访问为 {f["access"]}；只表示接口权限，不保证动态读值恒定。',{'access':f['access'],'continuous_snapshot_equality':False if f['access']=='RO' else None},ls)
            ds['legal_encoding']=dim('PASS',f'本字段是{width}位配置/数据表示；以下为寄存器抽象的位域输入范围，不声称全部模拟工况均有效。',{'range':[0,(1<<width)-1],'coverage':'storage_bits_only'},ls,'ABSTRACTION_ASSUMPTION') if f['access'] in ['RW','W'] else dim('EXCLUDE','只读字段没有软件写输入合法域；输出编码依字段格式。',{'assertion':'no_write_domain'},ls,'UNDEFINED_BEHAVIOR',False)
            ds['read_clear']=dim('EXCLUDE','所引寄存器契约未为本字段定义读清动作；本次不另设读清 oracle。',{'assertion':'none_claimed'},ls,'UNDEFINED_BEHAVIOR',False)
            ds['trigger_completion']=dim('EXCLUDE','本字段未被所引寄存器定义为独立写触发器；没有完成时序断言。',{'assertion':'none_claimed'},ls,'UNDEFINED_BEHAVIOR',False)
            ds['conditional_write']=dim('PASS','在所列合法配置基线内审查直接存储权限；其他模式、总线和物理功能不能由读回等同验证。',{'baseline':'fresh legal configuration','scope':'direct_register_contract'},ls,'ABSTRACTION_ASSUMPTION') if f['access']=='RW' else dim('EXCLUDE','本字段没有普通软件存储写。',{'assertion':'not_applicable'},ls,'UNDEFINED_BEHAVIOR',False)
            ds['reserved_policy']=dim('PASS','本字段为明确命名功能位，不把动态值或来源缺省强制解释为保留零。',{'reserved':False},ls,applicable=False)

            if chip in ['BME280','BMP280']:
                mp=27 if chip=='BME280' else 24
                if fn.startswith('UNUSED') and rn not in ['press_xlsb','temp_xlsb']:
                    setdim(record,'access','EXCLUDE','Table 18 灰色区域为 do not change / do not write；未给出普通RW/RO存储保证。',{'exclude_access_oracles':True},[loc(mp,'Table 18')],'UNDEFINED_BEHAVIOR')
                    setdim(record,'legal_encoding','EXCLUDE','灰色保留位必须保持复位/基线；非法位模式后行为未定义。',{'fixed_write':0,'do_not_infer_illegal_write_result':True},[loc(mp,'Table 18')],'UNDEFINED_BEHAVIOR')
                    setdim(record,'conditional_write','EXCLUDE','灰位没有可评分的翻转刺激。',{'fixed_write':0},[loc(mp,'Table 18')],'UNDEFINED_BEHAVIOR')
                    setdim(record,'reserved_policy','EXCLUDE','保留位reset=0与运行中恒零不是同一事实。',{'known_reset':True,'fixed_write':0,'exclude_runtime_oracle':True},[loc(mp,'Table 18')],'UNDEFINED_BEHAVIOR')
                elif fn=='UNUSED':
                    setdim(record,'access','PASS','Table18 黄色RO区域明确列低四位0。',{'access':'RO','read_value':0},[loc(mp,'Table 18')])
                    setdim(record,'reserved_policy','PASS','数据低四位在位图逐位标0，不是灰色保留。',{'known_reset':True,'fixed_read':0},[loc(mp,'Table 18')])
                if rn=='reset':
                    lsx=[loc(mp,'§5.4.2' if chip=='BME280' else '§4.3.2','Writing other values than 0xB6 has no effect.')]
                    setdim(record,'legal_encoding','PASS','0xB6触发完整POR；其余值明确无效；读值始终0。',{'write_key':0xb6,'other_writes':'no_effect','read_as':0},lsx)
                    setdim(record,'trigger_completion','CONDITIONAL','写0xB6走完整POR过程，不能用瞬时原子复位宣称实物时序。',{'completion':'POR finished and NVM im_update=0','abstraction':'atomic completed reset only'},lsx,'ABSTRACTION_ASSUMPTION')
                if rn=='status' and fn in ['measuring','im_update']:
                    sx=[loc(p,'Table 21' if chip=='BME280' else 'Table 19','Automatically set')]
                    setdim(record,'access','CONDITIONAL','状态RO但由转换/NVM操作置清；不能作永久快照保持断言。',{'access':'RO','dynamic':True,'exclude_snapshot_equality':True},sx)
                    setdim(record,'trigger_completion','CONDITIONAL','measuring在结果转入数据寄存器后清；im_update在拷贝完成后清，POR和每次转换均可置1。',{'event_model_required':True,'completion':'result_transfer / NVM_copy_complete'},sx)
                if rn=='ctrl_meas':
                    setdim(record,'conditional_write','CONDITIONAL','测量中模式切换延迟到当前测量结束；等待切换完成前进一步模式命令可忽略。',{'baseline':'sleep and no pending transition','no_unconditional_mode_write_persistence':True},[loc(15 if chip=='BME280' else 17,'§3.3.1 / Figure3' if chip=='BME280' else '§3.6.4 / Figure5')])
                    if fn in ['osrs_t','osrs_p']:
                        setdim(record,'legal_encoding','PASS','000 skipped；001/010/011/100为1/2/4/8倍；101/110/111为16倍。',{'legal_values':list(range(8))},[loc(29 if chip=='BME280' else (25 if fn=='osrs_p' else 26),'Table23/24' if chip=='BME280' else ('Table21' if fn=='osrs_p' else 'Table22'))])
                    if fn=='mode':
                        setdim(record,'legal_encoding','REPAIR' if chip=='BMP280' else 'PASS','00 sleep；01和10均forced；11 normal。BMP280旧说明10/11 normal不符原页。',{'legal_values':[0,1,2,3],'mode_names':['sleep','forced','forced','normal']},[loc(29 if chip=='BME280' else 15,'Table25' if chip=='BME280' else 'Table10')])
                        setdim(record,'trigger_completion','CONDITIONAL','forced在单次测量完成并保存结果后回到sleep。',{'static_test_values':[0,3],'forced_codes':[1,2],'completion_mode':0,'event_model_required':True},[loc(15,'§3.3.3' if chip=='BME280' else '§3.6.2')])
                        if chip=='BMP280': patch(chip,rn,fn,'desc',f.get('desc'),'00 sleep, 01/10 forced, 11 normal; forced returns to sleep after measurement; Table10 p.15',ds['legal_encoding']['locators'])
                if rn=='ctrl_hum' and fn=='osrs_h':
                    setdim(record,'legal_encoding','PASS','000 skipped，101及others均16倍。',{'legal_values':list(range(8))},[loc(28,'Table20')])
                    setdim(record,'conditional_write','CONDITIONAL','ctrl_hum改变仅在后续写ctrl_meas后生效；模式切换待执行时ctrl_hum写可能被忽略。',{'sequence':['wait sleep/no transition','write ctrl_hum','write ctrl_meas'],'storage_and_effect_separate':True},[loc(27,'§5.4.3','Changes to this register only become effective after a write operation to “ctrl_meas”.'),loc(15,'§3.3.1')])
                if rn=='config' and fn!='UNUSED':
                    setdim(record,'conditional_write','CONDITIONAL','normal下config写可能忽略；sleep下不忽略。',{'preconditions':{'ctrl_meas.mode':0},'wait_for_pending_measurement':True},[loc(p,'§5.4.6' if chip=='BME280' else '§4.3.5','In sleep mode writes are not ignored.')])
                    if fn=='t_sb': setdim(record,'legal_encoding','PASS','所有8种待机时长有定义；BME编码6/7=10/20ms，BMP=2000/4000ms。',{'legal_values':list(range(8))},[loc(30 if chip=='BME280' else 17,'Table27' if chip=='BME280' else 'Table11')])
                    if fn=='filter':
                        if chip=='BME280': setdim(record,'legal_encoding','PASS','Table28明确100及others均系数16。',{'legal_values':list(range(8))},[loc(30,'Table28','100, others')])
                        else: setdim(record,'legal_encoding','CONDITIONAL','BMP原页Table6列off/2/4/8/16但未逐行给出位编码；不能将BME的others自动移植成BMP官方编码保证。',{'exclude_functional_oracle_for_codes':[5,6,7],'storage_encoding':'not independently specified for aliases','candidate_defined_coefficients':['off',2,4,8,16]},[loc(14,'Table6'),loc(26,'Table23')],'ABSTRACTION_ASSUMPTION')
                        setdim(record,'trigger_completion','CONDITIONAL','写filter会重置滤波历史，下个值建立初始历史；skipped测量保留历史。',{'side_effect':'reset_filter_memory','exclude_sensor_function_from_storage_score':True},[loc(18 if chip=='BME280' else 14,'§3.4.4' if chip=='BME280' else '§3.3.3','When writing to the register filter, the filter is reset.')])
                if rn.startswith(('press_','temp_','hum_')) and fn!='UNUSED':
                    setdim(record,'access','CONDITIONAL','数据RO但随转换更新；跨字节一致性依单次burst，不保证独立读取快照恒定。',{'access':'RO','dynamic':True,'freeze_events_for_storage_protection':True,'exclude_analog_value_oracle':True},ls+[loc(23 if chip=='BME280' else 20,'§4.1–4.2' if chip=='BME280' else '§3.9–3.10')])

            if chip=='TMP100':
                if rn=='TEMP':
                    setdim(record,'access','CONDITIONAL','TEMP为12位RO格式；ADC分辨率9/10/11时未用LSB置0；旧15:7划分只适用于R1:R0=00。',{'access':'RO','preconditions':{'CONFIG.R1':0,'CONFIG.R0':0},'exclude_snapshot_equality':True},[loc(9,'§7.3.1'),loc(16,'Tables6–7')])
                    setdim(record,'conditional_write','CONDITIONAL','改变CONFIG.R1/R0改变TEMP有效位；低七位不能在全部分辨率下恒0。',{'format_by_resolution':{'00':'15:7','01':'15:6','10':'15:5','11':'15:4'},'always_zero':'3:0'},[loc(9,'§7.3.1'),loc(17,'Table10')])
                    if fn=='UNUSED': setdim(record,'reserved_policy','REPAIR','TEMP bits6:4是高分辨率的转换数据，不是全模式保留。',{'always_zero_bits':'3:0','mode_dependent_bits':'6:4'},[loc(9,'§7.3.1'),loc(16,'Table7')])
                if rn=='CONFIG':
                    if fn=='OS':
                        setdim(record,'access','REPAIR','写1在shutdown触发；读是比较器状态且POL反相，TM不影响，不能read_as=1无条件。',{'write_action':'one_shot_if_SD1','read_source':'comparator_hysteresis_state XOR polarity','remove_global_read_as':True},[loc(18,'§7.5.3.6','The state of the POL bit inverts the polarity of data returned from the OS/ALERT bit.')])
                        setdim(record,'trigger_completion','CONDITIONAL','SD=1写OS=1开始一次转换，结束后回shutdown。',{'preconditions':{'CONFIG.SD':1},'completion':'conversion_complete','read_is_not_busy_flag':True},[loc(14,'§7.4.2')])
                        setdim(record,'legal_encoding','PASS','OS写0/1有定义；读不是写值镜像。',{'legal_values':[0,1],'static_readback_requires':['POL0','no_threshold_fault']},[loc(18,'§7.5.3.6')])
                    elif fn in ['R1','R0','F1','F0']:
                        setdim(record,'legal_encoding','PASS','R成对00/01/10/11=9/10/11/12位；F成对=1/2/4/6次故障。',{'legal_values':[0,1],'paired_field':'R1:R0' if fn.startswith('R') else 'F1:F0'},[loc(17,'Table10' if fn.startswith('R') else 'Table9')])
                    elif fn=='SD': setdim(record,'trigger_completion','CONDITIONAL','SD=1的关断在当前转换完成后实施。',{'completion':'current_conversion_completed'},[loc(16,'§7.5.3.1')])
                    elif fn=='POL': setdim(record,'conditional_write','CONDITIONAL','POL更改也会反转OS/ALERT读状态。',{'side_effect_fields':['CONFIG.OS'],'no_full_CONFIG_snapshot_equality':True},[loc(18,'§7.5.3.6')])
                    elif fn=='TM': setdim(record,'trigger_completion','EXCLUDE','ALERT引脚TM功能描述限TMP101，TMP100没有ALERT引脚；寄存器位存储与实际引脚语义区分。',{'scope':'TMP100 storage only; no TMP101 ALERT assertion'},[loc(14,'§7.4.3')])
                if rn in ['TLOW','THIGH'] and fn=='UNUSED': setdim(record,'reserved_policy','PASS','门限格式低四位逐位0；所有ADC分辨率仍保留12位门限。',{'known_reset':True,'fixed_read':0},[loc(18,'Tables11–14')])

            if chip=='TMP102':
                if rn in ['TEMP','TLOW','THIGH']:
                    setdim(record,'access','CONDITIONAL','EM=0为12位，EM=1为13位；TEMP bit0是EM格式标志而门限bit0仍为0。',{'preconditions':{'CONFIG.EM':0},'extended_format':'15:3','TEMP_bit0':'EM','limit_bits2_0':0,'exclude_uncontrolled_snapshots':rn=='TEMP'},[loc(15,'§6.4.2'),loc(17,'Tables6-8–6-9'),loc(19,'Tables6-13–6-15'),loc(20,'Table6-16')])
                    if fn=='UNUSED':
                        setdim(record,'reserved_policy','REPAIR','bits3:0仅在EM=0全0；EM=1 bit3是数据，TEMP bit0=1；门限bit0仍0，旧“bit0有意义”不宜外推。',{'baseline_EM':0,'always_zero_TEMP':'2:1','always_zero_limits':'2:0','mode_data_bit':3},[loc(17,'Table6-9'),loc(19,'Table6-14'),loc(20,'Table6-16')])
                if rn=='CONFIG':
                    if fn=='OS':
                        setdim(record,'access','REPAIR','OS写触发而读转换状态；转换中0，单次完成后1，不是普通RW持久。',{'exclude_persistence':True,'read_during_conversion':0,'read_completed_one_shot':1},[loc(15,'§6.4.4')])
                        setdim(record,'trigger_completion','CONDITIONAL','仅SD=1时OS=1启动单次；当前时刻的状态取决于完成事件。',{'preconditions':{'CONFIG.SD':1},'completion':'one_shot_conversion_complete','requires_event_model':True},[loc(15,'§6.4.4'),loc(18,'§6.5.3.6')])
                    elif fn=='AL':
                        setdim(record,'access','REPAIR','AL是RO比较器状态并受POL反转，不是恒1。',{'access':'RO','dynamic':True,'exclude_snapshot_equality':True,'read_source':'comparator hysteresis and POL'},[loc(19,'§6.5.3.8')])
                        setdim(record,'read_clear','CONDITIONAL','TM=1读任一寄存器清的是ALERT引脚/中断状态；AL位仍是比较器状态，TM不影响AL读值。',{'do_not_clear_AL_as_interrupt_flag':True,'pin_clear_events':['any_register_read','SMBus_ARA','shutdown','general_call_reset']},[loc(19,'§6.5.3.8 / §6.5.4')])
                    elif fn in ['R1','R0']: setdim(record,'access','PASS','R1/R0为明确只读11。',{'access':'RO','fixed_read':1},[loc(18,'§6.5.3.5')])
                    elif fn in ['F1','F0']: setdim(record,'legal_encoding','PASS','F1:F0四种编码=1/2/4/6故障。',{'legal_values':[0,1]},[loc(18,'Table6-12')])
                    elif fn in ['CR1','CR0']: setdim(record,'legal_encoding','PASS','CR1:CR0=00/01/10/11对应0.25/1/4/8Hz。',{'legal_values':[0,1]},[loc(15,'Table6-5')])
                    elif fn=='POL': setdim(record,'conditional_write','CONDITIONAL','POL翻转AL读状态和ALERT引脚极性。',{'side_effect_fields':['CONFIG.AL']},[loc(19,'§6.5.3.8')])
                    elif fn=='SD': setdim(record,'trigger_completion','CONDITIONAL','SD置1需当前转换完成后关断；同时TM1下可清ALERT引脚。',{'completion':'current conversion completed','pin_side_effect':'interrupt alert clear'},[loc(15,'§6.4.3'),loc(19,'§6.5.4')])
                    elif fn=='EM': setdim(record,'conditional_write','REPAIR','EM改变三个温度寄存器格式，候选旧固定12位harness没有此格式模型。',{'storage_test_values':[0],'functional_values':[0,1],'exclude_EM1_without_format_model':True},[loc(15,'§6.4.2'),loc(17,'Table6-9')])
                    elif fn=='UNUSED':
                        setdim(record,'access','EXCLUDE','Table6-11标低四位格式0但没有单独的access代码；不把IR的RO推作厂商权限事实。',{'exclude_access_oracles':True,'known_reset':True},[loc(17,'Table6-11')],'UNDEFINED_BEHAVIOR')
                        setdim(record,'reserved_policy','PASS','CONFIG低四位在复位/格式表明确0；本次只保留已知reset和合法基线0，不从图0推广非零写入响应。',{'known_reset':True,'fixed_write':0,'exclude_flip_oracle':True},[loc(17,'Table6-11')])

            if chip=='TMP1075':
                if rn=='TEMP':
                    if fn=='T': setdim(record,'access','CONDITIONAL','TEMP为12位最近转换结果，首次完成前0，不是运行中恒定。',{'access':'RO','dynamic':True,'freeze_events_for_protection':True},[loc(21,'Table7-7 / §7.5.1.1')])
                    else: setdim(record,'reserved_policy','PASS','正文明确first12bit温度，所有其他位0。',{'fixed_read':0,'known_reset':True},[loc(21,'§7.5.1.1','with all remaining bits equal to zero.')])
                if rn=='CFGR':
                    if fn=='OS':
                        setdim(record,'access','PASS','非N型OS写触发，读恒0；N型完成读1不纳入。',{'access':'RW_action','read_as':0,'variant':'non-N'},[loc(19,'§7.4.2'),loc(22,'Table7-8')])
                        setdim(record,'trigger_completion','CONDITIONAL','仅shutdown下启动；完成回shutdown，读0本身不能证明转换已完成。',{'preconditions':{'CFGR.SD':1},'completion':'conversion_complete','do_not_use_read0_as_completion':True},[loc(19,'§7.4.2')])
                        setdim(record,'conditional_write','REPAIR','当前read_as检查在reset SD0基线写OS，未满足功能触发条件。',{'preconditions':{'CFGR.SD':1}},[loc(19,'§7.4.2')])
                    elif fn=='R': setdim(record,'legal_encoding','PASS','非N型四种转换周期27.5/55/110/220ms。',{'legal_values':[0,1,2,3],'variant':'non-N'},[loc(22,'Table7-8')])
                    elif fn=='F': setdim(record,'legal_encoding','PASS','非N四编码1/2/3/4次；N型1/2/4/6次。',{'legal_values':[0,1,2,3],'variant':'non-N'},[loc(22,'Table7-8')])
                    elif fn=='TM': setdim(record,'trigger_completion','CONDITIONAL','写TM清故障计数、alert历史并使引脚inactive；仅非N。',{'side_effect':'clear_fault_counter_and_alert_history','variant':'non-N'},[loc(20,'§7.4.4','Any write to the TM bit')])
                    elif fn=='SD': setdim(record,'trigger_completion','CONDITIONAL','shutdown命令清interrupt pin与历史，单次需SD1。',{'side_effect':'clear_interrupt_alert_history'},[loc(20,'§7.4.4.2')])
                if (rn=='CFGR' and fn=='UNUSED_LOW') or (rn in ['LLIM','HLIM'] and fn=='UNUSED'):
                    setdim(record,'access','CONDITIONAL','TYPE明确R/W，描述Not used；不把R/W抹成RO，也不能由此认证功能。',{'access_label':'RW','pure_storage_is_protocol_assumption':True},ls)
                    setdim(record,'legal_encoding','EXCLUDE','Not used位无功能编码说明。',{'fixed_write':exp,'exclude_nondefault_functional_oracle':True},ls,'UNDEFINED_BEHAVIOR')
                    setdim(record,'reserved_policy','REPAIR','保留默认，不把unused字段边界翻转通过当厂商存储事实。',{'fixed_write':exp,'known_reset':True,'exclude_persistence':True},ls,'ABSTRACTION_ASSUMPTION')
                if rn=='DIEID':
                    setdim(record,'access','CONDITIONAL','总表/正文/位图为RO，Table7-11 TYPE列R/W，属于来源冲突，不能称官方勘误。',{'main_policy':'exclude disputed write-access oracle','optional_hypothesis':'prose_and_diagram_priority_RO','variant':'non-N'},[loc(21,'Table7-5'),loc(24,'Figure7-16 / Table7-11')],'SOURCE_CONFLICT')

            if chip=='TMP126':
                if fn.startswith('RESERVED'):
                    guaranteed=(rn=='TEMP_RESULT' or rn in ['TLOW_LIMIT','THIGH_LIMIT']) and fn=='RESERVED_1_0'
                    setdim(record,'reserved_policy','PASS' if guaranteed else 'CONDITIONAL','明确always read00b。' if guaranteed else 'Type R、reset0明确，但不能只凭R-n的default标注把全部运行行为叫硬连恒0。',{'access':'RO','known_reset':True,'fixed_read':0 if guaranteed else None,'baseline_write':0,'scope':'explicit constant' if guaranteed else 'quiescent abstract read protection'},ls,'MANUFACTURER_FACT' if guaranteed else 'ABSTRACTION_ASSUMPTION')
                if rn in ['TEMP_RESULT','SLEW_RESULT'] and not fn.startswith('RESERVED'):
                    setdim(record,'access','CONDITIONAL','转换/连续测量更新动态RO结果；slew需连续模式两次转换且负斜率数值不能保证。',{'access':'RO','dynamic':True,'exclude_snapshot_equality':True,'exclude_negative_slew_numeric_oracle':rn=='SLEW_RESULT'},[loc(26,'Table8-5 / Table8-6 / §8.6.2')])
                    if rn=='TEMP_RESULT': setdim(record,'read_clear','REPAIR','读TEMP_RESULT也清ALERT_STATUS.DATA_READY_FLAG，不能只按同寄存器read-clear。',{'cross_register_clear':{'ALERT_STATUS':'0x01'}},[loc(28,'Table8-7 Data_Ready_Flag','Reading Alert_Status register or the Temperature Results register will clear this bit.')])
                if rn=='ALERT_STATUS' and not fn.startswith('RESERVED'):
                    setdim(record,'access','CONDITIONAL','R/RC字段由转换或CRC事件更新；状态与锁存flag不同。',{'access':'RC' if fn in ['CRC_FLAG','SLEW_FLAG','THIGH_FLAG','TLOW_FLAG','DATA_READY_FLAG'] else 'RO','dynamic':True,'exclude_snapshot_equality':True},ls)
                    if fn in ['CRC_FLAG','SLEW_FLAG','THIGH_FLAG','TLOW_FLAG','DATA_READY_FLAG']:
                        setdim(record,'read_clear','REPAIR','Alert_Status仅single register read且无auto increment时清除；DR另由TEMP_RESULT读取清除。',{'preconditions':{'transaction':'single_register_read','auto_increment':False},'cross_read':'TEMP_RESULT' if fn=='DATA_READY_FLAG' else None,'requires_nonzero_event_before_read':True},[loc(27,'§8.6.3','This register will currently only clear with a single register read without auto increment.'),loc(28 if fn in ['THIGH_FLAG','TLOW_FLAG','DATA_READY_FLAG'] else 27,'Table8-7')])
                    elif fn in ['THIGH_STATUS','TLOW_STATUS','SLEW_POS_STATUS']: setdim(record,'read_clear','PASS','状态位不是RC；阈值/迟滞转换条件驱动置清。',{'not_read_clear':True,'physical_conversion_required':True},[loc(27,'Table8-7'),loc(16,'§8.4.4.1')])
                if rn=='CONFIG':
                    if fn=='RESETS':
                        setdim(record,'access','PASS','R/W动作位读恒0，写1触发0.5ms软复位。',{'access':'RW_action','read_as':0},[loc(29,'Table8-8')])
                        setdim(record,'trigger_completion','CONDITIONAL','写数据第16个上升沿开始reset，需新的CS下降沿恢复SPI。',{'abstraction':'completed reset atomic only','physical_duration_ms':0.5,'bus_resume':'new CS falling edge'},[loc(29,'Table8-8'),loc(18,'§8.5.2')])
                    elif fn=='ONE_SHOT':
                        setdim(record,'access','PASS','写1立即开始转换并丢弃未完结果；读恒0。',{'access':'RW_action','read_as':0},[loc(29,'Table8-8'),loc(15,'§8.4.3')])
                        setdim(record,'trigger_completion','REPAIR','完成后MODE自动置1，DR置1，重复触发会重启转换；读0不能证明完成。',{'completion_event':'conversion_complete','completed_changes':{'CONFIG.MODE':1,'ALERT_STATUS.DATA_READY_FLAG':1,'CONFIG.ONE_SHOT':0},'repeat_trigger':'restart and discard partial'},[loc(15,'§8.4.3')])
                    elif fn=='MODE': setdim(record,'trigger_completion','CONDITIONAL','MODE1立即关断、终止当前转换；不清已有alert；SLEW_RESULT回default。',{'shutdown':'immediate abort partial conversion','clear_alerts':False,'side_effect_registers':['SLEW_RESULT']},[loc(14,'§8.4.2'),loc(26,'§8.6.2')])
                    elif fn=='INT_COMP': setdim(record,'trigger_completion','REPAIR','从Comparator切回Interrupt立即清Alert_Status并reset ALERT pin。',{'transition':{'from':1,'to':0},'clear_register':'ALERT_STATUS'},[loc(16,'§8.4.4.1')])
                    elif fn=='AVG': setdim(record,'trigger_completion','CONDITIONAL','AVG1对每次测量包含one-shot做8次平均；完成条件不能当单次raw conversion。',{'completed_sample':'eight_conversion_average_when_AVG1'},[loc(29,'Table8-8')])
                    elif fn=='CONV_PERIOD': setdim(record,'legal_encoding','PASS','8个编码全部定义，111=2s。',{'legal_values':list(range(8))},[loc(29,'Table8-8')])
                if rn=='ALERT_ENABLE' and not fn.startswith('RESERVED'):
                    setdim(record,'trigger_completion','CONDITIONAL','disable alert不会立即抹flag；已有ALERT引脚需status读取或新转换才deassert。',{'flag_still_sets_when_disabled':True,'pin_update_events':['status read','new conversion']},[loc(30,'§8.6.5')])
                if rn in ['TLOW_LIMIT','THIGH_LIMIT'] and not fn.startswith('RESERVED'):
                    setdim(record,'conditional_write','CONDITIONAL','THigh<=TLow时limits被忽略，直到High>Low；仍区分位存储与告警功能。',{'storage_signed_range':[-8192,8191],'functional_precondition':'signed(THIGH_LIMIT)>signed(TLOW_LIMIT)'},[loc(31,'§§8.6.6–8.6.7')])
            relevant=[x['status'] for x in ds.values() if x.get('applicable',True)]
            record['overall_status']='REPAIR' if 'REPAIR' in relevant else ('EXCLUDE' if 'EXCLUDE' in relevant else ('CONDITIONAL' if 'CONDITIONAL' in relevant else 'PASS'))
            ROWS.append(record)

finding('ROOT-TMP100-OS','TMP100',['CONFIG.OS','CONFIG.POL'],'read_as=1覆盖动态比较器/POL副作用','global read_as=1',{'exclude_unconditional_readback':True,'read_source':'comparator state and POL','trigger_requires_SD':1},[loc(18,'§7.5.3.6')])
finding('ROOT-TMP100-FORMAT','TMP100',['TEMP.T','TEMP.UNUSED'],'9位TEMP分区外推至全部可写resolution','TEMP[15:7], UNUSED[6:0]',{'format_by_R':'9–12bits','always_zero':'3:0','baseline_resolution':'00'},[loc(9,'§7.3.1'),loc(16,'Tables6–7')])
finding('ROOT-TMP102-OS-AL','TMP102',['CONFIG.OS','CONFIG.AL','CONFIG.POL'],'动态状态被普通存储/恒值保护覆盖','OS ordinary RW; AL protected fixed1',{'exclude_OS_persistence':True,'exclude_AL_snapshot_equality':True,'event_model':'conversion and hysteresis and POL'},[loc(15,'§6.4.4'),loc(19,'§6.5.3.8')])
finding('ROOT-TMP102-EM','TMP102',['CONFIG.EM','TEMP','TLOW','THIGH'],'EM1改变位格式，旧mask不覆盖；门限bit0不是EM标志','fixed12bits; threshold desc bit0 meaningful',{'static_EM_test_values':[0],'extended_format':'15:3','TEMP_bit0':1,'threshold_bits2_0':0},[loc(17,'Table6-9'),loc(19,'Table6-14'),loc(20,'Table6-16')])
finding('ROOT-TMP1075-UNUSED','TMP1075',['CFGR.UNUSED_LOW','LLIM.UNUSED','HLIM.UNUSED'],'TYPE RW与not-used功能未定义并存','unrestricted boundary RW testing',{'preserve_defaults':True,'exclude_nondefault_function_oracle':True,'pure_storage_if_explicit_assumption_only':True},[loc(22,'Table7-8'),loc(23,'Tables7-9–7-10')])
finding('ROOT-TMP1075-OS','TMP1075',['CFGR.OS'],'写触发需shutdown；always read0不证明完成','read_as under SD0 reset baseline',{'preconditions':{'CFGR.SD':1},'completion':'conversion complete','variant':'non-N'},[loc(19,'§7.4.2')])
finding('ROOT-TMP1075-TM','TMP1075',['CFGR.TM','CFGR.SD'],'遗漏模式写清fault counter/alert history副作用','storage-only',{'TM_write':'clear fault count and alert history','SD_command':'clear interrupt history'},[loc(20,'§7.4.4 / §7.4.4.2')])
finding('ROOT-TMP1075-ID-CONFLICT','TMP1075',['DIEID.DID'],'Table7-11 TYPE RW vs prose/map/diagram RO，旧注释称笔误/erratum缺官方证据','official-looking erratum claim',{'conflict_status':'UNRESOLVED','mask_access_dispute':True,'optional_RO_assumption':'prose+diagram priority'},[loc(21,'Table7-5'),loc(24,'Figure7-16 / Table7-11')],evidence_class='SOURCE_CONFLICT')
finding('ROOT-TMP126-COR','TMP126',['ALERT_STATUS.CRC_FLAG','ALERT_STATUS.SLEW_FLAG','ALERT_STATUS.THIGH_FLAG','ALERT_STATUS.TLOW_FLAG','ALERT_STATUS.DATA_READY_FLAG','TEMP_RESULT.TEMP'],'缺single read无auto increment约束与跨TEMP清DR','unconditional per-register clear',{'single_register_read_only':True,'auto_increment':False,'cross_clear':{'TEMP_RESULT':'ALERT_STATUS.DATA_READY_FLAG'},'require_nonzero_event':True},[loc(27,'§8.6.3'),loc(28,'Table8-7')])
finding('ROOT-TMP126-MODE','TMP126',['CONFIG.ONE_SHOT','CONFIG.INT_COMP','CONFIG.MODE','SLEW_RESULT.SLEW'],'遗漏one-shot完成置MODE1，模式切换clear/abort副作用，负slew数值未保证','read_as0 only',{'one_shot_complete':'MODE1 DR1','comparator_to_interrupt':'clear ALERT_STATUS','shutdown':'abort partial conversion; slew result0; keep alerts','negative_slew':'exclude numeric oracle'},[loc(14,'§8.4.2'),loc(15,'§8.4.3'),loc(16,'§8.4.4.1'),loc(26,'§8.6.2')])
finding('ROOT-BOSCH-DYNAMIC','BME280',['status','data registers','ctrl_hum','ctrl_meas'],'状态/输出动态与切换/写入commit条件未在静态策略明确执行','fresh instance only',{'freeze_events_for_protection':True,'wait_pending_transition':True,'ctrl_hum_commit':'write ctrl_meas','separate_burst_read_consistency':True},[loc(15,'§3.3.1'),loc(27,'§5.4.3'),loc(28,'Table21')])
finding('ROOT-BMP-MODE','BMP280',['ctrl_meas.mode','press_xlsb','temp_xlsb'],'候选描述仍把10写normal，寄存器描述把XLSB有效位置写低四位','10/11 normal; XLSB low nibble valid',{'mode':{'0':'sleep','1':'forced','2':'forced','3':'normal'},'XLSB_position':'7:4','unused':'3:0'},[loc(15,'Table10'),loc(24,'Table18'),loc(26,'Table24'),loc(27,'Table25')])
finding('ROOT-BMP-FILTER','BMP280',['config.filter'],'该版BMP没有BME式others编码逐行表；泛边界7不能算功能编码认证','generic max7',{'alias_function_not_certified':[5,6,7],'coefficient_set':['off',2,4,8,16]},[loc(14,'Table6'),loc(26,'Table23')],evidence_class='UNDEFINED_BEHAVIOR')
finding('ROOT-BOSCH-UNMAPPED','BMP280',['unmapped address behavior'],'原手册reserved registers读值不保证，旧未定义地址read0属于基准约定','unmapped reads zero',{'source_guarantee':'none','mark_as':'ABSTRACTION_ASSUMPTION','exclude_from_silicon_fact':True},[loc(24,'§4.1')])
finding('ROOT-BME-VERSION','BME280',['source version'],'封面1.24与正文1.23标识并存','single revision label',{'source_lock':'full file SHA256','retain_cover_and_footer':True},[loc(1,'cover'),loc(27,'footer')],severity='minor',evidence_class='SOURCE_CONFLICT')

tmp100=json.loads((OUT/'review_inputs'/'TMP100.json').read_text(encoding='utf-8'))['ir']
tr=next(r for r in tmp100['registers'] if r['name']=='TEMP')
patch('TMP100','TEMP',None,'desc',tr.get('desc'),'Twelve-bit read-only register at bits15:4, bits3:0 zero. Effective conversion resolution selected by R1:R0=9/10/11/12bits; at POR default9bits, unneeded result LSBs zero until higher resolution selected. Result0 before first conversion completes.',[loc(9,'§7.3.1'),loc(16,'Tables6–7')])
for rn in ['TEMP','CONFIG']:
    for f in next(r for r in tmp100['registers'] if r['name']==rn)['fields']:
        if rn=='TEMP':
            patch('TMP100',rn,f['name'],'bits',f['bits'],'15:4' if f['name']=='T' else '3:0',[loc(16,'Tables6–7'),loc(9,'§7.3.1')])
            patch('TMP100',rn,f['name'],'desc',f.get('desc'),'Full twelve-bit register format; R1:R0 selects effective ADC resolution and zeros unused LSBs.' if f['name']=='T' else 'Low four bits always zero in the twelve-bit temperature register format; bits6:4 belong to conversion data.',[loc(9,'§7.3.1'),loc(16,'Table7')])
            if f['name']=='UNUSED':
                patch('TMP100',rn,f['name'],'tier',f.get('tier'),'SOURCE_EXPLICIT_ZERO',[loc(16,'Table7')])
                patch('TMP100',rn,f['name'],'tier_evidence',f.get('tier_evidence'),'Table7 p.16 explicitly shows bits3:0 zero; effective resolution unused LSBs from §7.3.1 p.9.',[loc(16,'Table7'),loc(9,'§7.3.1')])
        if rn=='CONFIG' and f['name']=='OS':
            patch('TMP100',rn,'OS','read_as',f.get('read_as'),None,[loc(18,'§7.5.3.6')])
            PATCHES[-1]['op']='remove'
            patch('TMP100',rn,'OS','desc',f.get('desc'),'Write1 triggers one-shot only when SD1. Read reports comparator state with POL inversion; not an invariant1 and not a conversion-busy bit.',[loc(18,'§7.5.3.6')])
for chip in ['TMP100','TMP102']:
    inp=json.loads((OUT/'review_inputs'/f'{chip}.json').read_text(encoding='utf-8'))['ir']
    for rn in ['TLOW','THIGH']:
        for f in next(r for r in inp['registers'] if r['name']==rn)['fields']:
            if chip=='TMP102' and f['name']=='UNUSED': patch(chip,rn,f['name'],'desc',f.get('desc'),'Normal EM0: bits3:0 zero; Extended EM1: bit3 is threshold data, bits2:0 remain zero (Tables6-14/6-16).', [loc(19,'Table6-14'),loc(20,'Table6-16')])
for chip in ['BME280','BMP280']:
    inp=json.loads((OUT/'review_inputs'/f'{chip}.json').read_text(encoding='utf-8'))['ir']
    if chip=='BMP280':
        for rn in ['press_xlsb','temp_xlsb']:
            r=next(r for r in inp['registers'] if r['name']==rn)
            patch(chip,rn,None,'desc',r.get('desc'),'Raw output low four data bits occupy register bits7:4; bits3:0 are explicitly RO zero (Table18 p.24).',[loc(24,'Table18')])
write('fields.json',ROWS);write('findings.json',FINDINGS);write('ir_patches.json',PATCHES);write('register_gaps.json',[])
write('sources.json',{c:{**SOURCE[c],'manual_version':VERSIONS[c],'reviewed_pages':sorted({l['pdf_page'] for x in ROWS if x['chip']==c for d in x['dimensions'].values() for l in d['locators']})} for c in CHIPS})
write('expert_return.json',dict(contract_version='1.0',expert_skill='sci-skills-paper-deep-reading',project_id='d2d-twin',paper_family='M',stage_id='M4',task_id='source_root',task_status='COMPLETE',inputs_reviewed=['seven requested protocol documents','129 fields in six candidate IRs','six local original manufacturer PDFs'],outputs=['fields.json','findings.json','ir_patches.json','sources.json'],evidence_status=['VERIFIED_SOURCE with per-claim locators','EXECUTED_LOCAL source hashes','AI_INFERENCE for abstractions','NOT_EXECUTED physical timing and model generation'],assumptions=['completed_reset epoch','TMP1075 non-N','storage abstraction distinct from physical operation'],author_input_needed=[],manual_actions=[],quality_checks=['129 unique fields','key bitmaps visually inspected'],conflicts=['TMP1075_DIEID_ACCESS','BME280_COVER_FOOTER_VERSION'],conflict_resolution_status='UNRESOLVED',merge_permission='orchestrator_only',recommended_next_action='Apply source repairs only in a new candidate, then implement scoped harness before freeze.',stage_acceptance_recommendation='REPAIR'))
(DEST/'REVIEW.md').write_text('# 主审分组来源签审\n\n已逐项登记六芯片129字段、903个维度；出处为本地原始厂商PDF。关键位图已另行渲染核对。状态/输出RO权限、复位读回与运行中不变分别记录；not used的TYPE标签与功能定义分别记录。\n\n新增差异包括TMP100 OS极性和分辨率、TMP102动态OS/AL及EM格式、TMP1075动作前置条件/模式写清/unused策略、TMP126单寄存器无auto-increment读清及跨TEMP清DR/模式副作用、BMP280模式和XLSB文字、Bosch动态状态及写入commit。见findings.json和fields.json。\n\nTMP1075 DIEID访问内部冲突及BME封面/正文版本差异保持未解决；不称官方勘误。无模型运行、无参考测试准入、无实物测量。下一步：在新输入候选与新harness兑现条件后重新冻结。\n',encoding='utf-8')
print('root review fields',len(ROWS),'dimensions',len(ROWS)*7,'findings',len(FINDINGS),'patches',len(PATCHES))
