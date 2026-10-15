"""Source-bounded INA226 digital events; no silicon/ADC/calibration timing model.

read_masked projects one complete 16-bit register transaction onto a mask;
it is not a partial-byte/bit read. Snapshot then clear is a linearized benchmark
convention with no concurrent event interleaving, not I2C byte-level clear timing.
Unknown masks are epistemic and do not imply zero-valued physical bits.
"""
import copy

class OutsideContract(ValueError):
    """Stimulus or observation outside this declared benchmark profile."""

def integer(value, maximum=0xFFFF):
    if type(value) is not int or not 0 <= value <= maximum:
        raise OutsideContract('Exact unsigned integer required')
    return value

DEFAULTS={'CONFIG':0x4127,'SHUNT_VOLTAGE':0,'BUS_VOLTAGE':0,'POWER':0,
          'CURRENT':0,'CALIBRATION':0,'MASK_ENABLE':0,'ALERT_LIMIT':0,
          'MANUFACTURER_ID':0x5449,'DIE_ID':0}
RESERVED={'CONFIG':0x7000,'CALIBRATION':0x8000,'MASK_ENABLE':0x03E0}
RESERVED_DEFAULT={'CONFIG':0x4000,'CALIBRATION':0,'MASK_ENABLE':0}
AFF=0x10
CVRF=0x08
CONTROL=0xFC03
FUNCTIONS={'SOL':0x8000,'SUL':0x4000,'BOL':0x2000,'BUL':0x1000,'POL':0x0800}
AVG_SAMPLES=(1,4,16,64,128,256,512,1024)
TIME_US=(140,204,332,588,1100,2116,4156,8244)

class Semantics:
    def __init__(self, chip='INA226', profile='common_source'):
        if type(chip) is not str or chip!='INA226' or type(profile) is not str or profile not in (
            'common_source','config_clear_candidate','register_detail_candidate'):
            raise OutsideContract('Unknown chip/profile')
        self.chip=chip; self.profile=profile
        self.values=dict(DEFAULTS); self.known={r:0xFFFF for r in DEFAULTS}
        self.known['DIE_ID']=0 # Table7-1 documents 2260 or2261; no variant selected.
        self.phase='idle'; self.operating_state='continuous_idle'
        self.staged=None; self.alert_history=False; self.calibration_ever_programmed=False
        self.configuration_epoch=0; self.sequence_id=0; self.active_sequence=None
        self.trace=[]

    def _trace(self, op, **data):
        self.trace.append({'chip':self.chip,'profile':self.profile,'op':op,**copy.deepcopy(data)})

    def _register(self, reg):
        if type(reg) is not str or reg not in self.values: raise OutsideContract('Unknown register')
        if self.phase=='reset_pending': raise OutsideContract('No observation/access while reset pending')

    def _set_flag(self, mask, value):
        self.values['MASK_ENABLE']=(self.values['MASK_ENABLE']&~mask)|(mask if value else 0)
        self.known['MASK_ENABLE'] |= mask

    def selected_function(self):
        return next((n for n,b in FUNCTIONS.items() if self.values['MASK_ENABLE']&b),None)

    def nominal_settings(self):
        self._register('CONFIG')
        v=self.values['CONFIG']
        return {'samples':AVG_SAMPLES[(v>>9)&7],
                'bus_conversion_time_us':TIME_US[(v>>6)&7],
                'shunt_conversion_time_us':TIME_US[(v>>3)&7]}

    def read(self, reg): return self.read_masked(reg,0xFFFF)

    def read_masked(self, reg, mask):
        self._register(reg); integer(mask)
        if not mask: raise OutsideContract('Empty observation mask')
        if self.known[reg]&mask != mask: raise OutsideContract('Observation contains unknown bits')
        observed=self.values[reg]&mask
        if reg=='MASK_ENABLE':
            self._set_flag(CVRF,0)
            if self.values[reg]&1: self._set_flag(AFF,0)
        self._trace('read',register=reg,mask=mask,result=observed,
                    observation_convention='linearized_preclear_snapshot')
        return observed

    def write(self, reg, value):
        self._register(reg); integer(value)
        if reg not in ('CONFIG','CALIBRATION','MASK_ENABLE','ALERT_LIMIT'):
            raise OutsideContract('Measurement/identity writes not in this profile')
        if reg in RESERVED and value&RESERVED[reg] != RESERVED_DEFAULT[reg]:
            raise OutsideContract('Reserved access excluded; only POR-baseline input admitted')
        if reg=='CONFIG':
            mode=value&7
            if not value&0x8000 and mode not in (0,3,4,7):
                raise OutsideContract('Single-channel modes not implemented in bounded profile')
            if value&0x8000:
                self.phase='reset_pending'; self.operating_state='reset_pending'; self.staged=None
                self.active_sequence=None
            else:
                self.values[reg]=value
                self.known[reg]=0x8FFF # reserved POR knownness is not a write-retention guarantee.
                self.staged=None
                if mode not in (0,4): self._set_flag(CVRF,0)
                if self.values['MASK_ENABLE']&1:
                    if self.profile=='common_source': self.known['MASK_ENABLE'] &= ~AFF
                    elif self.profile=='config_clear_candidate': self._set_flag(AFF,0)
                    # register_detail_candidate preserves existing flag knowledge explicitly.
                self.phase='converting' if mode==3 else 'idle'
                self.operating_state=('triggered_conversion' if mode==3 else
                                      'powerdown' if mode in (0,4) else 'continuous_idle')
            self.configuration_epoch += 1
            if not value&0x8000 and mode==3:
                self.sequence_id += 1
                self.active_sequence=(self.configuration_epoch,self.sequence_id)
            else: self.active_sequence=None
        elif reg=='CALIBRATION':
            self.values[reg]=value; self.known[reg]=0x7FFF
            if value: self.calibration_ever_programmed=True
            if self.calibration_ever_programmed:
                self.known['CURRENT']=self.known['POWER']=0
        elif reg=='MASK_ENABLE':
            if value&0x001C:
                raise OutsideContract('Software status-bit writes not modelled; write zeros to status positions')
            old=self.values[reg]&CONTROL
            if self.alert_history and (value&CONTROL)!=old:
                raise OutsideContract('Alert-control changes with alert history not source-closed')
            self.values[reg]=(self.values[reg]&0x001C)|(value&CONTROL)
            self.known[reg] &= ~RESERVED[reg]
        else:
            self.values[reg]=value; self.known[reg]=0xFFFF
        self._trace('write',register=reg,value=value)

    def event(self, name, **payload):
        if type(name) is not str: raise OutsideContract('Exact event identity required')
        requirements={'reset_completed':set(),'conversion_started':set(),
                      'qualified_results_staged':{'shunt_word','bus_code','configuration_epoch','sequence_id'},
                      'whole_sequence_completed':{'configuration_epoch','sequence_id','conversions_complete',
                                                  'averaging_complete','multiplication_complete'},
                      'qualified_alert_conversion':{'function','fault','configuration_epoch','sequence_id'}}
        if name not in requirements or set(payload)!=requirements[name]:
            raise OutsideContract('Unknown event or payload shape')
        if self.phase=='reset_pending':
            if name!='reset_completed': raise OutsideContract('Pending reset must complete explicitly')
        elif name=='reset_completed': raise OutsideContract('No reset request pending')
        if name in ('qualified_results_staged','whole_sequence_completed','qualified_alert_conversion'):
            epoch=integer(payload['configuration_epoch'],2**63-1)
            sequence=integer(payload['sequence_id'],2**63-1)
            if self.active_sequence is None or (epoch,sequence)!=self.active_sequence:
                raise OutsideContract('Completion/fault evidence must bind current configuration and sequence')
        if name=='reset_completed':
            trace=self.trace; profile=self.profile
            epoch=self.configuration_epoch; sequence=self.sequence_id
            self.__init__(profile=profile); self.trace=trace
            self.configuration_epoch=epoch; self.sequence_id=sequence
        elif name=='conversion_started':
            if self.phase!='idle' or self.values['CONFIG']&7!=7:
                raise OutsideContract('Only idle both-channel continuous start admitted')
            self.phase='converting'; self.operating_state='continuous_conversion'; self.staged=None
            self.sequence_id += 1
            self.active_sequence=(self.configuration_epoch,self.sequence_id)
        elif name=='qualified_results_staged':
            if self.phase!='converting': raise OutsideContract('No conversion sequence available')
            shunt=integer(payload['shunt_word']); bus=integer(payload['bus_code'],0x7FFF)
            # Values already carry qualified averaged digital interpretation. No ADC/average computation.
            self.staged=(shunt,bus); self.phase='results_staged'
        elif name=='whole_sequence_completed':
            if self.phase!='results_staged': raise OutsideContract('Need staged results and full completion qualification')
            if any(type(payload[k]) is not bool or not payload[k] for k in
                   ('conversions_complete','averaging_complete','multiplication_complete')):
                raise OutsideContract('Require externally qualified conversions, averaging and multiplication completion')
            shunt,bus=self.staged
            self.values['SHUNT_VOLTAGE']=shunt; self.values['BUS_VOLTAGE']=bus
            self.known['SHUNT_VOLTAGE']=self.known['BUS_VOLTAGE']=0xFFFF
            self._set_flag(CVRF,1)
            self.known['MASK_ENABLE'] &= ~4 # OVF lifetime/math cannot be inferred from missing event.
            self.phase='idle'; self.staged=None
            self.active_sequence=None
            self.operating_state='triggered_sleep' if self.values['CONFIG']&7==3 else 'continuous_idle'
        else:
            function=payload['function']; fault=payload['fault']
            if type(function) is not str or function not in FUNCTIONS or type(fault) is not bool:
                raise OutsideContract('Qualified alert function and boolean required')
            if self.phase not in ('converting','results_staged') or function!=self.selected_function():
                raise OutsideContract('Requires active conversion and selected priority function')
            if fault:
                self._set_flag(AFF,1); self.alert_history=True
            elif not self.values['MASK_ENABLE']&1:
                self._set_flag(AFF,0)
            # Latch retains known/unknown history on nonfault conversion; no synthetic deassertion.
        self._trace('event',name=name,payload=payload)
