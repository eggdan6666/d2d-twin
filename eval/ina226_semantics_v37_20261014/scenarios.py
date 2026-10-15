"""Actual scoped digital histories; qualified inputs do not measure analog hardware."""
import copy
from ina226 import Semantics, OutsideContract

class Checks:
    def __init__(self): self.checks=[]; self.trace=[]
    def equal(self, actual, expected, clause):
        assert type(actual) is type(expected) and actual==expected, clause
        self.checks.append({'clause':clause,'actual':copy.deepcopy(actual),'expected':copy.deepcopy(expected)})
    def outside(self,d,fn,clause):
        before=copy.deepcopy(vars(d))
        try: fn()
        except OutsideContract: assert vars(d)==before,clause+' must reject atomically'
        else: raise AssertionError(clause)
        self.checks.append({'clause':clause,'outside_contract':True,'atomic_rejection':True})
    def capture(self,d,label): self.trace.extend({**r,'instance':label} for r in d.trace)

def token(d): return {'configuration_epoch':d.configuration_epoch,'sequence_id':d.sequence_id}
def alert(d,fault=True,function='SOL'):
    d.event('qualified_alert_conversion',function=function,fault=fault,**token(d))
def stage(d,shunt=0xFFF0,bus=1000):
    d.event('qualified_results_staged',shunt_word=shunt,bus_code=bus,**token(d))
def finish(d):
    d.event('whole_sequence_completed',conversions_complete=True,averaging_complete=True,
            multiplication_complete=True,**token(d))
def convert(d,shunt=0xFFF0,bus=1000):
    d.event('conversion_started'); stage(d,shunt,bus); finish(d)

def cold_defaults():
    c=Checks(); d=Semantics()
    for r,v in [('CONFIG',0x4127),('CALIBRATION',0),('MASK_ENABLE',0),('ALERT_LIMIT',0),
                ('SHUNT_VOLTAGE',0),('BUS_VOLTAGE',0),('CURRENT',0),('POWER',0),('MANUFACTURER_ID',0x5449)]:
        c.equal(d.read(r),v,'Table7-1 documented reset '+r)
    c.outside(d,lambda:d.read('DIE_ID'),'2260/2261 variant not selected')
    c.capture(d,'cold'); return c

def reserved_boundaries():
    c=Checks()
    for reg,mask,baseline in [('CONFIG',0x7000,0x4000),('CALIBRATION',0x8000,0),('MASK_ENABLE',0x3E0,0)]:
        d=Semantics(); c.equal(d.read_masked(reg,mask),baseline,'POR knownness is not access certification')
        values=([n<<12 for n in range(8)] if reg=='CONFIG' else [0,0x8000] if reg=='CALIBRATION' else [n<<5 for n in range(32)])
        for v in values:
            if v!=baseline: c.outside(d,lambda v=v:d.write(reg,v),'nondefault reserved stimulus excluded '+reg)
        d.write(reg,0x4127 if reg=='CONFIG' else 0x1234 if reg=='CALIBRATION' else 0x8000)
        c.equal(d.known[reg]&mask,0,'default write is not a reserved retention oracle')
        c.outside(d,lambda:d.read_masked(reg,mask),'postwrite reserved observation remains unknown')
        c.capture(d,reg)
    return c

def dirty_reset():
    c=Checks(); d=Semantics(); d.write('MASK_ENABLE',0x8001); d.write('CALIBRATION',0x1234)
    d.write('ALERT_LIMIT',0x2468); d.write('CONFIG',0x4123)
    alert(d); stage(d); finish(d)
    c.equal(d.values['MASK_ENABLE']&0x18,0x18,'nonzero AFF and CVRF pre-reset digital witness')
    old=token(d); d.write('CONFIG',0xC000)
    c.equal(d.phase,'reset_pending','request is not qualified completion')
    for r in d.values: c.outside(d,lambda r=r:d.read(r),'no pending-reset numeric oracle '+r)
    c.outside(d,lambda:d.event('conversion_started'),'pending reset rejects new conversion')
    d.event('reset_completed')
    for r,v in [('CONFIG',0x4127),('CALIBRATION',0),('MASK_ENABLE',0),('ALERT_LIMIT',0),
                ('SHUNT_VOLTAGE',0),('BUS_VOLTAGE',0),('CURRENT',0),('POWER',0)]:
        c.equal(d.read(r),v,'completed POR-equivalent reset '+r)
    c.equal(d.values['CONFIG']&0x8000,0,'completed RST self-clear')
    c.equal(d.calibration_ever_programmed,False,'qualified reset clears calibration history')
    c.outside(d,lambda:d.event('reset_completed'),'duplicate reset completion excluded')
    d.event('conversion_started')
    c.outside(d,lambda:d.event('qualified_results_staged',shunt_word=1,bus_code=1,**old),'pre-reset completion token is stale')
    c.capture(d,'reset'); return c

def latched_aff():
    c=Checks(); d=Semantics(); d.write('MASK_ENABLE',0x8001); d.event('conversion_started')
    alert(d,True); alert(d,False)
    c.equal(d.values['MASK_ENABLE']&0x10,0x10,'latched AFF survives next nofault conversion')
    c.equal(d.read('SHUNT_VOLTAGE'),0,'other register read not a MASK clear')
    c.equal(d.read_masked('MASK_ENABLE',0x10),0x10,'linearized preclear snapshot convention')
    c.equal(d.values['MASK_ENABLE']&0x10,0,'latched MASK transaction clears AFF')
    alert(d,True)
    c.equal(d.read_masked('MASK_ENABLE',0x10),0x10,'new qualified fault reasserts latched AFF')
    c.capture(d,'latch'); return c

def transparent_aff():
    c=Checks(); d=Semantics(); d.write('MASK_ENABLE',0x8000); d.event('conversion_started'); alert(d,True)
    for n in range(2):
        c.equal(d.read_masked('MASK_ENABLE',0x10),0x10,'transparent MASK read does not itself clear AFF')
    alert(d,False)
    c.equal(d.read_masked('MASK_ENABLE',0x10),0,'next related nofault conversion clears transparent AFF')
    alert(d,True); c.equal(d.values['MASK_ENABLE']&0x10,0x10,'transparent flag reasserts')
    c.capture(d,'transparent'); return c

def cv_sequence():
    c=Checks(); d=Semantics(); d.event('conversion_started'); before=d.values['SHUNT_VOLTAGE']
    c.equal(d.values['MASK_ENABLE']&8,0,'start does not certify full conversion completion')
    stage(d,0x8300,28800)
    c.equal(d.values['SHUNT_VOLTAGE'],before,'qualified staged results do not prematurely publish outputs')
    c.equal(d.values['MASK_ENABLE']&8,0,'staged voltage results not sufficient for CVRF')
    for key in ('conversions_complete','averaging_complete','multiplication_complete'):
        flags={k:True for k in ('conversions_complete','averaging_complete','multiplication_complete')}; flags[key]=False
        c.outside(d,lambda flags=flags:d.event('whole_sequence_completed',**flags,**token(d)),'incomplete '+key+' rejected')
    finish(d)
    c.equal(d.read('SHUNT_VOLTAGE'),0x8300,'supplied settled signed code, no ADC accuracy claim')
    c.equal(d.read('BUS_VOLTAGE'),28800,'supplied settled bus code, no analog safety claim')
    c.equal(d.values['MASK_ENABLE']&8,8,'full qualified sequence sets CVRF even CNVR disabled')
    c.equal(d.read_masked('MASK_ENABLE',8),8,'read observes ready before protocol clear')
    c.equal(d.values['MASK_ENABLE']&8,0,'MASK read clears CVRF')
    c.capture(d,'sequence'); return c

def cv_config_boundaries():
    c=Checks()
    for mode in (0,4,3,7):
        d=Semantics(); convert(d); d.write('CONFIG',(0x4127&~7)|mode)
        c.equal(d.values['MASK_ENABLE']&8,8 if mode in (0,4) else 0,'CVRF CONFIG clear except both powerdown modes')
        c.equal(d.read_masked('MASK_ENABLE',8),8 if mode in (0,4) else 0,'powerdown still allows flag read-clear')
        c.equal(d.values['MASK_ENABLE']&8,0,'MASK read is distinct from CONFIG exception')
        c.capture(d,'mode'+str(mode))
    d=Semantics(); convert(d); d.write('CONFIG',0x4127)
    c.equal(d.values['MASK_ENABLE']&8,0,'same active-mode rewrite also clears CVRF')
    c.capture(d,'same_mode'); return c

def aff_config_conflict():
    c=Checks(); d=Semantics(); d.write('MASK_ENABLE',0x8001); d.event('conversion_started'); alert(d)
    d.write('CONFIG',0x4127)
    c.equal(d.known['MASK_ENABLE']&0x10,0,'disputed CONFIG clear invalidates AFF knowledge')
    c.outside(d,lambda:d.read_masked('MASK_ENABLE',0x10),'common profile must not pick p13 or p27')
    d.read_masked('MASK_ENABLE',8)
    c.equal(d.known['MASK_ENABLE']&0x10,0x10,'successful MASK transaction gives common latch-clear evidence')
    c.equal(d.values['MASK_ENABLE']&0x10,0,'common latch clear after disputed write')
    c.capture(d,'common'); return c

def named_conflict_candidates():
    c=Checks()
    for profile,expected in [('config_clear_candidate',0),('register_detail_candidate',0x10)]:
        d=Semantics(profile=profile); d.write('MASK_ENABLE',0x8001); d.event('conversion_started'); alert(d)
        d.write('CONFIG',0x4127)
        c.equal(d.read_masked('MASK_ENABLE',0x10),expected,'named source-conditioned candidate, not resolved fact')
        c.capture(d,profile)
    return c

def alert_priority():
    c=Checks()
    for function,control in [('SOL',0xF800),('SUL',0x7800),('BOL',0x3800),('BUL',0x1800),('POL',0x0800)]:
        d=Semantics(); d.write('MASK_ENABLE',control); d.event('conversion_started')
        c.equal(d.selected_function(),function,'highest selected alert bit priority')
        alert(d,True,function); c.equal(d.values['MASK_ENABLE']&0x10,0x10,'qualified selected function sets AFF')
        c.capture(d,function)
    return c

def token_and_domain_guards():
    c=Checks(); d=Semantics(); d.write('CONFIG',0x4123); old=token(d)
    d.write('CONFIG',0x4123)
    c.outside(d,lambda:d.event('qualified_results_staged',shunt_word=1,bus_code=1,**old),'previous trigger token invalid')
    for val in (-1,65536,True,1.5,'1',None):
        c.outside(d,lambda val=val:d.write('ALERT_LIMIT',val),'malformed numeric write')
    for val in (0,-1,65536,True,'1',None):
        c.outside(d,lambda val=val:d.read_masked('CONFIG',val),'malformed/empty mask')
    for mode in (1,2,5,6):
        c.outside(d,lambda mode=mode:d.write('CONFIG',0x4120|mode),'documented single-channel mode outside implemented scope')
    c.outside(d,lambda:d.event('physical_adc_done'),'unrecognised physical event')
    c.outside(d,lambda:d.write('MASK_ENABLE',0x10),'hardware status input not emulated software write')
    c.capture(d,'guards'); return c

def nominal_table():
    c=Checks()
    for avg,n in enumerate((1,4,16,64,128,256,512,1024)):
        for ct,t in enumerate((140,204,332,588,1100,2116,4156,8244)):
            d=Semantics(); d.write('CONFIG',0x4007|(avg<<9)|(ct<<6)|(ct<<3))
            c.equal(d.nominal_settings(),{'samples':n,'bus_conversion_time_us':t,'shunt_conversion_time_us':t},
                    'Tables7-3/4/5 metadata only, not elapsed-time measurement')
            c.capture(d,'avg'+str(avg)+'ct'+str(ct))
    return c

SCENARIOS={f.__name__:f for f in (cold_defaults,reserved_boundaries,dirty_reset,latched_aff,transparent_aff,
    cv_sequence,cv_config_boundaries,aff_config_conflict,named_conflict_candidates,alert_priority,
    token_and_domain_guards,nominal_table)}
