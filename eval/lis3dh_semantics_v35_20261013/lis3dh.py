"""Source-bounded LIS3DH defaults/access and qualified XYZ event adapter.

The primary datasheet does not specify status acknowledgement triggers. Main
post-read status becomes unknown; read-consumption rules are a separate candidate.
"""
import hashlib
import json
from pathlib import Path
import types
HERE=Path(__file__).resolve().parent
AUDIT=HERE.parent/'independent_source_admission_20261012'
BASE=HERE.parent/'semantic_protocol_v3_20261012/runtime.py'
IR=AUDIT/'candidate_ir/LIS3DH_gold_ir.json'
if hashlib.sha256(IR.read_bytes()).hexdigest()!=json.loads((AUDIT/'audit_bundle_manifest.json').read_text(encoding='utf-8'))['files']['candidate_ir/LIS3DH_gold_ir.json']:
    raise ValueError('Frozen layout changed')
if hashlib.sha256(BASE.read_bytes()).hexdigest()!=json.loads((BASE.parent/'artifact_manifest.json').read_text(encoding='utf-8'))['files']['runtime.py']:
    raise ValueError('Frozen utility changed')
_base=types.ModuleType('_frozen_lis3dh_util');_base.__file__=str(BASE)
exec(compile(BASE.read_bytes(),str(BASE),'exec'),_base.__dict__)
OutsideContract=_base.OutsideContract
AXES=('X','Y','Z')
STATUS_RESET_MASK=0xFE


def integer(value,maximum):
    if type(value) is not int or not 0<=value<=maximum: raise OutsideContract('Unsigned integer width required')
    return value


class Semantics(_base.Semantics):
    def __init__(self,chip='LIS3DH',profile='common_source'):
        if type(chip) is not str or chip!='LIS3DH' or type(profile) is not str or profile not in ('common_source','read_consumption_candidate'):
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
        self.known['STATUS_REG']=STATUS_RESET_MASK  # XDA table row is absent.
        self.has_sample=False
        self.unread={a:False for a in AXES}
        self.overrun={a:False for a in AXES}
        self.bytes_seen={a:set() for a in AXES}
        self.trace=[]

    def _trace(self,op,**data): self.trace.append({'chip':'LIS3DH','profile':self.profile,'op':op,**data})

    @staticmethod
    def _mode(ctrl1,ctrl4):
        lp=bool(ctrl1&8);hr=bool(ctrl4&8);odr=ctrl1>>4
        if lp and hr: raise OutsideContract('LPen1 HR1 not allowed')
        if ctrl4&0x40 and not hr: raise OutsideContract('BLE requires high-resolution mode')
        if odr>9 or odr==8 and not lp: raise OutsideContract('NA ODR/mode combination')
        return 8 if lp else 12 if hr else 10

    def resolution_bits(self): return self._mode(self.values['CTRL_REG1'],self.values['CTRL_REG4'])

    def nominal_odr_hz(self):
        odr=self.values['CTRL_REG1']>>4
        if odr==8:
            if self.profile=='common_source': raise OutsideContract('1.60k versus1620 metadata discrepancy')
            return 1600  # Explicit Table31 choice, not measured frequency.
        return (0,1,10,25,50,100,200,400)[odr] if odr<8 else 5376 if self.values['CTRL_REG1']&8 else 1344

    def write(self,reg,value):
        integer(value,255)
        if type(reg) is not str or reg not in ('CTRL_REG1','CTRL_REG4','CTRL_REG0','TEMP_CFG_REG'):
            raise OutsideContract('RO/unimplemented write')
        if self.has_sample: raise OutsideContract('Configuration changes after event history are outside profile')
        if reg=='CTRL_REG1':
            if value&7!=7: raise OutsideContract('Disabled-axis group status is not implemented')
            self._mode(value,self.values['CTRL_REG4'])
        elif reg=='CTRL_REG4':
            if (value>>1)&3==3: raise OutsideContract('ST11 is undefined')
            self._mode(self.values['CTRL_REG1'],value)
        elif reg=='CTRL_REG0':
            if value & 0x7F != 0x10: raise OutsideContract('Boot-loaded fixed bits must retain defaults')
        elif value!=0: raise OutsideContract('Auxiliary ADC/temperature events excluded')
        self._rw(reg,value)
        self._trace('write',register=reg,value=value)

    def _refresh_candidate_status(self):
        da=sum((1<<i) for i,a in enumerate(AXES) if self.unread[a])
        ov=sum((1<<(i+4)) for i,a in enumerate(AXES) if self.overrun[a])
        # ANY aggregation and two-byte consumption are declared candidate rules.
        self.values['STATUS_REG']=da|ov|(8 if any(self.unread.values()) else 0)|(0x80 if any(self.overrun.values()) else 0)
        self.known['STATUS_REG']=STATUS_RESET_MASK  # XDA remains excluded even here.

    def read(self,reg,transaction='single',auto_increment=False):
        return self.read_masked(reg,255,transaction,auto_increment)

    def read_masked(self,reg,mask,transaction='single',auto_increment=False):
        integer(mask,255)
        if not mask or type(reg) is not str or reg not in self.values: raise OutsideContract('Unknown register/empty observation')
        if transaction!='single' or type(auto_increment) is not bool or auto_increment:
            raise OutsideContract('Only direct byte observations implemented')
        if self.known[reg]&mask!=mask: raise OutsideContract('Unknown bits may not be fabricated')
        before=self.values[reg]&mask
        output=reg.startswith('OUT_')
        if self.has_sample and (reg=='STATUS_REG' or output):
            if self.profile=='common_source':
                self.known['STATUS_REG']=0  # Primary source does not establish post-read status.
            elif output:
                axis=reg.split('_')[1];part=reg.split('_')[2]
                self.bytes_seen[axis].add(part)
                if self.bytes_seen[axis]=={'L','H'}:
                    self.unread[axis]=False;self.overrun[axis]=False
                    self._refresh_candidate_status()
        self._trace('read',register=reg,mask=mask,value=before,transaction=transaction,auto_increment=auto_increment)
        return before

    def event(self,name,**payload):
        shapes={'qualified_sample_completed':{'x_word','y_word','z_word','overwritten'},
            'sample_completed':{'x_word','y_word','z_word'},'power_on_completed':set()}
        if type(name) is not str or name not in shapes or set(payload)!=shapes[name]: raise OutsideContract('Unknown/malformed event')
        if name=='power_on_completed':
            trace=self.trace;profile=self.profile;self.__init__(profile=profile);self.trace=trace
        else:
            if self.values['CTRL_REG1']>>4==0: raise OutsideContract('No samples in power-down profile')
            if self.field('CTRL_REG4','ST'):
                raise OutsideContract('Self-test response physics/settling are not implemented')
            if self.field('CTRL_REG4','BDU') and self.profile=='common_source':
                raise OutsideContract('Main qualified sample profile is BDU0; initial/pending BDU1 history is not certified')
            if name=='sample_completed' and self.profile!='read_consumption_candidate':
                raise OutsideContract('Autoderived consumption requires explicit candidate profile')
            if name=='qualified_sample_completed' and type(payload['overwritten']) is not bool:
                raise OutsideContract('Overwrite qualifier must be boolean')
            if name=='qualified_sample_completed' and payload['overwritten'] and not self.has_sample:
                raise OutsideContract('No prior qualified sample to overwrite at the cold boundary')
            resolution=self.resolution_bits()
            words=[integer(payload[a.lower()+'_word'],65535) for a in AXES]
            if any(w & ((1<<(16-resolution))-1) for w in words):
                raise OutsideContract('Only declared left-justified precision-grid stimuli admitted')
            if self.field('CTRL_REG4','BDU') and self.has_sample:
                if self.profile=='common_source' or any(self.unread.values()):
                    raise OutsideContract('BDU pending/release history not modeled; no invented sample selection')
            for axis,word in zip(AXES,words):
                previous_unread=self.unread[axis]
                self.overrun[axis]=(self.overrun[axis] or previous_unread) if name=='sample_completed' else payload['overwritten']
                self.unread[axis]=True;self.bytes_seen[axis]=set()
                lo,hi=(word&255,word>>8) if not self.values['CTRL_REG4']&0x40 else (word>>8,word&255)
                self._field('OUT_'+axis+'_L','DATA',lo);self._field('OUT_'+axis+'_H','DATA',hi)
            self.has_sample=True
            if self.profile=='read_consumption_candidate': self._refresh_candidate_status()
            else:
                self.values['STATUS_REG']=0x0E|(0xF0 if payload['overwritten'] else 0)
                self.known['STATUS_REG']=STATUS_RESET_MASK
        self._trace('event',name=name,payload=payload,
            interpretation='EXPLICIT_READ_CONSUMPTION_CANDIDATE' if self.profile=='read_consumption_candidate' else 'QUALIFIED_COHERENT_XYZ_NO_POST_READ_STATUS_ORACLE')
