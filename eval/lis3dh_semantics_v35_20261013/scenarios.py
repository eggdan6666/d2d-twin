"""Source-bound defaults/access, qualified whole-XYZ events and candidate reads."""
import copy
from lis3dh import Semantics,OutsideContract


class Checks:
    def __init__(self):self.checks=[];self.trace=[]
    def equal(self,actual,expected,clause):
        self.checks.append({'clause':clause,'actual':copy.deepcopy(actual),'expected':copy.deepcopy(expected)})
        assert actual==expected,clause
    def outside(self,fn,clause):
        try:fn()
        except OutsideContract:self.checks.append({'clause':clause,'outside_contract':True})
        else:raise AssertionError(clause)
    def capture(self,d,label):self.trace.extend({**r,'instance':label} for r in d.trace)


WORDS={'x_word':0x1000,'y_word':0xFC00,'z_word':0x2800}
SECOND={'x_word':0x2000,'y_word':0xF800,'z_word':0x3000}


def active(d):d.write('CTRL_REG1',0x17)
def qualified(d,overwritten=False,words=None):d.event('qualified_sample_completed',**(words or WORDS),overwritten=overwritten)
def candidate(d,words=None):d.event('sample_completed',**(words or WORDS))
def read_all(d):
    return {r:d.read(r) for a in ('X','Y','Z') for r in ('OUT_'+a+'_L','OUT_'+a+'_H')}


def settled_default():
    c=Checks();d=Semantics();d.write('CTRL_REG4',2)
    for mask in (0x80,0x40,0x20,0x10,8,4,2,0xFE):
        c.equal(d.read_masked('STATUS_REG',mask),0,'seven documented zero-default fields before events')
    c.equal(d.known['STATUS_REG'],0xFE,'default knownmask excludes absent XDA row')
    c.outside(lambda:d.read('STATUS_REG'),'whole STATUS includes unknown XDA')
    for a in ('X','Y','Z'):
        for part in ('L','H'):
            c.outside(lambda r='OUT_'+a+'_'+part:d.read(r),'default Output byte not fabricatedzero')
    c.equal(d.read('CTRL_REG1'),7,'documented powerdown/allaxes default')
    c.equal(d.read('WHO_AM_I'),0x33,'documented fixed identity')
    c.capture(d,'settled_default');return c


def legal_st_access():
    c=Checks()
    for neighbor in (0,1,8,0x10,0x20,0x48,0x80,0xF9):
        d=Semantics()
        for st in (0,1,2):
            value=neighbor|(st<<1)
            d.write('CTRL_REG4',value)
            c.equal(d.read('CTRL_REG4'),value,'ST RW legalcode and legalneighbor storage')
            c.equal(d.read('CTRL_REG4')&6,st<<1,'ST field readback doesnot pretendselfclear')
        before=d.read('CTRL_REG4')
        c.outside(lambda:d.write('CTRL_REG4',neighbor|6),'ST11 no ordinary storageoracle')
        c.equal(d.read('CTRL_REG4'),before,'illegal ST rejection doesnotmutate neighbors')
        c.capture(d,'neighbor_'+hex(neighbor))
    return c


def selftest_response_boundary():
    c=Checks()
    for st in (1,2):
        d=Semantics();d.write('CTRL_REG4',st<<1);active(d)
        c.outside(lambda:qualified(d),'legal ST storage is not sensorresponse execution')
        c.equal(d.read('CTRL_REG4')&6,st<<1,'excludedresponse doesnotalter storedselftestcode')
        c.equal(d.read_masked('STATUS_REG',0xFE),0,'no fakecomplete data from selftest config')
        c.capture(d,'ST_'+str(st))
    return c


def simultaneous_new_set():
    c=Checks();d=Semantics();active(d);qualified(d)
    c.equal(d.read_masked('STATUS_REG',0xFE),0x0E,'qualified coherentXYZ firstset makes knownnewdata bitsnonzero')
    c.equal(d.known['STATUS_REG'],0,'first STATUSread has no common postreadflagoracle')
    c.outside(lambda:d.read_masked('STATUS_REG',0xFE),'no unsourced STATUS repeat-retention or clear guarantee')
    data=read_all(d)
    c.equal(data,{'OUT_X_L':0,'OUT_X_H':0x10,'OUT_Y_L':0,'OUT_Y_H':0xFC,'OUT_Z_L':0,'OUT_Z_H':0x28},'qualified signed output bytes')
    c.capture(d,'simultaneous_firstset');return c


def simultaneous_overwrite():
    c=Checks();d=Semantics();active(d);qualified(d);qualified(d,True,SECOND)
    c.equal(d.read_masked('STATUS_REG',0xFE),0xFE,'second qualified wholeXYZ overwrites prior set with no interveningreads')
    c.outside(lambda:d.read('STATUS_REG'),'XDA remains excluded even after qualifiedoverwrite')
    data=read_all(d)
    c.equal(data,{'OUT_X_L':0,'OUT_X_H':0x20,'OUT_Y_L':0,'OUT_Y_H':0xF8,'OUT_Z_L':0,'OUT_Z_H':0x30},'latest qualified overwrite data')
    c.capture(d,'no_read_overwrite');return c


def common_read_boundary():
    c=Checks()
    for reg in ('STATUS_REG','OUT_X_L','OUT_X_H','OUT_Y_L','OUT_Y_H','OUT_Z_L','OUT_Z_H'):
        d=Semantics();active(d);qualified(d)
        if reg=='STATUS_REG':d.read_masked(reg,0xFE)
        else:d.read(reg)
        c.equal(d.known['STATUS_REG'],0,'no common sourcepostread acknowledgement knowledge')
        c.outside(lambda:d.read_masked('STATUS_REG',0xFE),'postread statusunknown after '+reg)
        c.capture(d,'postread_'+reg)
    return c


def word_formats():
    c=Checks()
    for ctrl1,ctrl4,word,bits,lower,upper in [(0x1F,0,0x1200,8,0,0x12),
        (0x17,0,0x1240,10,0x40,0x12),(0x17,8,0x1230,12,0x30,0x12),(0x17,0x48,0x1230,12,0x12,0x30)]:
        d=Semantics();d.write('CTRL_REG4',ctrl4);d.write('CTRL_REG1',ctrl1)
        c.equal(d.resolution_bits(),bits,'source operatingmode outputwidth')
        qualified(d,words={a+'_word':word for a in ('x','y','z')})
        c.equal(d.read('OUT_X_L'),lower,'lower registeraddress byte follows BLE in HRonly')
        c.equal(d.read('OUT_X_H'),upper,'upper registeraddress byte follows BLE')
        c.capture(d,'format_'+str(bits)+'_'+hex(ctrl4))
    return c


def candidate_consumption():
    c=Checks();d=Semantics(profile='read_consumption_candidate');active(d);candidate(d)
    c.equal(d.read_masked('STATUS_REG',0xFE),0x0E,'candidate newset ready')
    d.read('OUT_X_L');d.read('OUT_X_L')
    c.equal(d.unread['X'],True,'candidate duplicatehalf is not a completedpair')
    d.read('OUT_X_H');c.equal(d.unread['X'],False,'candidate pair consumesaxis')
    candidate(d,SECOND)
    c.equal(d.read_masked('STATUS_REG',0xFE),0xEE,'candidate peraxis overwrite andANYaggregate under partial consumption')
    read_all(d)
    c.equal(d.read_masked('STATUS_REG',0xFE),0,'candidate completeallaxes consumesready andoverrun')
    candidate(d)
    c.equal(d.read_masked('STATUS_REG',0xFE),0x0E,'candidate newset afterfullyconsumedpredecessor')
    c.outside(lambda:d.read_masked('STATUS_REG',1),'candidatepolicy cannotpromote missing XDA source')
    c.capture(d,'experimental_read_consumption');return c


def bdu_boundary():
    c=Checks()
    for profile in ('common_source','read_consumption_candidate'):
        d=Semantics(profile=profile);d.write('CTRL_REG4',0x80);active(d)
        if profile=='common_source':
            c.outside(lambda:qualified(d),'main BDU1 initial history has no certifiedcaptureoracle')
            c.outside(lambda:d.read('OUT_X_H'),'excluded BDUcapture cannotfabricate knownoutput')
            c.capture(d,'BDU_main_guard')
            continue
        candidate(d)
        call=lambda:qualified(d,True,SECOND) if profile=='common_source' else candidate(d,SECOND)
        c.outside(call,'BDU hold doesnotpretendoverwrite whenpendingrelease undefined')
        c.equal(d.read('OUT_X_H'),0x10,'held oldword remainsobserved, no fakependingreplacement')
        d.read('OUT_X_L');d.read('OUT_Y_L');d.read('OUT_Y_H');d.read('OUT_Z_L');d.read('OUT_Z_H')
        if profile=='common_source':c.outside(call,'common BDU postreadrelease selection unknown')
        else:
            candidate(d,SECOND)
            c.equal(d.read('OUT_X_H'),0x20,'candidate explicitnextarrival acceptedafterallaxesread')
        c.capture(d,'BDU_'+profile)
    return c


def power_on_defaults():
    c=Checks();d=Semantics(profile='read_consumption_candidate');active(d);candidate(d);candidate(d,SECOND)
    c.equal(d.read_masked('STATUS_REG',0xFE),0xFE,'dirtycandidate samplehistory nonzero')
    d.event('power_on_completed')
    c.equal(d.read('CTRL_REG1'),7,'qualified power-on restores documenteddefault')
    c.equal(d.read('CTRL_REG4'),0,'qualified power-on restores ST00')
    c.equal(d.read_masked('STATUS_REG',0xFE),0,'qualified settled cold defaultsrestore sevenknownzero fields')
    c.outside(lambda:d.read('STATUS_REG'),'qualified resetdoesnotadd XDAknowledge')
    c.outside(lambda:d.read('OUT_Y_H'),'qualified reset restores outputunknown')
    c.capture(d,'logical_settled_poweron');return c


def source_scope_guards():
    c=Checks();d=Semantics();d.write('CTRL_REG4',0x10)
    c.outside(lambda:qualified(d),'powerdown sample forbidden')
    c.outside(lambda:d.write('CTRL_REG1',0xA7),'undefinedODRcode excluded')
    c.outside(lambda:d.write('CTRL_REG1',0x87),'ODR8 onlyLPmode')
    c.outside(lambda:d.write('CTRL_REG4',0x40),'BLE withoutHR excluded')
    d.write('CTRL_REG4',8)
    c.outside(lambda:d.write('CTRL_REG1',0x1F),'LPen1HR1 notallowed')
    c.outside(lambda:d.write('CTRL_REG1',0x11),'disabledaxisaggregation unknown')
    c.outside(lambda:d.write('CTRL_REG0',0),'fixedbootbits mustremain default')
    c.outside(lambda:d.write('STATUS_REG',255),'ROstatuswrite noteventinjection')
    d.write('CTRL_REG4',0);active(d)
    c.outside(lambda:qualified(d,True),'coldframe cannotalreadyoverwrite priorqualifiedframe')
    c.outside(lambda:d.event('qualified_sample_completed',**WORDS,overwritten=1),'overwritequalifier strictbool')
    c.outside(lambda:d.event('qualified_sample_completed',x_word=True,y_word=64,z_word=64,overwritten=False),'strictsampletype')
    c.outside(lambda:d.event('qualified_sample_completed',x_word=1,y_word=64,z_word=64,overwritten=False),'declaredprecisiongrid scope only')
    c.outside(lambda:candidate(d),'auto-consumption not common source')
    qualified(d)
    c.outside(lambda:d.write('CTRL_REG4',2),'activehistory selftestswitch notmodeled')
    c.capture(d,'source_guards');return c


def nominal_odr_table():
    c=Checks()
    for lp,hr in ((0,0),(1,0),(0,1)):
        d=Semantics();d.write('CTRL_REG4',hr<<3)
        for odr,hz in [(0,0),(1,1),(2,10),(3,25),(4,50),(5,100),(6,200),(7,400),(9,5376 if lp else 1344)]:
            d.write('CTRL_REG1',(odr<<4)|(lp<<3)|7)
            c.equal(d.nominal_odr_hz(),hz,'nominal sourcedODR table notphysicaltiming')
        if lp:
            d.write('CTRL_REG1',0x8F)
            c.outside(lambda:d.nominal_odr_hz(),'1.60kHz vs1620 source discrepancy leftunresolved')
        c.capture(d,'ODR_LP'+str(lp)+'_HR'+str(hr))
    return c


SCENARIOS={f.__name__:f for f in (settled_default,legal_st_access,selftest_response_boundary,
    simultaneous_new_set,simultaneous_overwrite,common_read_boundary,word_formats,
    candidate_consumption,bdu_boundary,power_on_defaults,source_scope_guards,nominal_odr_table)}
CLAIM_SCENARIOS={'C1':['legal_st_access'],'C2':['legal_st_access','source_scope_guards'],
    'C3':['settled_default','power_on_defaults'],'C4':['selftest_response_boundary'],
    'C5':['simultaneous_new_set'],'C6':['simultaneous_overwrite'],
    'C7':['word_formats'],'C8':['bdu_boundary'],'C9':['source_scope_guards','nominal_odr_table'],
    'C10':['source_scope_guards'],'C11':['common_read_boundary'],
    'C12':['common_read_boundary','source_scope_guards']}
