"""Source-domain and mutation regressions for the separate candidate protocol.

Synthetic IR and deliberately faulty sensors below are test fixtures, not model
results or silicon evidence. Assertions state source-domain requirements rather
than replaying the helper's own validation method.
"""
import atexit
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'harness'))
from protocol_rules import Contract, bounds, number


def load_contract(chip):
    ir = json.loads((ROOT / 'ir' / (chip + '_gold_ir.json')).read_text(encoding='utf-8'))
    policies = json.loads((ROOT / 'source_policy.json').read_text(encoding='utf-8'))
    return Contract(ir, policies)


def load_harness(monkeypatch, chip):
    monkeypatch.setenv('D2D_V2_ROOT', str(ROOT))
    monkeypatch.setenv('D2D_IR', chip + '_gold_ir.json')
    spec = importlib.util.spec_from_file_location('policy_review_harness_' + chip,
                ROOT / 'harness/test_d2d_protocol_v2.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Direct function tests must not write the runner's execution diagnostics.
    atexit.unregister(module.flush)
    return module


def load_runner():
    spec = importlib.util.spec_from_file_location('policy_review_runner',
                ROOT.parents[1] / '_setup/run_protocol_v2.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def field(state, contract, qualified):
    rn = qualified.split('.', 1)[0]
    hi, lo, _ = bounds(contract.fields[qualified])
    return (state[rn] >> lo) & ((1 << (hi - lo + 1)) - 1)


def planned_states(contract):
    addresses = {number(r.get('write_addr', r['addr'])): rn
                 for rn, r in contract.regs.items()}
    for qualified, value in contract.rw_cases():
        state = {rn: number(r.get('reset', 0)) for rn, r in contract.regs.items()}
        for addr, data in contract.writes(qualified, value):
            state[addresses[addr]] = data
            yield qualified, value, copy.copy(state)


def synthetic_ir(registers):
    return {'device': 'SYNTHETIC', 'reg_width': 8, 'registers': registers}


def test_lis3dh_every_write_remains_in_a_defined_mode():
    contract = load_contract('LIS3DH')
    seen_odr = set()
    for qualified, value, state in planned_states(contract):
        odr = field(state, contract, 'CTRL_REG1.ODR')
        lp = field(state, contract, 'CTRL_REG1.LPen')
        hr = field(state, contract, 'CTRL_REG4.HR')
        assert odr in range(10), (qualified, value, state)
        assert not (lp and hr), (qualified, value, state)
        if odr == 8:
            assert lp == 1 and hr == 0, state
        assert state['CTRL_REG0'] & 0x7F == 0x10, state
        if qualified == 'CTRL_REG1.ODR':
            seen_odr.add(value)
    assert seen_odr == set(range(10)), 'ODR=8 must be safely covered, not silently omitted'


def test_lis3dh_undefined_odr_is_rejected():
    with pytest.raises((AssertionError, ValueError)):
        load_contract('LIS3DH').writes('CTRL_REG1.ODR', 15)


def test_ads1220_stimuli_never_enter_reserved_domains():
    contract = load_contract('ADS1220')
    for qualified, value, state in planned_states(contract):
        assert field(state, contract, 'CONFIG0.MUX') <= 14, (qualified, value)
        assert field(state, contract, 'CONFIG1.DR') <= 6, (qualified, value)
        assert field(state, contract, 'CONFIG1.MODE') <= 2, (qualified, value)
        assert field(state, contract, 'CONFIG3.I1MUX') <= 6, (qualified, value)
        assert field(state, contract, 'CONFIG3.I2MUX') <= 6, (qualified, value)
        assert state['CONFIG3'] & 1 == 0, state
        mux = field(state, contract, 'CONFIG0.MUX')
        if mux in (8, 9, 10, 11):
            assert field(state, contract, 'CONFIG0.PGA_BYPASS') == 1
            assert field(state, contract, 'CONFIG0.GAIN') <= 2
        if mux in (12, 13):
            assert field(state, contract, 'CONFIG0.PGA_BYPASS') == 1
        if field(state, contract, 'CONFIG2.FIFTY_SIXTY'):
            assert field(state, contract, 'CONFIG1.MODE') in (0, 1)
            assert field(state, contract, 'CONFIG1.DR') == 0


def test_ads1220_defined_high_codes_are_not_misclassified_reserved():
    cases = set(load_contract('ADS1220').rw_cases())
    assert ('CONFIG0.GAIN', 7) in cases  # gain128, p.43
    assert ('CONFIG2.VREF', 3) in cases  # analog supply, p.45
    assert ('CONFIG2.IDAC', 7) in cases  # 1500 uA, p.45
    assert not any(q == 'CONFIG3.RESERVED' for q, _ in cases)


@pytest.mark.parametrize('qualified,invalid', [
    ('CONFIG0.MUX', 15), ('CONFIG1.DR', 7), ('CONFIG1.MODE', 3),
    ('CONFIG3.I1MUX', 7), ('CONFIG3.I2MUX', 7), ('CONFIG3.RESERVED', 1),
])
def test_ads1220_explicit_undefined_inputs_have_no_oracle(qualified, invalid):
    with pytest.raises((AssertionError, ValueError)):
        load_contract('ADS1220').writes(qualified, invalid)


def test_hdc2021_legal_precision_and_unknown_access_are_separate():
    contract = load_contract('HDC2021')
    cases = set(contract.rw_cases())
    for key in ('MEAS_CONFIG.TACC', 'MEAS_CONFIG.HACC'):
        assert {v for q, v in cases if q == key} == {0, 1, 2}
    assert {v for q, v in cases if q == 'MEAS_CONFIG.MEAS_CONF'} == {0, 1}
    for rn in ('STATUS', 'INTERRUPT_ENABLE'):
        assert contract.known_mask(rn, 'reset') & 7 == 7
        assert contract.known_mask(rn, 'protection') & 7 == 0
    assert not any(q in ('STATUS.UNUSED', 'INTERRUPT_ENABLE.UNUSED')
                   for q, _ in contract.ro_field_cases())


def test_tmp117_unknown_revision_does_not_hide_identity_errors(monkeypatch):
    harness = load_harness(monkeypatch, 'TMP117')
    mask = harness.CONTRACT.known_mask('DEVICE_ID')
    assert mask == 0x0FFF
    harness.check('revision variants', 0xA117, 0x0117, mask)
    with pytest.raises(AssertionError):
        harness.check('identity mutation', 0xA116, 0x0117, mask)


def test_ina3221_conflicting_shunt_limit_has_no_write_oracle():
    contract = load_contract('INA3221')
    assert contract.known_mask('SHUNT_SUM_LIMIT') == 0x8001
    assert not any(q.startswith('SHUNT_SUM_LIMIT.') for q, _ in contract.rw_cases())
    assert not any(q.startswith('SHUNT_SUM_LIMIT.') for q, _ in contract.ro_field_cases())


@pytest.mark.parametrize('chip,qualified,expected', [
    ('TMP461', 'CONV_RATE.CR', set(range(10))),
    ('TMP461', 'CONSECUTIVE_ALERT.CONAL', {0, 1, 3, 7}),
    ('TMP461', 'DIGITAL_FILTER.DF', {0, 1, 2}),
    ('MPU6050', 'CONFIG.DLPF_CFG', set(range(7))),
    ('MPU6050', 'PWR_MGMT_1.CLKSEL', {0, 1, 2, 3, 4, 5, 7}),
    # p.29 prose explicitly requires Bits[4:3]=11; Table15 grouping is ambiguous.
    ('AD5592R', 'DAC_RD.DAC_RD_EN', {0, 3}),
    ('LIS2DW12', 'CTRL1.ODR', set(range(10))),
    ('LIS2DW12', 'CTRL1.MODE', {0, 1, 2}),
    ('LIS2DW12', 'FIFO_CTRL.FMODE', {0, 1, 3, 4, 6}),
])
def test_additional_reviewed_domains_exclude_undefined_codes(chip, qualified, expected):
    assert {v for q, v in load_contract(chip).rw_cases() if q == qualified} == expected


@pytest.mark.parametrize('normalize', [False, True])
def test_tmp117_mode2_readback_has_a_distinct_source_oracle(monkeypatch, normalize):
    harness = load_harness(monkeypatch, 'TMP117')
    monkeypatch.setattr(harness.CONTRACT, 'rw_cases', lambda: [('CONFIG.MOD', 2)])
    monkeypatch.setattr(harness.CONTRACT, 'ro_field_cases', lambda: [])
    address = number(harness.REGS['CONFIG']['addr'])
    _, lo, mask = bounds(harness.CONTRACT.fields['CONFIG.MOD'])
    class ModeStorage:
        def __init__(self):
            self.config = number(harness.REGS['CONFIG']['reset'])
        def write_register(self, addr, value, nbytes=2):
            assert addr == address
            self.config = value
        def read_register(self, addr, nbytes=2):
            assert addr == address
            if normalize and self.config & mask == 2 << lo:
                return self.config & ~mask
            return self.config
    if normalize:
        harness.test_rw_field_persistence(ModeStorage)
    else:
        with pytest.raises(AssertionError):
            harness.test_rw_field_persistence(ModeStorage)


@pytest.mark.parametrize('chip', ['AD5592R', 'ADS1220'])
def test_chips_without_ro_registers_skip_protection(chip):
    assert load_contract(chip).applicable()['test_readonly_protection'] is False


def test_known_reset_only_does_not_create_vacuous_ro_protection():
    ir = synthetic_ir([{'name': 'ONLY', 'addr': '0x00', 'access': 'RO', 'reset': '0x00',
            'fields': [{'name': 'U', 'bits': '7:0', 'access': 'UNSPEC', 'reset': 0}]}])
    policies = {'chips': {'SYNTHETIC': {'fields': {'ONLY.U': {'known_reset': True}}}}}
    contract = Contract(ir, policies)
    assert contract.applicable()['test_reset_values'] is True
    assert contract.applicable()['test_readonly_protection'] is False


def test_ro_read_clear_only_bits_do_not_create_vacuous_protection():
    ir = synthetic_ir([{'name': 'FLAGS', 'addr': '0x00', 'access': 'RO', 'reset': '0x01',
            'fields': [{'name': 'F', 'bits': '7:0', 'access': 'RO', 'reset': 1,
                        'read_action': 'clear'}]}])
    assert Contract(ir, {}).applicable()['test_readonly_protection'] is False


def test_excluded_alias_fields_do_not_create_vacuous_alias_dimension():
    ir = synthetic_ir([{'name': 'ALIAS', 'addr': '0x01', 'write_addr': '0x02',
            'access': 'RW', 'reset': '0x00',
            'fields': [{'name': 'U', 'bits': '7:0', 'access': 'UNSPEC', 'reset': 0}]}])
    assert Contract(ir, {}).applicable()['test_read_write_alias'] is False


def test_rw_with_no_known_output_does_not_create_vacuous_assertion():
    ir = synthetic_ir([{'name': 'RW', 'addr': '0x00', 'access': 'RW', 'reset': '0x00',
            'fields': [{'name': 'D', 'bits': '7:0', 'access': 'RW', 'reset': 0}]}])
    policies = {'chips': {'SYNTHETIC': {'registers': {'RW': {'known_mask': '0x00'}}}}}
    assert Contract(ir, policies).applicable()['test_rw_field_persistence'] is False


@pytest.mark.parametrize('dimension', ['trigger', 'alias', 'cor'])
def test_mixed_valid_and_zero_mask_cases_skip_only_the_unknown_case(monkeypatch, dimension):
    harness = load_harness(monkeypatch, 'AD5592R')
    regs = []
    for name, addr in [('KNOWN', 1), ('UNKNOWN', 3)]:
        r = {'name': name, 'addr': hex(addr), 'access': 'RW', 'reset': '0x00',
             'fields': [{'name': 'D', 'bits': '7:0', 'access': 'RW', 'reset': 0}]}
        if dimension == 'trigger':
            r['fields'][0]['read_as'] = 0
        if dimension == 'alias':
            r['write_addr'] = hex(addr + 1)
        if dimension == 'cor':
            r.update(access='RO', reset='0x01', cor_addr=hex(addr + 1))
            r['fields'][0].update(access='RO', reset=1)
        regs.append(r)
    contract = Contract(synthetic_ir(regs), {'chips': {'SYNTHETIC': {
                        'registers': {'UNKNOWN': {'known_mask': '0x00'}}}}})
    harness.CONTRACT, harness.REGS, harness.IR, harness.MASK = contract, contract.regs, contract.ir, contract.mask
    class GoodKnownStorage:
        def __init__(self):
            self.state = {number(r['addr']): number(r['reset']) for r in regs}
        def read_register(self, addr, nbytes=1):
            if dimension == 'cor' and addr in (2, 4):
                old = self.state[addr - 1]
                self.state[addr - 1] = 0
                return old
            return self.state.get(addr, 0)
        def write_register(self, addr, value, nbytes=1):
            if dimension == 'alias' and addr in (2, 4):
                self.state[addr - 1] = value
    functions = {'trigger': harness.test_write_trigger_fields,
                 'alias': harness.test_read_write_alias,
                 'cor': harness.test_clear_on_read}
    functions[dimension](GoodKnownStorage)
    assert harness.TRACE['assertions']
    assert all(t['known_mask'] for t in harness.TRACE['assertions'])
    assert not any(t['label'].startswith('UNKNOWN.') for t in harness.TRACE['assertions'])


def test_byte_dimension_requires_known_output():
    ir = synthetic_ir([{'name': 'BYTE', 'addr': '0x01', 'access': 'RW', 'reset': '0x00',
              'fields': [{'name': 'D', 'bits': '7:0', 'access': 'RW', 'reset': 0}]}])
    ir['single_byte_semantics'] = {'test_register': 'BYTE', 'applies_to': 'all'}
    policies = {'chips': {'SYNTHETIC': {'registers': {'BYTE': {'known_mask': '0x00'}}}}}
    assert Contract(ir, policies).applicable()['test_single_byte_semantics'] is False


def test_reset_key_with_no_legal_observable_perturbation_is_inapplicable():
    ir = synthetic_ir([
        {'name': 'ID', 'addr': '0x00', 'access': 'RO', 'reset': '0x17',
         'fields': [{'name': 'D', 'bits': '7:0', 'access': 'RO', 'reset': 23}]},
        {'name': 'KEY', 'addr': '0x01', 'access': 'W', 'reset': '0x00',
         'write_key': '0xB6', 'fields': []},
    ])
    assert Contract(ir, {}).applicable()['test_write_only_reset_key'] is False


def test_readback_normalization_cannot_create_a_false_reset_perturbation():
    ir = synthetic_ir([
        {'name': 'MODE', 'addr': '0x00', 'access': 'RW', 'reset': '0x00',
         'fields': [{'name': 'M', 'bits': '1:0', 'access': 'RW', 'reset': 0}]},
        {'name': 'KEY', 'addr': '0x01', 'access': 'W', 'reset': '0x00',
         'write_key': '0xB6', 'fields': []},
    ])
    policies = {'chips': {'SYNTHETIC': {'fields': {'MODE.M': {
        'legal_values': [0, 2], 'readback_values': {'2': 0}}}}}}
    # Both legal writes read0: neither creates dirty state for a reset command.
    assert Contract(ir, policies).applicable()['test_write_only_reset_key'] is False


def test_clear_on_read_must_return_flags_before_clearing(monkeypatch):
    harness = load_harness(monkeypatch, 'TPS23861')
    class ReturnsClearedValue:
        def __init__(self):
            self.state = {number(r['addr']): number(r.get('reset', 0))
                          for r in harness.REGS.values()}
        def read_register(self, addr, nbytes=1):
            for r in harness.REGS.values():
                if r.get('cor_addr') and addr == number(r['cor_addr']):
                    self.state[number(r['addr'])] = 0
                    return 0  # Wrong: SUPPLY_EVENT should return its pending0x30.
            return self.state.get(addr, 0)
    with pytest.raises(AssertionError):
        harness.test_clear_on_read(ReturnsClearedValue)


@pytest.mark.parametrize('mode', ['never', 'every'])
def test_reset_key_rejects_noop_and_any_write_reset_mutants(monkeypatch, mode):
    harness = load_harness(monkeypatch, 'AD5592R')
    class FaultyReset:
        def __init__(self):
            self.defaults = {number(r['addr']): number(r.get('reset', 0))
                             for r in harness.REGS.values() if r['access'] != 'W'}
            self.state = dict(self.defaults)
        def read_register(self, addr, nbytes=2):
            return self.state.get(addr, 0)
        def write_register(self, addr, value, nbytes=2):
            command = next((r for r in harness.REGS.values()
                            if r['access'] == 'W' and number(r['addr']) == addr), None)
            if command:
                if mode == 'every':
                    self.state = dict(self.defaults)
                return
            self.state[addr] = value
    with pytest.raises(AssertionError):
        harness.test_write_only_reset_key(FaultyReset)


def test_timeout_never_reuses_old_success_evidence(monkeypatch, tmp_path):
    runner = load_runner()
    monkeypatch.setattr(runner, 'OUT', tmp_path)
    harness = tmp_path / 'harness'
    harness.mkdir()
    for filename in ('protocol_rules.py', 'test_d2d_protocol_v2.py'):
        (harness / filename).write_text('# isolated fixture', encoding='utf-8')
    folder = tmp_path / 'work/reference/SYNTHETIC/0_0'
    folder.mkdir(parents=True)
    (folder / 'result.xml').write_text(
        '<testsuite><testcase name="old_success"/></testsuite>', encoding='utf-8')
    (folder / 'd2d_diag.json').write_text(
        json.dumps({'assertions': [{'passed': True}], 'stimuli': [{}]}), encoding='utf-8')
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired('synthetic pytest fixture', 90)
    monkeypatch.setattr(runner.subprocess, 'run', timeout)
    result = runner.run_one(('reference', 'SYNTHETIC', 0, 0, '# fixture', {}))
    assert result['rc'] == 124
    assert result['tests'] == [], 'Timeout must not inherit previous passing cases'
    assert result['assertions_executed'] == 0
    assert result['stimuli_executed'] == 0


def test_changed_protocol_cannot_reuse_stale_reference_admission(monkeypatch, tmp_path):
    runner = load_runner()
    monkeypatch.setattr(runner, 'OUT', tmp_path)
    monkeypatch.setattr(runner, 'verify', lambda: None)
    (tmp_path / 'ir').mkdir()
    (tmp_path / 'protocol_manifest.json').write_text('{"version":"changed"}', encoding='utf-8')
    (tmp_path / 'reference_results.json').write_text(
        json.dumps([{'rc': 0} for _ in range(20)]), encoding='utf-8')
    (tmp_path / 'reference_execution_manifest.json').write_text(
        json.dumps({'protocol_manifest_sha256': 'a_previous_protocol_hash',
                    'status': 'EXECUTED_LOCAL'}), encoding='utf-8')
    with pytest.raises((AssertionError, ValueError)):
        runner.run(models=True)
