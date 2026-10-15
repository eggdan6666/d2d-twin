"""Scoped source histories. Events qualify digital/filter results, not physical timing."""
import copy
from ina3221 import Semantics,OutsideContract
class Checks:
    def __init__(self):self.checks=[];self.trace=[]
    def equal(self,actual,expected,clause):
        assert type(actual) is type(expected) and actual==expected,clause
        self.checks.append({'clause':clause,'actual':copy.deepcopy(actual),'expected':copy.deepcopy(expected)})
    def outside(self,d,fn,clause):
        before=copy.deepcopy(vars(d))
        try:fn()
        except OutsideContract:assert vars(d)==before,clause+' atomicity'
        else:raise AssertionError(clause)
        self.checks.append({'clause':clause,'outside_contract':True,'atomic_rejection':True})
    def capture(self,d,label):self.trace.extend({**r,'instance':label} for r in d.trace)
def token(d):return {'configuration_epoch':d.configuration_epoch,'sequence_id':d.sequence_id}
def stage(d,channel,kind,word=None):
    if word is None:word=(100*channel+(7 if kind=='bus' else 3))<<3
    d.event('qualified_filtered_result',channel=channel,kind=kind,encoded_word=word,
            filter_processing_complete=True,**token(d))
def finish(d):d.event('whole_sequence_completed',all_enabled_conversions_complete=True,**token(d))
def convert(d):
    if d.phase=='idle':d.event('conversion_started')
    for ch,kind in d.required_results():stage(d,ch,kind)
    finish(d)
def tc_start(d):d.event('tc_channel1_threshold_qualified',startup_epoch=d.startup_epoch,channel1_at_threshold=True)
def tc_cycle(d,valid=False):d.event('tc_cycle_qualified',startup_epoch=d.startup_epoch,cycle_index=d.tc_cycles+1,
    all_three_channels_complete=True,channel2_at_threshold=valid)
def pv(d,high):d.event('qualified_pv_detection_complete',startup_epoch=d.startup_epoch,
    configuration_epoch=d.configuration_epoch,high=high,detection_sequence_complete=True)

def cold_scope():
    c=Checks();d=Semantics()
    for r,v in [('CONFIG',0x7127),('SHUNT1',0),('VBUS1',0),('CRIT1',0x7FF8),('WARN1',0x7FF8),
                ('PV_UPPER',0x2710),('PV_LOWER',0x2328),('MANUF_ID',0x5449),('DIE_ID',0x3220)]:
        c.equal(d.read(r),v,'uncontested documented default '+r)
    c.outside(d,lambda:d.read('SHUNT_SUM_LIMIT'),'0Eh reset/access conflict not resolved by reference')
    c.outside(d,lambda:d.read_masked('MASK_ENABLE',2),'TCF literal/header conflict common numeric default unknown')
    c.equal(d.read_masked('MASK_ENABLE',1),0,'uncontested CVRF reset0')
    c.capture(d,'cold');return c

def reset_and_pv_exception():
    c=Checks();d=Semantics();pv(d,True);old_start=d.startup_epoch
    d.write('PV_UPPER',0x3330);d.write('PV_LOWER',0x1110);d.write('CRIT1',0x1230)
    d.write('CONFIG',0x5127);convert(d)
    c.equal(d.values['MASK_ENABLE']&1,1,'nonzero CVRF prior to reset')
    old=token(d);d.write('CONFIG',0x8000);request=d.configuration_epoch
    c.equal(d.phase,'reset_pending','request is not completed reset')
    for r in ('CONFIG','MASK_ENABLE','CRIT1','VBUS1'):c.outside(d,lambda r=r:d.read(r),'pending read unknown')
    d.write('CONFIG',0x8000)
    c.outside(d,lambda:d.event('reset_completed',request_epoch=request),'older same-value reset request cannot complete newer one')
    d.event('reset_completed',request_epoch=d.configuration_epoch)
    for r,v in [('CONFIG',0x7127),('CRIT1',0x7FF8),('PV_UPPER',0x2710),('PV_LOWER',0x2328),('VBUS1',0)]:
        c.equal(d.read(r),v,'qualified reset restores defined dirty defaults '+r)
    c.equal(d.pv_pin_logical_level,True,'software reset holds previously qualified PV output')
    c.outside(d,lambda:d.read_masked('MASK_ENABLE',4),'held PV pin vs default flag relation not fabricated')
    c.outside(d,lambda:d.read_masked('MASK_ENABLE',2),'reset does not resolve TCF literal')
    c.equal(d.tc_phase,'waiting_channel1','software reset rearms TC')
    c.equal(d.startup_epoch,old_start+1,'fresh startup identity')
    c.outside(d,lambda:d.event('reset_completed',request_epoch=d.configuration_epoch),'duplicate completion cannot reset again')
    d.event('conversion_started')
    c.outside(d,lambda:d.event('qualified_filtered_result',channel=1,kind='shunt',encoded_word=8,
        filter_processing_complete=True,**old),'pre-reset conversion witness rejected')
    pv(d,False);c.equal(d.pv_pin_logical_level,False,'qualified new PV detection ends held state')
    c.capture(d,'reset');return c

def enabled_mode_sequences():
    c=Checks()
    for enable in range(1,8):
        for mode in (1,2,3,5,6,7):
            d=Semantics();d.write('CONFIG',(enable<<12)|0x120|mode)
            if mode in (5,6,7):d.event('conversion_started')
            chs=tuple(i for i,b in ((1,4),(2,2),(3,1)) if enable&b)
            kinds=('shunt',) if mode in (1,5) else ('bus',) if mode in (2,6) else ('shunt','bus')
            expected=tuple((i,k) for i in chs for k in kinds)
            c.equal(d.required_results(),expected,'selected enabled channels and mode source geometry')
            for ch,kind in expected:stage(d,ch,kind)
            if enable==7:c.equal(d.values['MASK_ENABLE']&1,0,'individual qualified results not whole sequence flag')
            else:c.outside(d,lambda:d.read_masked('MASK_ENABLE',1),'subset CONFIG clear remains source-unknown until full completion')
            finish(d);c.equal(d.read_masked('MASK_ENABLE',1),1,'all selected conversions complete')
            c.equal(d.values['MASK_ENABLE']&1,0,'MASK read clears nonzero CVRF')
            c.equal(d.operating_state,'triggered_sleep' if mode in (1,2,3) else 'continuous_idle','triggered vs continuous end')
            c.capture(d,'e'+str(enable)+'m'+str(mode))
    return c

def partial_and_read_clear():
    c=Checks();d=Semantics();d.event('conversion_started');stage(d,1,'shunt')
    c.equal(d.read('SHUNT1'),824,'corresponding filtered output updates before remaining channel sequence')
    c.equal(d.read('CONFIG'),0x7127,'CONFIG read does not affect conversion')
    c.equal(d.values['MASK_ENABLE']&1,0,'partial channel set not CVRF complete')
    c.outside(d,lambda:finish(d),'partial enabled signal coverage cannot complete')
    for ch,kind in ((1,'bus'),(2,'shunt'),(2,'bus'),(3,'shunt'),(3,'bus')):stage(d,ch,kind)
    finish(d);c.equal(d.read('VBUS3'),2456,'other-address reading leaves ready flag')
    c.equal(d.values['MASK_ENABLE']&1,1,'CVRF remains until MASK/config clear')
    d.write('MASK_ENABLE',0x400)
    c.equal(d.values['MASK_ENABLE']&1,1,'MASK control write does not clear flag')
    c.equal(d.read_masked('MASK_ENABLE',1),1,'complete-word projected preclear snapshot convention')
    c.equal(d.read_masked('MASK_ENABLE',1),0,'subsequent MASK read sees cleared CVRF')
    c.capture(d,'partial');return c

def config_clear_and_disable():
    c=Checks()
    for mode in (0,4,1,2,3,5,6,7):
        d=Semantics();convert(d);d.write('CONFIG',0x7120|mode)
        c.equal(d.values['MASK_ENABLE']&1,1 if mode in (0,4) else 0,'common powerdown exception vs active clear')
        if mode in (0,4):c.outside(d,lambda:d.event('conversion_started'),'powerdown cannot synthesize completion')
        c.capture(d,'mode'+str(mode))
    d=Semantics();convert(d);d.write('CONFIG',0x0127)
    c.outside(d,lambda:d.read_masked('MASK_ENABLE',1),'all-disabled clear disagreement yields unknown')
    c.outside(d,lambda:d.event('conversion_started'),'empty enabled set cannot complete vacuously')
    c.capture(d,'disabled')
    for enable in range(1,7):
        d=Semantics();convert(d);d.write('CONFIG',(enable<<12)|0x127)
        c.outside(d,lambda:d.read_masked('MASK_ENABLE',1),'undefined disable-mode may include partial channel subset')
        convert(d);c.equal(d.read_masked('MASK_ENABLE',1),1,'complete currently enabled subset establishes ready independently')
        c.equal(d.values['MASK_ENABLE']&1,0,'subsequent MASK read establishes clear0')
        c.capture(d,'subset'+str(enable))
    return c

def recursive_filter_scope():
    c=Checks();d=Semantics();d.write('CONFIG',0x7F27);old=token(d)
    c.equal(d.nominal_settings()['filter_factor'],1024,'AVG identity is filter factor, not a completion countdown')
    d.event('conversion_started');first=token(d)
    stage(d,1,'shunt',0x1230)
    c.equal(d.read('SHUNT1'),0x1230,'supplied post-filter result updates corresponding register once')
    for ch,kind in ((1,'bus'),(2,'shunt'),(2,'bus'),(3,'shunt'),(3,'bus')):stage(d,ch,kind)
    finish(d);c.equal(d.read_masked('MASK_ENABLE',1),1,'one qualified full enabled cycle completes even AVG1024')
    d.write('CONFIG',0x7123)
    c.outside(d,lambda:d.event('qualified_filtered_result',channel=1,kind='bus',encoded_word=8,
        filter_processing_complete=True,**first),'old AVG/config result cannot enter new trigger')
    c.capture(d,'filter');return c

def trigger_rewrite_and_tokens():
    c=Checks();d=Semantics();d.write('CONFIG',0x7123);old=token(d);stage(d,1,'shunt')
    d.write('CONFIG',0x7123)
    c.outside(d,lambda:d.event('qualified_filtered_result',channel=1,kind='bus',encoded_word=8,
        filter_processing_complete=True,**old),'same MODE rewritten starts new token')
    c.equal(len(d.completed_results),0,'reconfiguration cancels prior partial set')
    for ch,kind in d.required_results():stage(d,ch,kind)
    finish(d);c.equal(d.read_masked('MASK_ENABLE',1),1,'new single-shot sequence completes')
    c.outside(d,lambda:finish(d),'completed token cannot produce duplicate completion')
    c.capture(d,'retrigger');return c

def tc_common_unknown():
    c=Checks();d=Semantics();tc_start(d)
    for n in range(3):tc_cycle(d);c.equal(d.tc_pin_logical_level,True,'default full-cycle qualification before fourth timeout')
    c.outside(d,lambda:d.event('tc_cycle_qualified',startup_epoch=d.startup_epoch,cycle_index=d.tc_cycles+1,all_three_channels_complete=False,
        channel2_at_threshold=False),'partial default cycle cannot count')
    c.outside(d,lambda:d.event('tc_cycle_qualified',startup_epoch=d.startup_epoch,cycle_index=3,all_three_channels_complete=True,
        channel2_at_threshold=False),'duplicate qualified TC cycle cannot count')
    tc_cycle(d);c.equal(d.tc_phase,'complete_timeout','four full default cycles without CH2 threshold')
    c.equal(d.tc_pin_logical_level,False,'source diagram digital TC level, not electrical measurement')
    c.outside(d,lambda:d.read_masked('MASK_ENABLE',2),'postfault TCF polarity common numeric unknown')
    phase=d.tc_phase;d.read_masked('MASK_ENABLE',1);d.write('MASK_ENABLE',0x400)
    c.equal(d.tc_phase,phase,'read/write MASK does not clear or rearm timing monitor')
    c.equal(d.known['MASK_ENABLE']&2,0,'read does not invent TCF0 or1')
    c.outside(d,lambda:tc_cycle(d),'completed monitor is terminal until restart')
    c.capture(d,'TCcommon');return c

def tc_cancel_and_rearm():
    c=Checks();d=Semantics();tc_start(d);old=d.startup_epoch;d.write('CONFIG',0x7127)
    c.equal(d.tc_phase,'disabled','even same CONFIG early write disables startup TC')
    c.outside(d,lambda:tc_cycle(d),'disabled late TC evidence rejected')
    d.write('CONFIG',0x8000);d.event('reset_completed',request_epoch=d.configuration_epoch)
    c.equal(d.tc_phase,'waiting_channel1','software reset rearm after disable')
    c.outside(d,lambda:d.event('tc_channel1_threshold_qualified',startup_epoch=old,channel1_at_threshold=True),'old startup token cannot rearm')
    tc_start(d);tc_cycle(d,True);c.equal(d.tc_phase,'complete_valid','qualified CH2 in valid window')
    d.event('power_cycle_completed');c.equal(d.tc_phase,'waiting_channel1','power cycle also rearms')
    c.equal(d.pv_pin_logical_level,False,'POR-qualified default differs from software held PV exception')
    c.capture(d,'TCcancel');return c

def tcf_named_candidates():
    c=Checks()
    for profile,expected in [('bitmap_pin_candidate',0),('bitmap_active_high_candidate',2)]:
        d=Semantics(profile=profile)
        c.equal(d.read_masked('MASK_ENABLE',2),2,'candidate bitmap default1, reset literal conflict retained')
        c.equal(d.read_masked('MASK_ENABLE',2),2,'candidate nonzero TCF not globally read-cleared')
        tc_start(d)
        for _ in range(4):tc_cycle(d)
        c.equal(d.read_masked('MASK_ENABLE',2),expected,'unverified named candidate polarity')
        c.equal(d.read_masked('MASK_ENABLE',2),expected,'candidate TCF lifetime not CVRF read-clear')
        d.write('CONFIG',0x8000);d.event('reset_completed',request_epoch=d.configuration_epoch)
        c.equal(d.read_masked('MASK_ENABLE',2),2,'candidate reset reinitializes even nondefault pin-level state')
        c.capture(d,profile)
    return c

def domain_guards():
    c=Checks();d=Semantics();d.event('conversion_started')
    for v in (-1,65536,True,1.5,'1',None):c.outside(d,lambda v=v:d.write('CONFIG',v),'malformed write atomic')
    for v in (0,-1,65536,True,'1',None):c.outside(d,lambda v=v:d.read_masked('CONFIG',v),'malformed/empty mask atomic')
    for v in (False,1,None):c.outside(d,lambda v=v:d.event('qualified_filtered_result',channel=1,kind='shunt',
        encoded_word=8,filter_processing_complete=v,**token(d)),'strict result processing qualification')
    stage(d,1,'shunt')
    c.outside(d,lambda:stage(d,1,'shunt'),'duplicate result cannot satisfy remaining coverage')
    c.outside(d,lambda:d.write('SHUNT_SUM_LIMIT',0x1234),'0Eh access conflict excluded')
    c.outside(d,lambda:d.write('MASK_ENABLE',2),'ordinary TCF RW persistence excluded')
    c.outside(d,lambda:d.event('physical_timeout_ms',value=28.6),'physical timing not an implemented event')
    c.capture(d,'guards');return c

def nominal_filter_metadata():
    c=Checks()
    for avg,factor in enumerate((1,4,16,64,128,256,512,1024)):
        for ct,t in enumerate((140,204,332,588,1100,2116,4156,8244)):
            d=Semantics();d.write('CONFIG',0x7007|(avg<<9)|(ct<<6)|(ct<<3))
            c.equal(d.nominal_settings(),{'filter_factor':factor,'bus_conversion_time_us':t,'shunt_conversion_time_us':t},
                'source table identity only, not AVG-loop count or physical latency')
            c.capture(d,'avg'+str(avg)+'ct'+str(ct))
    return c
SCENARIOS={f.__name__:f for f in (cold_scope,reset_and_pv_exception,enabled_mode_sequences,partial_and_read_clear,
    config_clear_and_disable,recursive_filter_scope,trigger_rewrite_and_tokens,tc_common_unknown,tc_cancel_and_rearm,
    tcf_named_candidates,domain_guards,nominal_filter_metadata)}
