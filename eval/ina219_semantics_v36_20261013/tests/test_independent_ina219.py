"""Independent INA219 source oracles; unknown is not numeric zero."""
import copy
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('independent_ina219_v36', ROOT / 'ina219.py')
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
Semantics, OutsideContract = runtime.Semantics, runtime.OutsideContract
sys.path.insert(0, str(ROOT))


def reject_atomic(s, operation):
    before = copy.deepcopy(vars(s))
    with pytest.raises(OutsideContract):
        operation()
    assert vars(s) == before


@pytest.mark.parametrize('reg,expected', [('CONFIGURATION', 0x399F), ('CALIBRATION', 0), ('CURRENT', 0), ('POWER', 0)])
def test_documented_cold_defaults(reg, expected):
    s = Semantics()
    assert s.read(reg) == expected


@pytest.mark.parametrize('reg,mask', [('SHUNT_VOLTAGE', 0xFFFF), ('BUS_VOLTAGE', 0xFFF8),
                                    ('BUS_VOLTAGE', 2), ('BUS_VOLTAGE', 1), ('BUS_VOLTAGE', 4),
                                    ('BUS_VOLTAGE', 0xFFFF)])
def test_measurement_and_flag_reset_never_fabricated(reg, mask):
    s = Semantics()
    assert s.known[reg] == 0
    reject_atomic(s, lambda: s.read_masked(reg, mask))
    reject_atomic(s, lambda: s.read(reg))


@pytest.mark.parametrize('value', [-1, 65536, True, 1.0, '1', None])
def test_malformed_write_rejects_atomically(value):
    s = Semantics()
    reject_atomic(s, lambda: s.write('CONFIGURATION', value))


@pytest.mark.parametrize('mask', [0, -1, 65536, True, 1.0, '1', None])
def test_malformed_observation_mask_rejects_atomically(mask):
    s = Semantics()
    reject_atomic(s, lambda: s.read_masked('CONFIGURATION', mask))


@pytest.mark.parametrize('reg', ['SHUNT_VOLTAGE', 'BUS_VOLTAGE', 'CURRENT', 'POWER', 'unknown'])
def test_measurements_are_read_only_or_unknown(reg):
    s = Semantics()
    reject_atomic(s, lambda: s.write(reg, 0x1234))


@pytest.mark.parametrize('name', ['ADC_done', 'physical_conversion', 'elapsed_time', 'crc_checked'])
def test_unrecognized_and_physical_events_cannot_become_evidence(name):
    s = Semantics()
    reject_atomic(s, lambda: s.event(name))


def completed(profile='common_source', shunt=0x1234, bus=1000, cal=0):
    s = Semantics(profile=profile)
    if cal: s.write('CALIBRATION', cal)
    s.event('conversion_started')
    s.event('voltage_results_completed', shunt_word=shunt, bus_code=bus)
    s.event('whole_sequence_completed')
    return s


@pytest.mark.parametrize('profile', ['common_source', 'register_detail_candidate'])
def test_partial_results_do_not_set_cnvr_until_whole_sequence(profile):
    s = Semantics(profile=profile)
    s.event('conversion_started')
    assert s.known['BUS_VOLTAGE'] & 2 == 0
    s.event('voltage_results_completed', shunt_word=0x8300, bus_code=3000)
    assert s.read('SHUNT_VOLTAGE') == 0x8300
    assert s.known['BUS_VOLTAGE'] & 2 == 0
    s.event('whole_sequence_completed')
    assert s.read_masked('BUS_VOLTAGE', 2) == 2


@pytest.mark.parametrize('bus', [0, 1, 3000, 6500, 8000])
def test_bus_leftshifted_and_reserved_ovf_stay_unknown(bus):
    s = completed(bus=bus)
    assert s.known['BUS_VOLTAGE'] & 4 == 0
    assert s.known['BUS_VOLTAGE'] & 1 == 0
    reject_atomic(s, lambda: s.read('BUS_VOLTAGE'))
    assert s.read_masked('BUS_VOLTAGE', 0xFFF8) == bus << 3
    reject_atomic(s, lambda: s.read_masked('BUS_VOLTAGE', 2))


@pytest.mark.parametrize('shunt', [0, 1, 0xFFFF, 0x7D00, 0x8300])
def test_supplied_signed_shunt_word_keeps_two_complement(shunt):
    s = completed(shunt=shunt)
    assert s.read('SHUNT_VOLTAGE') == shunt


@pytest.mark.parametrize('reg', ['BUS_VOLTAGE', 'POWER'])
def test_main_read_ends_cnvr_knowledge_without_inventing_clear(reg):
    s = completed()
    assert s.known['BUS_VOLTAGE'] & 2
    if reg == 'BUS_VOLTAGE': assert s.read_masked(reg, 2) == 2
    else: assert s.read(reg) == 0
    assert not s.known['BUS_VOLTAGE'] & 2
    reject_atomic(s, lambda: s.read_masked('BUS_VOLTAGE', 2))


def test_candidate_power_crossclear_and_bus_nonclear_remain_explicit_candidate():
    s = completed(profile='register_detail_candidate')
    assert s.read_masked('BUS_VOLTAGE', 2) == 2
    assert s.read_masked('BUS_VOLTAGE', 2) == 2
    assert s.read('POWER') == 0
    assert s.read_masked('BUS_VOLTAGE', 2) == 0


@pytest.mark.parametrize('mode', [0, 4])
def test_powerdown_adcoff_cnvr_exception_preserves_known_one(mode):
    s = completed()
    s.write('CONFIGURATION', (0x399F & ~7) | mode)
    assert s.read_masked('BUS_VOLTAGE', 2) == 2


@pytest.mark.parametrize('profile', ['common_source', 'register_detail_candidate'])
def test_changed_active_mode_clear_and_trigger_start(profile):
    s = completed(profile=profile)
    s.write('CONFIGURATION', (0x399F & ~7) | 3)
    assert s.read_masked('BUS_VOLTAGE', 2) == 0
    # Trigger write already started; externally starting again is not qualified.
    reject_atomic(s, lambda: s.event('conversion_started'))
    s.event('voltage_results_completed', shunt_word=0xFFFF, bus_code=2000)
    s.event('whole_sequence_completed')
    assert s.read_masked('BUS_VOLTAGE', 2) == 2


@pytest.mark.parametrize('profile,known', [('common_source', False), ('register_detail_candidate', True)])
def test_same_active_mode_write_keeps_source_conflict(profile, known):
    s = completed(profile=profile)
    s.write('CONFIGURATION', 0x399F)
    assert bool(s.known['BUS_VOLTAGE'] & 2) == known
    if known: assert s.read_masked('BUS_VOLTAGE', 2) == 0
    else: reject_atomic(s, lambda: s.read_masked('BUS_VOLTAGE', 2))


@pytest.mark.parametrize('word', [1, 3, 0x1235, 0xFFFF])
def test_calibration_void_bit_is_documented_zero_and_math_not_simulated(word):
    s = Semantics()
    s.write('CALIBRATION', word)
    assert s.read('CALIBRATION') == word & 0xFFFE
    if word & 0xFFFE:
        reject_atomic(s, lambda: s.read('CURRENT'))
        reject_atomic(s, lambda: s.read('POWER'))


@pytest.mark.parametrize('reg', ['CURRENT', 'POWER'])
def test_previously_programmed_calibration_clear_does_not_imply_instant_zero(reg):
    s = Semantics()
    s.write('CALIBRATION', 0x1234)
    s.write('CALIBRATION', 0)
    assert s.read('CALIBRATION') == 0
    reject_atomic(s, lambda: s.read(reg))
    s.event('conversion_started')
    s.event('voltage_results_completed', shunt_word=0, bus_code=0)
    s.event('whole_sequence_completed')
    reject_atomic(s, lambda: s.read(reg))
    s.write('CONFIGURATION', 0x8000); s.event('reset_completed')
    assert s.read(reg) == 0


def test_overflow_positive_qualification_requires_calibration_and_preserves_no_clear_gap():
    s = Semantics()
    s.write('CALIBRATION', 0x1000)
    s.event('conversion_started')
    s.event('voltage_results_completed', shunt_word=0x1234, bus_code=1000)
    reject_atomic(s, lambda: s.read_masked('BUS_VOLTAGE', 1))
    s.event('qualified_math_overflow')
    s.event('whole_sequence_completed')
    assert s.read_masked('BUS_VOLTAGE', 1) == 1
    reject_atomic(s, lambda: s.read('CURRENT'))
    reject_atomic(s, lambda: s.read('POWER'))
    reject_atomic(s, lambda: s.event('qualified_math_overflow', overflow=False))
    s.event('conversion_started')
    s.event('voltage_results_completed', shunt_word=0, bus_code=0)
    s.event('whole_sequence_completed')
    reject_atomic(s, lambda: s.read_masked('BUS_VOLTAGE', 1))


def test_uncalibrated_voltage_range_is_not_math_overflow():
    s = completed(bus=8000)
    reject_atomic(s, lambda: s.event('qualified_math_overflow'))
    reject_atomic(s, lambda: s.read_masked('BUS_VOLTAGE', 1))
    assert s.read('CURRENT') == 0
    assert s.read('POWER') == 0


@pytest.mark.parametrize('reg', ['CONFIGURATION', 'CALIBRATION', 'CURRENT', 'POWER', 'BUS_VOLTAGE', 'SHUNT_VOLTAGE'])
def test_reset_pending_never_promises_readback(reg):
    s = completed(cal=0x1234)
    s.write('CONFIGURATION', 0x8000)
    reject_atomic(s, lambda: s.read(reg))
    reject_atomic(s, lambda: s.read_masked(reg, 1))


@pytest.mark.parametrize('word', [0x8000, 0xB99F, 0x8003])
def test_reset_completion_restores_only_documented_defaults(word):
    s = completed(cal=0x1234)
    s.write('CONFIGURATION', word)
    s.event('reset_completed')
    assert s.read('CONFIGURATION') == 0x399F
    for reg in ['CALIBRATION', 'CURRENT', 'POWER']: assert s.read(reg) == 0
    for reg in ['BUS_VOLTAGE', 'SHUNT_VOLTAGE']:
        assert s.known[reg] == 0
        reject_atomic(s, lambda reg=reg: s.read(reg))
    reject_atomic(s, lambda: s.event('reset_completed'))


@pytest.mark.parametrize('kind', ['voltage_results_completed', 'whole_sequence_completed', 'qualified_math_overflow'])
def test_out_of_order_completion_rejects_atomically(kind):
    s = Semantics()
    kwargs = dict(shunt_word=0x1000, bus_code=1000) if kind == 'voltage_results_completed' else {}
    reject_atomic(s, lambda: s.event(kind, **kwargs))


@pytest.mark.parametrize('shunt,bus', [(-1, 0), (65536, 0), (True, 0), (1.0, 0), (0, -1), (0, 8192), (0, True), (0, 1.0)])
def test_malformed_result_rejects_without_losing_pending_phase(shunt, bus):
    s = Semantics()
    s.event('conversion_started')
    reject_atomic(s, lambda: s.event('voltage_results_completed', shunt_word=shunt, bus_code=bus))


@pytest.mark.parametrize('field', ['BADC', 'SADC'])
@pytest.mark.parametrize('code', range(16))
def test_adc_table_all_codes_including_dontcare_aliases(field, code):
    s = Semantics()
    shift = 7 if field == 'BADC' else 3
    value = (0x399F & ~(15 << shift)) | (code << shift)
    s.write('CONFIGURATION', value)
    result = s.nominal_adc_settings(field)
    assert result['samples'] == (1 if code < 9 else 1 << (code - 8))
    assert result['resolution_bits'] == (9 + (code & 3) if code < 8 else 12)
    expected = [84, 148, 276, 532, 84, 148, 276, 532, 532, 1060, 2130, 4260, 8510, 17020, 34050, 68100][code]
    assert result['conversion_time_us'] == expected


@pytest.mark.parametrize('mode', [1, 2, 5, 6])
def test_selected_channel_modes_are_profile_exclusions_not_reserved_encodings(mode):
    s = Semantics()
    reject_atomic(s, lambda: s.write('CONFIGURATION', (0x399F & ~7) | mode))


@pytest.mark.parametrize('operation', ['calibration', 'config', 'double_start', 'early_complete'])
def test_pending_sequence_history_guards_do_not_mutate(operation):
    s = Semantics(); s.event('conversion_started')
    funcs = {'calibration': lambda: s.write('CALIBRATION', 0x1234),
             'config': lambda: s.write('CONFIGURATION', 0x399B),
             'double_start': lambda: s.event('conversion_started'),
             'early_complete': lambda: s.event('whole_sequence_completed')}
    reject_atomic(s, funcs[operation])


@pytest.mark.parametrize('args', [dict(chip='TMP117'), dict(chip=0), dict(profile='physical'), dict(profile=True)])
def test_foreign_identity_or_profile_is_not_admitted(args):
    with pytest.raises(OutsideContract): Semantics(**args)


@pytest.mark.parametrize('mask', [4, 5, 6, 7, 0xFFFF])
@pytest.mark.parametrize('profile', ['common_source', 'register_detail_candidate'])
def test_reserved_bit_never_becomes_known_in_any_profile(mask, profile):
    s = completed(profile=profile)
    reject_atomic(s, lambda: s.read_masked('BUS_VOLTAGE', mask))


@pytest.mark.parametrize('kwargs', [dict(transaction='burst'), dict(auto_increment=True), dict(auto_increment=1)])
def test_bus_framing_outside_register_profile_not_certified(kwargs):
    s = completed()
    reject_atomic(s, lambda: s.read_masked('BUS_VOLTAGE', 2, **kwargs))


class ColdMeasurementZero(Semantics):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.known['SHUNT_VOLTAGE'] = 0xFFFF


class ReservedBitInvented(Semantics):
    def event(self, kind, **kwargs):
        result = super().event(kind, **kwargs)
        if kind == 'whole_sequence_completed': self.known['BUS_VOLTAGE'] |= 4
        return result


class EarlyCnvr(Semantics):
    def event(self, kind, **kwargs):
        result = super().event(kind, **kwargs)
        if kind == 'voltage_results_completed':
            self.known['BUS_VOLTAGE'] |= 2
            self.values['BUS_VOLTAGE'] |= 2
        return result


class BusRightAligned(Semantics):
    def event(self, kind, **kwargs):
        result = super().event(kind, **kwargs)
        if kind == 'voltage_results_completed': self.values['BUS_VOLTAGE'] = kwargs['bus_code']
        return result


class UnknownOvfForcedZero(Semantics):
    def event(self, kind, **kwargs):
        result = super().event(kind, **kwargs)
        if kind == 'whole_sequence_completed': self.known['BUS_VOLTAGE'] |= 1
        return result


class MainCnvrRetainedAfterRead(Semantics):
    def read_masked(self, reg, mask):
        previous = self.known['BUS_VOLTAGE']
        result = super().read_masked(reg, mask)
        if reg == 'BUS_VOLTAGE': self.known['BUS_VOLTAGE'] |= previous & 2
        return result


class CalibrationVoidWritable(Semantics):
    def write(self, reg, value):
        result = super().write(reg, value)
        if reg == 'CALIBRATION': self.values[reg] |= value & 1
        return result


class CalibrationClearInventsInstantZero(Semantics):
    def write(self, reg, value):
        result = super().write(reg, value)
        if reg == 'CALIBRATION' and value == 0:
            self.values['CURRENT'] = self.values['POWER'] = 0
            self.known['CURRENT'] = self.known['POWER'] = 0xFFFF
        return result


class BadResetConfiguration(Semantics):
    def event(self, kind, **kwargs):
        result = super().event(kind, **kwargs)
        if kind == 'reset_completed': self.values['CONFIGURATION'] = 0
        return result


class ResetDynamicZeroInvented(Semantics):
    def event(self, kind, **kwargs):
        result = super().event(kind, **kwargs)
        if kind == 'reset_completed': self.known['BUS_VOLTAGE'] = 0xFFFF
        return result


class SameModeInventedClear(Semantics):
    def write(self, reg, value):
        result = super().write(reg, value)
        if reg == 'CONFIGURATION' and value == 0x399F: self._field('BUS_VOLTAGE', 'CNVR', 0)
        return result


class PowerdownWrongClear(Semantics):
    def write(self, reg, value):
        result = super().write(reg, value)
        if reg == 'CONFIGURATION' and value & 7 == 0: self._field('BUS_VOLTAGE', 'CNVR', 0)
        return result


class CandidatePowerFailsClear(Semantics):
    def read_masked(self, reg, mask, transaction='single', auto_increment=False):
        previous = self.values['BUS_VOLTAGE']
        result = super().read_masked(reg, mask, transaction, auto_increment)
        if reg == 'POWER': self.values['BUS_VOLTAGE'] |= previous & 2
        return result


def qualified_for_oracle(cls):
    s = cls()
    s.event('conversion_started')
    s.event('voltage_results_completed', shunt_word=0x1234, bus_code=1000)
    s.event('whole_sequence_completed')
    return s


def oracle_cold(cls):
    assert cls().known['SHUNT_VOLTAGE'] == 0


def oracle_reserved(cls):
    assert qualified_for_oracle(cls).known['BUS_VOLTAGE'] & 4 == 0


def oracle_early(cls):
    s = cls(); s.event('conversion_started')
    s.event('voltage_results_completed', shunt_word=0x1234, bus_code=1000)
    assert s.known['BUS_VOLTAGE'] & 2 == 0


def oracle_bus(cls):
    assert qualified_for_oracle(cls).read_masked('BUS_VOLTAGE', 0xFFF8) == 8000


def oracle_ovf(cls):
    assert qualified_for_oracle(cls).known['BUS_VOLTAGE'] & 1 == 0


def oracle_read_unknown(cls):
    s = qualified_for_oracle(cls)
    assert s.read_masked('BUS_VOLTAGE', 2) == 2
    assert s.known['BUS_VOLTAGE'] & 2 == 0


def oracle_cal(cls):
    s = cls(); s.write('CALIBRATION', 0x1235)
    assert s.read('CALIBRATION') == 0x1234


def oracle_cal_history(cls):
    s = cls(); s.write('CALIBRATION', 0x1234); s.write('CALIBRATION', 0)
    assert s.known['CURRENT'] == s.known['POWER'] == 0


def oracle_reset(cls):
    s = qualified_for_oracle(cls)
    s.write('CONFIGURATION', 0x8000)
    s.event('reset_completed')
    assert s.read('CONFIGURATION') == 0x399F


def oracle_reset_unknown(cls):
    s = qualified_for_oracle(cls); s.write('CONFIGURATION', 0x8000)
    s.event('reset_completed')
    assert s.known['BUS_VOLTAGE'] == 0


def oracle_same_mode(cls):
    s = qualified_for_oracle(cls); s.write('CONFIGURATION', 0x399F)
    assert s.known['BUS_VOLTAGE'] & 2 == 0


def oracle_powerdown(cls):
    s = qualified_for_oracle(cls); s.write('CONFIGURATION', 0x3998)
    assert s.read_masked('BUS_VOLTAGE', 2) == 2


def oracle_candidate_power(cls):
    s = cls(profile='register_detail_candidate')
    s.event('conversion_started')
    s.event('voltage_results_completed', shunt_word=0x1234, bus_code=1000)
    s.event('whole_sequence_completed')
    assert s.read('POWER') == 0
    assert s.read_masked('BUS_VOLTAGE', 2) == 0


FAULT_ORACLES = [(ColdMeasurementZero, oracle_cold), (ReservedBitInvented, oracle_reserved),
    (EarlyCnvr, oracle_early), (BusRightAligned, oracle_bus), (UnknownOvfForcedZero, oracle_ovf),
    (MainCnvrRetainedAfterRead, oracle_read_unknown), (CalibrationVoidWritable, oracle_cal),
    (CalibrationClearInventsInstantZero, oracle_cal_history),
    (BadResetConfiguration, oracle_reset), (ResetDynamicZeroInvented, oracle_reset_unknown),
    (SameModeInventedClear, oracle_same_mode),
    (PowerdownWrongClear, oracle_powerdown), (CandidatePowerFailsClear, oracle_candidate_power)]


@pytest.mark.parametrize('fault,oracle', FAULT_ORACLES, ids=[fault.__name__ for fault, _ in FAULT_ORACLES])
def test_source_oracle_detects_synthetic_runtime_fault(fault, oracle):
    oracle(Semantics)
    with pytest.raises(AssertionError): oracle(fault)


def admission():
    import admission as result
    return result


def witnesses():
    a = admission()
    return {name: a.produce_witness(name) for name in a.SCENARIOS}


def advice():
    return json.loads((ROOT / 'source_review.json').read_text(encoding='utf-8'))


def test_exact_evidence_retains_six_fields_seven_dimensions_and_zero_promotions():
    rows = admission().build_closure(advice(), witnesses())
    assert len(rows) == 7
    assert len({r['inventory_field_id'] for r in rows}) == 6
    assert all(r['assessment'] == 'BOUNDED_CLAUSES_VERIFIED' and r['source_verdict'] == 'REPAIR' for r in rows)
    assert all(r['whole_field_promoted'] is False and r['whole_dimension_closed'] is False for r in rows)
    assert sum(r['dimension'] == 'reset' for r in rows) == 5
    assert sum(r['dimension'] == 'reserved_policy' for r in rows) == 1
    assert sum(r['dimension'] == 'trigger_completion' for r in rows) == 1


@pytest.mark.parametrize('scenario', list(__import__('scenarios').SCENARIOS))
def test_missing_required_scenario_retains_partial_or_unaffected_not_full_admission(scenario):
    data = witnesses(); del data[scenario]
    rows = admission().build_closure(advice(), data)
    source = advice()
    needed_claims = {claim for item in source['field_closure_advice'] for claim in item['claims']}
    if any(scenario in admission().CLAIM_SCENARIOS.get(claim, []) for claim in needed_claims):
        assert any(r['assessment'] == 'PARTIAL' and r['missing_claim_ids'] for r in rows)
    else:
        assert all(r['assessment'] == 'BOUNDED_CLAUSES_VERIFIED' and not r['missing_claim_ids'] for r in rows)
    assert all(r['whole_field_promoted'] is False and r['whole_dimension_closed'] is False for r in rows)


@pytest.mark.parametrize('name,kind', [('candidate_read_clear', 'EXPLORATORY_REGISTER_DETAIL_POLICY'),
    ('mode_clear_boundaries', 'MIXED_SOURCE_AND_CANDIDATE_POLICY'), ('nominal_adc_table', 'SOURCE_TABLE_METADATA')])
def test_exploratory_policy_and_metadata_cannot_be_relabelled_as_manufacturer_equivalence(name, kind):
    a = admission(); data = {name: a.produce_witness(name)}
    assert data[name]['execution_kind'] == kind
    assert all(r['assessment'] == 'PARTIAL' for r in a.build_closure(advice(), data))
    data[name]['execution_kind'] = 'VERIFIED_MANUFACTURER_HARDWARE_FACT'
    with pytest.raises(ValueError): a.validate_execution(data)


@pytest.mark.parametrize('variant', ['empty_checks', 'empty_trace', 'bool_count', 'float_count', 'count_change',
    'fake_equal', 'fake_clause', 'wrong_chip', 'wrong_profile', 'missing_trace', 'reverse_trace',
    'fake_kind', 'extra_key', 'unknown_scenario', 'wrong_scenario', 'failed_status', 'null_result'])
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
    elif variant == 'fake_clause': r['checks'][0]['clause'] = 'silicon certification'
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


@pytest.mark.parametrize('variant', ['foreign_project', 'wrong_task', 'fake_sha', 'unknown_claim',
    'missing_field', 'duplicate_field', 'foreign_field', 'no_conflicts'])
def test_changed_source_identity_or_advice_rejected(variant):
    data = advice()
    if variant == 'foreign_project': data['project_id'] = 'other'
    elif variant == 'wrong_task': data['task_id'] = 'tmp117-v31/source_review'
    elif variant == 'fake_sha': data['source']['sha256'] = '0' * 64
    elif variant == 'unknown_claim': data['field_closure_advice'][0]['claims'] = ['FAKE']
    elif variant == 'missing_field': data['field_closure_advice'].pop()
    elif variant == 'duplicate_field': data['field_closure_advice'][-1] = data['field_closure_advice'][0]
    elif variant == 'foreign_field': data['field_closure_advice'][0]['field'] = 'TMP126.CONFIG.ONE_SHOT'
    elif variant == 'no_conflicts': data['conflicts'] = []
    with pytest.raises(ValueError): admission().build_closure(data, witnesses())


@pytest.mark.parametrize('target', ['corpus/data/raw_pdf/TI/INA219.pdf', 'eval/independent_source_admission_20261012/field_evidence.json'])
def test_primary_pdf_and_frozen_authority_are_rehashed(monkeypatch, target):
    a = admission()
    source, execution = advice(), witnesses()
    absolute = (ROOT.parents[1] / target).resolve()
    original = Path.read_bytes
    def fake_read(path):
        data = original(path)
        return data + b'\nFAKE' if path.resolve() == absolute else data
    monkeypatch.setattr(Path, 'read_bytes', fake_read)
    with pytest.raises(ValueError): a.build_closure(source, execution)
