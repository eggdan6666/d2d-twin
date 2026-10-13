"""TMP126 scoped register/event model. No physical SPI/CRC/timing claim."""
import hashlib
import json
from pathlib import Path
import types

HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'semantic_protocol_v3_20261012/runtime.py'
MANIFEST=HERE.parent/'semantic_protocol_v3_20261012/artifact_manifest.json'
if hashlib.sha256(BASE.read_bytes()).hexdigest()!=json.loads(MANIFEST.read_text(encoding='utf-8'))['files']['runtime.py']:
    raise ValueError('Frozen base changed')
_base=types.ModuleType('_frozen_tmp126_base')
_base.__file__=str(BASE)
exec(compile(BASE.read_bytes(),str(BASE),'exec'),_base.__dict__)
OutsideContract=_base.OutsideContract
RC_MASK=0xA7
LIVE_MASK=0x58
PERIOD_MS=(6,31.25,62.5,125,250,500,1000,2000)


def word(value):
    if type(value) is not int or not 0<=value<=0xFFFF:
        raise OutsideContract('Unsigned16 word required')
    return value


def temp_code(value):
    word(value)
    if value & 3:
        raise OutsideContract('Temperature format requires zero low2 bits')
    q=value>>2
    return q-0x4000 if q & 0x2000 else q


class Semantics(_base.Semantics):
    def __init__(self,chip='TMP126',profile='common_source'):
        if chip!='TMP126' or profile not in ('common_source','body_candidate'):
            raise OutsideContract('Unknown chip/profile')
        super().__init__(chip)
        self.profile=profile
        self.operating_mode='continuous'
        self.conversion_state='idle'
        self.required_samples=1
        self.samples=[]
        self.continuous_outputs=[]
        self.trace=[]

    def _trace(self,op,**data):
        self.trace.append({'chip':'TMP126','profile':self.profile,'op':op,**data})

    def nominal_period_ms(self):
        return PERIOD_MS[self.field('CONFIG','CONV_PERIOD')]

    def alert_level(self):
        enabled=self.values['ALERT_ENABLE']
        status=self.values['ALERT_STATUS']
        active=bool(enabled & 0x10 and status & 0x80 or enabled & 1 and status & 1)
        if self.field('CONFIG','INT_COMP'):
            active |= bool(enabled & 8 and status & 0x40 or enabled & 4 and status & 0x10 or enabled & 2 and status & 8)
        else:
            active |= bool(enabled & 8 and status & 0x20 or enabled & 4 and status & 4 or enabled & 2 and status & 2)
        return 0 if active else 1  # Logical active-low hook, not electrical timing.

    def _validate_write(self,reg,value):
        word(value)
        if type(reg) is not str or reg not in ('CONFIG','ALERT_ENABLE','THIGH_LIMIT','TLOW_LIMIT','HYSTERESIS','SLEW_LIMIT'):
            raise OutsideContract('Unimplemented/RO register write')
        if reg=='CONFIG':
            if value & ~0x00BF:
                raise OutsideContract('Reset and reserved input values excluded')
            if self.conversion_state=='running' and not value & 0x10:
                if not value & 8 or value & 0xA7 != self.values['CONFIG'] & 0xA7:
                    raise OutsideContract('Only same-control MODE1 abort or explicit one-shot retrigger admitted')
            old=self.field('CONFIG','INT_COMP')
            if old==0 and value & 0x20 and self.values['ALERT_STATUS'] and self.profile=='common_source':
                raise OutsideContract('Reverse mode transition with active history is source-conflicted')
        elif self.conversion_state=='running':
            raise OutsideContract('Mid-conversion non-CONFIG reconfiguration excluded')
        if reg in ('THIGH_LIMIT','TLOW_LIMIT') and value & 3:
            raise OutsideContract('Limit reserved low2 input bits must be zero')
        if reg=='ALERT_ENABLE':
            if value & ~0x1F:
                raise OutsideContract('Reserved enable bits excluded')
            if (self.profile=='common_source' and self.alert_level()==0
                    and self.values[reg] & ~value & 0x1F):
                raise OutsideContract('Immediate active-alert disable response is source-conflicted')
        if reg=='SLEW_LIMIT' and value & 0x8003:
            raise OutsideContract('Slew-limit reserved bits excluded')

    def _start(self,mode):
        self.operating_mode=mode
        self.conversion_state='running'
        self.samples=[]
        self.required_samples=8 if self.field('CONFIG','AVG') else 1
        if mode!='continuous':
            self.continuous_outputs=[]
            self.values['SLEW_RESULT']=0
            self.known['SLEW_RESULT']=0xFFFF

    def write(self,reg,value):
        self._validate_write(reg,value)
        if reg=='CONFIG':
            old=self.field('CONFIG','INT_COMP')
            self._rw(reg,value)
            self._field('CONFIG','ONE_SHOT',0)
            new=self.field('CONFIG','INT_COMP')
            if old!=new:
                # 1->0 is directly supported; active0->1 is exploratory only.
                self.values['ALERT_STATUS']=0
            if value & 0x10:
                self._start('one_shot')  # Sourced immediate restart discards partial.
            elif value & 8:
                self.operating_mode='shutdown'
                self.conversion_state='idle'
                self.samples=[]
                self.continuous_outputs=[]
                self.values['SLEW_RESULT']=0
                self.known['SLEW_RESULT']=0xFFFF
            else:
                self.operating_mode='continuous'
        else:
            self._rw(reg,value)
        self._trace('write',register=reg,value=value)

    def read(self,reg,transaction='single',auto_increment=False,word_count=1):
        if (type(reg) is not str or reg not in self.values or type(transaction) is not str
                or transaction not in ('single','burst') or type(auto_increment) is not bool
                or type(word_count) is not int or not 1<=word_count<=10):
            raise OutsideContract('Unsupported transaction metadata')
        if transaction=='single' and word_count!=1:
            raise OutsideContract('Single observation must have one data word')
        single=transaction=='single' and not auto_increment and word_count==1
        if reg=='ALERT_STATUS' and not single and self.profile=='common_source':
            raise OutsideContract('Noncommon status read outcome is source-conflicted')
        if reg=='TEMP_RESULT' and not auto_increment and word_count>1:
            raise OutsideContract('Repeated temperature reads are body-restricted/source-conflicted')
        if reg=='SLEW_RESULT' and self.operating_mode=='continuous':
            raise OutsideContract('Actual slew numeric result is outside this prototype')
        if self.known[reg]!=0xFFFF:
            raise OutsideContract('Unknown register value')
        before=self.values[reg]
        if reg=='ALERT_STATUS' and single:
            self.values[reg] &= ~RC_MASK
        if reg=='TEMP_RESULT':
            self._field('ALERT_STATUS','DATA_READY_FLAG',0)
        self._trace('read',register=reg,value=before,transaction=transaction,
                    auto_increment=auto_increment,word_count=word_count)
        return before

    def _temperature_update(self,q):
        low=temp_code(self.values['TLOW_LIMIT'])
        high=temp_code(self.values['THIGH_LIMIT'])
        high_old=bool(self.values['ALERT_STATUS'] & 0x10)
        low_old=bool(self.values['ALERT_STATUS'] & 8)
        high_hyst=(self.values['HYSTERESIS']>>8)*16  # 0.5C / (1/32C).
        low_hyst=(self.values['HYSTERESIS'] & 255)*16
        high_new=high_old
        low_new=low_old
        if not high_old and q>high: high_new=True
        elif high_old and q<high-high_hyst: high_new=False
        if not low_old and q<low: low_new=True
        elif low_old and q>low+low_hyst: low_new=False
        self._field('ALERT_STATUS','THIGH_STATUS',int(high_new))
        self._field('ALERT_STATUS','TLOW_STATUS',int(low_new))
        if high_new!=high_old: self._field('ALERT_STATUS','THIGH_FLAG',1)
        if low_new!=low_old: self._field('ALERT_STATUS','TLOW_FLAG',1)
        self._field('TEMP_RESULT','TEMP',q & 0x3FFF)
        self._field('ALERT_STATUS','DATA_READY_FLAG',1)

    def event(self,name,**payload):
        allowed={'conversion_started':set(),'conversion_sample_completed':{'temperature_word'},
                 'qualified_crc_write_completed':{'register','value','success'},
                 'qualified_positive_slew_changed':{'exceeded'}}
        if type(name) is not str or name not in allowed or set(payload)!=allowed[name]:
            raise OutsideContract('Unknown/malformed event')
        if name=='conversion_started':
            if self.operating_mode!='continuous' or self.conversion_state!='idle':
                raise OutsideContract('Only an idle continuous cycle needs explicit start')
            if temp_code(self.values['THIGH_LIMIT'])<=temp_code(self.values['TLOW_LIMIT']):
                raise OutsideContract('Ignored-limit behavior excluded by ordered benchmark profile')
            self._start('continuous')
        elif name=='conversion_sample_completed':
            q=temp_code(payload['temperature_word'])
            if self.conversion_state!='running':
                raise OutsideContract('No active conversion')
            if temp_code(self.values['THIGH_LIMIT'])<=temp_code(self.values['TLOW_LIMIT']):
                raise OutsideContract('Ignored-limit snapshot behavior not asserted')
            proposed=self.samples+[q]
            if len(proposed)==self.required_samples:
                total=sum(proposed)
                if total % self.required_samples:
                    raise OutsideContract('Fractional averaging rounding not specified')
                result=total//self.required_samples
                self._temperature_update(result)
                self.samples=proposed
                self.conversion_state='idle'
                if self.operating_mode=='one_shot':
                    self.operating_mode='shutdown'
                    self._field('CONFIG','MODE',1)
                    self.values['SLEW_RESULT']=0
                else:
                    self.continuous_outputs=(self.continuous_outputs+[result])[-2:]
            else:
                self.samples=proposed
        elif name=='qualified_crc_write_completed':
            reg,value,success=payload['register'],payload['value'],payload['success']
            if type(success) is not bool or reg=='CONFIG':
                raise OutsideContract('CRC CONFIG outcome and malformed result excluded')
            self._validate_write(reg,value)
            if success: self.write(reg,value)
            self._field('ALERT_STATUS','CRC_FLAG',int(not success))
        else:
            exceeded=payload['exceeded']
            if (type(exceeded) is not bool or self.operating_mode!='continuous'
                    or self.conversion_state!='idle' or len(self.continuous_outputs)!=2
                    or self.continuous_outputs[-1]<=self.continuous_outputs[-2]):
                raise OutsideContract('Positive slew qualification requires two completed increasing continuous results')
            old=bool(self.field('ALERT_STATUS','SLEW_POS_STATUS'))
            self._field('ALERT_STATUS','SLEW_POS_STATUS',int(exceeded))
            if old!=exceeded: self._field('ALERT_STATUS','SLEW_FLAG',1)
        self._trace('event',name=name,payload=payload)
