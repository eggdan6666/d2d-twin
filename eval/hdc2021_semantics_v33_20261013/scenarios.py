"""Executed clauses; candidate stimuli do not settle contradictory source prose."""
import copy
from hdc2021 import Semantics,OutsideContract


class Checks:
    def __init__(self): self.checks=[]; self.trace=[]
    def equal(self,actual,expected,clause):
        self.checks.append({'clause':clause,'actual':copy.deepcopy(actual),'expected':copy.deepcopy(expected)})
        assert actual==expected,clause
    def outside(self,fn,clause):
        try: fn()
        except OutsideContract: self.checks.append({'clause':clause,'outside_contract':True})
        else: raise AssertionError(clause)
    def capture(self,d,label): self.trace.extend({**r,'instance':label} for r in d.trace)


def prepare(d,enable=0xF8):
    d.write('INTERRUPT_ENABLE',enable)
    for r,v in [('TEMP_THR_L',0x40),('TEMP_THR_H',0xC0),('RH_THR_L',0x40),('RH_THR_H',0xC0)]: d.write(r,v)


def measure(d,t,h,request=True):
    if request: d.write('MEAS_CONFIG',d.read('MEAS_CONFIG')|1)
    d.event('measurement_started')
    d.event('measurement_completed',temperature_code=t,humidity_code=h)


def flags(d):
    prepare(d)
    for t,h in [(0xF000,0xF000),(0x1000,0x1000),(0x8000,0x8000)]: measure(d,t,h)


def latched_flags():
    c=Checks(); d=Semantics(); flags(d)
    c.equal(d.read_masked('STATUS',0xF8),0xF8,'five nonzero flags survive return inside in mode0 then return preclear')
    c.equal(d.read_masked('STATUS',0xF8),0,'defined flags cleared with no new event')
    measure(d,0xF000,0xF000)
    c.equal(d.read_masked('STATUS',0xF8),0xD0,'controlled completed measurement re-arms high flags')
    c.capture(d,'common_COR_under_candidate_threshold_stimuli'); return c


def dr_cross_clear():
    c=Checks()
    for reg in ('TEMP_LOW','TEMP_HIGH','HUM_LOW','HUM_HIGH','STATUS'):
        d=Semantics(); flags(d)
        if reg=='STATUS':
            c.equal(d.read_masked(reg,0xF8),0xF8,'STATUS returns old flags then clears')
            c.equal(d.read_masked('STATUS',0xF8),0,'STATUS clears all defined flags')
        else:
            c.equal(d.read(reg),0x80 if reg.endswith('HIGH') else 0,'data byte returned from selected completed sample')
            c.equal(d.read_masked('STATUS',0xF8),0x78,'data register clears DR only, preserves four threshold flags')
        c.capture(d,'fresh_DR_'+reg)
    d=Semantics(); flags(d); d.read('DEVICE_CONFIG')
    c.equal(d.read_masked('STATUS',0xF8),0xF8,'nondata configuration read does not clear DR')
    c.capture(d,'unrelated_read'); return c


def trigger_boundary():
    c=Checks(); d=Semantics(); prepare(d)
    d.write('MEAS_CONFIG',1)
    c.equal(d.phase,'start_requested','trigger request is distinct logical boundary')
    c.outside(lambda:d.read('MEAS_CONFIG'),'pending trigger readback not assumed observable')
    c.equal(d.read_masked('STATUS',0xF8),0,'no completion DR at request')
    d.event('measurement_started')
    c.equal(d.read('MEAS_CONFIG')&1,0,'TRIG selfclear at start')
    c.equal(d.read('TEMP_HIGH'),0,'old data before completion')
    c.equal(d.read_masked('STATUS',0xF8),0,'start alone does not assert completion')
    d.event('measurement_completed',temperature_code=0x1234,humidity_code=0x5678)
    c.equal(d.phase,'idle','completion returns sleep boundary')
    c.equal(d.read_masked('STATUS',0x80),0x80,'completion asserts DR')
    for reg,v in [('TEMP_LOW',0x34),('TEMP_HIGH',0x12),('HUM_LOW',0x78),('HUM_HIGH',0x56)]:
        c.equal(d.read(reg),v,'completion updates '+reg)
    c.equal(d.read('MEAS_CONFIG')&1,0,'TRIG stays zero at completion')
    c.outside(lambda:d.event('measurement_started'),'one-shot does not schedule another measurement')
    c.capture(d,'one_shot'); return c


def periodic_series():
    c=Checks()
    for cc in range(1,8):
        d=Semantics(); prepare(d); d.write('DEVICE_CONFIG',cc<<4)
        c.outside(lambda:d.event('measurement_started'),'CC setting alone not a qualified series start')
        measure(d,0x5004,0x6008)
        c.equal(d.continuous_armed,True,'trigger arms periodic series')
        c.equal(d.read('MEAS_CONFIG')&1,0,'continuous TRIG clears at start')
        measure(d,0x700C,0x8010,request=False)
        c.equal(d.read('TEMP_LOW'),0x0C,'autonomous qualified completion updates data')
        c.equal(d.read('HUM_LOW'),0x10,'periodic selected humidity updated')
        c.equal(d.phase,'idle','periodic measurement returns sleep between events')
        d.write('DEVICE_CONFIG',0)
        c.equal(d.continuous_armed,False,'quiescent CC0 disables periodic series')
        c.outside(lambda:d.event('measurement_started'),'CC0 requires new trigger')
        c.capture(d,'CC_'+str(cc))
    return c


def channel_and_resolution():
    c=Checks()
    for ta in range(3):
        for ha in range(3):
            d=Semantics(); prepare(d); measure(d,0x6004,0x7008)
            d.write('MEAS_CONFIG',(ta<<6)|(ha<<4)|3)
            d.event('measurement_started')
            c.equal(d.read('MEAS_CONFIG'),(ta<<6)|(ha<<4)|2,'legal precision encodings retained; TRIGclear')
            d.event('measurement_completed',temperature_code=0x9014,humidity_code=None)
            c.equal(d.read('TEMP_LOW'),0x14,'qualified post-quantized unsigned data, no invented resolution LSB rule')
            c.equal(d.read('TEMP_HIGH'),0x90,'temperature-only channel updated')
            c.equal(d.read('HUM_LOW'),8,'temperature-only retains previous humidity low')
            c.equal(d.read('HUM_HIGH'),0x70,'temperature-only retains previous humidity high')
            c.capture(d,'TACC'+str(ta)+'_HACC'+str(ha))
    return c


def reset_completion():
    c=Checks()
    for active in (False,True):
        d=Semantics(); flags(d); d.write('DEVICE_CONFIG',0x74)
        if active:
            d.write('MEAS_CONFIG',0xA1); d.event('measurement_started')
        d.write('DEVICE_CONFIG',0x80)
        c.equal(d.phase,'reset_pending','reset trigger and completion are separate')
        c.outside(lambda:d.read('DEVICE_CONFIG'),'no guaranteed bus read during reset')
        c.outside(lambda:d.read_masked('STATUS',0xF8),'no status snapshot during reset')
        d.event('reset_completed')
        c.equal(d.read('DEVICE_CONFIG'),0,'completed reset selfclears SOFT_RES and resets configuration')
        c.equal(d.read('MEAS_CONFIG'),0,'completed reset initializes measurement config')
        c.equal(d.read_masked('STATUS',0xF8),0,'completed reset clears status')
        for reg,value in [('TEMP_THR_L',1),('TEMP_THR_H',255),('RH_THR_L',0),('RH_THR_H',255),
            ('TEMP_LOW',0),('TEMP_HIGH',0),('HUM_LOW',0),('HUM_HIGH',0),('MANUF_ID_L',0x49),('DEVICE_ID_H',7)]:
            c.equal(d.read(reg),value,'documented reset boundary '+reg)
        c.equal(d.continuous_armed,False,'reset cancels periodic series')
        c.outside(lambda:d.event('measurement_started'),'reset restores one-shot idle')
        c.capture(d,'active_reset' if active else 'idle_reset')
    return c


def mode_encoding():
    c=Checks()
    for mode in (0,1):
        d=Semantics(); d.write('DEVICE_CONFIG',mode)
        c.equal(d.read('DEVICE_CONFIG')&1,mode,'unambiguous INT_MODE encoding0COR/1comparator')
        c.capture(d,'quiescent_mode_'+str(mode))
    return c


def threshold_candidate_comparisons():
    c=Checks(); d=Semantics(profile='table_figure_candidate'); prepare(d)
    for t,h,expected in [(0xC004,0x8000,0xC0),(0x3FFC,0x8000,0xA0),(0x8000,0xC004,0x90),(0x8000,0x3FFC,0x88)]:
        measure(d,t,h)
        c.equal(d.read_masked('STATUS',0xF8),expected,'table/figure candidate16bit vs threshold<<8 comparison')
    c.capture(d,'disputed_numeric_trigger_mapping'); return c


def comparator_candidate():
    c=Checks(); d=Semantics(profile='table_figure_candidate'); prepare(d); d.write('DEVICE_CONFIG',1)
    measure(d,0xF000,0xF000)
    c.equal(d.read_masked('STATUS',0xF8),0xD0,'candidate current high result and DR')
    c.equal(d.read_masked('STATUS',0xF8),0x50,'candidate preserves high statuses, clears DR')
    measure(d,0x8000,0x8000)
    c.equal(d.read_masked('STATUS',0xF8),0x80,'candidate return inside replaces prior high statuses')
    measure(d,0x1000,0x1000)
    c.equal(d.read_masked('STATUS',0xF8),0xA8,'candidate current low statuses')
    c.equal(d.read_masked('STATUS',0xF8),0x28,'candidate low statuses survive read')
    c.capture(d,'exploratory_comparator_read_policy'); return c


def pin_priority():
    c=Checks()
    for pol in (0,1):
        d=Semantics(); prepare(d); measure(d,0x8000,0xF000)
        c.equal(d.interrupt_pin(),'HIGH_Z','pin output disabled is high impedance')
        d.write('INTERRUPT_ENABLE',0x50); d.write('DEVICE_CONFIG',4|(pol<<1))
        c.equal(d.interrupt_pin(),1-pol,'THenabled inactive wins over HHactive; not OR')
        d.write('INTERRUPT_ENABLE',0x10)
        c.equal(d.interrupt_pin(),pol,'isolated HHactive follows polarity')
        d.read_masked('STATUS',0xF8)
        c.equal(d.interrupt_pin(),1-pol,'mode0 selected interrupt deasserts after read')
        c.capture(d,'priority_pol'+str(pol))
        e=Semantics(); e.write('INTERRUPT_ENABLE',0x80); e.write('DEVICE_CONFIG',4|(pol<<1))
        measure(e,0x8000,0x8000)
        c.equal(e.interrupt_pin(),pol,'isolated DRactive polarity')
        e.read('TEMP_LOW')
        c.equal(e.interrupt_pin(),1-pol,'isolated DRdeassert after data read')
        c.capture(e,'DR_pol'+str(pol))
    return c


def source_scope_guards():
    c=Checks(); d=Semantics(); prepare(d); flags(d)
    c.outside(lambda:d.write('DEVICE_CONFIG',1),'active-history mode switch excluded')
    c.outside(lambda:d.read('STATUS'),'reserved bits not fabricated')
    c.outside(lambda:d.write('MEAS_CONFIG',0xC0),'NA temperature precision excluded')
    c.outside(lambda:d.write('MEAS_CONFIG',4),'NA humidity-only channel excluded')
    c.outside(lambda:d.write('DEVICE_CONFIG',8),'heater physics excluded')
    c.outside(lambda:d.write('TEMP_OFFSET',1),'offset pipeline arithmetic excluded')
    c.outside(lambda:d.read('TEMP_MAX'),'unimplemented peak cannot stay fictitiously zero')
    d.write('DEVICE_CONFIG',4)
    c.outside(lambda:d.interrupt_pin(),'ambiguous DRplus threshold composition excluded')
    d.write('MEAS_CONFIG',1); d.event('measurement_started')
    c.outside(lambda:d.write('MEAS_CONFIG',1),'midconversion retrigger excluded')
    c.outside(lambda:d.event('measurement_completed',temperature_code=0x4000,humidity_code=0x8000),'exact threshold equality unspecified')
    c.outside(lambda:d.event('measurement_completed',temperature_code=True,humidity_code=0x8000),'malformed completion value excluded')
    c.capture(d,'scope_guards')
    e=Semantics(); prepare(e); e.write('DEVICE_CONFIG',1); measure(e,0xF000,0xF000)
    c.outside(lambda:e.read_masked('STATUS',0xF8),'common comparator read conflict unscored')
    c.capture(e,'common_comparator_guard')
    f=Semantics(); measure(f,0x8000,0x8000)
    c.outside(lambda:f.read_masked('STATUS',0xF8),'disabled status generation remains unknown')
    c.capture(f,'disabled_generation_guard'); return c


def nominal_period_table():
    c=Checks(); d=Semantics()
    c.equal(d.nominal_reset_max_ms(),3.5,'tPOR source maximum metadata, not executed reset deadline')
    for cc,period in enumerate((None,120,60,10,5,1,0.5,0.2)):
        d.write('DEVICE_CONFIG',cc<<4)
        c.equal(d.nominal_period_seconds(),period,'nominal CC table only, not measured intervals')
        d.read('DEVICE_CONFIG')
    c.capture(d,'nominal_metadata'); return c


SCENARIOS={fn.__name__:fn for fn in (latched_flags,dr_cross_clear,trigger_boundary,periodic_series,
    channel_and_resolution,reset_completion,mode_encoding,threshold_candidate_comparisons,
    comparator_candidate,pin_priority,source_scope_guards,nominal_period_table)}
CLAIM_SCENARIOS={'C1':['latched_flags'],'C2':['dr_cross_clear'],'C3':['mode_encoding','latched_flags','source_scope_guards'],
    'C4':['trigger_boundary'],'C5':['reset_completion','nominal_period_table'],'C6':['periodic_series','nominal_period_table'],
    'C7':['channel_and_resolution'],'C8':['threshold_candidate_comparisons'],
    'C9':['latched_flags','source_scope_guards'],'C10':['pin_priority','source_scope_guards'],
    'C11':['source_scope_guards'],'C12':['source_scope_guards']}
