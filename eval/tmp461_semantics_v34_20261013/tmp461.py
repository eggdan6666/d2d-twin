"""TMP461 bounded digital events; STATUS POR unknown and action byte unstored."""
import copy
import hashlib
import json
from pathlib import Path
import types
HERE=Path(__file__).resolve().parent
AUDIT=HERE.parent/'independent_source_admission_20261012'
BASE=HERE.parent/'semantic_protocol_v3_20261012/runtime.py'
IR=AUDIT/'candidate_ir/TMP461_gold_ir.json'
manifest=json.loads((AUDIT/'audit_bundle_manifest.json').read_text(encoding='utf-8'))
if hashlib.sha256(IR.read_bytes()).hexdigest()!=manifest['files']['candidate_ir/TMP461_gold_ir.json']:
    raise ValueError('Frozen layout changed')
if hashlib.sha256(BASE.read_bytes()).hexdigest()!=json.loads((BASE.parent/'artifact_manifest.json').read_text(encoding='utf-8'))['files']['runtime.py']:
    raise ValueError('Frozen utility changed')
_base=types.ModuleType('_frozen_tmp461_util');_base.__file__=str(BASE)
exec(compile(BASE.read_bytes(),str(BASE),'exec'),_base.__dict__)
OutsideContract=_base.OutsideContract
PERIOD_SECONDS=(16,8,4,2,1,0.5,0.25,0.125,0.0625,0.03125)


def unsigned(value,maximum):
    if type(value) is not int or not 0<=value<=maximum:
        raise OutsideContract('Unsigned width required')
    return value


def decode(code,extended,temperature=True):
    unsigned(code,4095)
    q=code-1024 if extended else code-4096 if code & 2048 else code
    if temperature and q < -1024: raise OutsideContract('Below documented -64C data scope')
    return q


class Semantics(_base.Semantics):
    def __init__(self,chip='TMP461',profile='common_source'):
        if type(chip) is not str or chip!='TMP461' or type(profile) is not str or profile not in ('common_source','therm2_candidate'):
            raise OutsideContract('Unknown chip/profile')
        self.chip=chip; self.profile=profile
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
        self.values['STATUS']=0;self.known['STATUS']=0
        self.values['ONE_SHOT']=0;self.known['ONE_SHOT']=0  # Placeholder never observed.
        self.phase='idle';self.one_shot=False;self.alert_latched=None
        self.retired={m:None for m in (0x40,0x20,0x10,8,4)}
        self.therm2_state={0x40:None,0x10:None}
        self.pending_pair=None
        self.trace=[]

    def _trace(self,op,**data): self.trace.append({'chip':'TMP461','profile':self.profile,'op':op,**data})
    def nominal_period_seconds(self): return PERIOD_SECONDS[self.field('CONV_RATE','CR')]

    def _start(self,one_shot=False):
        if self.phase!='idle' or self.values['CHANNEL_ENABLE']!=3:
            raise OutsideContract('Idle both-channel event profile required')
        if not one_shot and self.field('CONFIG','SD'):
            raise OutsideContract('Shutdown needs one-shot action')
        self.phase='converting';self.one_shot=one_shot
        self._field('STATUS','BUSY',1)

    def write(self,reg,value):
        unsigned(value,255)
        if type(reg) is not str or reg not in self.registers: raise OutsideContract('Unknown register')
        if reg=='ONE_SHOT':
            if not self.field('CONFIG','SD'): raise OutsideContract('One-shot outside shutdown not specified')
            self._start(True)
        else:
            allowed={'CONFIG','CONV_RATE','LOCAL_HIGH_LIMIT','LOCAL_LOW_LIMIT','REMOTE_HIGH_LIMIT_HIGH',
                'REMOTE_LOW_LIMIT_HIGH','REMOTE_HIGH_LIMIT_LOW','REMOTE_LOW_LIMIT_LOW','LOCAL_THERM_LIMIT',
                'REMOTE_THERM_LIMIT','THERM_HYSTERESIS','CHANNEL_ENABLE','CONSECUTIVE_ALERT',
                'DIGITAL_FILTER','REMOTE_OFFSET_HIGH','REMOTE_OFFSET_LOW','N_FACTOR'}
            if reg not in allowed: raise OutsideContract('RO/unimplemented write')
            # SD may request shutdown while a current conversion finishes.
            sd_only=(reg=='CONFIG' and self.phase=='converting' and value & 0x40
                and (value ^ self.values['CONFIG']) & ~0x40 == 0)
            if self.phase!='idle' and not sd_only: raise OutsideContract('Active reconfiguration/retrigger excluded')
            if reg=='CONFIG':
                if value & ~0xE4: raise OutsideContract('Reserved config inputs excluded')
                if value & 0x20 and self.profile!='therm2_candidate': raise OutsideContract('THERM2 branch requires declared candidate profile')
                if (value ^ self.values[reg]) & 0x24 and self.known['STATUS'] and self.values['STATUS'] & 0x7F:
                    raise OutsideContract('Range/output switch with active history unspecified')
            if reg=='CONV_RATE' and value>9: raise OutsideContract('Rate code not documented')
            if reg=='CHANNEL_ENABLE' and value!=3: raise OutsideContract('Disabled channel state propagation not implemented')
            if reg=='CONSECUTIVE_ALERT' and value!=1: raise OutsideContract('Nondefault queue timing/source interpretation excluded')
            if reg in ('DIGITAL_FILTER','REMOTE_OFFSET_HIGH','REMOTE_OFFSET_LOW','N_FACTOR') and value:
                raise OutsideContract('Filter startup/rounding/calibration excluded')
            if reg in ('REMOTE_HIGH_LIMIT_LOW','REMOTE_LOW_LIMIT_LOW') and value & 15:
                raise OutsideContract('Reserved limit low bits excluded')
            old=self.values[reg]
            self._rw(reg,value)
            if reg in ('LOCAL_HIGH_LIMIT','LOCAL_LOW_LIMIT'):
                self.retired[0x40]=self.retired[0x20]=None
            if reg in ('REMOTE_HIGH_LIMIT_HIGH','REMOTE_LOW_LIMIT_HIGH','REMOTE_HIGH_LIMIT_LOW','REMOTE_LOW_LIMIT_LOW'):
                self.retired[0x10]=self.retired[8]=None
            if reg=='CONFIG' and (old ^ value) & 0x20:
                self.known['STATUS'] &= ~0x78
                self.therm2_state={0x40:None,0x10:None}
        self._trace('write',register=reg,value=value,stored=reg!='ONE_SHOT')

    def read(self,reg,transaction='single',auto_increment=False):
        return self.read_masked(reg,255,transaction,auto_increment)

    def read_masked(self,reg,mask,transaction='single',auto_increment=False):
        unsigned(mask,255)
        if not mask or type(reg) is not str or reg not in self.values or reg=='ONE_SHOT':
            raise OutsideContract('Unknown register/empty mask/write-only action read')
        if transaction!='single' or type(auto_increment) is not bool or auto_increment:
            raise OutsideContract('Only direct single-byte observations implemented')
        if self.known[reg] & mask != mask: raise OutsideContract('Unknown bits must not be returned as zero')
        before=self.values[reg] & mask
        if reg=='STATUS':
            clearable=(4,) if self.field('CONFIG','ALERT_THERM2') else (0x40,0x20,0x10,8,4)
            for m in clearable:
                if self.retired[m] is True:
                    self.values[reg] &= ~m;self.known[reg] |= m
        pairs={'TEMP_LOCAL_HIGH':'TEMP_LOCAL_LOW','TEMP_LOCAL_LOW':'TEMP_LOCAL_HIGH',
            'TEMP_REMOTE_HIGH':'TEMP_REMOTE_LOW','TEMP_REMOTE_LOW':'TEMP_REMOTE_HIGH'}
        if self.pending_pair==reg:
            self.pending_pair=None
        else:
            self.pending_pair=pairs.get(reg)
        self._trace('read',register=reg,mask=mask,value=before,transaction=transaction,auto_increment=auto_increment)
        return before

    def alert_pin(self):
        if self.field('CONFIG','ALERT_THERM2'):
            if any(v is None for v in self.therm2_state.values()): raise OutsideContract('Unknown THERM2 state')
            return 0 if any(self.therm2_state.values()) else 1
        if self.field('CONFIG','MASK1'): return 1
        if self.alert_latched is None: raise OutsideContract('Unknown boot ALERT latch')
        return 0 if self.alert_latched else 1

    def therm_pin(self):
        if self.known['STATUS'] & 3 != 3: raise OutsideContract('Unknown THERM state')
        return 0 if self.values['STATUS'] & 3 else 1

    def _hysteretic(self,mask,q,limit):
        if q>limit: value=True
        elif q<=limit-self.values['THERM_HYSTERESIS']*16: value=False
        elif self.known['STATUS'] & mask: value=bool(self.values['STATUS'] & mask)
        else: return
        self.values['STATUS']=(self.values['STATUS'] & ~mask) | (mask if value else 0)
        self.known['STATUS'] |= mask

    def _limits(self,extended):
        byte=lambda v:decode(v<<4,extended,False)
        return {'local':(byte(self.values['LOCAL_LOW_LIMIT']),byte(self.values['LOCAL_HIGH_LIMIT'])),
            'remote':(decode((self.values['REMOTE_LOW_LIMIT_HIGH']<<4)|(self.values['REMOTE_LOW_LIMIT_LOW']>>4),extended,False),
                      decode((self.values['REMOTE_HIGH_LIMIT_HIGH']<<4)|(self.values['REMOTE_HIGH_LIMIT_LOW']>>4),extended,False)),
            'therm_local':byte(self.values['LOCAL_THERM_LIMIT']),'therm_remote':byte(self.values['REMOTE_THERM_LIMIT'])}

    def _completed(self,local_code,remote_code,remote_open):
        if self.phase!='converting' or type(remote_open) is not bool: raise OutsideContract('No conversion or malformed fault qualifier')
        if self.pending_pair is not None:
            raise OutsideContract('Concurrent ADC updates inside an unfinished byte snapshot are outside this profile')
        extended=bool(self.field('CONFIG','RANGE'))
        local=decode(local_code,extended)
        if remote_open:
            if remote_code is not None: raise OutsideContract('Open remote channel needs no fabricated result')
            remote=None
        else: remote=decode(remote_code,extended)
        limits=self._limits(extended)
        if any(lo>=hi for lo,hi in (limits['local'],limits['remote'])): raise OutsideContract('Ordered limits required')
        therm2=bool(self.field('CONFIG','ALERT_THERM2'))
        for channel,q,hi_mask,lo_mask,th_mask in [('local',local,0x40,0x20,1),('remote',remote,0x10,8,2)]:
            lo,hi=limits[channel]
            if q is None:
                self.retired[hi_mask]=self.retired[lo_mask]=None
                # An already known latched1 cannot disappear merely because
                # the newest remote comparison has become unknown.
                retain=0 if therm2 else self.known['STATUS'] & self.values['STATUS'] & (hi_mask|lo_mask)
                self.known['STATUS'] &= ~((hi_mask|lo_mask|th_mask) & ~retain)
                if therm2: self.therm2_state[hi_mask]=None
                continue
            inside=lo<=q<=hi
            self.retired[hi_mask]=self.retired[lo_mask]=inside
            if therm2:
                self._hysteretic(hi_mask,q,hi)
                self.therm2_state[hi_mask]=bool(self.values['STATUS'] & hi_mask) if self.known['STATUS'] & hi_mask else None
                self.known['STATUS'] &= ~lo_mask  # Low flag outcome not asserted in THERM2.
            else:
                for m,violated in ((hi_mask,q>hi),(lo_mask,q<lo)):
                    if violated: self.values['STATUS']|=m;self.known['STATUS']|=m
            self._hysteretic(th_mask,q,limits['therm_'+channel])
        self.retired[4]=not remote_open
        if remote_open: self.values['STATUS']|=4;self.known['STATUS']|=4
        self._field('TEMP_LOCAL_HIGH','LT_HIGH',local_code>>4)
        self._field('TEMP_LOCAL_LOW','LT_LOW',local_code&15)
        if remote_open:
            self.known['TEMP_REMOTE_HIGH']=self.known['TEMP_REMOTE_LOW']=0
        else:
            self._field('TEMP_REMOTE_HIGH','RT_HIGH',remote_code>>4)
            self._field('TEMP_REMOTE_LOW','RT_LOW',remote_code&15)
        if not therm2 and (remote_open or local>limits['local'][1] or local<limits['local'][0]
            or remote is not None and (remote>limits['remote'][1] or remote<limits['remote'][0])):
            self.alert_latched=True
        self._field('STATUS','BUSY',0);self.phase='idle';self.one_shot=False

    def event(self,name,**payload):
        shapes={'conversion_started':set(),'conversion_completed':{'local_code','remote_code','remote_open'},
            'qualified_remote_open_detected':set(),
            'qualified_alert_service_completed':set(),'general_call_reset_completed':{'second_byte'}}
        if type(name) is not str or name not in shapes or set(payload)!=shapes[name]: raise OutsideContract('Unknown/malformed event')
        snapshot=copy.deepcopy(vars(self))
        try:
            if name=='conversion_started': self._start()
            elif name=='conversion_completed': self._completed(**payload)
            elif name=='qualified_remote_open_detected':
                if self.phase!='converting': raise OutsideContract('Fault detector event requires active remote conversion')
                self._field('STATUS','OPEN',1);self.retired[4]=False
                if not self.field('CONFIG','ALERT_THERM2'): self.alert_latched=True
            elif name=='qualified_alert_service_completed':
                if (self.phase!='idle' or self.field('CONFIG','ALERT_THERM2') or self.known['STATUS'] & 0x7C != 0x7C
                    or self.values['STATUS'] & 0x7C or not all(v is True for v in self.retired.values())):
                    raise OutsideContract('Service needs retired causes and already cleared known flags')
                self.alert_latched=False
            else:
                unsigned(payload['second_byte'],255)
                if payload['second_byte']==6:
                    trace=self.trace;profile=self.profile;self.__init__(profile=profile);self.trace=trace
        except OutsideContract:
            self.__dict__.clear();self.__dict__.update(snapshot);raise
        self._trace('event',name=name,payload=payload)
