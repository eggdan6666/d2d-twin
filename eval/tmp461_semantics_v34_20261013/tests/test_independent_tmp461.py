"""Source-derived TMP461 checks; no physical SMBus/ADC certification."""
import copy
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('independent_tmp461_v34', ROOT / 'tmp461.py')
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
Semantics, OutsideContract = runtime.Semantics, runtime.OutsideContract
sys.path.insert(0, str(ROOT))


def reject_atomic(s, operation):
    before = copy.deepcopy(vars(s))
    with pytest.raises(OutsideContract):
        operation()
    assert vars(s) == before


def code(celsius):
    return (celsius * 16) & 0xFFF


def measure(s, local=25, remote=25, opened=False):
    s.event('conversion_started')
    s.event('conversion_completed', local_code=code(local), remote_code=None if opened else code(remote), remote_open=opened)


def limits(s):
    # Explicit conversion and cause-qualified STATUS read remove unknown old latches.
    measure(s)
    assert s.read_masked('STATUS', 0x80) == 0
    s.write('LOCAL_HIGH_LIMIT', 50)
    s.write('LOCAL_LOW_LIMIT', 10)
    s.write('REMOTE_HIGH_LIMIT_HIGH', 50)
    s.write('REMOTE_HIGH_LIMIT_LOW', 0)
    s.write('REMOTE_LOW_LIMIT_HIGH', 10)
    s.write('REMOTE_LOW_LIMIT_LOW', 0)
    s.write('LOCAL_THERM_LIMIT', 70)
    s.write('REMOTE_THERM_LIMIT', 70)
    s.write('THERM_HYSTERESIS', 10)
    measure(s)
    assert s.read_masked('STATUS',0x80) == 0


@pytest.mark.parametrize('mask', [1,2,4,8,16,32,64,128,255])
def test_por_status_unknown_not_fabricated(mask):
    s = Semantics()
    reject_atomic(s, lambda: s.read_masked('STATUS', mask))


def test_one_shot_is_write_only_no_retained_reset_byte():
    s = Semantics()
    reject_atomic(s, lambda: s.read('ONE_SHOT'))
    reject_atomic(s, lambda: s.read_masked('ONE_SHOT', 255))


@pytest.mark.parametrize('byte', [0,1,6,128,255])
def test_any_byte_starts_one_shot_in_shutdown_and_returns_shutdown(byte):
    s = Semantics()
    s.write('CONFIG', 0x40)
    s.write('ONE_SHOT', byte)
    assert s.read_masked('STATUS', 0x80) == 0x80
    reject_atomic(s, lambda: s.event('conversion_started'))
    s.event('conversion_completed', local_code=code(25), remote_code=code(25), remote_open=False)
    assert s.read_masked('STATUS', 0x80) == 0
    assert s.read('CONFIG') & 0x40 == 0x40
    reject_atomic(s, lambda: s.event('conversion_started'))
    reject_atomic(s, lambda: s.read('ONE_SHOT'))


def test_one_shot_during_continuous_or_running_rejects_atomically():
    s = Semantics()
    reject_atomic(s, lambda: s.write('ONE_SHOT', 0))
    s.write('CONFIG', 0x40)
    s.write('ONE_SHOT', 0)
    reject_atomic(s, lambda: s.write('ONE_SHOT', 255))


def test_sd_does_not_abort_current_conversion():
    s = Semantics()
    s.event('conversion_started')
    s.write('CONFIG', 0x40)
    assert s.read_masked('STATUS', 0x80) == 0x80
    s.event('conversion_completed', local_code=code(30), remote_code=code(35), remote_open=False)
    assert s.read_masked('STATUS', 0x80) == 0
    assert s.read('TEMP_LOCAL_HIGH') == 30
    reject_atomic(s, lambda: s.event('conversion_started'))


@pytest.mark.parametrize('local,remote,opened,mask', [(60,25,False,0x40),(0,25,False,0x20),(25,60,False,0x10),(25,0,False,0x08),(25,25,True,0x04)])
def test_each_active_alert_cause_survives_read_then_clears_after_recovery(local,remote,opened,mask):
    s = Semantics()
    limits(s)
    measure(s,local,remote,opened)
    assert s.read_masked('STATUS',mask) == mask
    assert s.read_masked('STATUS',mask) == mask
    measure(s)
    assert s.read_masked('STATUS',mask) == mask
    assert s.read_masked('STATUS',mask) == 0


def test_all_five_nonzero_latches_return_preclear_then_clear():
    s = Semantics()
    limits(s)
    measure(s,60,60)
    measure(s,0,0)
    measure(s,25,25,True)
    measure(s)
    assert s.read('STATUS') == 0x7C
    assert s.read('STATUS') == 0


def test_masked_busy_observation_still_clears_all_eligible_flags():
    s = Semantics()
    limits(s)
    measure(s,60,60)
    measure(s)
    assert s.read_masked('STATUS',0x80) == 0
    assert s.read_masked('STATUS',0x7C) == 0


def test_temperature_and_config_reads_do_not_clear_recovered_alert_flags():
    s = Semantics()
    limits(s)
    measure(s,60,60)
    measure(s)
    assert s.read('TEMP_LOCAL_HIGH') == 25
    assert s.read('TEMP_REMOTE_HIGH') == 25
    assert s.read('CONFIG') == 0
    assert s.read_masked('STATUS',0x50) == 0x50


@pytest.mark.parametrize('local,remote,mask',[(-1,25,0x20),(25,-1,0x08)])
def test_signed_negative_temperature_causes_correct_low_flag(local,remote,mask):
    s = Semantics()
    limits(s)
    measure(s,local,remote)
    assert s.read_masked('STATUS',mask) == mask


def test_fractional_temperature_register_bytes_are_correct():
    s = Semantics()
    s.event('conversion_started')
    s.event('conversion_completed',local_code=161,remote_code=162,remote_open=False)
    assert s.read('TEMP_LOCAL_HIGH') == 10
    assert s.read('TEMP_LOCAL_LOW') == 0x10
    assert s.read('TEMP_REMOTE_HIGH') == 10
    assert s.read('TEMP_REMOTE_LOW') == 0x20


@pytest.mark.parametrize('first,partner',[('TEMP_LOCAL_HIGH','TEMP_LOCAL_LOW'),('TEMP_LOCAL_LOW','TEMP_LOCAL_HIGH'),('TEMP_REMOTE_HIGH','TEMP_REMOTE_LOW'),('TEMP_REMOTE_LOW','TEMP_REMOTE_HIGH')])
def test_unfinished_temperature_pair_guards_concurrent_completion(first,partner):
    s = Semantics()
    limits(s)
    s.read(first)
    s.event('conversion_started')
    payload=dict(local_code=code(30),remote_code=code(35),remote_open=False)
    reject_atomic(s,lambda:s.event('conversion_completed',**payload))
    s.read(partner)
    s.event('conversion_completed',**payload)
    assert s.read('TEMP_LOCAL_HIGH') == 30


def test_read_other_register_abandons_temperature_pair_guard():
    s = Semantics()
    limits(s)
    s.read('TEMP_REMOTE_HIGH')
    s.read('CONFIG')
    measure(s,30,35)
    assert s.read('TEMP_REMOTE_HIGH') == 35


def test_therm_pin_is_live_or_of_channels():
    s = Semantics()
    limits(s)
    assert s.therm_pin() == 1
    measure(s,80,25)
    assert s.therm_pin() == 0
    measure(s,60,80)
    assert s.therm_pin() == 0
    measure(s,60,60)
    assert s.therm_pin() == 1


def test_status_clear_does_not_ack_alert_latch():
    s = Semantics()
    limits(s)
    s.event('qualified_alert_service_completed')
    assert s.alert_pin() == 1
    measure(s,60,25)
    assert s.alert_pin() == 0
    reject_atomic(s,lambda:s.event('qualified_alert_service_completed'))
    assert s.alert_pin() == 0
    measure(s)
    assert s.read_masked('STATUS',0x40) == 0x40
    assert s.read_masked('STATUS',0x40) == 0
    assert s.alert_pin() == 0
    s.event('qualified_alert_service_completed')
    assert s.alert_pin() == 1


def test_mask_disables_pin_but_preserves_status_and_latch():
    s = Semantics()
    limits(s)
    s.write('CONFIG',0x80)
    measure(s,60,25)
    assert s.alert_pin() == 1
    assert s.read_masked('STATUS',0x40) == 0x40
    s.write('CONFIG',0)
    assert s.alert_pin() == 0


def test_general_call_reset_aborts_and_restores_unknown_dynamic_state():
    s = Semantics()
    limits(s)
    measure(s,80,80,True)
    s.write('CONV_RATE',5)
    s.event('conversion_started')
    s.event('general_call_reset_completed',second_byte=6)
    assert s.read('CONFIG') == 0
    assert s.read('CONV_RATE') == 8
    assert s.read('REMOTE_HIGH_LIMIT_LOW') == 0xF0
    assert s.read('LOCAL_LOW_LIMIT') == 0x80
    reject_atomic(s,lambda:s.read('STATUS'))
    reject_atomic(s,lambda:s.read('ONE_SHOT'))
    reject_atomic(s,lambda:s.event('conversion_completed',local_code=code(25),remote_code=code(25),remote_open=False))


def test_unknown_open_result_cannot_be_returned_as_numeric_remote_temperature():
    s = Semantics()
    limits(s)
    measure(s,25,25,True)
    assert s.read_masked('STATUS',4) == 4
    reject_atomic(s,lambda:s.read('TEMP_REMOTE_HIGH'))
    reject_atomic(s,lambda:s.read_masked('STATUS',2))


def test_qualified_open_detection_requires_converting_and_sets_flag_without_fake_temperature():
    s = Semantics()
    limits(s)
    reject_atomic(s,lambda:s.event('qualified_remote_open_detected'))
    s.event('conversion_started')
    s.event('qualified_remote_open_detected')
    assert s.read_masked('STATUS',4) == 4
    assert s.read_masked('STATUS',4) == 4
    assert s.read('TEMP_REMOTE_HIGH') == 25
    assert s.alert_pin() == 0
    s.read('CONFIG')  # Explicitly abandon unfinished two-byte temperature observation.
    s.event('conversion_completed',local_code=code(25),remote_code=code(25),remote_open=False)
    assert s.read_masked('STATUS',4) == 4
    assert s.read_masked('STATUS',4) == 0


def test_reprogrammed_threshold_cannot_clear_old_flag_before_new_comparison():
    s = Semantics()
    limits(s)
    measure(s,60,25)
    s.write('LOCAL_HIGH_LIMIT',65)
    assert s.read_masked('STATUS',0x40) == 0x40
    assert s.read_masked('STATUS',0x40) == 0x40
    measure(s,60,25)
    assert s.read_masked('STATUS',0x40) == 0x40
    assert s.read_masked('STATUS',0x40) == 0


def test_therm2_candidate_high_is_hysteretic_not_readclear_mask_has_no_pin_effect():
    s = Semantics(profile='therm2_candidate')
    s.write('CONFIG',0x20)
    limits(s)
    measure(s,60,25)
    assert s.read_masked('STATUS',0x40) == 0x40
    assert s.read_masked('STATUS',0x40) == 0x40
    assert s.alert_pin() == 0
    s.write('CONFIG',0xA0)
    assert s.alert_pin() == 0
    measure(s,45,25)
    assert s.read_masked('STATUS',0x40) == 0x40
    measure(s,40,25)
    assert s.read_masked('STATUS',0x40) == 0
    assert s.alert_pin() == 1


def test_therm2_low_flags_excluded_and_low_open_do_not_trip_pin():
    s = Semantics(profile='therm2_candidate')
    s.write('CONFIG',0x20)
    limits(s)
    measure(s,0,0)
    assert s.alert_pin() == 1
    reject_atomic(s,lambda:s.read_masked('STATUS',0x28))
    s.event('conversion_started')
    s.event('qualified_remote_open_detected')
    assert s.alert_pin() == 1
    assert s.read_masked('STATUS',4) == 4
    s.event('conversion_completed',local_code=code(25),remote_code=code(25),remote_open=False)
    assert s.read_masked('STATUS',4) == 4
    assert s.read_masked('STATUS',4) == 0


@pytest.mark.parametrize('reg,value',[('CONFIG',0x20),('CONFIG',1),('CONV_RATE',10),('CHANNEL_ENABLE',1),('CONSECUTIVE_ALERT',3),('DIGITAL_FILTER',1),('REMOTE_OFFSET_HIGH',1),('REMOTE_HIGH_LIMIT_LOW',1)])
def test_outside_declared_profile_inputs_reject_atomically(reg,value):
    s = Semantics()
    reject_atomic(s,lambda:s.write(reg,value))


@pytest.mark.parametrize('byte',[0,1,5,7,255])
def test_non_reset_general_call_bytes_preserve_state(byte):
    s = Semantics()
    limits(s)
    s.write('CONV_RATE',5)
    s.event('general_call_reset_completed',second_byte=byte)
    assert s.read('CONV_RATE') == 5
    assert s.read('LOCAL_HIGH_LIMIT') == 50


@pytest.mark.parametrize('rate,period',list(enumerate([16,8,4,2,1,.5,.25,.125,.0625,.03125])))
def test_nominal_rate_table_metadata_only(rate,period):
    s = Semantics()
    s.write('CONV_RATE',rate)
    assert s.nominal_period_seconds() == period


def test_status_read_never_clears_busy_or_therm_live_bits():
    s = Semantics()
    limits(s)
    measure(s,80,80)
    s.event('conversion_started')
    assert s.read_masked('STATUS',0x83) == 0x83
    assert s.read_masked('STATUS',0x83) == 0x83


@pytest.mark.parametrize('local,remote,mask',[(80,25,1),(25,80,2)])
def test_therm_hysteresis_hold_and_inclusive_release(local,remote,mask):
    s = Semantics()
    limits(s)
    measure(s,local,remote)
    assert s.read_masked('STATUS',mask) == mask
    measure(s,65 if local==80 else 25,65 if remote==80 else 25)
    assert s.read_masked('STATUS',mask) == mask
    measure(s,60 if local==80 else 25,60 if remote==80 else 25)
    assert s.read_masked('STATUS',mask) == 0


@pytest.mark.parametrize('value',[-1,256,True,1.5,'1',None])
def test_invalid_one_shot_bytes_reject_atomically(value):
    s = Semantics()
    s.write('CONFIG',0x40)
    reject_atomic(s,lambda:s.write('ONE_SHOT',value))


@pytest.mark.parametrize('mask',[-1,0,256,True,1.5,'1',None])
def test_invalid_masks_reject_atomically(mask):
    s = Semantics()
    reject_atomic(s,lambda:s.read_masked('STATUS',mask))


@pytest.mark.parametrize('payload',[dict(local_code=-1,remote_code=0,remote_open=False),dict(local_code=4096,remote_code=0,remote_open=False),dict(local_code=True,remote_code=0,remote_open=False),dict(local_code=0,remote_code=0,remote_open=1),dict(local_code=0,remote_code=0,remote_open='false')])
def test_invalid_completion_rejects_atomically(payload):
    s = Semantics()
    s.event('conversion_started')
    reject_atomic(s,lambda:s.event('conversion_completed',**payload))


def oracle_flags(factory):
    s = factory()
    limits(s)
    measure(s,60,60)
    measure(s)
    assert s.read_masked('STATUS',0x50) == 0x50
    assert s.read_masked('STATUS',0x50) == 0


def oracle_active(factory):
    s = factory()
    limits(s)
    measure(s,60,60)
    assert s.read_masked('STATUS',0x50) == 0x50
    assert s.read_masked('STATUS',0x50) == 0x50


def oracle_busy(factory):
    s = factory()
    s.event('conversion_started')
    assert s.read_masked('STATUS',0x80) == 0x80
    assert s.read_masked('STATUS',0x80) == 0x80


def oracle_whole_read(factory):
    s = factory()
    limits(s)
    measure(s,60,60)
    measure(s)
    assert s.read_masked('STATUS',0x80) == 0
    assert s.read_masked('STATUS',0x50) == 0


def oracle_alert(factory):
    s = factory()
    limits(s)
    measure(s,60,25)
    assert s.alert_pin() == 0
    measure(s)
    assert s.read_masked('STATUS',0x40) == 0x40
    assert s.alert_pin() == 0
    s.event('qualified_alert_service_completed')
    assert s.alert_pin() == 1


def oracle_therm(factory):
    s = factory()
    limits(s)
    measure(s,80,80)
    assert s.read_masked('STATUS',3) == 3
    assert s.read_masked('STATUS',3) == 3
    measure(s,65,65)
    assert s.read_masked('STATUS',3) == 3
    measure(s,60,60)
    assert s.read_masked('STATUS',3) == 0


class NoReadClear(Semantics):
    def read_masked(self,reg,mask):
        old = self.values.get('STATUS')
        result = super().read_masked(reg,mask)
        if reg == 'STATUS': self.values['STATUS'] = old
        return result


class PostClearReturn(Semantics):
    def read_masked(self,reg,mask):
        result = super().read_masked(reg,mask)
        return self.values['STATUS'] & mask if reg == 'STATUS' else result


class ClearActiveCauses(Semantics):
    def read_masked(self,reg,mask):
        result = super().read_masked(reg,mask)
        if reg == 'STATUS': self.values['STATUS'] &= ~0x7C
        return result


class ReadClearsBusy(Semantics):
    def read_masked(self,reg,mask):
        result = super().read_masked(reg,mask)
        if reg == 'STATUS': self.values['STATUS'] &= ~0x80
        return result


class MaskSuppressesWholeRead(Semantics):
    def read_masked(self,reg,mask):
        old = self.values.get('STATUS')
        result = super().read_masked(reg,mask)
        if reg == 'STATUS': self.values['STATUS'] |= old & ~mask
        return result


class StatusReadAcknowledgesAlert(Semantics):
    def read_masked(self,reg,mask):
        result = super().read_masked(reg,mask)
        if reg == 'STATUS': self.alert_latched = False
        return result


class AlertTracksFlagsInsteadOfLatch(Semantics):
    def alert_pin(self):
        return 0 if self.values['STATUS'] & 0x7C else 1


class ReadClearsTherm(Semantics):
    def read_masked(self,reg,mask):
        result = super().read_masked(reg,mask)
        if reg == 'STATUS': self.values['STATUS'] &= ~3
        return result


FAULT_ORACLES = [(NoReadClear,oracle_flags),(PostClearReturn,oracle_flags),
                 (ClearActiveCauses,oracle_active),(ReadClearsBusy,oracle_busy),
                 (MaskSuppressesWholeRead,oracle_whole_read),
                 (StatusReadAcknowledgesAlert,oracle_alert),
                 (AlertTracksFlagsInsteadOfLatch,oracle_alert),
                 (ReadClearsTherm,oracle_therm)]


@pytest.mark.parametrize('fault,oracle',FAULT_ORACLES,ids=[f.__name__ for f,_ in FAULT_ORACLES])
def test_source_oracle_detects_synthetic_runtime_fault(fault,oracle):
    oracle(Semantics)
    with pytest.raises(AssertionError): oracle(fault)


def admission():
    import admission as result
    return result


def witnesses():
    a = admission()
    return {name:a.produce_witness(name) for name in a.SCENARIOS}


def advice():
    return json.loads((ROOT/'source_review.json').read_text(encoding='utf-8'))


def test_replayed_evidence_retains_nine_repair_fields_fourteen_dimensions_no_promotions():
    rows = admission().build_closure(advice(),witnesses())
    assert len(rows) == 14
    assert len({r['inventory_field_id'] for r in rows}) == 9
    assert all(r['assessment']=='BOUNDED_CLAUSES_VERIFIED' and r['source_verdict']=='REPAIR' for r in rows)
    assert all(r['whole_field_promoted'] is False and r['whole_dimension_closed'] is False for r in rows)
    assert sum(r['dimension']=='reset' for r in rows) == 9
    assert sum(r['dimension']=='read_clear' for r in rows) == 5


@pytest.mark.parametrize('scenario',list(__import__('scenarios').SCENARIOS))
def test_missing_required_scenario_remains_partial_not_admitted(scenario):
    data = witnesses()
    del data[scenario]
    rows = admission().build_closure(advice(),data)
    assert any(r['assessment']=='PARTIAL' and r['missing_claim_ids'] for r in rows)
    assert all(r['whole_field_promoted'] is False for r in rows)


def test_exploratory_policy_cannot_be_relabelled_as_unconflicted_fact():
    a = admission()
    result = {'therm2_candidate':a.produce_witness('therm2_candidate')}
    assert result['therm2_candidate']['execution_kind']=='EXPLORATORY_THERM2_POLICY'
    assert all(r['assessment']=='PARTIAL' for r in a.build_closure(advice(),result))
    result['therm2_candidate']['execution_kind']='VERIFIED_MANUFACTURER_HARDWARE_FACT'
    with pytest.raises(ValueError): a.validate_execution(result)


@pytest.mark.parametrize('variant',[
    'empty_checks','empty_trace','bool_count','float_count','count_change','fake_equal',
    'fake_clause','wrong_chip','wrong_profile','missing_trace','reverse_trace','fake_kind',
    'extra_key','unknown_scenario','wrong_scenario','failed_status','null_result'])
def test_corrupted_or_fabricated_execution_is_rejected(variant):
    data = witnesses()
    names = list(data)
    r = data[names[0]]
    if variant=='empty_checks': r['checks']=[]
    elif variant=='empty_trace': r['trace']=[]
    elif variant=='bool_count': r['check_count']=True
    elif variant=='float_count': r['check_count']=float(r['check_count'])
    elif variant=='count_change': r['check_count']+=1
    elif variant=='fake_equal': r['checks'][0]['actual']=r['checks'][0]['expected']='fabricated'
    elif variant=='fake_clause': r['checks'][0]['clause']='official certification'
    elif variant=='wrong_chip': r['trace'][0]['chip']='TMP126'
    elif variant=='wrong_profile': r['trace'][0]['profile']='invented'
    elif variant=='missing_trace': r['trace'].pop()
    elif variant=='reverse_trace': r['trace'].reverse()
    elif variant=='fake_kind': r['execution_kind']='PHYSICAL_CHIP_EQUIVALENCE'
    elif variant=='extra_key': r['hardware_pass']=True
    elif variant=='unknown_scenario': data['unknown']=copy.deepcopy(r)
    elif variant=='wrong_scenario': data[names[1]]=copy.deepcopy(r)
    elif variant=='failed_status': r['status']='FAIL'
    elif variant=='null_result': data[names[0]]=None
    with pytest.raises(ValueError): admission().validate_execution(data)


@pytest.mark.parametrize('variant',[
    'foreign_project','wrong_task','fake_sha','unknown_claim','missing_field',
    'duplicate_field','foreign_field','no_conflicts'])
def test_changed_source_identity_or_advice_rejected(variant):
    data = advice()
    if variant=='foreign_project': data['project_id']='other'
    elif variant=='wrong_task': data['task_id']='tmp117-v31/source_review'
    elif variant=='fake_sha': data['source']['sha256']='0'*64
    elif variant=='unknown_claim': data['field_closure_advice'][0]['claims']=['FAKE']
    elif variant=='missing_field': data['field_closure_advice'].pop()
    elif variant=='duplicate_field': data['field_closure_advice'][-1]=data['field_closure_advice'][0]
    elif variant=='foreign_field': data['field_closure_advice'][0]['field']='TMP126.CONFIG.ONE_SHOT'
    elif variant=='no_conflicts': data['conflicts']=[]
    with pytest.raises(ValueError): admission().build_closure(data,witnesses())


@pytest.mark.parametrize('target',[
    'corpus/data/raw_pdf/TI/TMP461.pdf',
    'eval/independent_source_admission_20261012/field_evidence.json'])
def test_primary_pdf_and_frozen_authority_are_rehashed(monkeypatch,target):
    a = admission()
    source = advice()
    execution = witnesses()
    absolute = (ROOT.parents[1]/target).resolve()
    original = Path.read_bytes
    def fake_read(path):
        data = original(path)
        return data+b'\nFAKE' if path.resolve()==absolute else data
    monkeypatch.setattr(Path,'read_bytes',fake_read)
    with pytest.raises(ValueError): a.build_closure(source,execution)
