"""Bounded source-clause execution; these are not new model samples."""
import copy
from tmp126 import Semantics, OutsideContract


class Checks:
    def __init__(self):
        self.checks=[]
        self.trace=[]
    def equal(self,actual,expected,clause):
        self.checks.append({'clause':clause,'actual':copy.deepcopy(actual),'expected':copy.deepcopy(expected)})
        assert actual==expected,clause
    def outside(self,fn,clause):
        try: fn()
        except OutsideContract: self.checks.append({'clause':clause,'outside_contract':True})
        else: raise AssertionError(clause)
    def capture(self,d,label):
        self.trace.extend({**r,'instance':label} for r in d.trace)


def convert(d,w):
    d.event('conversion_started')
    d.event('conversion_sample_completed',temperature_word=w)


def flags(d):
    d.write('THIGH_LIMIT',0x100)
    d.write('TLOW_LIMIT',0xFF00)
    d.write('HYSTERESIS',0)
    for w in (0x200,0xFE00,0x300): convert(d,w)
    d.event('qualified_positive_slew_changed',exceeded=True)
    d.event('qualified_crc_write_completed',register='THIGH_LIMIT',value=0x180,success=False)


def flags_and_live():
    c=Checks(); d=Semantics(); flags(d)
    c.equal(d.read('ALERT_STATUS'),0xF7,'five nonzero RC flags and high/slew live states returned before clear')
    c.equal(d.read('ALERT_STATUS'),0x50,'only RC0xA7 cleared; live0x58 preserved')
    c.capture(d,'five_flags'); return c


def temp_cross_clear():
    c=Checks(); d=Semantics(); flags(d)
    c.equal(d.read('TEMP_RESULT'),0x300,'signed14 result returned')
    c.equal(d.read('ALERT_STATUS'),0xF6,'TEMP clears only DR; other flags/live survive')
    c.equal(d.read('ALERT_STATUS'),0x50,'qualified status read clears remaining RC')
    c.capture(d,'cross_clear'); return c


def comparator_to_interrupt():
    c=Checks(); d=Semantics(); d.write('CONFIG',0x20); d.write('ALERT_ENABLE',4); flags(d)
    c.equal(d.alert_level(),0,'enabled high comparator uses live state')
    c.equal(d.read('ALERT_STATUS'),0xF7,'preclear comparator flag history')
    c.equal(d.alert_level(),0,'clearing flags preserves comparator live alert')
    d.write('CONFIG',0)
    c.equal(d.read('ALERT_STATUS'),0,'1to0 clears whole status including live')
    c.equal(d.alert_level(),1,'1to0 deasserts logical ALERT')
    c.capture(d,'candidate_encoding'); return c


def oneshot_average_restart():
    c=Checks()
    for avg in (0,0x80):
        d=Semantics(); d.write('CONFIG',avg|0x18)
        c.equal(d.read('CONFIG')&0x10,0,'ONE_SHOT reads zero during active conversion')
        if avg:
            for _ in range(3): d.event('conversion_sample_completed',temperature_word=0x100)
            d.write('CONFIG',avg|0x18)
            c.equal(d.samples,[],'retrigger discards partial average')
        words=[0xFFF8,0]*4 if avg else [0x200]
        for i,w in enumerate(words):
            d.event('conversion_sample_completed',temperature_word=w)
            c.equal(d.conversion_state,'idle' if i==len(words)-1 else 'running','complete after required sample count')
            c.equal(d.read('CONFIG')&0x10,0,'ONE_SHOT reads zero through completion')
        c.equal(d.read('CONFIG')&8,8,'one-shot completion sets MODEshutdown')
        c.equal(d.operating_mode,'shutdown','one-shot returns shutdown')
        c.equal(d.read('ALERT_STATUS')&1,1,'completion sets DR')
        c.equal(d.read('TEMP_RESULT'),0xFFFC if avg else 0x200,'distinct signed sample exact-grid average result')
        c.equal(d.read('SLEW_RESULT'),0,'noncontinuous slew default zero')
        c.capture(d,'average8' if avg else 'single')
    return c


def abort_preserves_alerts():
    c=Checks(); d=Semantics(); flags(d); d.write('CONFIG',0x80)
    before=d.values['ALERT_STATUS']; prior=d.read('TEMP_RESULT'); before&=~1
    d.event('conversion_started'); d.event('conversion_sample_completed',temperature_word=0x100)
    d.write('CONFIG',0x88)
    c.equal(d.conversion_state,'idle','MODE1 aborts partial average')
    c.equal(d.samples,[],'aborted samples discarded')
    c.equal(d.read('TEMP_RESULT'),prior,'abort retains last completed temperature')
    c.equal(d.read('ALERT_STATUS'),before,'shutdown retains all alert history')
    c.equal(d.read('SLEW_RESULT'),0,'shutdown slew default')
    c.outside(lambda:d.event('conversion_sample_completed',temperature_word=0x200),'no completion after abort')
    c.capture(d,'abort'); return c


def signed_hysteresis():
    c=Checks(); d=Semantics(); d.write('THIGH_LIMIT',0x100); d.write('TLOW_LIMIT',0xFF00); d.write('HYSTERESIS',0x0101)
    for w,live,flag in [(0x200,0x10,4),(0x100,0x10,0),(0xC0,0x10,0),(0xBC,0,4),
                        (0xFE00,8,2),(0xFF00,8,0),(0xFF40,8,0),(0xFF44,0,2)]:
        convert(d,w)
        c.equal(d.read('ALERT_STATUS')&0x1E,live|flag,'signed crossing, strict hysteresis boundary and re-arm')
        c.equal(d.read('TEMP_RESULT'),w,'signed14 temperature word preserved')
    c.capture(d,'low_limit_candidate'); return c


def crc_discard():
    c=Checks(); d=Semantics(); d.write('THIGH_LIMIT',0x100)
    d.event('qualified_crc_write_completed',register='THIGH_LIMIT',value=0x200,success=False)
    c.equal(d.read('THIGH_LIMIT'),0x100,'qualified failed CRC discards settings')
    c.equal(d.read('ALERT_STATUS')&0x80,0x80,'failed CRC flag set')
    d.event('qualified_crc_write_completed',register='THIGH_LIMIT',value=0x200,success=True)
    c.equal(d.read('THIGH_LIMIT'),0x200,'qualified successful write applied')
    c.equal(d.read('ALERT_STATUS')&0x80,0,'latest valid CRC clears error')
    c.capture(d,'qualified_event_not_crc_algorithm'); return c


def source_scope_guards():
    c=Checks(); d=Semantics(); flags(d)
    c.outside(lambda:d.read('ALERT_STATUS',auto_increment=True),'conflicted auto-increment clear unscored')
    c.outside(lambda:d.read('ALERT_STATUS',transaction='burst'),'conflicted burst clear unscored')
    c.outside(lambda:d.read('TEMP_RESULT',transaction='burst',word_count=2),'repeated TEMP body restriction unscored')
    c.outside(lambda:d.event('qualified_crc_write_completed',register='CONFIG',value=0,success=False),'conflicted CRC CONFIG unscored')
    c.outside(lambda:d.read('SLEW_RESULT'),'numerical slew outside scope')
    c.outside(lambda:d.write('CONFIG',0x20),'reverse INT_COMP with history unscored')
    c.outside(lambda:d.write('ALERT_ENABLE',0),'active alert disable conflict unscored')
    d2=Semantics(); d2.write('CONFIG',0x98)
    for _ in range(7): d2.event('conversion_sample_completed',temperature_word=0)
    c.outside(lambda:d2.event('conversion_sample_completed',temperature_word=4),'fractional mean rounding unscored')
    c.capture(d,'scope_guards'); c.capture(d2,'rounding_guard'); return c


def nominal_period_table():
    c=Checks(); d=Semantics()
    for code,period in enumerate((6,31.25,62.5,125,250,500,1000,2000)):
        d.write('CONFIG',code)
        c.equal(d.nominal_period_ms(),period,'nominal source table only; not measured timing')
        d.read('CONFIG')
    c.capture(d,'nominal_metadata'); return c


def exploratory_burst():
    c=Checks(); d=Semantics(profile='body_candidate'); flags(d)
    c.equal(d.read('ALERT_STATUS',transaction='burst'),0xF7,'exploratory body policy preserves flags')
    c.equal(d.read('ALERT_STATUS'),0xF7,'exploratory followed by qualified clear')
    c.capture(d,'disputed_body_policy'); return c


SCENARIOS={fn.__name__:fn for fn in (flags_and_live,temp_cross_clear,comparator_to_interrupt,
    oneshot_average_restart,abort_preserves_alerts,signed_hysteresis,crc_discard,
    source_scope_guards,nominal_period_table,exploratory_burst)}
CLAIM_SCENARIOS={'C1':['flags_and_live'],'C2':['flags_and_live','source_scope_guards'],
    'C3':['temp_cross_clear'],'C4':['comparator_to_interrupt'],'C5':['oneshot_average_restart'],
    'C6':['abort_preserves_alerts'],'C7':['oneshot_average_restart','source_scope_guards'],
    'C8':['signed_hysteresis'],'C9':['flags_and_live','source_scope_guards'],
    'C10':['comparator_to_interrupt','signed_hysteresis'],'C11':['crc_discard','source_scope_guards'],
    'C12':['source_scope_guards']}
