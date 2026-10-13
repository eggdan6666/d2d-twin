"""HDC2021 digital event profile; no ADC, real I2C or elapsed-time model.

Threshold numeric interpretation follows register tables and figures, with the
contradictory prose retained in source_review. Comparator read behavior is an
explicit table_figure_candidate policy, never an unconditional hardware oracle.
"""
import hashlib
import json
from pathlib import Path
import types

HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'semantic_protocol_v3_20261012/runtime.py'
AUDIT=HERE.parent/'independent_source_admission_20261012'
if hashlib.sha256(BASE.read_bytes()).hexdigest()!=json.loads((BASE.parent/'artifact_manifest.json').read_text(encoding='utf-8'))['files']['runtime.py']:
    raise ValueError('Frozen runtime changed')
IR=AUDIT/'candidate_ir/HDC2021_gold_ir.json'
if hashlib.sha256(IR.read_bytes()).hexdigest()!=json.loads((AUDIT/'audit_bundle_manifest.json').read_text(encoding='utf-8'))['files']['candidate_ir/HDC2021_gold_ir.json']:
    raise ValueError('Frozen candidate layout changed')
_base=types.ModuleType('_frozen_hdc2021_base'); _base.__file__=str(BASE)
exec(compile(BASE.read_bytes(),str(BASE),'exec'),_base.__dict__)
OutsideContract=_base.OutsideContract
CC_PERIOD_SECONDS=(None,120,60,10,5,1,0.5,0.2)
STATUS_MASK=0xF8


def integer(value,limit):
    if type(value) is not int or not 0<=value<=limit:
        raise OutsideContract('Unsigned integer width required')
    return value


class Semantics(_base.Semantics):
    def __init__(self,chip='HDC2021',profile='common_source'):
        if chip!='HDC2021' or type(profile) is not str or profile not in ('common_source','table_figure_candidate'):
            raise OutsideContract('Unknown chip/profile')
        super().__init__(chip)
        self.profile=profile
        self.continuous_armed=False
        self.known['STATUS'] &= STATUS_MASK
        self.known['INTERRUPT_ENABLE'] &= STATUS_MASK
        self.trace=[]

    def _trace(self,op,**data):
        self.trace.append({'chip':'HDC2021','profile':self.profile,'op':op,**data})

    def nominal_period_seconds(self):
        if self.phase=='reset_pending': raise OutsideContract('Reset pending metadata read excluded')
        return CC_PERIOD_SECONDS[self.field('DEVICE_CONFIG','CC')]

    def nominal_reset_max_ms(self):
        return 3.5  # Table6.6 design/characterization metadata, not measured time.

    def interrupt_pin(self):
        if self.phase=='reset_pending': raise OutsideContract('Reset pending pin excluded')
        if not self.field('DEVICE_CONFIG','DRDY_INT_EN'): return 'HIGH_Z'
        enabled=self.values['INTERRUPT_ENABLE'] & STATUS_MASK
        threshold=enabled & 0x78
        if enabled & 0x80 and threshold:
            raise OutsideContract('Equal DRDY/threshold priority composition unspecified')
        winner=next((m for m in (0x40,0x20,0x10,8) if threshold & m),0)
        if not winner:
            if not enabled & 0x80 or self.field('DEVICE_CONFIG','INT_MODE'): return 'HIGH_Z'
            winner=0x80
        if self.known['STATUS'] & winner != winner:
            raise OutsideContract('Unknown selected status')
        active=bool(self.values['STATUS'] & winner)
        polarity=self.field('DEVICE_CONFIG','INT_POL')
        return polarity if active else 1-polarity

    def write(self,reg,value):
        integer(value,255)
        if type(reg) is not str or reg not in ('DEVICE_CONFIG','MEAS_CONFIG','INTERRUPT_ENABLE',
            'TEMP_THR_L','TEMP_THR_H','RH_THR_L','RH_THR_H','TEMP_OFFSET','HUM_OFFSET'):
            raise OutsideContract('Unimplemented/RO register write')
        reset=reg=='DEVICE_CONFIG' and value==0x80
        if self.phase!='idle' and not (reset and self.phase in ('start_requested','converting')):
            raise OutsideContract('Active/pending reconfiguration excluded')
        if reg=='DEVICE_CONFIG':
            if value & 0x80 and not reset: raise OutsideContract('Combined reset/config write excluded')
            if value & 8: raise OutsideContract('Heater analog behavior excluded')
            if not reset and (value ^ self.values[reg]) & 1 and self.values['STATUS'] & STATUS_MASK:
                raise OutsideContract('Mode switch with active status history unspecified')
        if reg=='MEAS_CONFIG':
            if value>>6==3 or (value>>4)&3==3 or value & 8 or (value>>1)&3 not in (0,1):
                raise OutsideContract('Unspecified resolution/channel/reserved input excluded')
        if reg=='INTERRUPT_ENABLE' and value & 7:
            raise OutsideContract('Blank access-code reserved bits excluded')
        if reg in ('TEMP_OFFSET','HUM_OFFSET') and value:
            raise OutsideContract('Offset arithmetic/quantization not implemented')
        if reset:
            self._field('DEVICE_CONFIG','SOFT_RES',1)
            self.phase='reset_pending'; self.continuous_armed=False
        else:
            old_cc=self.field('DEVICE_CONFIG','CC')
            self._rw(reg,value)
            if reg=='DEVICE_CONFIG' and old_cc!=self.field('DEVICE_CONFIG','CC'):
                self.continuous_armed=False
            if reg=='MEAS_CONFIG' and value & 1:
                self.phase='start_requested'
        self._trace('write',register=reg,value=value)

    def read(self,reg,transaction='single',auto_increment=False):
        return self.read_masked(reg,255,transaction=transaction,auto_increment=auto_increment)

    def read_masked(self,reg,mask,transaction='single',auto_increment=False):
        integer(mask,255)
        if not mask or type(reg) is not str or reg not in self.values:
            raise OutsideContract('Unknown register or empty observation mask')
        if transaction!='single' or type(auto_increment) is not bool or auto_increment:
            raise OutsideContract('Only direct single-byte observations implemented')
        if self.phase=='reset_pending': raise OutsideContract('Reset-pending readback unspecified')
        if reg=='MEAS_CONFIG' and self.phase=='start_requested' and mask & 1:
            raise OutsideContract('Requested/start boundary is logical; no guaranteed pending trigger readback')
        if reg=='STATUS' and self.field('DEVICE_CONFIG','INT_MODE') and self.profile=='common_source':
            raise OutsideContract('Comparator STATUS read outcome is source-conflicted')
        if self.known[reg] & mask != mask: raise OutsideContract('Unknown bits cannot be fabricated as zero')
        before=self.values[reg] & mask
        if reg=='STATUS':
            if self.field('DEVICE_CONFIG','INT_MODE')==0:
                self.values[reg] &= ~STATUS_MASK
                self.known[reg] |= STATUS_MASK
            else:
                self._field('STATUS','DRDY_STATUS',0)
        elif reg in ('TEMP_LOW','TEMP_HIGH','HUM_LOW','HUM_HIGH'):
            self._field('STATUS','DRDY_STATUS',0)
        self._trace('read',register=reg,mask=mask,value=before,transaction=transaction,auto_increment=auto_increment)
        return before

    def event(self,name,**payload):
        shapes={'measurement_started':set(),'measurement_completed':{'temperature_code','humidity_code'},'reset_completed':set()}
        if type(name) is not str or name not in shapes or set(payload)!=shapes[name]:
            raise OutsideContract('Unknown/malformed event')
        if name=='reset_completed':
            if self.phase!='reset_pending': raise OutsideContract('No pending reset')
            trace=self.trace
            profile=self.profile
            self.__init__(profile=profile)
            self.trace=trace
        elif name=='measurement_started':
            if self.phase!='start_requested' and not (self.phase=='idle' and self.continuous_armed):
                raise OutsideContract('No requested or armed periodic measurement')
            self._field('MEAS_CONFIG','MEAS_TRIG',0)
            self.continuous_armed=self.field('DEVICE_CONFIG','CC')!=0
            self.phase='converting'
        else:
            if self.phase!='converting': raise OutsideContract('No active measurement')
            t=integer(payload['temperature_code'],65535)
            h=payload['humidity_code']
            selected=self.field('MEAS_CONFIG','MEAS_CONF')==0
            if selected: integer(h,65535)
            elif h is not None: raise OutsideContract('Unselected humidity channel must have no new sample')
            pairs=[(t,'TEMP_THR_H','TEMP_THR_L',0x40,0x20)]
            if selected: pairs.append((h,'RH_THR_H','RH_THR_L',0x10,8))
            current=0
            for code,high_reg,low_reg,hi_mask,lo_mask in pairs:
                high,low=self.values[high_reg]<<8,self.values[low_reg]<<8
                if high<=low or code in (high,low):
                    raise OutsideContract('Ordered, strictly separated threshold stimuli required')
                if code>high: current |= hi_mask
                if code<low: current |= lo_mask
            mode=self.field('DEVICE_CONFIG','INT_MODE')
            channel_mask=0x78 if selected else 0x60
            old=self.values['STATUS']
            updated=((old & ~channel_mask) | current) if mode else old | current
            self.values['STATUS']=updated | 0x80
            self.known['STATUS'] |= channel_mask | 0x80
            if mode and not selected: self.known['STATUS'] &= ~0x18
            if self.profile=='common_source':
                # p25 says status independent of enables; pp13-17 phrase
                # status generation as enabled. Unenabled event outcomes stay
                # unknown, instead of silently resolving that contradiction.
                self.known['STATUS'] &= ~(channel_mask | 0x80) | (self.values['INTERRUPT_ENABLE'] & STATUS_MASK)
            self._field('TEMP_LOW','TEMP7_0',t & 255); self._field('TEMP_HIGH','TEMP15_8',t>>8)
            if selected:
                self._field('HUM_LOW','HUM7_0',h & 255); self._field('HUM_HIGH','HUM15_8',h>>8)
            self.known['TEMP_MAX']=0
            if selected: self.known['HUM_MAX']=0
            self.phase='idle'
        self._trace('event',name=name,payload=payload,
            threshold_policy='TABLE_FIGURE_CANDIDATE' if name=='measurement_completed' else 'NOT_APPLICABLE')
