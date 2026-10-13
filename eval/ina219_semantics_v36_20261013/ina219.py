"""INA219 source-bounded voltage/reset adapter, not calibrated analog hardware."""
import hashlib
import json
from pathlib import Path
import types
HERE=Path(__file__).resolve().parent
AUDIT=HERE.parent/'independent_source_admission_20261012'
BASE=HERE.parent/'semantic_protocol_v3_20261012/runtime.py'
IR=AUDIT/'candidate_ir/INA219_gold_ir.json'
if hashlib.sha256(IR.read_bytes()).hexdigest()!=json.loads((AUDIT/'audit_bundle_manifest.json').read_text(encoding='utf-8'))['files']['candidate_ir/INA219_gold_ir.json']:
    raise ValueError('Frozen layout changed')
if hashlib.sha256(BASE.read_bytes()).hexdigest()!=json.loads((BASE.parent/'artifact_manifest.json').read_text(encoding='utf-8'))['files']['runtime.py']:
    raise ValueError('Frozen utility changed')
_base=types.ModuleType('_frozen_ina219_util');_base.__file__=str(BASE)
exec(compile(BASE.read_bytes(),str(BASE),'exec'),_base.__dict__)
OutsideContract=_base.OutsideContract


def integer(value,maximum):
    if type(value) is not int or not 0<=value<=maximum: raise OutsideContract('Unsigned integer width required')
    return value


class Semantics(_base.Semantics):
    def __init__(self,chip='INA219',profile='common_source'):
        if type(chip) is not str or chip!='INA219' or type(profile) is not str or profile not in ('common_source','register_detail_candidate'):
            raise OutsideContract('Unknown chip/profile')
        self.chip=chip;self.profile=profile
        self.ir=json.loads(IR.read_text(encoding='utf-8'))
        self.registers={r['name']:r for r in self.ir['registers']}
        self.fields={(r['name'],f['name']):f for r in self.ir['registers'] for f in r['fields']}
        self.values={};self.known={}
        for reg,item in self.registers.items():
            value=mask=0
            for f in item['fields']:
                if f.get('reset') is not None:
                    m,lo=_base.geometry(f['bits']);value|=(_base.number(f['reset'])<<lo)&m;mask|=m
            self.values[reg]=value;self.known[reg]=mask
        self.known['BUS_VOLTAGE']=self.known['SHUNT_VOLTAGE']=0
        self.phase='idle';self.operating_state='continuous_idle'
        self.has_voltage_result=False;self.overflow_observed=False
        self.calibration_ever_programmed=False
        self.trace=[]

    def _trace(self,op,**data):self.trace.append({'chip':'INA219','profile':self.profile,'op':op,**data})

    def nominal_adc_settings(self,field):
        if type(field) is not str or field not in ('BADC','SADC'): raise OutsideContract('Unknown ADC field')
        n=self.field('CONFIGURATION',field)
        if n<8:
            return {'resolution_bits':9+(n&3),'samples':1,'conversion_time_us':(84,148,276,532)[n&3]}
        return {'resolution_bits':12,'samples':1<<(n-8),
            'conversion_time_us':(532,1060,2130,4260,8510,17020,34050,68100)[n-8]}

    def _start(self,triggered=False):
        if self.phase!='idle' or self.field('CONFIGURATION','MODE') not in ((3,) if triggered else (7,)):
            raise OutsideContract('Only idle both-channel conversion profile implemented')
        self.phase='converting';self.operating_state='triggered_conversion' if triggered else 'continuous_conversion'
        self.overflow_observed=False
        self.known['BUS_VOLTAGE'] &= ~1  # No universal lifetime/clear rule for prior OVF.

    def write(self,reg,value):
        integer(value,65535)
        if type(reg) is not str or reg not in ('CONFIGURATION','CALIBRATION'): raise OutsideContract('RO/unimplemented register write')
        reset=reg=='CONFIGURATION' and bool(value&0x8000)
        if self.phase=='reset_pending' or self.phase!='idle' and not reset:
            raise OutsideContract('Active write/retrigger excluded')
        if reg=='CONFIGURATION':
            if value&0x4000: raise OutsideContract('Reserved CONFIG bit14 nondefault write excluded')
            if reset:
                self._field('CONFIGURATION','RST',1)
                self.phase='reset_pending';self.operating_state='reset_pending'
                self._trace('write',register=reg,value=value)
                return
            mode=value&7;oldmode=self.field('CONFIGURATION','MODE')
            if mode in (1,2,5,6): raise OutsideContract('Selected-channel arithmetic/history not implemented; encodings are not NA')
            self._rw(reg,value)
            if mode not in (0,4):
                if oldmode!=mode or self.profile=='register_detail_candidate':self._field('BUS_VOLTAGE','CNVR',0)
                else:self.known['BUS_VOLTAGE'] &= ~2
            self.operating_state='power_down' if mode==0 else 'adc_off' if mode==4 else 'triggered_idle' if mode==3 else 'continuous_idle'
            if mode==3:self._start(True)  # Source p9 write also triggers an unchanged MODE3.
        else:
            self._rw(reg,value)  # FS0 is explicit RO0, not an unspecified reserved bit.
            if self.values[reg]:
                self.calibration_ever_programmed=True
                self.known['CURRENT']=self.known['POWER']=0
            elif not self.calibration_ever_programmed:
                self.values['CURRENT']=self.values['POWER']=0
                self.known['CURRENT']=self.known['POWER']=65535
            else:
                # The pre-first-programming zero guarantee is not an immediate
                # reset oracle for clearing previously programmed calibration.
                self.known['CURRENT']=self.known['POWER']=0
            self.known['BUS_VOLTAGE'] &= ~1
        self._trace('write',register=reg,value=value)

    def read(self,reg,transaction='single',auto_increment=False):
        return self.read_masked(reg,65535,transaction,auto_increment)

    def read_masked(self,reg,mask,transaction='single',auto_increment=False):
        integer(mask,65535)
        if not mask or type(reg) is not str or reg not in self.values: raise OutsideContract('Unknown register/empty observation')
        if transaction!='single' or type(auto_increment) is not bool or auto_increment:
            raise OutsideContract('Only direct register observations implemented')
        if self.phase=='reset_pending': raise OutsideContract('No guaranteed pending-reset readback')
        if self.known[reg]&mask!=mask: raise OutsideContract('Unknown bits cannot be fabricated')
        before=self.values[reg]&mask
        if reg in ('BUS_VOLTAGE','POWER'):
            if self.profile=='common_source':self.known['BUS_VOLTAGE'] &= ~2
            elif reg=='POWER':self._field('BUS_VOLTAGE','CNVR',0)
        self._trace('read',register=reg,mask=mask,value=before,transaction=transaction,auto_increment=auto_increment)
        return before

    def event(self,name,**payload):
        shapes={'conversion_started':set(),'voltage_results_completed':{'shunt_word','bus_code'},
            'whole_sequence_completed':set(),'qualified_math_overflow':set(),'reset_completed':set()}
        if type(name) is not str or name not in shapes or set(payload)!=shapes[name]: raise OutsideContract('Unknown/malformed event')
        if name=='reset_completed':
            if self.phase!='reset_pending': raise OutsideContract('No pending reset')
            trace=self.trace;profile=self.profile;self.__init__(profile=profile);self.trace=trace
        elif name=='conversion_started':self._start()
        elif name=='voltage_results_completed':
            if self.phase!='converting':raise OutsideContract('No active voltage sequence')
            shunt=integer(payload['shunt_word'],65535);bus=integer(payload['bus_code'],8191)
            signed=shunt-65536 if shunt&32768 else shunt
            if abs(signed)>4000*(1<<self.field('CONFIGURATION','PG')):
                raise OutsideContract('Only in-range post-ADC PGA stimuli admitted; no saturation model')
            if bus>(8000 if self.field('CONFIGURATION','BRNG') else 4000):
                raise OutsideContract('Only declared digital FSR stimuli admitted, not physical voltage safety proof')
            self._field('SHUNT_VOLTAGE','SV',shunt);self._field('BUS_VOLTAGE','BD',bus)
            self.has_voltage_result=True;self.phase='calculating'
        elif name=='qualified_math_overflow':
            if self.phase!='calculating' or not self.values['CALIBRATION']:
                raise OutsideContract('Overflow qualifier needs post-voltage nonzero-calibration math stage')
            self._field('BUS_VOLTAGE','OVF',1);self.overflow_observed=True
            self.known['CURRENT']=self.known['POWER']=0  # Out-of-range data may be meaningless.
        else:
            if self.phase!='calculating':raise OutsideContract('Full sequence completion requires voltage and math boundary')
            self._field('BUS_VOLTAGE','CNVR',1)
            if not self.overflow_observed:self.known['BUS_VOLTAGE'] &= ~1
            self.phase='idle'
            self.operating_state='triggered_sleep' if self.field('CONFIGURATION','MODE')==3 else 'continuous_idle'
        self._trace('event',name=name,payload=payload)
