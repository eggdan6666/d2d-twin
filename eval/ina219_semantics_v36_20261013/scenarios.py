"""Qualified INA219 digital histories; no analog or calibration arithmetic proof."""
import copy
from ina219 import Semantics, OutsideContract


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


def convert(d,shunt=100,bus=1000):
    d.event('conversion_started')
    d.event('voltage_results_completed',shunt_word=shunt,bus_code=bus)
    d.event('whole_sequence_completed')


def cold_unknown():
    c=Checks();d=Semantics()
    for mask in (0xFFF8,2,1,4,0xFFFF):
        c.outside(lambda m=mask:d.read_masked('BUS_VOLTAGE',m),'no numeric cold BUS field oracle')
    c.outside(lambda:d.read('SHUNT_VOLTAGE'),'measurement reset is unknown')
    for reg,value in [('CONFIGURATION',0x399F),('CALIBRATION',0),('CURRENT',0),('POWER',0)]:
        c.equal(d.read(reg),value,'documented factory default '+reg)
    c.equal(d.known['BUS_VOLTAGE'],0,'cold mask excludes all dynamic and reserved bits')
    c.capture(d,'cold');return c


def reset_completion():
    c=Checks();d=Semantics();d.write('CALIBRATION',0x1234);convert(d,0xFFF0,1200)
    d.write('CONFIGURATION',0x8000)
    c.equal(d.phase,'reset_pending','request is not completed reset')
    for reg in d.values:
        c.outside(lambda r=reg:d.read(r),'pending reset has no readback guarantee')
    c.outside(lambda:d.event('whole_sequence_completed'),'reset abort has no old conversion completion')
    d.event('reset_completed')
    for reg,value in [('CONFIGURATION',0x399F),('CALIBRATION',0),('CURRENT',0),('POWER',0)]:
        c.equal(d.read(reg),value,'completed reset restores documented default '+reg)
    c.equal(d.known['BUS_VOLTAGE'],0,'completed reset does not invent measurement defaults')
    c.outside(lambda:d.read('SHUNT_VOLTAGE'),'completed reset retains unknown SHUNT')
    c.outside(lambda:d.event('reset_completed'),'no duplicate reset completion')
    c.capture(d,'reset');return c


def sequence_completion():
    c=Checks();d=Semantics();d.write('CONFIGURATION',0x399B)
    c.equal(d.phase,'converting','MODE3 write starts one shot')
    c.equal(d.read_masked('BUS_VOLTAGE',2),0,'changed active mode clears CNVR before ambiguous read')
    d.event('voltage_results_completed',shunt_word=100,bus_code=1000)
    c.equal(d.phase,'calculating','voltage completion does not complete math')
    c.outside(lambda:d.read_masked('BUS_VOLTAGE',2),'ambiguous prior read retains no CNVR oracle')
    c.equal(d.read('SHUNT_VOLTAGE'),100,'settled supplied shunt result')
    d.event('whole_sequence_completed')
    c.equal(d.read_masked('BUS_VOLTAGE',0xFFFA),8002,'whole completion sets CNVR and encodes BD')
    c.equal(d.operating_state,'triggered_sleep','completed one shot sleeps without MODE storage rewrite')
    c.equal(d.read('CONFIGURATION')&7,3,'MODE storage remains programmed')
    d.write('CONFIGURATION',0x399B)
    c.equal(d.phase,'converting','unchanged MODE3 also triggers')
    c.equal(d.known['BUS_VOLTAGE']&2,0,'same-mode CNVR consequence remains unknown')
    c.capture(d,'sequence');return c


def signed_voltage_formats():
    c=Checks()
    for pg in range(4):
        for signed in (-4000*(1<<pg),-1,1,4000*(1<<pg)):
            d=Semantics();d.write('CONFIGURATION',(0x399F&~0x1800)|(pg<<11))
            convert(d,signed&65535,4000)
            c.equal(d.read('SHUNT_VOLTAGE'),signed&65535,'signed in-range supplied code and PGA sign extension')
            c.equal(d.read_masked('BUS_VOLTAGE',0xFFF8),32000,'BD shifted three places with 4mV units')
            c.equal(d.known['BUS_VOLTAGE']&4,0,'result event cannot supply reserved bit')
            c.capture(d,'PG'+str(pg)+'_'+str(signed))
    return c


def common_read_unknown():
    c=Checks()
    for reg,mask in [('BUS_VOLTAGE',2),('BUS_VOLTAGE',0xFFF8),('POWER',65535)]:
        d=Semantics();convert(d)
        c.equal(d.read_masked(reg,mask),2 if mask==2 else 8000 if reg=='BUS_VOLTAGE' else 0,'first qualified observation')
        c.equal(d.known['BUS_VOLTAGE']&2,0,'main profile does not choose disputed read-clear rule')
        c.outside(lambda:d.read_masked('BUS_VOLTAGE',2),'no repeated CNVR value guaranteed')
        c.capture(d,'postread_'+reg+'_'+str(mask))
    return c


def candidate_read_clear():
    c=Checks();d=Semantics(profile='register_detail_candidate');convert(d)
    c.equal(d.read_masked('BUS_VOLTAGE',2),2,'candidate BUS observation retains CNVR')
    c.equal(d.read_masked('BUS_VOLTAGE',2),2,'candidate repeated BUS observation')
    c.equal(d.read('POWER'),0,'candidate POWER default observation')
    c.equal(d.read_masked('BUS_VOLTAGE',2),0,'candidate follows detailed POWER clear text')
    c.outside(lambda:d.read_masked('BUS_VOLTAGE',4),'candidate cannot invent reserved bit')
    c.capture(d,'candidate_read');return c


def mode_clear_boundaries():
    c=Checks()
    for mode in (0,4):
        d=Semantics();convert(d);d.write('CONFIGURATION',(0x399F&~7)|mode)
        c.equal(d.read_masked('BUS_VOLTAGE',2),2,'explicit mode0/4 exception preserves prior CNVR observation')
        c.capture(d,'off_'+str(mode))
    d=Semantics();convert(d);d.write('CONFIGURATION',0x399B)
    c.equal(d.read_masked('BUS_VOLTAGE',2),0,'changed active mode clears')
    c.capture(d,'changed')
    for profile in ('common_source','register_detail_candidate'):
        d=Semantics(profile=profile);convert(d);d.write('CONFIGURATION',0x399F)
        if profile=='common_source':c.outside(lambda:d.read_masked('BUS_VOLTAGE',2),'same-mode conflicting source left unknown')
        else:c.equal(d.read_masked('BUS_VOLTAGE',2),0,'candidate chooses any active CONFIG write clears')
        c.capture(d,'same_'+profile)
    return c


def calibration_boundary():
    c=Checks();d=Semantics();d.write('CALIBRATION',0x1235)
    c.equal(d.read('CALIBRATION'),0x1234,'explicit FS0 RO0 differs from unspecified BUS reserved bit')
    for reg in ('CURRENT','POWER'):
        c.outside(lambda r=reg:d.read(r),'nonzero calibration arithmetic not fabricated')
    convert(d)
    c.outside(lambda:d.read_masked('BUS_VOLTAGE',1),'absence of qualified overflow does not prove zero')
    d.write('CALIBRATION',0)
    for reg in ('CURRENT','POWER'):
        c.outside(lambda r=reg:d.read(r),'later calibration clear is not immediate result reset')
    d.write('CONFIGURATION',0x8000);d.event('reset_completed')
    for reg in ('CURRENT','POWER'):c.equal(d.read(reg),0,'reset restores pre-first-programming zero guarantee')
    c.capture(d,'calibration');return c


def qualified_overflow():
    c=Checks();d=Semantics();d.write('CALIBRATION',0x1000)
    d.event('conversion_started')
    c.outside(lambda:d.event('qualified_math_overflow'),'math overflow cannot precede voltage result')
    d.event('voltage_results_completed',shunt_word=100,bus_code=1000)
    d.event('qualified_math_overflow');d.event('whole_sequence_completed')
    c.equal(d.read_masked('BUS_VOLTAGE',0xFFFB),8003,'qualified overflow sets OVF with completed CNVR')
    c.outside(lambda:d.read('POWER'),'out-of-range result has no fabricated representation')
    d.event('conversion_started')
    c.outside(lambda:d.read_masked('BUS_VOLTAGE',1),'later sequence cannot certify prior OVF lifetime or zero')
    d.event('voltage_results_completed',shunt_word=1,bus_code=1);d.event('whole_sequence_completed')
    c.outside(lambda:d.read_masked('BUS_VOLTAGE',1),'no unsourced no-overflow clearing rule')
    c.equal(d.known['BUS_VOLTAGE']&4,0,'overflow does not assign reserved bit')
    c.capture(d,'overflow');return c


def source_scope_guards():
    c=Checks();d=Semantics()
    for mode in (1,2,5,6):
        c.outside(lambda m=mode:d.write('CONFIGURATION',(0x399F&~7)|m),'legal selected-channel mode outside implemented histories')
    c.outside(lambda:d.write('CONFIGURATION',0x799F),'no reserved CONFIG nondefault policy')
    c.outside(lambda:d.event('whole_sequence_completed'),'completion requires an active sequence')
    c.outside(lambda:d.event('qualified_math_overflow'),'overflow needs qualified math history')
    c.outside(lambda:d.event('convert_pin'),'manual conflict cannot invent a pin')
    c.outside(lambda:d.write('BUS_VOLTAGE',4),'RO write not reserved-bit stimulus')
    c.outside(lambda:d.read('CONFIGURATION',transaction='burst'),'physical I2C framing excluded')
    d.event('conversion_started')
    c.outside(lambda:d.event('voltage_results_completed',shunt_word=True,bus_code=1),'strict word type')
    c.outside(lambda:d.event('voltage_results_completed',shunt_word=32767,bus_code=1),'out-of-range PGA saturation excluded')
    c.outside(lambda:d.event('voltage_results_completed',shunt_word=1,bus_code=8001),'digital range guard')
    c.equal(d.phase,'converting','rejected payloads do not complete conversion')
    c.outside(lambda:d.write('CONFIGURATION',0x399B),'active retrigger/discard history excluded')
    d.write('CONFIGURATION',0x8000);d.event('reset_completed')
    c.equal(d.read('CONFIGURATION'),0x399F,'reset may abort conversion through qualified completion')
    c.capture(d,'guards');return c


def nominal_adc_table():
    c=Checks();times=(84,148,276,532,84,148,276,532,532,1060,2130,4260,8510,17020,34050,68100)
    for field,shift in [('BADC',7),('SADC',3)]:
        d=Semantics()
        for code in range(16):
            d.write('CONFIGURATION',(0x399F&~(15<<shift))|(code<<shift))
            c.equal(d.nominal_adc_settings(field),{'resolution_bits':9+(code&3) if code<8 else 12,
                'samples':1 if code<8 else 1<<(code-8),'conversion_time_us':times[code]},'all16 source encodings including legal alias4..7; nominal metadata only')
        c.capture(d,'table_'+field)
    return c


SCENARIOS={f.__name__:f for f in (cold_unknown,reset_completion,sequence_completion,signed_voltage_formats,
    common_read_unknown,candidate_read_clear,mode_clear_boundaries,calibration_boundary,qualified_overflow,
    source_scope_guards,nominal_adc_table)}
CLAIM_SCENARIOS={
    'INA219-RESET-UNKNOWN':['cold_unknown','reset_completion'],
    'INA219-DEFINED-DEFAULTS':['cold_unknown','reset_completion'],
    'INA219-RST-COMPLETION':['reset_completion','source_scope_guards'],
    'INA219-BUS-RSV2-UNKNOWN':['cold_unknown','signed_voltage_formats','source_scope_guards'],
    'INA219-BUS-FORMAT':['signed_voltage_formats'],
    'INA219-SHUNT-FORMAT':['signed_voltage_formats'],
    'INA219-CNVR-SET':['sequence_completion'],
    'INA219-CNVR-MODE-CHANGE':['mode_clear_boundaries'],
    'INA219-CNVR-POWER-CANDIDATE':['common_read_unknown','candidate_read_clear'],
    'INA219-OVF-QUALIFIED':['qualified_overflow','calibration_boundary'],
    'INA219-TRIGGERED-WRITE':['sequence_completion'],
    'INA219-ADC-ENCODINGS':['nominal_adc_table'],
    'INA219-CAL-VOID':['calibration_boundary'],
    'INA219-REGISTER-TIMING':['source_scope_guards']}
