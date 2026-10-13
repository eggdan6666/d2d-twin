"""Actual source-clause witnesses, separated from independent fault fixtures."""
import copy
from tmp461 import Semantics,OutsideContract


class Checks:
    def __init__(self): self.checks=[];self.trace=[]
    def equal(self,actual,expected,clause):
        self.checks.append({'clause':clause,'actual':copy.deepcopy(actual),'expected':copy.deepcopy(expected)})
        assert actual==expected,clause
    def outside(self,fn,clause):
        try: fn()
        except OutsideContract: self.checks.append({'clause':clause,'outside_contract':True})
        else: raise AssertionError(clause)
    def capture(self,d,label): self.trace.extend({**r,'instance':label} for r in d.trace)


def code(c): return (c*16)&4095
def measure(d,l=25,r=25):
    d.event('conversion_started')
    d.event('conversion_completed',local_code=code(l),remote_code=code(r),remote_open=False)


def prepare(d):
    measure(d)
    d.read_masked('STATUS',0x80)  # Known BUSY read clears retired but unknown old latches.
    d.event('qualified_alert_service_completed')
    for reg,value in [('LOCAL_HIGH_LIMIT',50),('LOCAL_LOW_LIMIT',10),('REMOTE_HIGH_LIMIT_HIGH',50),
        ('REMOTE_HIGH_LIMIT_LOW',0),('REMOTE_LOW_LIMIT_HIGH',10),('REMOTE_LOW_LIMIT_LOW',0),
        ('LOCAL_THERM_LIMIT',70),('REMOTE_THERM_LIMIT',70),('THERM_HYSTERESIS',10)]: d.write(reg,value)
    measure(d);d.read('STATUS')


def unknown_por():
    c=Checks();d=Semantics();d.write('CONV_RATE',9)
    c.equal(d.known['STATUS'],0,'STATUS no numeric POR authority')
    for mask in (0x80,0x40,0x20,0x10,8,4,2,1,255):
        c.outside(lambda m=mask:d.read_masked('STATUS',m),'unknown STATUS POR observation mask'+hex(mask))
    c.outside(lambda:d.read('ONE_SHOT'),'write-only undefined action byte has no zero reset readback')
    c.equal(d.known['ONE_SHOT'],0,'ONE_SHOT has no sourced stored/reset bits')
    c.equal(d.read('LOCAL_HIGH_LIMIT'),127,'documented nonzero limit POR retained')
    c.equal(d.read('CONSECUTIVE_ALERT'),1,'CONAL default source01')
    c.capture(d,'unknown_POR');return c


def active_retired_flags():
    c=Checks()
    for l,r,mask in [(60,25,0x40),(5,25,0x20),(25,60,0x10),(25,5,8)]:
        d=Semantics();prepare(d);measure(d,l,r)
        c.equal(d.read('STATUS'),mask,'active temperature cause returned before any qualified clear')
        c.equal(d.read('STATUS'),mask,'active cause remains after repeated STATUS reads')
        measure(d)
        c.equal(d.read('STATUS'),mask,'retired cause flag latched until read')
        c.equal(d.read('STATUS'),0,'eligible flag cleared only after cause retirement')
        c.equal(d.alert_pin(),0,'STATUS clear alone does not release ALERT latch')
        d.event('qualified_alert_service_completed')
        c.equal(d.alert_pin(),1,'qualified device-address service releases retired ALERT')
        c.capture(d,'flag_'+hex(mask))
    return c


def selective_retirement():
    c=Checks();d=Semantics();prepare(d);measure(d,60,60)
    measure(d,25,60)
    c.equal(d.read_masked('STATUS',0x80),0,'masked BUSY observation is still a whole STATUS read')
    c.equal(d.read('STATUS'),0x10,'local cause cleared while active remote flag persists')
    c.outside(lambda:d.event('qualified_alert_service_completed'),'active remote cause/flag blocks latch service')
    measure(d)
    c.equal(d.read('STATUS'),0x10,'remote latch returns preclear after retirement')
    c.equal(d.read('STATUS'),0,'all retired flags cleared')
    d.event('qualified_alert_service_completed');c.equal(d.alert_pin(),1,'service follows all cleared causes')
    c.capture(d,'selective_clear');return c


def all_five_latches():
    c=Checks();d=Semantics();prepare(d);measure(d,60,60);measure(d,5,5)
    d.event('conversion_started');d.event('qualified_remote_open_detected')
    c.equal(d.read_masked('STATUS',0x84),0x84,'BUSY live and qualified OPEN nonzero during conversion')
    d.event('conversion_completed',local_code=code(25),remote_code=code(25),remote_open=False)
    c.equal(d.read('STATUS'),0x7C,'five retired nonzero latches return old state')
    c.equal(d.read('STATUS'),0,'retired mask7C cleared; BUSY/THERM distinct')
    c.equal(d.alert_pin(),0,'fiveflag clear does not acknowledge ALERT')
    c.capture(d,'combined_flags');return c


def open_cause():
    c=Checks();d=Semantics();prepare(d);d.event('conversion_started')
    d.event('conversion_completed',local_code=code(25),remote_code=None,remote_open=True)
    c.equal(d.read_masked('STATUS',4),4,'qualified open result sets OPEN')
    c.equal(d.read_masked('STATUS',4),4,'persistent open cause survives STATUS read')
    c.outside(lambda:d.read('TEMP_REMOTE_HIGH'),'faulted remote ADC result not fabricated')
    measure(d)
    c.equal(d.read_masked('STATUS',4),4,'functional remote retires cause but keeps OPEN until read')
    c.equal(d.read('STATUS'),0,'OPEN clears after functional recovery')
    c.capture(d,'open_recovery');return c


def busy_one_shot():
    c=Checks()
    for value in (0,1,6,127,128,255):
        d=Semantics();d.write('CONFIG',0x40);d.write('ONE_SHOT',value)
        c.equal(d.phase,'converting','any byte is an action, not stored conversion data')
        c.equal(d.read_masked('STATUS',0x80),0x80,'one-shot starts BUSY without completion')
        c.equal(d.read_masked('STATUS',0x80),0x80,'STATUSread does not clear BUSY')
        c.outside(lambda:d.read('ONE_SHOT'),'no trigger-register readback/selfclear oracle')
        d.event('conversion_completed',local_code=code(25),remote_code=code(30),remote_open=False)
        c.equal(d.read_masked('STATUS',0x80),0,'completion clears live BUSY')
        c.equal(d.read('CONFIG')&0x40,0x40,'one-shot returns shutdown')
        c.equal(d.read('TEMP_LOCAL_HIGH'),25,'completed local result independent of action payload')
        c.equal(d.read('TEMP_LOCAL_LOW'),0,'local word pair completed')
        c.equal(d.read('TEMP_REMOTE_HIGH'),30,'completed remote result independent of action payload')
        c.equal(d.read('TEMP_REMOTE_LOW'),0,'remote word pair completed')
        c.outside(lambda:d.event('conversion_started'),'shutdown does not continue without action')
        c.capture(d,'payload_'+str(value))
    d=Semantics();d.event('conversion_started');d.write('CONFIG',0x40)
    c.equal(d.read_masked('STATUS',0x80),0x80,'SD request finishes current conversion, does not abort')
    d.event('conversion_completed',local_code=code(25),remote_code=code(25),remote_open=False)
    c.equal(d.read_masked('STATUS',0x80),0,'pending shutdown completes current conversion')
    c.capture(d,'deferred_shutdown');return c


def live_therm_hysteresis():
    c=Checks();d=Semantics();prepare(d)
    for l,r,expected in [(71,25,1),(65,71,3),(60,65,2),(25,60,0)]:
        measure(d,l,r)
        c.equal(d.read('STATUS')&3,expected,'THERM sets above limit and resets at/below limit minus hysteresis')
        c.equal(d.read('STATUS')&3,expected,'live THERM is not read-clear')
        c.equal(d.therm_pin(),0 if expected else 1,'THERM ORs local and remote thermal causes')
    c.capture(d,'THERM_live');return c


def therm2_candidate():
    c=Checks();d=Semantics(profile='therm2_candidate');prepare(d);d.write('CONFIG',0x20)
    measure(d);d.read_masked('STATUS',0x80)
    for t,expected in [(60,0x50),(45,0x50),(40,0),(5,0)]:
        measure(d,t,t)
        c.equal(d.read_masked('STATUS',0xD7)&0x50,expected,'THERM2 high flags follow explicit hysteresis branch')
        c.equal(d.read_masked('STATUS',0xD7)&0x50,expected,'THERM2 highs are not read-clear')
        c.equal(d.alert_pin(),0 if expected else 1,'THERM2 lowtemperature alone does not trip high pin')
        c.outside(lambda:d.read_masked('STATUS',0x28),'THERM2 low numeric state remains unspecified')
    d.write('CONFIG',0xA0);c.equal(d.alert_pin(),1,'MASK1 has no effect on THERM2')
    d.event('conversion_started');d.event('qualified_remote_open_detected')
    c.equal(d.read_masked('STATUS',4),4,'THERM2 OPEN latch persists while cause active')
    c.equal(d.alert_pin(),1,'qualified OPEN-only event does not independently trip THERM2 before unknown ADC outcome')
    d.event('conversion_completed',local_code=code(25),remote_code=code(25),remote_open=False)
    c.equal(d.read_masked('STATUS',4),4,'THERM2 retired OPEN returns preclear')
    c.equal(d.read_masked('STATUS',4),0,'THERM2 only OPEN latch readcleared')
    c.capture(d,'candidate_THERM2');return c


def reset_unknown_boundary():
    c=Checks();d=Semantics();prepare(d);measure(d,71,71);d.write('CONV_RATE',3)
    d.event('conversion_started')
    d.event('general_call_reset_completed',second_byte=5)
    c.equal(d.read_masked('STATUS',0x80),0x80,'non06 generalcall byte has no reset effect')
    d.event('general_call_reset_completed',second_byte=6)
    c.equal(d.phase,'idle','qualified reset aborts conversion')
    c.equal(d.read('CONFIG'),0,'reset restores documented CONFIG')
    c.equal(d.read('CONV_RATE'),8,'reset restores documented nonzero rate')
    c.equal(d.read('LOCAL_HIGH_LIMIT'),127,'reset restores nonzero high limit')
    c.equal(d.read('THERM_HYSTERESIS'),10,'reset restores nonzero hysteresis')
    c.equal(d.known['STATUS'],0,'reset returns unknown STATUS boundary')
    c.outside(lambda:d.read('STATUS'),'reset does not fabricate numeric STATUS00')
    c.outside(lambda:d.read('ONE_SHOT'),'reset does not create action register storage')
    c.outside(lambda:d.event('conversion_completed',local_code=320,remote_code=320,remote_open=False),'aborted conversion has no completion')
    c.capture(d,'dirty_generalcall_reset');return c


def signed_and_extended_words():
    c=Checks()
    for raw,config,high,low in [(0xFF8,0,255,128),(0x198,0,25,128),(0x400,4,64,0),(0xFE8,4,254,128)]:
        d=Semantics();d.write('CONFIG',config)
        if config:
            for reg,value in [('LOCAL_LOW_LIMIT',0),('LOCAL_HIGH_LIMIT',255),('REMOTE_LOW_LIMIT_HIGH',0),('REMOTE_HIGH_LIMIT_HIGH',255)]: d.write(reg,value)
        d.event('conversion_started')
        d.event('conversion_completed',local_code=raw,remote_code=raw,remote_open=False)
        c.equal(d.read('TEMP_LOCAL_HIGH'),high,'normal signed or extended unsigned raw high byte')
        c.equal(d.read('TEMP_LOCAL_LOW'),low,'fraction nibble at bits7:4 and lower zeros')
        c.equal(d.read('TEMP_REMOTE_HIGH'),high,'remote follows source data format')
        c.equal(d.read('TEMP_REMOTE_LOW'),low,'remote fractional byte')
        c.capture(d,'format_'+hex(raw)+'_'+str(config))
    return c


def source_scope_guards():
    c=Checks();d=Semantics();prepare(d)
    c.outside(lambda:d.write('ONE_SHOT',0),'SD0 one-shot outcome excluded')
    for reg,value in [('CONSECUTIVE_ALERT',3),('DIGITAL_FILTER',1),('REMOTE_OFFSET_HIGH',1),('N_FACTOR',1),('CHANNEL_ENABLE',1)]:
        c.outside(lambda r=reg,v=value:d.write(r,v),'unqualified branch '+reg)
    c.outside(lambda:d.write('CONFIG',0x20),'THERM2 requires separate declared profile')
    measure(d,60,60)
    c.outside(lambda:d.write('CONFIG',4),'active RANGE history mix excluded')
    c.outside(lambda:d.read('STATUS',transaction='burst'),'unimplemented read transaction excluded')
    d.event('conversion_started')
    c.outside(lambda:d.write('LOCAL_HIGH_LIMIT',40),'busy limit rewrite excluded')
    c.outside(lambda:d.event('conversion_completed',local_code=True,remote_code=320,remote_open=False),'malformed digital sample rejected atomically')
    d.event('conversion_completed',local_code=320,remote_code=320,remote_open=False)
    d.read('TEMP_LOCAL_HIGH');d.event('conversion_started')
    c.outside(lambda:d.event('conversion_completed',local_code=336,remote_code=336,remote_open=False),'unfinished snapshot pair prevents unsupported interleaved ADC update')
    d.read('TEMP_LOCAL_LOW')
    d.event('conversion_completed',local_code=336,remote_code=336,remote_open=False)
    c.capture(d,'source_exclusions');return c


def nominal_period_table():
    c=Checks();d=Semantics()
    for rate,period in enumerate((16,8,4,2,1,0.5,0.25,0.125,0.0625,0.03125)):
        d.write('CONV_RATE',rate)
        c.equal(d.nominal_period_seconds(),period,'source rate table only, not measured conversion period')
        d.read('CONV_RATE')
    c.capture(d,'nominal_metadata');return c


SCENARIOS={f.__name__:f for f in (unknown_por,active_retired_flags,selective_retirement,all_five_latches,
    open_cause,busy_one_shot,live_therm_hysteresis,therm2_candidate,reset_unknown_boundary,
    signed_and_extended_words,source_scope_guards,nominal_period_table)}
CLAIM_SCENARIOS={'C1':['unknown_por','reset_unknown_boundary'],'C2':['busy_one_shot','live_therm_hysteresis'],
    'C3':['active_retired_flags','selective_retirement','all_five_latches'],
    'C4':['active_retired_flags','selective_retirement'],'C5':['live_therm_hysteresis'],
    'C6':['therm2_candidate'],'C7':['busy_one_shot'],'C8':['busy_one_shot','source_scope_guards'],
    'C9':['signed_and_extended_words','source_scope_guards'],'C10':['source_scope_guards'],
    'C11':['open_cause','therm2_candidate'],'C12':['reset_unknown_boundary','nominal_period_table'],
    'C13':['source_scope_guards']}
