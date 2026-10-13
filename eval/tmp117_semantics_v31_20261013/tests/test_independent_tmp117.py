"""Independent source-derived TMP117 fault checks.

Expected constants are from SNOSD82D pp12,14-15,18,25-32; they are not
computed from candidate rules or root scenario outputs. Synthetic faults are
negative fixtures, not empirical LLM samples. No physical time is modeled.
"""
import copy
import importlib.util
from pathlib import Path
import json
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('independent_tmp117_v31', ROOT / 'tmp117.py')
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
Semantics, OutsideContract = runtime.Semantics, runtime.OutsideContract
sys.path.insert(0, str(ROOT))
import scenarios as witness_scenarios
import admission as admission_module

FACTORY = {'CONFIG': 0x0220, 'THIGH': 0x6000, 'TLOW': 0x8000, 'TEMP_OFFSET': 0}
MASKS = {'CONFIG': 0x07FC, 'THIGH': 0xFFFF, 'TLOW': 0xFFFF, 'TEMP_OFFSET': 0xFFFF}
CUSTOM = {'CONFIG': 0x057C, 'THIGH': 0x4A31, 'TLOW': 0xC523, 'TEMP_OFFSET': 0xFF81}
AVG_COUNTS = (1, 8, 32, 64)


def masked(s, register, mask):
    return s.read_masked(register, mask)


def reload(s):
    s.event('general_call_reset_started')
    s.event('por_load_completed')


def start(s, avg=0, mode=3, conv=0, offset=0):
    s.write('TEMP_OFFSET', offset)
    s.write('CONFIG', (mode << 10) | (conv << 7) | (avg << 5))
    s.event('conversion_started')


def sample(s, value):
    s.event('conversion_sample_completed', temperature_code=value)


def snapshot(s):
    return copy.deepcopy(vars(s))


def rejection_atomic(s, operation):
    before = snapshot(s)
    with pytest.raises(OutsideContract):
        operation()
    assert snapshot(s) == before


@pytest.mark.parametrize('register', tuple(MASKS))
def test_factory_image_is_explicit_and_locked_writes_are_volatile(register):
    # SNOSD82D p18, p25 footnote(1), p30 Table7-10.
    s = Semantics()
    value = CUSTOM[register]
    s.write(register, value)
    assert masked(s, register, MASKS[register]) == value
    assert s.read('EEPROM_UL') == 0
    reload(s)
    assert masked(s, register, MASKS[register]) == FACTORY[register]
    assert s.read('EEPROM_UL') == 0


@pytest.mark.parametrize('register', tuple(MASKS))
def test_completed_programming_reloads_customer_value_not_later_scratch(register):
    s = Semantics()
    s.write('EEPROM_UL', 0x8000)
    s.write(register, CUSTOM[register])
    assert masked(s, 'CONFIG', 0x1000) == 0x1000
    assert s.read('EEPROM_UL') & 0xC000 == 0xC000
    rejection_atomic(s, lambda: s.write('THIGH', 0x1111))
    s.event('eeprom_program_completed')
    assert masked(s, 'CONFIG', 0x1000) == 0
    assert s.read('EEPROM_UL') & 0xC000 == 0x8000
    reload(s)  # Establish known activation via sourced programming sequence.
    s.write(register, (CUSTOM[register] ^ MASKS[register]) & MASKS[register])
    reload(s)
    assert masked(s, register, MASKS[register]) == CUSTOM[register]
    assert s.read('EEPROM_UL') == 0


@pytest.mark.parametrize('config', [0x0020, 0x041C, 0x07FC])
def test_customer_nv_constructor_loads_supplied_config_and_limits(config):
    image = dict(CUSTOM, CONFIG=config)
    s = Semantics(eeprom_image=image)
    assert masked(s, 'CONFIG', 0x07FC) == config
    for reg in ('THIGH', 'TLOW', 'TEMP_OFFSET'):
        assert s.read(reg) == image[reg]
    assert s.read('TEMP') == 0x8000
    assert s.read('EEPROM_UL') == 0


def test_constructor_must_not_retain_mutable_image_alias():
    image = dict(CUSTOM)
    s = Semantics(eeprom_image=image)
    image['THIGH'] = 1
    reload(s)
    assert s.read('THIGH') == CUSTOM['THIGH']


def test_config_one_shot_mod1_is_not_persistent():
    # p28 note(2), p15: programmed11 starts in shutdown, not one-shot.
    s = Semantics()
    s.write('EEPROM_UL', 0x8000)
    s.write('CONFIG', 0x0C7C)
    s.event('eeprom_program_completed')
    reload(s)
    assert masked(s, 'CONFIG', 0x07FC) == 0x047C
    assert s.operating_mode == 'shutdown'
    rejection_atomic(s, lambda: s.event('conversion_started'))


@pytest.mark.parametrize('register', ['CONFIG', 'THIGH', 'TLOW'])
def test_initial_por_write_ignore_is_limited_to_source_named_registers(register):
    s = Semantics()
    s.event('por_started')
    before = snapshot(s)
    s.write(register, CUSTOM[register])
    assert s.values == before['values']
    assert s.nvm == before['nvm']
    assert masked(s, 'CONFIG', 0x1000) == 0x1000
    s.event('por_load_completed')
    assert masked(s, register, MASKS[register]) == FACTORY[register]


@pytest.mark.parametrize('register', ['TEMP_OFFSET', 'EEPROM_UL'])
def test_unsourced_por_write_response_is_excluded_atomically(register):
    s = Semantics()
    s.event('por_started')
    rejection_atomic(s, lambda: s.write(register, 1))


@pytest.mark.parametrize('avg,count', list(enumerate(AVG_COUNTS)))
@pytest.mark.parametrize('conv', [0, 7])
def test_one_shot_complete_count_avg_and_conv_independence(avg, count, conv):
    s = Semantics()
    start(s, avg=avg, conv=conv)
    assert masked(s, 'CONFIG', 0x2000) == 0
    for _ in range(count - 1):
        sample(s, 0x1234)
        assert masked(s, 'CONFIG', 0x2000) == 0
        assert s.read('TEMP') == 0x8000
    sample(s, 0x1234)
    assert masked(s, 'CONFIG', 0x2000) == 0x2000
    assert s.read('TEMP') == 0x1234
    assert s.operating_mode == 'shutdown'
    # Exclude exact post-one-shot MOD readback; operational state is distinct.
    rejection_atomic(s, lambda: sample(s, 0x1234))
    rejection_atomic(s, lambda: s.event('conversion_started'))


@pytest.mark.parametrize('avg,count', list(enumerate(AVG_COUNTS))[1:])
def test_accumulated_signed_average_not_last_sample_or_running_mean(avg, count):
    s = Semantics()
    start(s, avg=avg)
    # Alternate -257 and -255: an exact signed mean of -256.
    for i in range(count):
        sample(s, 0xFEFF if i % 2 == 0 else 0xFF01)
    assert s.read('TEMP') == 0xFF00


@pytest.mark.parametrize('mode', [0, 2])
def test_continuous_average_cycles_are_accumulated_and_restart_without_old_samples(mode):
    s = Semantics()
    start(s, avg=1, mode=mode)
    assert masked(s, 'CONFIG', 0x0C00) == 0
    for value in [1000] * 7 + [1008]:
        sample(s, value)
    assert s.read('TEMP') == 1001
    assert s.operating_mode == 'continuous'
    s.event('conversion_started')
    for value in [2000] * 7 + [2008]:
        sample(s, value)
    assert s.read('TEMP') == 2001


@pytest.mark.parametrize('code,offset,expected', [
    (0x0100, 0xFF80, 0x0080),
    (0xFF00, 0x0080, 0xFF80),
    (0x7FF0, 0x0020, 0x7FFF),
    (0x8010, 0xFFE0, 0x8000),
])
def test_signed_offset_and_saturation_use_source_numeric_boundary(code, offset, expected):
    s = Semantics()
    start(s, offset=offset)
    sample(s, code)
    assert s.read('TEMP') == expected


def test_nonintegral_average_is_unknown_not_silent_rounding():
    s = Semantics()
    start(s, avg=1)
    for _ in range(7):
        sample(s, 1000)
    rejection_atomic(s, lambda: sample(s, 1001))
    sample(s, 1008)  # Retry lawful exact result after rejected last sample.
    assert s.read('TEMP') == 1001


def test_shutdown_abort_disposes_pending_samples_and_allows_fresh_one_shot():
    s = Semantics()
    start(s, avg=1)
    for _ in range(3):
        sample(s, 0x4000)
    s.write('CONFIG', 0x0420)  # Preserve AVG1 while requesting sourced MOD01 abort.
    rejection_atomic(s, lambda: sample(s, 0x4000))
    assert s.read('TEMP') == 0x8000
    start(s)
    sample(s, 0x0100)
    assert s.read('TEMP') == 0x0100


@pytest.mark.parametrize('register', ['THIGH', 'TLOW', 'TEMP_OFFSET'])
def test_unimplemented_mid_conversion_writes_do_not_partially_change_state(register):
    s = Semantics()
    start(s, avg=1)
    rejection_atomic(s, lambda: s.write(register, 1))


def test_busy_programming_and_unlocked_conversion_are_not_fabricated_oracles():
    s = Semantics()
    s.write('EEPROM_UL', 0x8000)
    rejection_atomic(s, lambda: s.event('conversion_started'))
    s.write('THIGH', 1)
    rejection_atomic(s, lambda: s.event('general_call_reset_started'))
    rejection_atomic(s, lambda: s.event('por_started'))
    rejection_atomic(s, lambda: s.event('conversion_started'))


@pytest.mark.parametrize('register', ['CONFIG', 'TEMP'])
def test_nonzero_data_ready_return_before_clear_with_unknown_mod(register):
    s = Semantics()
    start(s)
    sample(s, 0x1234)
    assert s.values['CONFIG'] & 0x2000
    if register == 'CONFIG':
        assert masked(s, 'CONFIG', 0x2000) == 0x2000
    else:
        assert s.read('TEMP') == 0x1234
    assert masked(s, 'CONFIG', 0x2000) == 0


def test_unknown_mod_cannot_be_manufactured_by_full_config_read():
    s = Semantics()
    start(s)
    rejection_atomic(s, lambda: s.read('CONFIG'))
    sample(s, 0x1234)
    rejection_atomic(s, lambda: s.read('CONFIG'))
    assert masked(s, 'CONFIG', 0x2000) == 0x2000


@pytest.mark.parametrize('operation', [
    lambda s: s.write('THIGH', True),
    lambda s: s.write('THIGH', -1),
    lambda s: s.write('THIGH', 65536),
    lambda s: s.write('THIGH', 1.0),
    lambda s: s.write('NOT_A_REGISTER', 1),
    lambda s: s.write('CONFIG', 2),
    lambda s: s.write('CONFIG', 1),
    lambda s: s.write('CONFIG', 0x8000),
    lambda s: s.read('DEVICE_ID'),
    lambda s: s.read('EEPROM1'),
    lambda s: s.read_masked('DEVICE_ID', 0xFFFF),
    lambda s: s.read_masked('CONFIG', True),
    lambda s: s.read_masked('CONFIG', 0),
    lambda s: s.read_masked('CONFIG', 0x10000),
    lambda s: s.event('pretend_conversion'),
    lambda s: s.event('por_started', unused=1),
    lambda s: s.event('conversion_sample_completed'),
    lambda s: s.event('eeprom_program_completed'),
])
def test_outside_contract_inputs_are_atomic(operation):
    s = Semantics()
    rejection_atomic(s, lambda: operation(s))


@pytest.mark.parametrize('payload', [
    {'temperature_code': True}, {'temperature_code': -1},
    {'temperature_code': 65536}, {'temperature_code': 1.0},
    {'temperature_code': '1234'}, {'temperature_code': 1234, 'extraneous': 1},
])
def test_malformed_sample_does_not_consume_a_conversion(payload):
    s = Semantics()
    start(s, avg=1)
    for _ in range(7):
        sample(s, 1000)
    rejection_atomic(s, lambda: s.event('conversion_sample_completed', **payload))
    sample(s, 1008)
    assert s.read('TEMP') == 1001


def test_known_device_id_submask_without_revision_oracle():
    s = Semantics()
    assert masked(s, 'DEVICE_ID', 0x0FFF) == 0x0117
    rejection_atomic(s, lambda: s.read('DEVICE_ID'))


def test_mode_change_with_latched_history_has_no_invented_transition_oracle():
    s = Semantics()
    s.write('CONFIG', 0)
    s.write('THIGH', 0x0100)
    s.write('TLOW', 0xFF00)
    s.event('conversion_started')
    sample(s, 0x0200)
    rejection_atomic(s, lambda: s.write('CONFIG', 0x10))
    assert masked(s, 'CONFIG', 0xC000) == 0x8000
    s.write('CONFIG', 0x10)  # Fresh cleared history baseline is in scope.
    assert masked(s, 'CONFIG', 0xC000) == 0


def test_alert_high_and_low_accumulate_until_config_read_not_temp_read():
    # Table7-6 p27 and alert mode p16; nonzero signed threshold events.
    s = Semantics()
    s.write('CONFIG', 0)
    s.write('THIGH', 0x0100)
    s.write('TLOW', 0xFF00)
    s.event('conversion_started')
    sample(s, 0x0200)
    assert s.read('TEMP') == 0x0200
    s.event('conversion_started')
    sample(s, 0xFE00)
    assert s.read('TEMP') == 0xFE00
    assert masked(s, 'CONFIG', 0xC000) == 0xC000
    assert masked(s, 'CONFIG', 0xC000) == 0


def test_therm_hysteresis_uses_strict_signed_boundaries_and_retains_config_reads():
    s = Semantics()
    s.write('CONFIG', 0x10)
    s.write('THIGH', 0x0100)
    s.write('TLOW', 0xFF00)
    for code, expected in [(0x0100, 0), (0x0200, 0x8000), (0xFF00, 0x8000),
                           (0xFE00, 0), (0x0100, 0)]:
        s.event('conversion_started')
        sample(s, code)
        assert masked(s, 'CONFIG', 0xC000) == expected
        assert masked(s, 'CONFIG', 0xC000) == expected


def test_offset_adjusted_result_drives_limit_flags():
    s = Semantics()
    s.write('THIGH', 0x0101)
    s.write('TLOW', 0xFF00)
    start(s, offset=0x10)
    sample(s, 0x0100)
    assert s.read('TEMP') == 0x0110
    assert masked(s, 'CONFIG', 0xC000) == 0x8000


@pytest.mark.parametrize('pol', [0, 1])
@pytest.mark.parametrize('dr_select', [0, 1])
@pytest.mark.parametrize('tna', [0, 1])
def test_logical_alert_selection_polarity_and_mode_dependent_read_clear(pol, dr_select, tna):
    # p27 POL/DR_Alert/TNA and pp16-17; abstract level, no electrical proof.
    s = Semantics()
    s.write('THIGH', 0x0100)
    s.write('TLOW', 0xFF00)
    s.write('CONFIG', 0x0C00 | (pol << 3) | (dr_select << 2) | (tna << 4))
    assert s.alert_level() == 1 - pol
    s.event('conversion_started')
    sample(s, 0x0200)
    assert s.alert_level() == pol
    assert s.read('TEMP') == 0x0200
    assert s.alert_level() == (1 - pol if dr_select else pol)
    assert masked(s, 'CONFIG', 0xC000) == 0x8000
    assert s.alert_level() == (pol if tna and not dr_select else 1 - pol)


def test_alert_pin_observation_is_blocked_for_unknown_program_activation():
    s = Semantics()
    s.write('EEPROM_UL', 0x8000)
    s.write('CONFIG', 0x047C)
    rejection_atomic(s, lambda: s.alert_level())


@pytest.mark.parametrize('reg', [[], {}, None, 1, True])
@pytest.mark.parametrize('operation', ['write', 'read', 'read_masked'])
def test_malformed_register_identity_is_rejected_consistently_without_mutation(reg, operation):
    s = Semantics()
    if operation == 'write':
        call = lambda: s.write(reg, 1)
    elif operation == 'read_masked':
        call = lambda: s.read_masked(reg, 1)
    else:
        call = lambda: s.read(reg)
    rejection_atomic(s, call)


@pytest.mark.parametrize('avg', [1, 2, 3])
def test_undefined_offset_and_average_order_cannot_be_certified_by_python_code(avg):
    s = Semantics()
    s.write('TEMP_OFFSET', 1)
    s.write('CONFIG', 0x0C00 | (avg << 5))
    rejection_atomic(s, lambda: s.event('conversion_started'))


@pytest.mark.parametrize('value', [0x0C20, 0x0CA0, 0x0060])
def test_active_retrigger_and_schedule_changes_are_atomic_scope_exclusions(value):
    s = Semantics()
    start(s, avg=1)
    sample(s, 1000)
    rejection_atomic(s, lambda: s.write('CONFIG', value))


@pytest.mark.parametrize('register', tuple(MASKS))
def test_intermediate_programmed_target_value_has_no_invented_readback(register):
    s = Semantics()
    s.write('EEPROM_UL', 0x8000)
    s.write(register, CUSTOM[register])
    rejection_atomic(s, lambda: s.read(register))
    s.event('eeprom_program_completed')
    rejection_atomic(s, lambda: s.read(register))
    reload(s)
    assert masked(s, register, MASKS[register]) == CUSTOM[register]


# Table7-7 printed p28, copied independently as nominal metadata, no timing test.
NOMINAL_TABLE = [
    [15.5, 125, 500, 1000], [125, 125, 500, 1000],
    [250, 250, 500, 1000], [500, 500, 500, 1000],
    [1000, 1000, 1000, 1000], [4000, 4000, 4000, 4000],
    [8000, 8000, 8000, 8000], [16000, 16000, 16000, 16000],
]


@pytest.mark.parametrize('conv', range(8))
@pytest.mark.parametrize('avg', range(4))
def test_conversion_table_is_explicit_nominal_metadata_not_completion_oracle(conv, avg):
    s = Semantics()
    s.write('CONFIG', (conv << 7) | (avg << 5))
    assert s.nominal_cc_cycle_ms() == NOMINAL_TABLE[conv][avg]
    assert masked(s, 'CONFIG', 0x2000) == 0
    assert s.read('TEMP') == 0x8000


@pytest.mark.parametrize('image', [
    {}, dict(CUSTOM, UNKNOWN=0), dict(CUSTOM, CONFIG=0x0800),
    dict(CUSTOM, CONFIG=2), dict(CUSTOM, THIGH=True),
    dict(CUSTOM, TLOW=65536), dict(CUSTOM, TEMP_OFFSET=-1),
])
def test_nv_image_requires_exact_scope_and_known_safe_bits(image):
    with pytest.raises(OutsideContract):
        Semantics(eeprom_image=image)


def assert_locked_reload(factory):
    s = factory()
    s.write('THIGH', 0x1234)
    reload(s)
    assert s.read('THIGH') == 0x6000


def assert_program_not_committed_before_complete(factory):
    s = factory()
    s.write('EEPROM_UL', 0x8000)
    before = copy.deepcopy(s.nvm)
    s.write('THIGH', 0x1234)
    # The internal oracle is declared NVM state, not a physical register read.
    # Its lifecycle distinguishes a programming request from completion.
    assert s.nvm == before


def assert_both_busy_mirrors(factory):
    s = factory()
    s.write('EEPROM_UL', 0x8000)
    s.write('TLOW', 0x8123)
    assert masked(s, 'CONFIG', 0x1000) == 0x1000
    assert s.read('EEPROM_UL') & 0x4000 == 0x4000


def assert_config_persists_only_masked_bits(factory):
    s = factory()
    s.write('EEPROM_UL', 0x8000)
    s.write('CONFIG', 0x0C7C)
    s.event('eeprom_program_completed')
    assert s.nvm['CONFIG'] == 0x047C
    reload(s)
    assert s.operating_mode == 'shutdown'


def assert_no_premature_dr(factory):
    s = factory()
    start(s, avg=1)
    assert masked(s, 'CONFIG', 0x2000) == 0
    sample(s, 1000)
    assert masked(s, 'CONFIG', 0x2000) == 0
    assert s.read('TEMP') == 0x8000


def assert_signed_accumulated_average(factory):
    s = factory()
    start(s, avg=1)
    for i in range(8):
        sample(s, 0xFEFF if i % 2 == 0 else 0xFF01)
    assert s.read('TEMP') == 0xFF00


def assert_operational_shutdown(factory):
    s = factory()
    start(s)
    sample(s, 0x0100)
    assert s.operating_mode == 'shutdown'


def assert_signed_negative_offset(factory):
    s = factory()
    start(s, offset=0xFF80)
    sample(s, 0x0100)
    assert s.read('TEMP') == 0x0080


def assert_offset_saturates_not_wraps(factory):
    s = factory()
    start(s, offset=0x0020)
    sample(s, 0x7FF0)
    assert s.read('TEMP') == 0x7FFF


def assert_bad_sample_atomic(factory):
    s = factory()
    start(s, avg=1)
    rejection_atomic(s, lambda: sample(s, True))


def assert_unknown_mod_excluded(factory):
    s = factory()
    start(s)
    with pytest.raises(OutsideContract):
        s.read('CONFIG')


def assert_por_restores_temp_sentinel(factory):
    s = factory()
    start(s)
    sample(s, 0x1234)
    reload(s)
    assert s.read('TEMP') == 0x8000


def assert_alert_polarity(factory):
    s = factory()
    s.write('CONFIG', 0x0C08)
    assert s.alert_level() == 0
    s.event('conversion_started')
    sample(s, 0x7000)
    assert s.alert_level() == 1


def assert_dr_selection_not_alert_flags(factory):
    s = factory()
    s.write('CONFIG', 0x0C04)
    s.event('conversion_started')
    sample(s, 0x7000)
    assert s.alert_level() == 0
    s.read('TEMP')
    assert s.alert_level() == 1


def assert_therm_config_read_retains_logical_alert(factory):
    s = factory()
    s.write('CONFIG', 0x0C10)
    s.event('conversion_started')
    sample(s, 0x7000)
    assert s.alert_level() == 0
    assert masked(s, 'CONFIG', 0x8000) == 0x8000
    assert s.alert_level() == 0


class LockedWritePersists(Semantics):
    def write(self, reg, value):
        locked = self.field('EEPROM_UL', 'EUN') == 0
        super().write(reg, value)
        if locked and reg == 'THIGH':
            self.nvm[reg] = value


class ProgrammingCommitsEarly(Semantics):
    def write(self, reg, value):
        super().write(reg, value)
        if self.phase == 'programming':
            target, data = self.pending
            self.nvm[target] = data


class MissingBusyMirror(Semantics):
    def write(self, reg, value):
        super().write(reg, value)
        if self.phase == 'programming':
            self.values['EEPROM_UL'] &= ~0x4000


class Mod1Persists(Semantics):
    def event(self, name, **payload):
        target = self.pending[0] if self.pending else None
        super().event(name, **payload)
        if name == 'eeprom_program_completed' and target == 'CONFIG':
            self.nvm['CONFIG'] |= 0x0800


class PrematureDataReady(Semantics):
    def event(self, name, **payload):
        super().event(name, **payload)
        if name == 'conversion_started':
            self.values['CONFIG'] |= 0x2000


class WrongAverageCount(Semantics):
    def event(self, name, **payload):
        super().event(name, **payload)
        if name == 'conversion_started':
            self.required_samples = 1


class LastSampleOnly(Semantics):
    def event(self, name, **payload):
        super().event(name, **payload)
        if name == 'conversion_sample_completed' and self.conversion_state == 'idle':
            self.values['TEMP'] = payload['temperature_code']


class NoAutomaticShutdown(Semantics):
    def event(self, name, **payload):
        was_one_shot = self.operating_mode == 'one_shot'
        super().event(name, **payload)
        if name == 'conversion_sample_completed' and was_one_shot:
            self.operating_mode = 'continuous'


class OffsetUnsigned(Semantics):
    def event(self, name, **payload):
        super().event(name, **payload)
        if name == 'conversion_started':
            self.offset_at_start = self.values['TEMP_OFFSET']


class OffsetWraps(Semantics):
    def event(self, name, **payload):
        super().event(name, **payload)
        if name == 'conversion_sample_completed' and self.conversion_state == 'idle':
            self.values['TEMP'] = (payload['temperature_code'] + self.offset_at_start) & 0xFFFF


class RejectedSampleMutates(Semantics):
    def event(self, name, **payload):
        try:
            return super().event(name, **payload)
        except OutsideContract:
            if name == 'conversion_sample_completed':
                self.samples.append(0)
            raise


class UnknownModManufactured(Semantics):
    def read(self, reg):
        if reg == 'CONFIG':
            self.known[reg] |= 0x0C00
        return super().read(reg)


class PorTemperatureZero(Semantics):
    def event(self, name, **payload):
        super().event(name, **payload)
        if name == 'por_load_completed':
            self.values['TEMP'] = 0


class InvertedPolarity(Semantics):
    def alert_level(self):
        return super().alert_level() ^ 1


class DataReadySelectionIgnored(Semantics):
    def alert_level(self):
        config = self.values['CONFIG']
        active = bool(config & 0xC000)
        polarity = bool(config & 8)
        return int(polarity if active else not polarity)


class ThermClearedByConfigRead(Semantics):
    def read_masked(self, reg, mask):
        result = super().read_masked(reg, mask)
        if reg == 'CONFIG' and self.values['CONFIG'] & 0x10:
            self.values['CONFIG'] &= ~0x8000
        return result


FAULT_ORACLES = [
    (LockedWritePersists, assert_locked_reload),
    (ProgrammingCommitsEarly, assert_program_not_committed_before_complete),
    (MissingBusyMirror, assert_both_busy_mirrors),
    (Mod1Persists, assert_config_persists_only_masked_bits),
    (PrematureDataReady, assert_no_premature_dr),
    (WrongAverageCount, assert_no_premature_dr),
    (LastSampleOnly, assert_signed_accumulated_average),
    (NoAutomaticShutdown, assert_operational_shutdown),
    (OffsetUnsigned, assert_signed_negative_offset),
    (OffsetWraps, assert_offset_saturates_not_wraps),
    (RejectedSampleMutates, assert_bad_sample_atomic),
    (UnknownModManufactured, assert_unknown_mod_excluded),
    (PorTemperatureZero, assert_por_restores_temp_sentinel),
    (InvertedPolarity, assert_alert_polarity),
    (DataReadySelectionIgnored, assert_dr_selection_not_alert_flags),
    (ThermClearedByConfigRead, assert_therm_config_read_retains_logical_alert),
]


@pytest.mark.parametrize('fault,oracle', FAULT_ORACLES, ids=[f.__name__ for f, _ in FAULT_ORACLES])
def test_source_oracles_reject_meaningful_synthetic_faults(fault, oracle):
    oracle(Semantics)  # The same source-derived oracle first passes baseline.
    with pytest.raises((AssertionError, OutsideContract, pytest.fail.Exception)):
        oracle(fault)


@pytest.fixture(scope='module')
def source_review():
    return json.loads((ROOT / 'source_review.json').read_text(encoding='utf-8'))


@pytest.fixture(scope='module')
def witness_execution():
    return {name: admission_module.produce_witness(name) for name in witness_scenarios.SCENARIOS}


def test_real_source_witnesses_keep_closure_at_clause_level(source_review, witness_execution):
    admission_module.validate_execution(witness_execution)
    rows = admission_module.build_closure(source_review, witness_execution)
    assert len(rows) == 16
    assert len({r['inventory_field_id'] for r in rows}) == 15
    assert all(r['whole_dimension_closed'] is False and r['whole_field_promoted'] is False for r in rows)


def test_no_execution_never_admits_source_only_claims(source_review):
    rows = admission_module.build_closure(source_review, {})
    assert all(r['assessment'] == 'PARTIAL' for r in rows)
    assert all(r['missing_claim_ids'] for r in rows)


def test_missing_qualifying_scenario_leaves_its_claim_partial(source_review, witness_execution):
    shortened = copy.deepcopy(witness_execution)
    shortened.pop('one_shot_matrix')
    rows = admission_module.build_closure(source_review, shortened)
    assert any(r['assessment'] == 'PARTIAL' and r['missing_claim_ids'] for r in rows)


def test_arbitrary_passing_labels_and_foreign_events_cannot_admit_claims(source_review, witness_execution):
    fabricated = {}
    for name in witness_execution:
        fabricated[name] = {'status': 'PASS', 'check_count': 1,
            'checks': [{'clause': 'unrelated equality', 'actual': 1, 'expected': 1}],
            'trace': [{'chip': 'TMP117', 'op': 'write', 'register': 'THIGH', 'value': 1},
                      {'chip': 'TMP117', 'op': 'event', 'name': 'pretend_completed', 'payload': {}}],
            'execution_kind': witness_execution[name]['execution_kind']}
    with pytest.raises(ValueError):
        admission_module.build_closure(source_review, fabricated)


@pytest.mark.parametrize('edit', ['missing_check', 'duplicate_check', 'unrelated_clause',
                                 'empty_comparison', 'wrong_expected', 'wrong_event',
                                 'missing_program_complete', 'wrong_chip', 'unknown_scenario',
                                 'metadata_as_event', 'bool_int_coercion'])
def test_scenario_evidence_rejects_specific_proof_corruption(witness_execution, edit):
    broken = copy.deepcopy(witness_execution)
    result = broken['eeprom_roundtrips']
    if edit == 'missing_check':
        result['checks'].pop()
        result['check_count'] = len(result['checks'])
    elif edit == 'duplicate_check':
        result['checks'][-1] = copy.deepcopy(result['checks'][0])
    elif edit == 'unrelated_clause':
        result['checks'][0]['clause'] = 'other mechanism succeeded'
    elif edit == 'empty_comparison':
        result['checks'][0]['actual'] = result['checks'][0]['expected'] = None
    elif edit == 'wrong_expected':
        result['checks'][0]['actual'] = result['checks'][0]['expected'] = 0
    elif edit == 'wrong_event':
        event = next(op for op in result['trace'] if op['op'] == 'event')
        event['name'] = 'unknown_event'
    elif edit == 'missing_program_complete':
        result['trace'] = [op for op in result['trace']
                           if op.get('name') != 'eeprom_program_completed']
    elif edit == 'wrong_chip':
        result['trace'][0]['chip'] = 'TMP126'
    elif edit == 'metadata_as_event':
        broken['nominal_cycle_table']['execution_kind'] = 'DIGITAL_EVENT_PROFILE'
    elif edit == 'bool_int_coercion':
        target = next(c for c in result['checks'] if c.get('actual') == 0 and c.get('expected') == 0)
        target['actual'] = target['expected'] = False
    else:
        broken['unknown_scenario'] = result
    with pytest.raises(ValueError):
        admission_module.validate_execution(broken)


@pytest.mark.parametrize('edit', ['unknown_field', 'unknown_dimension', 'duplicate_dimension',
                                 'source_repair_field_promoted', 'unknown_claim', 'dropped_required_claim'])
def test_source_advice_cannot_forge_inventory_identity_or_source_dimension(source_review, witness_execution, edit):
    broken = copy.deepcopy(source_review)
    item = broken['closure_advice'][0]
    if edit == 'unknown_field':
        item['inventory_field_id'] = 'TMP117.CONFIG.NEVER_DEFINED'
    elif edit == 'unknown_dimension':
        item['source_repair_dimensions'][0] = 'pretend_dimension'
    elif edit == 'duplicate_dimension':
        target = next(r for r in broken['closure_advice'] if len(r['source_repair_dimensions']) > 1)
        target['source_repair_dimensions'][1] = target['source_repair_dimensions'][0]
    elif edit == 'source_repair_field_promoted':
        item['source_overall_status'] = 'PASS'
    elif edit == 'dropped_required_claim':
        target = next(r for r in broken['closure_advice'] if len(r['required_claim_ids']) > 1)
        target['required_claim_ids'].pop()
    else:
        item['required_claim_ids'][0] = 'UNDEFINED-SOURCE-FACT'
    with pytest.raises(ValueError):
        admission_module.build_closure(broken, witness_execution)
