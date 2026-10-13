"""Source-derived independent TMP126 checks, not model-performance samples.

Expected bits and transitions are copied from SNIS209C pp14–17,26–29.
No physical SPI, CRC generation, elapsed conversion time or analog test implied.
"""
import copy
import importlib.util
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('independent_tmp126_v32', ROOT / 'tmp126.py')
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
Semantics, OutsideContract = runtime.Semantics, runtime.OutsideContract
sys.path.insert(0, str(ROOT))


def reject_atomic(s, call):
    before = copy.deepcopy(vars(s))
    with pytest.raises(OutsideContract):
        call()
    assert vars(s) == before


def convert(s, word):
    s.event('conversion_started')
    s.event('conversion_sample_completed', temperature_word=word)


def crc(s, success=False, value=0x180):
    s.event('qualified_crc_write_completed', register='THIGH_LIMIT', value=value, success=success)


def flags(s):
    s.write('THIGH_LIMIT', 0x0100)
    s.write('TLOW_LIMIT', 0xFF00)
    s.write('HYSTERESIS', 0)
    convert(s, 0x0200)
    convert(s, 0xFE00)
    convert(s, 0x0300)
    s.event('qualified_positive_slew_changed', exceeded=True)
    crc(s)


def assert_nonzero_flag_read(s):
    flags(s)
    before = s.read('ALERT_STATUS')
    assert before & 0xA7 == 0xA7
    assert before & 0x50 == 0x50
    after = s.read('ALERT_STATUS')
    assert after & 0xA7 == 0
    assert after & 0x58 == before & 0x58


def test_nonzero_flags_return_before_clear_live_bits_survive():
    assert_nonzero_flag_read(Semantics())


@pytest.mark.parametrize('kwargs', [
    {'auto_increment': True}, {'word_count': 2}, {'transaction': 'burst'},
    {'transaction': 'repeated'}, {'transaction': 'single', 'auto_increment': True, 'word_count': 2},
])
def test_ambiguous_status_transaction_is_excluded_atomically(kwargs):
    s = Semantics()
    flags(s)
    reject_atomic(s, lambda: s.read('ALERT_STATUS', **kwargs))
    assert s.read('ALERT_STATUS') & 0xA7 == 0xA7


def test_cross_temperature_read_clears_dr_only():
    s = Semantics()
    flags(s)
    assert s.read('TEMP_RESULT') == 0x0300
    status = s.read('ALERT_STATUS')
    assert status & 0xA6 == 0xA6
    assert status & 1 == 0
    assert status & 0x50 == 0x50


@pytest.mark.parametrize('avg,count', [(0, 1), (1, 8)])
@pytest.mark.parametrize('conv', [0, 7])
def test_one_shot_readzero_does_not_prove_completion(avg, count, conv):
    s = Semantics()
    s.write('CONFIG', (avg << 7) | 0x10 | conv)
    assert s.read('CONFIG') & 0x18 == 0
    assert s.read('ALERT_STATUS') & 1 == 0
    for _ in range(count - 1):
        s.event('conversion_sample_completed', temperature_word=0x1200)
        assert s.read('CONFIG') & 0x18 == 0
        assert s.read('ALERT_STATUS') & 1 == 0
        assert s.read('TEMP_RESULT') == 0
    s.event('conversion_sample_completed', temperature_word=0x1200)
    assert s.read('CONFIG') & 0x18 == 8
    assert s.read('ALERT_STATUS') & 1 == 1
    assert s.read('TEMP_RESULT') == 0x1200
    reject_atomic(s, lambda: s.event('conversion_started'))


@pytest.mark.parametrize('partial', [1, 4, 7])
def test_one_shot_retrigger_discards_partial_average(partial):
    s = Semantics()
    s.write('CONFIG', 0x90)
    for _ in range(partial):
        s.event('conversion_sample_completed', temperature_word=0x1000)
    s.write('CONFIG', 0x90)
    for _ in range(7):
        s.event('conversion_sample_completed', temperature_word=0x2000)
        assert s.read('TEMP_RESULT') == 0
        assert s.read('CONFIG') & 8 == 0
    s.event('conversion_sample_completed', temperature_word=0x2000)
    assert s.read('CONFIG') & 8 == 8
    assert s.read('TEMP_RESULT') == 0x2000


def test_signed_integral_average_uses_all_samples_not_last():
    s = Semantics()
    s.write('CONFIG', 0x90)
    for i in range(8):
        s.event('conversion_sample_completed', temperature_word=0xFFF8 if i % 2 == 0 else 0)
    assert s.read('TEMP_RESULT') == 0xFFFC


def test_shutdown_aborts_partial_conversion_without_clearing_crc_flag():
    s = Semantics()
    crc(s)
    s.write('CONFIG', 0x90)
    s.event('conversion_sample_completed', temperature_word=0x1000)
    s.write('CONFIG', 0x88)
    assert s.read('TEMP_RESULT') == 0
    assert s.read('ALERT_STATUS') & 0x80 == 0x80
    reject_atomic(s, lambda: s.event('conversion_sample_completed', temperature_word=0x1000))


def test_failed_qualified_crc_write_discards_register_success_updates_and_clears_flag():
    s = Semantics()
    before = s.read('THIGH_LIMIT')
    crc(s, False, 0x0100)
    assert s.read('THIGH_LIMIT') == before
    assert s.read('ALERT_STATUS') & 0x80
    crc(s, False, 0x0200)
    crc(s, True, 0x0300)
    assert s.read('THIGH_LIMIT') == 0x0300
    assert s.read('ALERT_STATUS') & 0x80 == 0


@pytest.mark.parametrize('bad', [True, None, -1, 65536, 1, 2, 3, '0', 1.0])
def test_bad_sample_is_rejected_atomically(bad):
    s = Semantics()
    s.write('CONFIG', 0x90)
    reject_atomic(s, lambda: s.event('conversion_sample_completed', temperature_word=bad))


@pytest.mark.parametrize('bad', [True, None, -1, 65536, '0', 1.0])
def test_bad_write_word_rejected_atomically(bad):
    s = Semantics()
    reject_atomic(s, lambda: s.write('CONFIG', bad))


@pytest.mark.parametrize('name,payload', [
    ('unknown_event', {}), ('conversion_started', {'extra': 1}),
    ('conversion_sample_completed', {}),
    ('conversion_sample_completed', {'temperature_word': 0, 'extra': True}),
    ('qualified_positive_slew_changed', {'exceeded': 1}),
    ('qualified_crc_write_completed', {'register': 'THIGH_LIMIT', 'value': 0, 'success': 1}),
    ('qualified_crc_write_completed', {'register': 'CONFIG', 'value': 0, 'success': False}),
])
def test_invalid_event_scope_is_atomic(name, payload):
    s = Semantics()
    reject_atomic(s, lambda: s.event(name, **payload))


@pytest.mark.parametrize('reg', [None, True, 1, [], {}, 'UNKNOWN'])
def test_register_identity_is_validated_before_mutation(reg):
    s = Semantics()
    reject_atomic(s, lambda: s.write(reg, 0))
    reject_atomic(s, lambda: s.read(reg))


@pytest.mark.parametrize('code,ms', list(enumerate([6, 31.25, 62.5, 125, 250, 500, 1000, 2000])))
def test_conversion_period_metadata_is_not_elapsed_time(code, ms):
    s = Semantics()
    s.write('CONFIG', code)
    assert s.nominal_period_ms() == ms
    assert s.read('ALERT_STATUS') & 1 == 0


def test_qualified_slew_requires_two_continuous_measurements():
    s = Semantics()
    reject_atomic(s, lambda: s.event('qualified_positive_slew_changed', exceeded=True))
    convert(s, 0x0100)
    reject_atomic(s, lambda: s.event('qualified_positive_slew_changed', exceeded=True))
    convert(s, 0x0200)
    s.event('qualified_positive_slew_changed', exceeded=True)
    before = s.read('ALERT_STATUS')
    assert before & 0x60 == 0x60
    assert s.read('ALERT_STATUS') & 0x60 == 0x40


def test_comparator_read_retains_live_alert_then_interrupt_transition_clears_all():
    s = Semantics()
    s.write('CONFIG', 0x20)
    flags(s)
    assert s.alert_level() == 0
    assert s.read('ALERT_STATUS') & 0xF7 == 0xF7
    assert s.alert_level() == 0  # Live high-status keeps comparator alert active.
    s.write('CONFIG', 0x20)
    assert s.read('ALERT_STATUS') & 0x50 == 0x50  # Same-mode write is not transition.
    s.write('CONFIG', 0)
    assert s.read('ALERT_STATUS') == 0
    assert s.alert_level() == 1


def test_interrupt_read_clears_enabled_flags_and_deasserts_alert_despite_live_high():
    s = Semantics()
    flags(s)
    assert s.alert_level() == 0
    assert s.read('ALERT_STATUS') & 0x10 == 0x10
    assert s.alert_level() == 1


def test_ambiguous_reverse_mode_and_active_enable_change_do_not_create_false_proof():
    s = Semantics()
    flags(s)
    reject_atomic(s, lambda: s.write('CONFIG', 0x20))
    reject_atomic(s, lambda: s.write('ALERT_ENABLE', 0))


@pytest.mark.parametrize('kwargs', [
    {'transaction': 'burst', 'auto_increment': False, 'word_count': 2},
    {'auto_increment': 1}, {'word_count': True}, {'word_count': 0},
    {'word_count': 11}, {'transaction': None},
])
def test_unsupported_or_malformed_temperature_transaction_is_atomic(kwargs):
    s = Semantics()
    convert(s, 0x0200)
    reject_atomic(s, lambda: s.read('TEMP_RESULT', **kwargs))
    assert s.read('ALERT_STATUS') & 1 == 1


def test_high_hysteresis_strict_boundaries_and_no_repeated_flag_until_crossing():
    s = Semantics()
    s.write('THIGH_LIMIT', 0x100)
    s.write('HYSTERESIS', 0x100)  # 0.5C = sixteen 1/32C codes.
    convert(s, 0x104)
    assert s.read('ALERT_STATUS') & 0x14 == 0x14
    convert(s, 0x100)
    assert s.read('ALERT_STATUS') & 0x14 == 0x10
    convert(s, 0xC0)
    assert s.read('ALERT_STATUS') & 0x14 == 0x10
    convert(s, 0xBC)
    assert s.read('ALERT_STATUS') & 0x14 == 4


def test_low_hysteresis_signed_candidate_boundaries_retained_as_declared_policy():
    s = Semantics()
    s.write('TLOW_LIMIT', 0xFF00)
    s.write('HYSTERESIS', 1)
    convert(s, 0xFEFC)
    assert s.read('ALERT_STATUS') & 0xA == 0xA
    convert(s, 0xFF00)
    assert s.read('ALERT_STATUS') & 0xA == 8
    convert(s, 0xFF40)
    assert s.read('ALERT_STATUS') & 0xA == 8
    convert(s, 0xFF44)
    assert s.read('ALERT_STATUS') & 0xA == 2


def test_non_grid_average_rejects_final_event_atomically_no_rounding_oracle():
    s = Semantics()
    s.write('CONFIG', 0x90)
    for _ in range(7):
        s.event('conversion_sample_completed', temperature_word=0)
    reject_atomic(s, lambda: s.event('conversion_sample_completed', temperature_word=4))
    assert s.read('TEMP_RESULT') == 0
    assert s.read('CONFIG') & 8 == 0


def test_numeric_slew_result_is_excluded_in_continuous_mode():
    s = Semantics()
    reject_atomic(s, lambda: s.read('SLEW_RESULT'))
    s.write('CONFIG', 8)
    assert s.read('SLEW_RESULT') == 0


@pytest.mark.parametrize('kwargs', [
    {'transaction': 'single', 'auto_increment': True},
    {'transaction': 'burst', 'auto_increment': False, 'word_count': 2},
])
def test_exploratory_body_profile_burst_preservation_is_separate_candidate_only(kwargs):
    # Source conflict unresolved: this is the explicitly labelled body candidate.
    s = Semantics(profile='body_candidate')
    flags(s)
    first = s.read('ALERT_STATUS', **kwargs)
    second = s.read('ALERT_STATUS', **kwargs)
    assert first == second and first & 0xA7 == 0xA7
    assert s.read('ALERT_STATUS') == first
    assert s.read('ALERT_STATUS') & 0xA7 == 0


def test_new_one_shot_does_not_silently_clear_preexisting_dr_or_alerts():
    s = Semantics()
    flags(s)
    s.write('CONFIG', 0x90)
    assert s.read('ALERT_STATUS') & 0xF7 == 0xF7
    assert s.read('TEMP_RESULT') == 0x0300
    assert s.read('CONFIG') & 8 == 0


def test_repeated_uncompleted_one_shots_never_publish_partial_results():
    s = Semantics()
    s.write('CONFIG', 0x90)
    for _ in range(5):
        for __ in range(7):
            s.event('conversion_sample_completed', temperature_word=0x800)
        s.write('CONFIG', 0x90)
        assert s.read('TEMP_RESULT') == 0
        assert s.read('ALERT_STATUS') & 1 == 0
        assert s.read('CONFIG') & 8 == 0


# Deliberate negative fixtures test the oracle; these are not generated models.
def oracle_status(factory):
    assert_nonzero_flag_read(factory())


def oracle_temperature_clear(factory):
    s = factory()
    flags(s)
    s.read('TEMP_RESULT')
    result = s.read('ALERT_STATUS')
    assert result & 0xF7 == 0xF6


def oracle_average(factory):
    s = factory()
    s.write('CONFIG', 0x90)
    s.event('conversion_sample_completed', temperature_word=0x200)
    assert s.read('TEMP_RESULT') == 0
    assert s.read('CONFIG') & 8 == 0
    for i in range(7):
        s.event('conversion_sample_completed', temperature_word=0x200 if i < 6 else 0x220)
    assert s.read('TEMP_RESULT') == 0x204


def oracle_mode(factory):
    s = factory()
    s.write('CONFIG', 0x10)
    assert s.read('CONFIG') & 0x18 == 0
    s.event('conversion_sample_completed', temperature_word=0x100)
    assert s.read('CONFIG') & 0x18 == 8


def oracle_restart(factory):
    s = factory()
    s.write('CONFIG', 0x90)
    for _ in range(7):
        s.event('conversion_sample_completed', temperature_word=0x100)
    s.write('CONFIG', 0x90)
    s.event('conversion_sample_completed', temperature_word=0x200)
    assert s.read('TEMP_RESULT') == 0
    assert s.read('CONFIG') & 8 == 0


def oracle_crc(factory):
    s = factory()
    prior = s.read('THIGH_LIMIT')
    crc(s, False, 0x200)
    assert s.read('THIGH_LIMIT') == prior
    assert s.read('ALERT_STATUS') & 0x80
    crc(s)
    crc(s, True)
    assert s.read('ALERT_STATUS') & 0x80 == 0


def oracle_transition(factory):
    s = factory()
    s.write('CONFIG', 0x20)
    flags(s)
    assert s.alert_level() == 0
    s.write('CONFIG', 0)
    assert s.read('ALERT_STATUS') == 0
    assert s.alert_level() == 1


class NoReadClear(Semantics):
    def read(self, reg, **kwargs):
        old = self.values['ALERT_STATUS']
        result = super().read(reg, **kwargs)
        if reg == 'ALERT_STATUS': self.values['ALERT_STATUS'] = old
        return result


class ClearsLiveBits(Semantics):
    def read(self, reg, **kwargs):
        result = super().read(reg, **kwargs)
        if reg == 'ALERT_STATUS': self.values['ALERT_STATUS'] = 0
        return result


class ReturnsPostclear(Semantics):
    def read(self, reg, **kwargs):
        result = super().read(reg, **kwargs)
        return self.values['ALERT_STATUS'] if reg == 'ALERT_STATUS' else result


class TemperatureClearsEverything(Semantics):
    def read(self, reg, **kwargs):
        result = super().read(reg, **kwargs)
        if reg == 'TEMP_RESULT': self.values['ALERT_STATUS'] = 0
        return result


class TemperatureDoesNotClearDR(Semantics):
    def read(self, reg, **kwargs):
        old = self.values['ALERT_STATUS']
        result = super().read(reg, **kwargs)
        if reg == 'TEMP_RESULT': self.values['ALERT_STATUS'] = old
        return result


class AverageIgnored(Semantics):
    def _start(self, mode):
        super()._start(mode)
        self.required_samples = 1


class LastSampleMean(Semantics):
    def event(self, name, **payload):
        super().event(name, **payload)
        if name == 'conversion_sample_completed' and self.conversion_state == 'idle':
            self.values['TEMP_RESULT'] = payload['temperature_word']


class OneShotBitPersists(Semantics):
    def write(self, reg, value):
        super().write(reg, value)
        if reg == 'CONFIG' and value & 0x10: self.values['CONFIG'] |= 0x10


class ModeDoesNotShutdown(Semantics):
    def event(self, name, **payload):
        super().event(name, **payload)
        if name == 'conversion_sample_completed': self.values['CONFIG'] &= ~8


class RestartKeepsPartial(Semantics):
    def write(self, reg, value):
        old_samples = list(self.samples)
        super().write(reg, value)
        if reg == 'CONFIG' and value & 0x10: self.samples = old_samples


class FailedCrcWrites(Semantics):
    def event(self, name, **payload):
        super().event(name, **payload)
        if name == 'qualified_crc_write_completed' and not payload['success']:
            self.values[payload['register']] = payload['value']


class CrcSuccessKeepsError(Semantics):
    def event(self, name, **payload):
        old = self.values['ALERT_STATUS'] & 0x80
        super().event(name, **payload)
        if name == 'qualified_crc_write_completed' and payload['success']:
            self.values['ALERT_STATUS'] |= old


class TransitionKeepsStatus(Semantics):
    def write(self, reg, value):
        old = self.values['ALERT_STATUS']
        super().write(reg, value)
        if reg == 'CONFIG': self.values['ALERT_STATUS'] = old


FAULT_ORACLES = [
    (NoReadClear, oracle_status), (ClearsLiveBits, oracle_status),
    (ReturnsPostclear, oracle_status), (TemperatureClearsEverything, oracle_temperature_clear),
    (TemperatureDoesNotClearDR, oracle_temperature_clear), (AverageIgnored, oracle_average),
    (LastSampleMean, oracle_average), (OneShotBitPersists, oracle_mode),
    (ModeDoesNotShutdown, oracle_mode), (RestartKeepsPartial, oracle_restart),
    (FailedCrcWrites, oracle_crc), (CrcSuccessKeepsError, oracle_crc),
    (TransitionKeepsStatus, oracle_transition),
]


@pytest.mark.parametrize('fault,oracle', FAULT_ORACLES, ids=[f.__name__ for f, _ in FAULT_ORACLES])
def test_source_oracle_detects_synthetic_fault(fault, oracle):
    oracle(Semantics)
    with pytest.raises(AssertionError):
        oracle(fault)


def admission():
    import admission as result
    return result


def witnesses():
    a = admission()
    return {name: a.produce_witness(name) for name in a.SCENARIOS if name != 'exploratory_burst'}


def source_advice():
    return json.loads((ROOT / 'source_review.json').read_text(encoding='utf-8'))


def test_real_local_witness_replays_and_keeps_all_eight_fields_unpromoted():
    rows = admission().build_closure(source_advice(), witnesses())
    assert len(rows) == 8
    assert len({r['inventory_field_id'] for r in rows}) == 8
    assert all(r['assessment'] == 'BOUNDED_CLAUSES_VERIFIED' for r in rows)
    assert all(r['whole_field_promoted'] is False and r['whole_dimension_closed'] is False for r in rows)
    assert all(r['source_verdict'] == 'REPAIR' for r in rows)
    assert all(len(r['source_conflict_ids']) == 6 for r in rows)


@pytest.mark.parametrize('scenario', [
    'flags_and_live', 'temp_cross_clear', 'comparator_to_interrupt',
    'oneshot_average_restart', 'abort_preserves_alerts', 'signed_hysteresis',
    'crc_discard', 'source_scope_guards',
])
def test_missing_required_scenario_yields_partial_not_admitted(scenario):
    execution = witnesses()
    del execution[scenario]
    rows = admission().build_closure(source_advice(), execution)
    assert any(r['assessment'] == 'PARTIAL' and r['missing_claim_ids'] for r in rows)
    assert all(r['whole_field_promoted'] is False for r in rows)


def corrupt_witness(result, variant):
    r = result['flags_and_live']
    if variant == 'empty_checks': r['checks'] = []
    elif variant == 'empty_trace': r['trace'] = []
    elif variant == 'bool_count': r['check_count'] = True
    elif variant == 'count_change': r['check_count'] += 1
    elif variant == 'fake_equal': r['checks'][0]['actual'] = r['checks'][0]['expected'] = 0
    elif variant == 'fake_clause': r['checks'][0]['clause'] = 'official proof'
    elif variant == 'wrong_chip': r['trace'][0]['chip'] = 'TMP117'
    elif variant == 'wrong_profile': r['trace'][0]['profile'] = 'body_candidate'
    elif variant == 'wrong_stimulus': r['trace'][0]['value'] = 0
    elif variant == 'missing_trace_step': r['trace'].pop()
    elif variant == 'reordered_trace': r['trace'] = list(reversed(r['trace']))
    elif variant == 'fake_kind': r['execution_kind'] = 'PHYSICAL_HARDWARE_MEASUREMENT'
    elif variant == 'extra_key': r['hardware_pass'] = True
    elif variant == 'unknown_scenario': result['unknown'] = copy.deepcopy(r)
    elif variant == 'wrong_scenario': result['temp_cross_clear'] = copy.deepcopy(r)
    elif variant == 'failed_status': r['status'] = 'FAIL'
    elif variant == 'null_result': result['flags_and_live'] = None
    else: raise AssertionError(variant)


@pytest.mark.parametrize('variant', [
    'empty_checks', 'empty_trace', 'bool_count', 'count_change', 'fake_equal',
    'fake_clause', 'wrong_chip', 'wrong_profile', 'wrong_stimulus',
    'missing_trace_step', 'reordered_trace', 'fake_kind', 'extra_key',
    'unknown_scenario', 'wrong_scenario', 'failed_status', 'null_result',
])
def test_fabricated_or_corrupted_execution_fails_exact_replay(variant):
    execution = witnesses()
    corrupt_witness(execution, variant)
    with pytest.raises(ValueError):
        admission().validate_execution(execution)


@pytest.mark.parametrize('variant', [
    'foreign_project', 'wrong_task', 'fake_sha', 'unknown_claim',
    'missing_field', 'duplicate_field', 'foreign_field', 'no_conflicts',
])
def test_changed_source_identity_or_advice_is_rejected(variant):
    source = source_advice()
    if variant == 'foreign_project': source['project_id'] = 'other'
    elif variant == 'wrong_task': source['task_id'] = 'tmp117-v31/source_review'
    elif variant == 'fake_sha': source['source']['sha256'] = '0' * 64
    elif variant == 'unknown_claim': source['field_closure_advice'][0]['claims'] = ['FAKE']
    elif variant == 'missing_field': source['field_closure_advice'].pop()
    elif variant == 'duplicate_field': source['field_closure_advice'][-1] = source['field_closure_advice'][0]
    elif variant == 'foreign_field': source['field_closure_advice'][0]['field'] = 'TMP117.CONFIG.DR'
    elif variant == 'no_conflicts': source['conflicts'] = []
    with pytest.raises(ValueError):
        admission().build_closure(source, witnesses())


def test_exploratory_policy_cannot_be_relabelled_manufacturer_fact():
    a = admission()
    execution = {'exploratory_burst': a.produce_witness('exploratory_burst')}
    assert execution['exploratory_burst']['execution_kind'] == 'EXPLORATORY_BODY_POLICY'
    a.validate_execution(execution)
    execution['exploratory_burst']['execution_kind'] = 'DIGITAL_EVENT_PROFILE'
    with pytest.raises(ValueError): a.validate_execution(execution)
    rows = a.build_closure(source_advice(), {'exploratory_burst': a.produce_witness('exploratory_burst')})
    assert all(r['assessment'] == 'PARTIAL' for r in rows)


@pytest.mark.parametrize('target', [
    'corpus/data/raw_pdf/TI/TMP126.pdf',
    'eval/independent_source_admission_20261012/field_evidence.json',
])
def test_rehashed_primary_and_frozen_authority_reject_changed_bytes_without_editing_files(monkeypatch, target):
    a = admission()
    review = source_advice()
    execution = witnesses()
    absolute = (ROOT.parents[1] / target).resolve()
    original = Path.read_bytes
    def modified_read(path):
        blob = original(path)
        return blob + b'\nFAKE' if path.resolve() == absolute else blob
    monkeypatch.setattr(Path, 'read_bytes', modified_read)
    with pytest.raises(ValueError):
        a.build_closure(review, execution)

