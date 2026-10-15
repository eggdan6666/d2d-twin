"""Source-bounded INA3221 events, not ADC/filter/electrical timing execution.

read_masked projects a complete abstract 16-bit read. Snapshot then clear is a
linearized protocol convention without interleaving, not partial-byte timing.
Common TCF numeric reset/polarity and subset-disabled CONFIG/CVRF are unknown.
"""
import copy
class OutsideContract(ValueError): pass
def integer(v,maximum=0xFFFF):
    if type(v) is not int or not 0<=v<=maximum: raise OutsideContract('Exact unsigned integer required')
    return v
DEFAULTS={'CONFIG':0x7127,**{k:0 for i in (1,2,3) for k in ('SHUNT'+str(i),'VBUS'+str(i))},
          **{k:0x7FF8 for i in (1,2,3) for k in ('CRIT'+str(i),'WARN'+str(i))},
          'SHUNT_SUM':0,'SHUNT_SUM_LIMIT':0,'MASK_ENABLE':2,'PV_UPPER':0x2710,'PV_LOWER':0x2328,
          'MANUF_ID':0x5449,'DIE_ID':0x3220}
CVRF=1; TCF=2; PVF=4; READ_CLEAR=0x03F9; CONTROL=0x7C00
AVG_FACTORS=(1,4,16,64,128,256,512,1024)
TIME_US=(140,204,332,588,1100,2116,4156,8244)
class Semantics:
    def __init__(self,chip='INA3221',profile='common_source'):
        if type(chip) is not str or chip!='INA3221' or type(profile) is not str or profile not in (
            'common_source','bitmap_pin_candidate','bitmap_active_high_candidate'):
            raise OutsideContract('Unknown chip/profile')
        self.chip=chip;self.profile=profile;self.values=dict(DEFAULTS)
        self.known={r:0xFFFF for r in self.values};self.known['SHUNT_SUM_LIMIT']=0
        if profile=='common_source':self.known['MASK_ENABLE'] &= ~TCF
        self.configuration_epoch=0;self.sequence_id=0;self.startup_epoch=0
        self.phase='idle';self.active_sequence=None;self.completed_results=set()
        self.operating_state='continuous_idle'
        self.tc_phase='waiting_channel1';self.tc_cycles=0;self.tc_enabled=True
        self.tc_pin_logical_level=True;self.pv_pin_logical_level=False
        self.trace=[]
    def _trace(self,op,**data):self.trace.append({'chip':self.chip,'profile':self.profile,'op':op,**copy.deepcopy(data)})
    def _register(self,reg):
        if type(reg) is not str or reg not in self.values:raise OutsideContract('Unknown register')
        if self.phase=='reset_pending':raise OutsideContract('Pending reset has no access/observation oracle')
    def _flag(self,mask,v):
        self.values['MASK_ENABLE']=(self.values['MASK_ENABLE']&~mask)|(mask if v else 0)
        self.known['MASK_ENABLE'] |= mask
    def enabled_channels(self):return tuple(i for i,b in ((1,0x4000),(2,0x2000),(3,0x1000)) if self.values['CONFIG']&b)
    def required_results(self):
        mode=self.values['CONFIG']&7
        kinds=() if mode in (0,4) else ('shunt',) if mode in (1,5) else ('bus',) if mode in (2,6) else ('shunt','bus')
        return tuple((i,k) for i in self.enabled_channels() for k in kinds)
    def nominal_settings(self):
        self._register('CONFIG');v=self.values['CONFIG']
        return {'filter_factor':AVG_FACTORS[(v>>9)&7],'bus_conversion_time_us':TIME_US[(v>>6)&7],
                'shunt_conversion_time_us':TIME_US[(v>>3)&7]}
    def read(self,reg):return self.read_masked(reg,0xFFFF)
    def read_masked(self,reg,mask):
        self._register(reg);integer(mask)
        if not mask or self.known[reg]&mask != mask:raise OutsideContract('Empty mask or unknown observation')
        observed=self.values[reg]&mask
        if reg=='MASK_ENABLE':
            self.values[reg] &= ~READ_CLEAR
            self.known[reg] |= READ_CLEAR
            # TCF and PVF are not silently folded into the generic flag-clear wording.
        self._trace('read',register=reg,mask=mask,result=observed,convention='complete_word_preclear_projection')
        return observed
    def _begin(self):
        if not self.required_results():raise OutsideContract('No enabled measurement sequence')
        self.sequence_id += 1;self.active_sequence=(self.configuration_epoch,self.sequence_id)
        self.completed_results=set();self.phase='converting'
        self.operating_state='triggered_conversion' if self.values['CONFIG']&7 in (1,2,3) else 'continuous_conversion'
        self.known['SHUNT_SUM']=0 # summation datapath is not implemented by this task.
    def write(self,reg,value):
        if self.phase=='reset_pending':
            if type(reg) is not str or reg!='CONFIG':raise OutsideContract('Only a newer reset request admitted while pending')
            integer(value)
            if not value&0x8000:raise OutsideContract('Ordinary writes excluded while pending')
        else:self._register(reg);integer(value)
        if reg=='CONFIG':
            mode=value&7
            self.configuration_epoch += 1;self.active_sequence=None;self.completed_results=set()
            if value&0x8000:
                self.phase='reset_pending';self.operating_state='reset_pending'
            else:
                self.values[reg]=value;self.known[reg]=0xFFFF
                if mode not in (0,4):
                    if value&0x7000==0x7000:self._flag(CVRF,0)
                    else:self.known['MASK_ENABLE'] &= ~CVRF
                if self.tc_phase in ('waiting_channel1','waiting_channel2'):
                    self.tc_enabled=False;self.tc_phase='disabled'
                    self.known['MASK_ENABLE'] &= ~TCF
                if mode in (0,4):self.phase='idle';self.operating_state='powerdown'
                elif not value&0x7000:self.phase='disabled';self.operating_state='all_channels_disabled'
                elif mode in (1,2,3):self._begin()
                else:self.phase='idle';self.operating_state='continuous_idle'
        elif reg=='MASK_ENABLE':
            if value&~CONTROL:raise OutsideContract('Only declared control inputs; status/reserved writes excluded')
            self.values[reg]=(self.values[reg]&~CONTROL)|(value&CONTROL)
            self.known[reg] &= ~0x8000 # nondefault reserved access is not a target.
        elif reg in ('CRIT1','CRIT2','CRIT3','WARN1','WARN2','WARN3','PV_UPPER','PV_LOWER'):
            if value&7 or (reg in ('PV_UPPER','PV_LOWER') and value&0x8000):
                raise OutsideContract('Only documented aligned limits; PV sign is fixed zero')
            self.values[reg]=value;self.known[reg]=0xFFFF
        else:raise OutsideContract('Measurement/identity/ambiguous 0Eh write outside scope')
        self._trace('write',register=reg,value=value)
    def event(self,name,**payload):
        if type(name) is not str:raise OutsideContract('Exact event identity required')
        bindings={'configuration_epoch','sequence_id'}
        requirements={'reset_completed':{'request_epoch'},'power_cycle_completed':set(),'conversion_started':set(),
            'qualified_filtered_result':bindings|{'channel','kind','encoded_word','filter_processing_complete'},
            'whole_sequence_completed':bindings|{'all_enabled_conversions_complete'},
            'tc_channel1_threshold_qualified':{'startup_epoch','channel1_at_threshold'},
            'tc_cycle_qualified':{'startup_epoch','cycle_index','all_three_channels_complete','channel2_at_threshold'},
            'qualified_pv_detection_complete':{'startup_epoch','configuration_epoch','high','detection_sequence_complete'}}
        if name not in requirements or set(payload)!=requirements[name]:raise OutsideContract('Unknown event/shape')
        if self.phase=='reset_pending' and name not in ('reset_completed','power_cycle_completed'):
            raise OutsideContract('Pending reset requires qualification')
        if name=='reset_completed' and self.phase!='reset_pending':raise OutsideContract('No reset pending')
        if name=='reset_completed' and integer(payload['request_epoch'],2**63-1)!=self.configuration_epoch:
            raise OutsideContract('Old reset request cannot complete a newer reset epoch')
        if name in ('qualified_filtered_result','whole_sequence_completed'):
            epoch=integer(payload['configuration_epoch'],2**63-1);seq=integer(payload['sequence_id'],2**63-1)
            if self.phase!='converting' or self.active_sequence!=(epoch,seq):raise OutsideContract('Stale/inactive sequence')
        if name in ('tc_channel1_threshold_qualified','tc_cycle_qualified','qualified_pv_detection_complete'):
            if integer(payload['startup_epoch'],2**63-1)!=self.startup_epoch:raise OutsideContract('Stale startup epoch')
        if name in ('reset_completed','power_cycle_completed'):
            trace=self.trace;profile=self.profile;cfg=self.configuration_epoch;seq=self.sequence_id
            startup=self.startup_epoch+1;pv=self.pv_pin_logical_level
            self.__init__(profile=profile);self.trace=trace;self.configuration_epoch=cfg;self.sequence_id=seq
            self.startup_epoch=startup
            if name=='reset_completed':
                self.pv_pin_logical_level=pv;self.known['MASK_ENABLE'] &= ~PVF
        elif name=='conversion_started':
            if self.phase!='idle' or self.values['CONFIG']&7 not in (5,6,7) or not self.required_results():
                raise OutsideContract('No idle continuous enabled sequence')
            self._begin()
        elif name=='qualified_filtered_result':
            channel=integer(payload['channel'],3);kind=payload['kind'];word=integer(payload['encoded_word'])
            if type(kind) is not str or kind not in ('shunt','bus') or (channel,kind) not in self.required_results():
                raise OutsideContract('Disabled or unselected channel/signal')
            if (channel,kind) in self.completed_results or word&7:
                raise OutsideContract('Duplicate conversion or invalid result alignment')
            if type(payload['filter_processing_complete']) is not bool or not payload['filter_processing_complete']:
                raise OutsideContract('Result must be already qualified after corresponding filter processing')
            reg=('SHUNT' if kind=='shunt' else 'VBUS')+str(channel)
            self.values[reg]=word;self.known[reg]=0xFFFF;self.completed_results.add((channel,kind))
        elif name=='whole_sequence_completed':
            if (type(payload['all_enabled_conversions_complete']) is not bool or not payload['all_enabled_conversions_complete']
                or self.completed_results!=set(self.required_results())):
                raise OutsideContract('Every selected conversion required, no vacuous completion')
            self._flag(CVRF,1);self.phase='idle';self.active_sequence=None
            self.operating_state='triggered_sleep' if self.values['CONFIG']&7 in (1,2,3) else 'continuous_idle'
        elif name=='qualified_pv_detection_complete':
            if type(payload['high']) is not bool or type(payload['detection_sequence_complete']) is not bool or not payload['detection_sequence_complete']:
                raise OutsideContract('Qualified PV detection result required')
            if (integer(payload['configuration_epoch'],2**63-1)!=self.configuration_epoch or self.values['CONFIG']!=0x7127
                or self.values['PV_UPPER']!=0x2710 or self.values['PV_LOWER']!=0x2328):
                raise OutsideContract('Supporting PV qualifier only under current default detector configuration')
            self.pv_pin_logical_level=payload['high'];self._flag(PVF,payload['high'])
        elif name=='tc_channel1_threshold_qualified':
            if (not self.tc_enabled or self.tc_phase!='waiting_channel1' or self.values['CONFIG']!=0x7127
                or type(payload['channel1_at_threshold']) is not bool or not payload['channel1_at_threshold']):
                raise OutsideContract('TC requires qualified CH1 threshold in default startup profile')
            self.tc_phase='waiting_channel2';self.tc_cycles=0
        else:
            if (not self.tc_enabled or self.tc_phase!='waiting_channel2' or self.values['CONFIG']!=0x7127
                or type(payload['all_three_channels_complete']) is not bool or not payload['all_three_channels_complete']
                or type(payload['channel2_at_threshold']) is not bool):
                raise OutsideContract('TC requires complete default three-channel cycle qualification')
            if integer(payload['cycle_index'],4)!=self.tc_cycles+1:
                raise OutsideContract('TC cycle evidence must be next unique qualified cycle')
            self.tc_cycles += 1
            if payload['channel2_at_threshold']:
                self.tc_phase='complete_valid'
            elif self.tc_cycles==4:
                self.tc_phase='complete_timeout';self.tc_pin_logical_level=False
                if self.profile=='common_source':self.known['MASK_ENABLE'] &= ~TCF
                else:self._flag(TCF,self.profile=='bitmap_active_high_candidate')
        self._trace('event',name=name,payload=payload)
