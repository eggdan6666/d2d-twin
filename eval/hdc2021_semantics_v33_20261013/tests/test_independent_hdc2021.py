"""Independent SNAS773A source-derived digital checks, not model or physical tests."""
import copy
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('independent_hdc2021_v33', ROOT / 'hdc2021.py')
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
Semantics, OutsideContract = runtime.Semantics, runtime.OutsideContract
sys.path.insert(0, str(ROOT))


def reject_atomic(s, operation):
    before = copy.deepcopy(vars(s))
    with pytest.raises(OutsideContract):
        operation()
    assert vars(s) == before


def measure(s, temperature=0x9000, humidity=0x9000, *, request=True):
    if request:
        s.write('MEAS_CONFIG', s.read('MEAS_CONFIG') | 1)
    s.event('measurement_started')
    s.event('measurement_completed', temperature_code=temperature, humidity_code=humidity)


def thresholds(s):
    s.write('TEMP_THR_H', 0x80)
    s.write('TEMP_THR_L', 0x40)
    s.write('RH_THR_H', 0x80)
    s.write('RH_THR_L', 0x40)
    s.write('INTERRUPT_ENABLE', 0x78)


def dirty_flags(s):
    thresholds(s)
    measure(s, 0x9000, 0x9000)
    measure(s, 0x3000, 0x3000)
    measure(s, 0x6000, 0x6000)


def status(s):
    return s.read_masked('STATUS', 0xF8)


def oracle_read_clear(factory):
    s = factory(profile='table_figure_candidate')
    dirty_flags(s)
    assert status(s) == 0xF8
    assert status(s) == 0


def test_nonzero_latch_returns_preclear_then_clears_defined_bits():
    oracle_read_clear(Semantics)


def test_common_all_enabled_nonzero_latch_readclear_and_new_conversion_rearm():
    s = Semantics()
    thresholds(s)
    s.write('INTERRUPT_ENABLE',0xF8)
    measure(s,0x9000,0x9000)
    measure(s,0x3000,0x3000)
    measure(s,0x6000,0x6000)
    assert status(s) == 0xF8
    assert status(s) == 0
    measure(s,0x9000,0x9000)
    assert status(s) == 0xD0


@pytest.mark.parametrize('register', ['TEMP_LOW', 'TEMP_HIGH', 'HUM_LOW', 'HUM_HIGH'])
def test_all_four_measurement_byte_reads_clear_drdy_only(register):
    s = Semantics(profile='table_figure_candidate')
    dirty_flags(s)
    assert s.read(register) == (0 if register.endswith('LOW') else 0x60)
    assert status(s) == 0x78


def test_start_selfclear_precedes_result_and_drdy_completion():
    s = Semantics()
    s.write('INTERRUPT_ENABLE', 0x80)
    s.write('MEAS_CONFIG', 1)
    assert s.read('TEMP_HIGH') == 0
    assert s.read_masked('STATUS', 0x80) == 0
    s.event('measurement_started')
    assert s.read('MEAS_CONFIG') & 1 == 0
    assert s.read('TEMP_HIGH') == 0
    assert status(s) == 0
    s.event('measurement_completed', temperature_code=0x1234, humidity_code=0x5678)
    assert s.read_masked('STATUS', 0x80) == 0x80
    assert s.read('TEMP_LOW') == 0x34
    assert s.read('TEMP_HIGH') == 0x12
    assert s.read('HUM_LOW') == 0x78
    assert s.read('HUM_HIGH') == 0x56
    reject_atomic(s, lambda: s.event('measurement_started'))


@pytest.mark.parametrize('cc', range(1, 8))
def test_continuous_needs_first_trigger_then_separate_started_completed_events(cc):
    s = Semantics()
    s.write('DEVICE_CONFIG', cc << 4)
    reject_atomic(s, lambda: s.event('measurement_started'))
    measure(s, 0x1234, 0x5678)
    assert s.read('MEAS_CONFIG') & 1 == 0
    measure(s, 0x4321, 0x8765, request=False)
    assert s.read('TEMP_HIGH') == 0x43
    assert s.read('HUM_HIGH') == 0x87


@pytest.mark.parametrize('accuracy', [0, 1, 2])
def test_temperature_only_preserves_old_humidity(accuracy):
    s = Semantics()
    measure(s, 0x1234, 0x5678)
    s.write('MEAS_CONFIG', (accuracy << 6) | 2)
    measure(s, 0xABCD, None)
    assert s.read('TEMP_HIGH') == 0xAB
    assert s.read('HUM_HIGH') == 0x56
    assert s.read('HUM_LOW') == 0x78


def test_comparator_profile_updates_current_thresholds_and_candidate_read_keeps_them():
    s = Semantics(profile='table_figure_candidate')
    s.write('DEVICE_CONFIG', 1)
    thresholds(s)
    measure(s, 0x9000, 0x9000)
    assert status(s) == 0xD0
    assert status(s) == 0x50
    measure(s, 0x3000, 0x3000)
    assert status(s) == 0xA8
    assert status(s) == 0x28
    measure(s, 0x6000, 0x6000)
    assert status(s) == 0x80
    assert status(s) == 0


def test_common_comparator_status_read_conflict_excluded_atomically():
    s = Semantics()
    s.write('DEVICE_CONFIG', 1)
    s.write('TEMP_THR_H', 0x80)
    s.write('INTERRUPT_ENABLE', 0x40)
    measure(s, 0x9000, 0x6000)
    reject_atomic(s, lambda: s.read_masked('STATUS', 0xF8))


def test_unknown_reserved_status_bits_are_not_silently_certified():
    s = Semantics()
    for operation in [lambda: s.read('STATUS'), lambda: s.read_masked('STATUS', 7)]:
        reject_atomic(s, operation)


def test_disabled_status_generation_conflict_is_unknown_until_defined_clear():
    s = Semantics()
    measure(s,0x6000,0x6000)
    reject_atomic(s,lambda:s.read_masked('STATUS',0xF8))
    s.read('TEMP_LOW')
    assert s.read_masked('STATUS',0x80) == 0
    assert status(s) == 0


@pytest.mark.parametrize('kwargs', [{'transaction':'burst'},{'auto_increment':True},
    {'transaction':None},{'auto_increment':1}])
def test_outside_read_context_rejects_before_clear(kwargs):
    s = Semantics(profile='table_figure_candidate')
    dirty_flags(s)
    reject_atomic(s,lambda:s.read_masked('STATUS',0xF8,**kwargs))
    assert status(s) == 0xF8


@pytest.mark.parametrize('mask',[0,-1,256,True,248.0,'248',None])
def test_invalid_masks_rejected_atomically(mask):
    s = Semantics()
    reject_atomic(s,lambda:s.read_masked('STATUS',mask))


@pytest.mark.parametrize('value',[0x80,0x40])
def test_equality_at_ambiguous_threshold_is_excluded_atomically(value):
    s = Semantics()
    thresholds(s)
    s.write('MEAS_CONFIG',1)
    s.event('measurement_started')
    reject_atomic(s,lambda:s.event('measurement_completed',temperature_code=value<<8,humidity_code=0x6000))


@pytest.mark.parametrize('reg,value',[('DEVICE_CONFIG',8),('DEVICE_CONFIG',0x81),
    ('INTERRUPT_ENABLE',7),('TEMP_OFFSET',1),('HUM_OFFSET',255)])
def test_unsupported_heater_reset_combination_reserved_and_offset_outcomes_guarded(reg,value):
    s = Semantics()
    reject_atomic(s,lambda:s.write(reg,value))


@pytest.mark.parametrize('value', [4, 6, 8, 0xC0, 0x30, 0xFF])
def test_na_reserved_measurement_configuration_rejected_atomically(value):
    s = Semantics()
    reject_atomic(s, lambda: s.write('MEAS_CONFIG', value))


@pytest.mark.parametrize('value', [-1, 256, True, 1.0, '1', None])
def test_nonbyte_or_nonstrict_word_types_rejected_atomically(value):
    s = Semantics()
    reject_atomic(s, lambda: s.write('TEMP_THR_H', value))


@pytest.mark.parametrize('payload', [
    {'temperature_code': -1, 'humidity_code': 0},
    {'temperature_code': 65536, 'humidity_code': 0},
    {'temperature_code': True, 'humidity_code': 0},
    {'temperature_code': 0.0, 'humidity_code': 0},
    {'temperature_code': 0, 'humidity_code': None},
    {'temperature_code': 0, 'humidity_code': 65536},
    {'temperature_code': 0, 'humidity_code': True},
    {'temperature_code': 0},
    {'temperature_code': 0, 'humidity_code': 0, 'elapsed_ms': 3},
])
def test_invalid_completed_payload_rejected_before_state_change(payload):
    s = Semantics()
    s.write('MEAS_CONFIG', 1)
    s.event('measurement_started')
    reject_atomic(s, lambda: s.event('measurement_completed', **payload))


@pytest.mark.parametrize('operation', [
    lambda s: s.event('measurement_completed', temperature_code=0, humidity_code=0),
    lambda s: s.event('reset_completed'), lambda s: s.event('unknown'),
    lambda s: s.write('STATUS', 0), lambda s: s.write('unknown', 0),
    lambda s: s.read('unknown'), lambda s: s.event('measurement_started', ticks=1),
])
def test_invalid_state_events_and_registers_rejected_atomically(operation):
    s = Semantics()
    reject_atomic(s, lambda: operation(s))


@pytest.mark.parametrize('register,value', [('DEVICE_CONFIG', 0x10), ('TEMP_THR_H', 0x20), ('MEAS_CONFIG', 1)])
def test_active_measurement_reconfiguration_excluded_atomically(register, value):
    s = Semantics()
    s.write('MEAS_CONFIG', 1)
    s.event('measurement_started')
    reject_atomic(s, lambda: s.write(register, value))


def oracle_reset(factory):
    s = factory(profile='table_figure_candidate')
    dirty_flags(s)
    s.write('DEVICE_CONFIG', 0x80)
    reject_atomic(s, lambda: s.read('TEMP_HIGH'))
    reject_atomic(s, lambda: s.read('DEVICE_CONFIG'))
    s.event('reset_completed')
    for reg, expected in [('TEMP_THR_L',1),('TEMP_THR_H',255),('RH_THR_L',0),
                          ('RH_THR_H',255),('TEMP_LOW',0),('TEMP_HIGH',0),('HUM_LOW',0),
                          ('HUM_HIGH',0),('DEVICE_CONFIG',0),('MEAS_CONFIG',0)]:
        assert s.read(reg) == expected
    assert s.read_masked('INTERRUPT_ENABLE', 0xF8) == 0
    assert status(s) == 0


def test_reset_after_dirty_state_preserves_distinct_completion_boundary():
    oracle_reset(Semantics)


@pytest.mark.parametrize('polarity', [0,1])
def test_priority_selects_highest_enabled_bit_instead_of_oring_active_flags(polarity):
    s = Semantics()
    s.write('DEVICE_CONFIG', 4 | (polarity << 1))
    s.write('TEMP_THR_H', 0x80)
    s.write('RH_THR_H', 0x80)
    s.write('INTERRUPT_ENABLE', 0x50)
    measure(s, 0x6000, 0x9000)
    assert s.interrupt_pin() == 1 - polarity


@pytest.mark.parametrize('flag,enable,temp,hum', [
    (0x40,0x78,0x9000,0x6000), (0x20,0x38,0x3000,0x6000),
    (0x10,0x18,0x6000,0x9000), (0x08,0x08,0x6000,0x3000),
])
@pytest.mark.parametrize('polarity', [0,1])
def test_priority_selected_threshold_asserts_requested_polarity(flag,enable,temp,hum,polarity):
    s = Semantics()
    s.write('DEVICE_CONFIG', 4 | (polarity << 1))
    thresholds(s)
    s.write('INTERRUPT_ENABLE', enable)
    measure(s,temp,hum)
    assert s.interrupt_pin() == polarity
    assert s.read_masked('STATUS',flag) == flag
    assert s.interrupt_pin() == 1 - polarity


def test_output_disabled_is_high_impedance_not_false_binary_level():
    s = Semantics()
    s.write('INTERRUPT_ENABLE',0x80)
    measure(s)
    assert s.interrupt_pin() == 'HIGH_Z'


def test_drdy_plus_threshold_tie_is_excluded_atomically():
    s = Semantics()
    s.write('DEVICE_CONFIG',4)
    s.write('TEMP_THR_H',0x80)
    s.write('INTERRUPT_ENABLE',0xC0)
    measure(s,0x9000,0x6000)
    reject_atomic(s,s.interrupt_pin)


class NoReadClear(Semantics):
    def read_masked(self, register, mask, **kwargs):
        before = self.values['STATUS']
        result = super().read_masked(register, mask, **kwargs)
        if register == 'STATUS': self.values['STATUS'] = before
        return result


class ReturnsPostclear(Semantics):
    def read_masked(self, register, mask, **kwargs):
        result = super().read_masked(register, mask, **kwargs)
        return self.values['STATUS'] & mask if register == 'STATUS' else result


class DirtyResetThreshold(Semantics):
    def event(self, name, **payload):
        old = self.values.get('TEMP_THR_H')
        super().event(name, **payload)
        if name == 'reset_completed': self.values['TEMP_THR_H'] = old


def oracle_cross_clear(factory):
    s = factory(profile='table_figure_candidate')
    dirty_flags(s)
    s.read('TEMP_HIGH')
    assert status(s) == 0x78


def oracle_start(factory):
    s = factory()
    s.write('INTERRUPT_ENABLE',0x80)
    s.write('MEAS_CONFIG',1)
    s.event('measurement_started')
    assert s.read('MEAS_CONFIG') & 1 == 0
    assert s.read_masked('STATUS',0x80) == 0
    assert s.read('TEMP_HIGH') == 0
    s.event('measurement_completed',temperature_code=0x1234,humidity_code=0x5678)
    assert s.read_masked('STATUS',0x80) == 0x80


def oracle_comparator(factory):
    s = factory(profile='table_figure_candidate')
    s.write('DEVICE_CONFIG',1)
    thresholds(s)
    measure(s,0x9000,0x9000)
    assert status(s) == 0xD0
    assert status(s) == 0x50
    measure(s,0x6000,0x6000)
    assert status(s) == 0x80


def oracle_channels(factory):
    s = factory()
    measure(s,0x1234,0x5678)
    s.write('MEAS_CONFIG',2)
    measure(s,0xABCD,None)
    assert s.read('HUM_HIGH') == 0x56
    assert s.read('HUM_LOW') == 0x78


def oracle_pin_priority(factory):
    s = factory()
    s.write('DEVICE_CONFIG',4)
    s.write('TEMP_THR_H',0x80)
    s.write('RH_THR_H',0x80)
    s.write('INTERRUPT_ENABLE',0x50)
    measure(s,0x6000,0x9000)
    assert s.interrupt_pin() == 1


class DataReadClearsAll(Semantics):
    def read(self,reg,**kwargs):
        result = super().read(reg,**kwargs)
        if reg in ('TEMP_LOW','TEMP_HIGH','HUM_LOW','HUM_HIGH'): self.values['STATUS'] = 0
        return result


class DataReadKeepsDRDY(Semantics):
    def read(self,reg,**kwargs):
        old = self.values['STATUS']
        result = super().read(reg,**kwargs)
        if reg in ('TEMP_LOW','TEMP_HIGH','HUM_LOW','HUM_HIGH'): self.values['STATUS'] = old
        return result


class StartRetainsTrigger(Semantics):
    def event(self,name,**payload):
        super().event(name,**payload)
        if name == 'measurement_started': self.values['MEAS_CONFIG'] |= 1


class StartPrematureDRDY(Semantics):
    def event(self,name,**payload):
        super().event(name,**payload)
        if name == 'measurement_started': self.values['STATUS'] |= 0x80


class ComparatorReadClearsFlags(Semantics):
    def read_masked(self,reg,mask,**kwargs):
        result = super().read_masked(reg,mask,**kwargs)
        if reg == 'STATUS': self.values['STATUS'] = 0
        return result


class ComparatorLatchesHistory(Semantics):
    def event(self,name,**payload):
        old = self.values['STATUS'] & 0x78
        super().event(name,**payload)
        if name == 'measurement_completed': self.values['STATUS'] |= old


class TemperatureOnlyClearsHumidity(Semantics):
    def event(self,name,**payload):
        super().event(name,**payload)
        if name == 'measurement_completed' and payload['humidity_code'] is None:
            self.values['HUM_LOW'] = self.values['HUM_HIGH'] = 0


class PinORsThresholds(Semantics):
    def interrupt_pin(self):
        if self.values['DEVICE_CONFIG'] & 4:
            return 0 if self.values['STATUS'] & self.values['INTERRUPT_ENABLE'] & 0x78 else 1
        return super().interrupt_pin()


FAULT_ORACLES = [(NoReadClear,oracle_read_clear),(ReturnsPostclear,oracle_read_clear),
    (DirtyResetThreshold,oracle_reset),(DataReadClearsAll,oracle_cross_clear),
    (DataReadKeepsDRDY,oracle_cross_clear),(StartRetainsTrigger,oracle_start),
    (StartPrematureDRDY,oracle_start),(ComparatorReadClearsFlags,oracle_comparator),
    (ComparatorLatchesHistory,oracle_comparator),(TemperatureOnlyClearsHumidity,oracle_channels),
    (PinORsThresholds,oracle_pin_priority)]


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
    return json.loads((ROOT / 'source_review.json').read_text(encoding='utf-8'))


def test_replayed_evidence_retains_eight_repair_fields_and_no_promotions():
    rows = admission().build_closure(advice(),witnesses())
    assert len(rows) == 8
    assert len({r['inventory_field_id'] for r in rows}) == 8
    assert all(r['assessment'] == 'BOUNDED_CLAUSES_VERIFIED' for r in rows)
    assert all(r['source_verdict'] == 'REPAIR' for r in rows)
    assert all(r['whole_field_promoted'] is False and r['whole_dimension_closed'] is False for r in rows)
    dimensions = {r['inventory_field_id']:r['dimension'] for r in rows}
    assert 'legal_encoding' in dimensions.values()


@pytest.mark.parametrize('scenario',[
    'latched_flags','dr_cross_clear','trigger_boundary','periodic_series',
    'channel_and_resolution','reset_completion','mode_encoding',
    'threshold_candidate_comparisons','pin_priority','source_scope_guards','nominal_period_table',
])
def test_missing_required_scenario_remains_partial_not_admitted(scenario):
    data = witnesses()
    del data[scenario]
    rows = admission().build_closure(advice(),data)
    assert any(r['assessment'] == 'PARTIAL' and r['missing_claim_ids'] for r in rows)
    assert all(r['whole_field_promoted'] is False for r in rows)


@pytest.mark.parametrize('scenario',['comparator_candidate','threshold_candidate_comparisons'])
def test_exploratory_policy_cannot_be_relabelled_as_unconflicted_fact(scenario):
    a = admission()
    result = {scenario:a.produce_witness(scenario)}
    assert result[scenario]['execution_kind'] == 'EXPLORATORY_TABLE_FIGURE_POLICY'
    rows = a.build_closure(advice(),result)
    assert all(r['assessment'] == 'PARTIAL' for r in rows)
    result[scenario]['execution_kind'] = 'VERIFIED_MANUFACTURER_HARDWARE_FACT'
    with pytest.raises(ValueError): a.validate_execution(result)


@pytest.mark.parametrize('variant', [
    'empty_checks','empty_trace','bool_count','float_count','count_change','fake_equal',
    'fake_clause','wrong_chip','wrong_profile','missing_trace','reverse_trace','fake_kind',
    'extra_key','unknown_scenario','wrong_scenario','failed_status','null_result',
])
def test_corrupted_or_fabricated_execution_is_rejected(variant):
    data = witnesses()
    names = list(data)
    r = data[names[0]]
    if variant == 'empty_checks': r['checks'] = []
    elif variant == 'empty_trace': r['trace'] = []
    elif variant == 'bool_count': r['check_count'] = True
    elif variant == 'float_count': r['check_count'] = float(r['check_count'])
    elif variant == 'count_change': r['check_count'] += 1
    elif variant == 'fake_equal': r['checks'][0]['actual'] = r['checks'][0]['expected'] = 'fabricated'
    elif variant == 'fake_clause': r['checks'][0]['clause'] = 'official certification'
    elif variant == 'wrong_chip': r['trace'][0]['chip'] = 'TMP126'
    elif variant == 'wrong_profile': r['trace'][0]['profile'] = 'invented'
    elif variant == 'missing_trace': r['trace'].pop()
    elif variant == 'reverse_trace': r['trace'].reverse()
    elif variant == 'fake_kind': r['execution_kind'] = 'PHYSICAL_CHIP_EQUIVALENCE'
    elif variant == 'extra_key': r['hardware_pass'] = True
    elif variant == 'unknown_scenario': data['unknown'] = copy.deepcopy(r)
    elif variant == 'wrong_scenario': data[names[1]] = copy.deepcopy(r)
    elif variant == 'failed_status': r['status'] = 'FAIL'
    elif variant == 'null_result': data[names[0]] = None
    with pytest.raises(ValueError): admission().validate_execution(data)


@pytest.mark.parametrize('variant', [
    'foreign_project','wrong_task','fake_sha','unknown_claim','missing_field',
    'duplicate_field','foreign_field','no_conflicts',
])
def test_changed_source_identity_or_advice_rejected(variant):
    data = advice()
    if variant == 'foreign_project': data['project_id'] = 'other'
    elif variant == 'wrong_task': data['task_id'] = 'tmp126-v32/source_review'
    elif variant == 'fake_sha': data['source']['sha256'] = '0' * 64
    elif variant == 'unknown_claim': data['field_closure_advice'][0]['claims'] = ['FAKE']
    elif variant == 'missing_field': data['field_closure_advice'].pop()
    elif variant == 'duplicate_field': data['field_closure_advice'][-1] = data['field_closure_advice'][0]
    elif variant == 'foreign_field': data['field_closure_advice'][0]['field'] = 'TMP126.CONFIG.ONE_SHOT'
    elif variant == 'no_conflicts': data['conflicts'] = []
    with pytest.raises(ValueError): admission().build_closure(data,witnesses())


@pytest.mark.parametrize('target', [
    'corpus/data/raw_pdf/TI/HDC2021.pdf',
    'eval/independent_source_admission_20261012/field_evidence.json',
])
def test_primary_pdf_and_frozen_authority_are_rehashed(monkeypatch,target):
    a = admission()
    source = advice()
    execution = witnesses()
    absolute = (ROOT.parents[1] / target).resolve()
    original = Path.read_bytes
    def fake_read(path):
        data = original(path)
        return data + b'\nFAKE' if path.resolve() == absolute else data
    monkeypatch.setattr(Path,'read_bytes',fake_read)
    with pytest.raises(ValueError): a.build_closure(source,execution)
