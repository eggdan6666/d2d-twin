"""Independent bounded event tests. Expected values come from cited PDF facts.

No production source or previous harness is modified. Fault subclasses are
synthetic negative fixtures; their rejection is not empirical model accuracy.
"""
import importlib.util
from pathlib import Path
import copy
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('independent_v3_runtime', ROOT / 'runtime.py')
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
Semantics, OutsideContract = runtime.Semantics, runtime.OutsideContract
sys.path.insert(0, str(ROOT))
import compiler


def test_unknown_chip_fails_closed():
    with pytest.raises(OutsideContract):
        Semantics('INA3221')


def test_unknown_event_fails_closed():
    with pytest.raises(OutsideContract):
        Semantics('HDC2021').event('pretend_completed')


def test_conflicted_revision_bits_never_return_fabricated_zero():
    with pytest.raises(OutsideContract):
        Semantics('TMP117').read('DEVICE_ID')


def test_empty_unimplemented_eeprom_register_has_no_zero_oracle():
    with pytest.raises(OutsideContract):
        Semantics('TMP117').read('EEPROM1')


def test_unknown_event_payload_fails_closed():
    s = Semantics('HDC2021')
    s.write('MEAS_CONFIG', 1)
    with pytest.raises(OutsideContract):
        s.event('measurement_started', undeclared=1)


def test_reserved_tmp126_stimulus_fails_closed():
    # TMP126 CONFIG bit6 and bits15:9 are reserved, no illegal-input oracle.
    for value in (0x40, 0x200, 0x8000):
        with pytest.raises(OutsideContract):
            Semantics('TMP126').write('CONFIG', value)


def test_tmp117_shutdown_not_qualifying_conversion():
    s = Semantics('TMP117')
    with pytest.raises(OutsideContract):
        s.write('CONFIG', 0x400)


def assert_tmp117_alert_reads(s):
    # SNOSD82D Table7-6 p27: flags retain on TEMP read, CONFIG clears.
    s.write('CONFIG', 0)
    s.write('THIGH', 0x2000)
    s.write('TLOW', 0x1800)
    s.event('qualifying_conversion_completed', temperature_code=0x2100)
    s.event('qualifying_conversion_completed', temperature_code=0x1700)
    s.read('TEMP')  # Read-clear side effect only; no numerical temperature oracle.
    before = s.read('CONFIG')
    assert before & 0xE000 == 0xC000
    assert s.read('CONFIG') & 0xE000 == 0


def test_tmp117_alert_return_before_clear():
    assert_tmp117_alert_reads(Semantics('TMP117'))


def test_tmp117_therm_high_hysteresis_and_low_zero():
    # SNOSD82D p17 and p27: between limits retains therm HIGH; low clears.
    s = Semantics('TMP117')
    s.write('CONFIG', 0x10)
    s.write('THIGH', 0x2000)
    s.write('TLOW', 0x1800)
    s.event('qualifying_conversion_completed', temperature_code=0x2100)
    assert s.read('CONFIG') & 0xC000 == 0x8000
    assert s.read('CONFIG') & 0xC000 == 0x8000
    s.event('qualifying_conversion_completed', temperature_code=0x1900)
    assert s.read('CONFIG') & 0xC000 == 0x8000
    s.event('qualifying_conversion_completed', temperature_code=0x1700)
    assert s.read('CONFIG') & 0xC000 == 0


def test_tmp117_unordered_thresholds_not_a_valid_therm_fixture():
    s = Semantics('TMP117')
    s.write('CONFIG', 0x10)
    s.write('THIGH', 0x1800)
    s.write('TLOW', 0x2000)
    with pytest.raises(OutsideContract):
        s.event('qualifying_conversion_completed', temperature_code=0x1900)


def test_tmp117_completed_raw_measurement_updates_temp_register():
    s = Semantics('TMP117')
    s.write('THIGH', 0x2000)
    s.write('TLOW', 0x1800)
    s.event('qualifying_conversion_completed', temperature_code=0x2100)
    assert s.read('TEMP') == 0x2100
    assert s.read('CONFIG') & 0xE000 == 0x8000


def test_tmp117_strict_threshold_equalities():
    s = Semantics('TMP117')
    s.write('CONFIG', 0)
    s.write('THIGH', 0x2000)
    s.write('TLOW', 0x1800)
    s.event('qualifying_conversion_completed', temperature_code=0x2000)
    assert s.read('CONFIG') & 0xC000 == 0
    s.write('CONFIG', 0x10)
    s.event('qualifying_conversion_completed', temperature_code=0x2100)
    assert s.read('CONFIG') & 0xC000 == 0x8000
    s.event('qualifying_conversion_completed', temperature_code=0x1800)
    assert s.read('CONFIG') & 0xC000 == 0x8000
    s.event('qualifying_conversion_completed', temperature_code=0x1700)
    assert s.read('CONFIG') & 0xC000 == 0


def test_tmp117_locked_scratch_does_not_program_eeprom():
    # SNOSD82D p18: EUN=0 writes volatile; factory-image reset re-loads.
    s = Semantics('TMP117')
    s.write('THIGH', 0x1234)
    assert s.read('THIGH') == 0x1234
    assert s.read('EEPROM_UL') & 0xC000 == 0
    s.event('por_started')
    s.event('por_load_completed')
    assert s.read('THIGH') == 0x6000


def test_tmp117_programming_busy_guard_and_completion():
    s = Semantics('TMP117')
    s.write('EEPROM_UL', 0x8000)
    s.write('THIGH', 0x3456)
    assert s.read('EEPROM_UL') & 0xC000 == 0xC000
    assert s.read('CONFIG') & 0x1000 == 0x1000
    with pytest.raises(OutsideContract):
        s.write('TLOW', 0x1111)
    s.event('eeprom_program_completed')
    assert s.read('EEPROM_UL') & 0xC000 == 0x8000
    s.event('por_started')
    s.event('por_load_completed')
    assert s.read('THIGH') == 0x3456
    assert s.read('EEPROM_UL') & 0xC000 == 0


def test_tmp117_por_loading_write_ignore():
    s = Semantics('TMP117')
    s.write('THIGH', 0x1234)
    s.event('por_started')
    s.write('THIGH', 0x4321)
    assert s.read('THIGH') == 0x1234
    s.event('por_load_completed')
    assert s.read('THIGH') == 0x6000


@pytest.mark.parametrize('transaction,auto_increment', [('burst', False), ('single', True), ('burst', True)])
def test_tmp126_only_single_nonincrement_read_clears(transaction, auto_increment):
    s = Semantics('TMP126')
    s.event('qualifying_flag_event', fields=['CRC_FLAG', 'SLEW_FLAG', 'THIGH_FLAG', 'TLOW_FLAG'])
    assert s.read('ALERT_STATUS', transaction=transaction, auto_increment=auto_increment) & 0xA6 == 0xA6
    assert s.read('ALERT_STATUS') & 0xA6 == 0xA6
    assert s.read('ALERT_STATUS') & 0xA6 == 0


def test_tmp126_average_requires_eight_completed_samples():
    s = Semantics('TMP126')
    s.write('CONFIG', 0x98)  # AVG=1, ONE_SHOT=1, MODE=1.
    assert s.read('CONFIG') & 0x10 == 0
    for _ in range(7):
        s.event('conversion_sample_completed')
        assert s.read('ALERT_STATUS', auto_increment=True) & 1 == 0
    s.event('conversion_sample_completed')
    assert s.read('CONFIG') & 8 == 8
    assert s.read('ALERT_STATUS', auto_increment=True) & 1 == 1
    s.read('TEMP_RESULT')
    assert s.read('ALERT_STATUS', auto_increment=True) & 1 == 0


@pytest.mark.parametrize('reg', ['TEMP_LOW', 'TEMP_HIGH', 'HUM_LOW', 'HUM_HIGH', 'STATUS'])
def test_hdc_start_complete_and_each_cross_clear(reg):
    # SNAS773A p23: all five documented read addresses clear DRDY.
    s = Semantics('HDC2021')
    s.write('MEAS_CONFIG', 1)
    assert s.read('MEAS_CONFIG') & 1 == 1
    assert s.read('STATUS') & 0x80 == 0
    s.event('measurement_started')
    assert s.read('MEAS_CONFIG') & 1 == 0
    assert s.read('STATUS') & 0x80 == 0
    s.event('conversion_completed')
    if reg == 'STATUS':
        assert s.read(reg) & 0x80 == 0x80
    else:
        # Separate paired witness confirms the event produces a nonzero flag;
        # reading STATUS in the tested device would itself clear the flag.
        witness = Semantics('HDC2021')
        witness.write('MEAS_CONFIG', 1)
        witness.event('measurement_started')
        witness.event('conversion_completed')
        assert witness.read('STATUS') & 0x80 == 0x80
        s.read(reg)
    assert s.read('STATUS') & 0x80 == 0


def assert_bme_commit(s):
    s.write('ctrl_hum', 3)
    assert s.read('ctrl_hum') == 3
    assert s.active_humidity == 0
    s.write('ctrl_meas', 0)
    assert s.active_humidity == 3


def test_bme_humidity_requires_meas_commit():
    assert_bme_commit(Semantics('BME280'))


@pytest.mark.parametrize('chip,mode', [('BME280', 1), ('BME280', 2), ('BMP280', 1), ('BMP280', 2)])
def test_bosch_forced_encoding_and_completion(chip, mode):
    s = Semantics(chip)
    s.write('ctrl_meas', 0x24 | mode)
    assert s.read('status') & 8 == 8
    assert s.read('ctrl_meas') & 3 == mode
    with pytest.raises(OutsideContract):
        s.write('config', 0x24)
    s.event('measurement_completed')
    assert s.read('status') & 8 == 0
    assert s.read('ctrl_meas') & 3 == 0
    s.write('config', 0x24)
    assert s.read('config') == 0x24


@pytest.mark.parametrize('chip', ['BME280', 'BMP280'])
def test_bosch_normal_config_has_no_guaranteed_response(chip):
    s = Semantics(chip)
    s.write('ctrl_meas', 0x27)
    with pytest.raises(OutsideContract):
        s.write('config', 0x24)


def test_negative_eager_humidity_fixture_detected():
    class EagerHumidity(Semantics):
        def write(self, reg, value):
            super().write(reg, value)
            if reg == 'ctrl_hum':
                self.active_humidity = value
    with pytest.raises(AssertionError):
        assert_bme_commit(EagerHumidity('BME280'))


def test_negative_eager_alert_clear_fixture_detected():
    class EagerClear(Semantics):
        def read(self, reg, **kwargs):
            value = super().read(reg, **kwargs)
            if reg == 'TEMP':
                self._field('CONFIG', 'HIGH_ALERT', 0)
                self._field('CONFIG', 'LOW_ALERT', 0)
            return value
    with pytest.raises(AssertionError):
        assert_tmp117_alert_reads(EagerClear('TMP117'))


def test_negative_no_event_storage_fixture_detected():
    class NoEvents(Semantics):
        def event(self, name, **payload):
            pass
    with pytest.raises(AssertionError):
        assert_tmp117_alert_reads(NoEvents('TMP117'))


def test_negative_program_while_locked_fixture_detected():
    class IgnoresEun(Semantics):
        def write(self, reg, value):
            super().write(reg, value)
            if reg == 'THIGH':
                self.nvm[reg] = value
    s = IgnoresEun('TMP117')
    s.write('THIGH', 0x1234)
    s.event('por_started')
    s.event('por_load_completed')
    with pytest.raises(AssertionError):
        assert s.read('THIGH') == 0x6000


def test_negative_premature_hdc_ready_fixture_detected():
    class PrematureReady(Semantics):
        def event(self, name, **payload):
            super().event(name, **payload)
            if name == 'measurement_started':
                self._field('STATUS', 'DRDY_STATUS', 1)
    s = PrematureReady('HDC2021')
    s.write('MEAS_CONFIG', 1)
    s.event('measurement_started')
    with pytest.raises(AssertionError):
        assert s.read('STATUS') & 0x80 == 0


def test_negative_missing_hdc_cross_clear_fixture_detected():
    class MissingCrossClear(Semantics):
        def read(self, reg, **kwargs):
            if reg == 'TEMP_LOW':
                return self.values[reg]
            return super().read(reg, **kwargs)
    s = MissingCrossClear('HDC2021')
    s.write('MEAS_CONFIG', 1)
    s.event('measurement_started')
    s.event('conversion_completed')
    s.read('TEMP_LOW')
    with pytest.raises(AssertionError):
        assert s.read('STATUS') & 0x80 == 0


def test_negative_premature_average_fixture_detected():
    class PrematureAverage(Semantics):
        def event(self, name, **payload):
            if name == 'conversion_sample_completed':
                self._field('CONFIG', 'AVG', 0)
            super().event(name, **payload)
    s = PrematureAverage('TMP126')
    s.write('CONFIG', 0x98)
    s.event('conversion_sample_completed')
    with pytest.raises(AssertionError):
        assert s.read('ALERT_STATUS', auto_increment=True) & 1 == 0


@pytest.fixture
def compiler_inputs():
    src = ROOT.parent / 'independent_source_admission_20261012'
    policy = compiler.load(src / 'candidate_source_policy.json')
    inventory = compiler.load(ROOT.parent / 'protocol_v2_20261012/field_policy_inventory.json')
    ir_map = {p.name.removesuffix('_gold_ir.json'): compiler.load(p) for p in (src / 'candidate_ir').glob('*.json')}
    return ir_map, policy, inventory


@pytest.mark.parametrize('tamper', ['duplicate', 'mask', 'source', 'dimension', 'schema', 'reset'])
def test_compiler_rejects_tampered_source_mapping(compiler_inputs, tamper):
    ir_map, policy, inventory = compiler_inputs
    policy = copy.deepcopy(policy)
    if tamper == 'duplicate':
        policy['field_rules'][1] = copy.deepcopy(policy['field_rules'][0])
    elif tamper == 'mask':
        policy['field_rules'][0]['candidate_bit_mask'] = '0'
    elif tamper == 'source':
        policy['field_rules'][0]['source_sha256'] = '0' * 64
    elif tamper == 'dimension':
        del policy['field_rules'][0]['dimensions']['reset']
    elif tamper == 'schema':
        policy['schema'] = 'pretend-v2'
    else:
        policy['field_rules'][0]['candidate_reset'] = 1
    with pytest.raises(ValueError):
        compiler.validate_policy(ir_map, policy, inventory)


def test_no_execution_prose_pass_is_not_executable_pass(compiler_inputs):
    rows = compiler.validate_policy(*compiler_inputs)
    ledger = compiler.compile_ledger(rows, {})
    assert len(ledger) == 4004
    assert not any(r['executed_clauses'] for r in ledger)
    assert not any(r['whole_dimension_closed'] for r in ledger)
    assert compiler.production_gate(rows, ledger, generation_context={'complete': True})['production_generation_ready'] is False


@pytest.mark.parametrize('result', [{'status': 'PASS', 'assertions': 0}, {'status': 'FAIL', 'assertions': 1}])
def test_failed_or_empty_scenario_cannot_link(compiler_inputs, result):
    rows = compiler.validate_policy(*compiler_inputs)
    with pytest.raises(ValueError):
        compiler.compile_ledger(rows, {'tmp117_eeprom': result})


def test_conflicted_aspect_cannot_link(compiler_inputs):
    rows = copy.deepcopy(compiler.validate_policy(*compiler_inputs))
    row = next(r for r in rows if r['inventory_field_id'] == 'TMP117.THIGH.H')
    row['dimensions']['conditional_write']['evidence_class'] = 'SOURCE_CONFLICT'
    actual = compiler.load(ROOT / 'scenario_execution.json')['tmp117_eeprom']
    with pytest.raises(ValueError, match='Source-conflicted'):
        compiler.compile_ledger(rows, {'tmp117_eeprom': actual})


def test_hash_verifier_rejects_path_escape_and_wrong_hash(tmp_path):
    (tmp_path / 'input.json').write_text('{}', encoding='utf-8')
    for entries in ({'../escape.json': '0' * 64}, {'input.json': '0' * 64}):
        with pytest.raises(ValueError):
            compiler.verify_hashes(tmp_path, entries)


@pytest.mark.parametrize('tamper', ['unknown_id', 'no_checks', 'no_trace', 'wrong_count', 'wrong_expected', 'noninteger', 'no_events', 'no_nonzero_write', 'wrong_chip'])
def test_compiler_rejects_fabricated_execution_proof(compiler_inputs, tamper):
    rows = compiler.validate_policy(*compiler_inputs)
    actual = copy.deepcopy(compiler.load(ROOT / 'scenario_execution.json')['tmp117_eeprom'])
    name = 'tmp117_eeprom'
    if tamper == 'unknown_id':
        name = 'not_a_scenario'
    elif tamper == 'no_checks':
        actual.pop('checks')
    elif tamper == 'no_trace':
        actual.pop('trace')
    elif tamper == 'wrong_count':
        actual['assertions'] += 1
    elif tamper == 'wrong_expected':
        actual['checks'][0]['expected'] ^= 1
    elif tamper == 'noninteger':
        actual['checks'][0]['actual'] = 4660.0
    elif tamper == 'no_events':
        actual['trace'] = [r for r in actual['trace'] if r['op'] != 'event']
    elif tamper == 'wrong_chip':
        for r in actual['trace']:
            r['chip'] = 'BMP280'
    else:
        for r in actual['trace']:
            if r['op'] == 'write':
                r['value'] = 0
    with pytest.raises(ValueError):
        compiler.compile_ledger(rows, {name: actual})
