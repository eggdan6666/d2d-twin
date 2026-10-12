"""Separate v2 scorer. Eight aggregate dimensions, fresh instance per stimulus.

Only registers in the IR abstraction are tested. Runtime/analog/bus timing and
undefined encodings are outside the oracle. Original v1 harness stays frozen.
"""
import atexit
import importlib
import json
import os
from pathlib import Path
import sys

import pytest
from protocol_rules import Contract, bounds, number

ROOT = Path(os.environ['D2D_V2_ROOT'])
IR = json.loads((ROOT / 'ir' / os.environ['D2D_IR']).read_text(encoding='utf-8'))
POLICY = json.loads((ROOT / 'source_policy.json').read_text(encoding='utf-8'))
CONTRACT = Contract(IR, POLICY)
DEVICE = IR['device']
MASK = CONTRACT.mask
REGS = CONTRACT.regs
sys.path.insert(0, str(ROOT / 'rtl'))
sys.path.insert(0, str(Path(__file__).parent))
from base_sensor import BaseVirtualSensor

TRACE = {'protocol_version': POLICY['protocol_version'], 'chip': DEVICE,
         'applicability': CONTRACT.applicable(), 'assertions': [], 'stimuli': []}
DIAG_ENABLED = bool(os.environ.get('D2D_DIAG'))


@atexit.register
def flush():
    if not DIAG_ENABLED:
        return
    (Path(__file__).parent / 'd2d_diag.json').write_text(
        json.dumps(TRACE, ensure_ascii=False, indent=1), encoding='utf-8')


@pytest.fixture(scope='module')
def factory():
    module = importlib.import_module(DEVICE.lower() + '_simulator')
    cls = getattr(module, DEVICE + '_Simulator')
    def make():
        sensor = cls()
        assert isinstance(sensor, BaseVirtualSensor), 'Must inherit BaseVirtualSensor'
        return sensor
    # Keep import/constructor errors distinct from semantic failures.
    make()
    return make


def check(label, actual, expected, mask=MASK):
    assert mask, 'No nonempty known-bit oracle: ' + label
    actual, expected = int(actual) & mask, int(expected) & mask
    TRACE['assertions'].append({'label': label, 'actual': actual, 'expected': expected,
                                'known_mask': mask, 'passed': actual == expected})
    assert actual == expected, f'{label}: got {actual:#x}, expected {expected:#x}, mask={mask:#x}'


def eligible(name):
    if not CONTRACT.applicable()[name]:
        pytest.skip('No applicable nonempty source-contract assertion')


def apply(sensor, qualified, value):
    writes = CONTRACT.writes(qualified, value)
    preserved = []
    for addr, data in writes:
        rn = next(name for name, r in REGS.items()
                  if number(r.get('write_addr', r['addr'])) == addr)
        for f in REGS[rn].get('fields', []):
            if CONTRACT.field_policy(rn + '.' + f['name']).get('preserve_write'):
                fm = bounds(f)[2]
                before = int(sensor.read_register(number(REGS[rn]['addr'])))
                data = (data & ~fm) | (before & fm)
        preserved.append((addr, data))
    writes = preserved
    TRACE['stimuli'].append({'field': qualified, 'value': value, 'writes': writes})
    for addr, data in writes:
        sensor.write_register(addr, data)


def test_reset_values(factory):
    eligible('test_reset_values')
    sensor = factory()
    for rn, r in REGS.items():
        if r['access'] == 'W' or r.get('runtime_value') or not CONTRACT.known_mask(rn):
            continue
        check(rn + '.reset', sensor.read_register(number(r['addr'])),
              number(r['reset']), CONTRACT.known_mask(rn))


def test_readonly_protection(factory):
    eligible('test_readonly_protection')
    for rn, r in REGS.items():
        mask = CONTRACT.known_mask(rn, 'protection') & ~CONTRACT.read_clear_mask(rn)
        if r['access'] != 'RO' or not mask:
            continue
        sensor = factory()
        addr = number(r['addr'])
        sensor.read_register(addr)  # Drain read-clear flags before baseline.
        before = sensor.read_register(addr)
        dirty = (number(r.get('reset', '0x0')) & ~mask) | ((~int(before)) & mask)
        sensor.write_register(addr, dirty & MASK)
        sensor.read_register(addr)
        after = sensor.read_register(addr)
        check(rn + '.readonly', after, before, mask)


def test_rw_field_persistence(factory):
    eligible('test_rw_field_persistence')
    for qualified, value in CONTRACT.rw_cases():
        rn = qualified.split('.', 1)[0]
        f = CONTRACT.fields[qualified]
        sensor = factory()
        apply(sensor, qualified, value)
        got = sensor.read_register(number(REGS[rn]['addr']))
        _, lo, fm = bounds(f)
        check(qualified + f'.write({value})', got, CONTRACT.expected_value(qualified, value) << lo,
              fm & CONTRACT.known_mask(rn))
    for qualified, f in CONTRACT.ro_field_cases():
        rn = qualified.split('.', 1)[0]
        sensor = factory()
        addr = number(REGS[rn]['addr'])
        before = sensor.read_register(addr)
        hi, lo, fm = bounds(f)
        # Attempt to flip only this RO field; RW fields retain legal defaults.
        value = ((int(before) >> lo) ^ ((1 << (hi - lo + 1)) - 1)) & ((1 << (hi - lo + 1)) - 1)
        apply(sensor, qualified, value)
        check(qualified + '.readonly', sensor.read_register(addr), before,
              fm & CONTRACT.known_mask(rn))


def test_write_trigger_fields(factory):
    eligible('test_write_trigger_fields')
    for rn, r in REGS.items():
        if r['access'] != 'RW' or CONTRACT.register_policy(rn).get('exclude_writes'):
            continue
        for f in r.get('fields', []):
            qualified = rn + '.' + f['name']
            if f['access'] != 'RW' or f.get('read_as') is None or CONTRACT.excluded_field(qualified):
                continue
            if not bounds(f)[2] & CONTRACT.known_mask(rn) or max(CONTRACT.legal_values(qualified)) <= 0:
                continue
            sensor = factory()
            value = max(CONTRACT.legal_values(qualified))
            apply(sensor, qualified, value)
            _, lo, fm = bounds(f)
            check(qualified + '.trigger', sensor.read_register(number(r['addr'])),
                  number(f['read_as']) << lo, fm & CONTRACT.known_mask(rn))


def test_single_byte_semantics(factory):
    eligible('test_single_byte_semantics')
    rn = IR['single_byte_semantics']['test_register']
    r = REGS[rn]
    sensor = factory()
    addr, rst = number(r['addr']), number(r['reset'])
    sensor.write_register(addr, 0x01, nbytes=1)
    full = int(sensor.read_register(addr, nbytes=2)) & MASK
    check(rn + '.byte-write', full, (0x01 << 8) | (rst & 0xFF), CONTRACT.known_mask(rn))
    check(rn + '.byte-read', sensor.read_register(addr, nbytes=1), full >> 8, 0xFF)


def test_read_write_alias(factory):
    eligible('test_read_write_alias')
    for rn, r in REGS.items():
        if not r.get('write_addr') or CONTRACT.register_policy(rn).get('exclude_writes'):
            continue
        ra, wa = number(r['addr']), number(r['write_addr'])
        for f in r.get('fields', []):
            qualified = rn + '.' + f['name']
            if f['access'] != 'RW' or f.get('read_as') is not None or CONTRACT.excluded_field(qualified):
                continue
            if not bounds(f)[2] & CONTRACT.known_mask(rn):
                continue
            values = CONTRACT.stimulus_values(qualified)
            if len(values) <= 1:
                continue
            sensor = factory()
            value = next(v for v in values if v != f.get('reset', 0))
            apply(sensor, qualified, value)
            _, lo, fm = bounds(f)
            check(qualified + '.write-alias', sensor.read_register(ra), CONTRACT.expected_value(qualified, value) << lo,
                  fm & CONTRACT.known_mask(rn))
            before = sensor.read_register(ra)
            sensor.write_register(ra, number(r['reset']))
            check(rn + '.read-address-protection', sensor.read_register(ra), before,
                  CONTRACT.known_mask(rn) & ~CONTRACT.read_clear_mask(rn))


def test_clear_on_read(factory):
    eligible('test_clear_on_read')
    for rn, r in REGS.items():
        if not r.get('cor_addr') or not CONTRACT.known_mask(rn):
            continue
        sensor = factory()
        ra, ca = number(r['addr']), number(r['cor_addr'])
        known, clr = CONTRACT.known_mask(rn), MASK
        for f in r.get('fields', []):
            if f.get('cor_clears') is False:
                clr &= ~bounds(f)[2]
        v1, v2 = sensor.read_register(ra), sensor.read_register(ra)
        check(rn + '.ordinary-read-stable', v2, v1, known)
        vc = sensor.read_register(ca)
        # Source contract: return the same data, then clear specified bits.
        check(rn + '.cor-returned-data', vc, v1, known)
        if known & clr:
            check(rn + '.cor-cleared', sensor.read_register(ra), 0, known & clr)


def snapshot(sensor):
    return {rn: int(sensor.read_register(number(r['addr']))) & CONTRACT.known_mask(rn)
            & ~CONTRACT.read_clear_mask(rn) for rn, r in REGS.items() if r['access'] != 'W'
            and not r.get('runtime_value') and CONTRACT.known_mask(rn)}


def test_write_only_reset_key(factory):
    eligible('test_write_only_reset_key')
    for rn, r in REGS.items():
        if r['access'] != 'W' or not r.get('write_key'):
            continue
        sensor = factory()
        addr, key = number(r['addr']), number(r['write_key'])
        garbage = ((key ^ 0xFF) & MASK) or 1
        snapshot(sensor)
        initial = snapshot(sensor)
        # Perturb before both key variants: resetting on every write must fail.
        candidates = CONTRACT.perturbation_cases()
        assert candidates, rn + ': no legal perturbation for reset-key oracle'
        apply(sensor, *candidates[0])
        before = snapshot(sensor)
        assert before != initial, rn + ': preparation could not produce observable nondefault state'
        sensor.write_register(addr, garbage)
        assert snapshot(sensor) == before, rn + ': non-key write changed stable known state'
        sensor.write_register(addr, key)
        for name, value in snapshot(sensor).items():
            mask = CONTRACT.known_mask(name) & ~CONTRACT.read_clear_mask(name)
            check(rn + '.reset-key.' + name, value, number(REGS[name]['reset']), mask)
