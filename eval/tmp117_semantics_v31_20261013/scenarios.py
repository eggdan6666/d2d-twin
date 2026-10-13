"""Executed source-clause witnesses, distinct from independent fault tests."""
import copy

from tmp117 import OutsideContract, Semantics

FACTORY = {'CONFIG': 0x0220, 'THIGH': 0x6000, 'TLOW': 0x8000, 'TEMP_OFFSET': 0}


class Checks:
    def __init__(self):
        self.checks = []
        self.trace = []

    def equal(self, actual, expected, clause):
        self.checks.append({'clause': clause, 'actual': copy.deepcopy(actual), 'expected': copy.deepcopy(expected)})
        assert actual == expected, f'{clause}: {actual!r} != {expected!r}'

    def outside(self, fn, clause):
        try:
            fn()
        except OutsideContract:
            self.checks.append({'clause': clause, 'outside_contract': True})
        else:
            raise AssertionError('Missing scope guard: ' + clause)

    def capture(self, d, label):
        self.trace.extend({**r, 'instance': label} for r in d.trace)


def reset(d):
    d.event('general_call_reset_started')
    d.event('por_load_completed')


def observe(d, reg):
    return d.read_masked(reg, 0x07FC if reg == 'CONFIG' else 0xFFFF)


def completed(d, code):
    d.event('conversion_started')
    d.event('conversion_sample_completed', temperature_code=code)


def eeprom_roundtrips():
    c = Checks()
    for reg in FACTORY:
        d = Semantics()
        d.write('CONFIG', 0x0400)  # Quiescent shutdown programming baseline.
        volatile = 0x049C if reg == 'CONFIG' else 0x1234
        programmed = 0x04DC if reg == 'CONFIG' else 0xA678
        mask = 0x07FC if reg == 'CONFIG' else 0xFFFF
        d.write(reg, volatile)
        c.equal(observe(d, reg), volatile & mask, reg + ' locked scratch write')
        reset(d)
        c.equal(observe(d, reg), FACTORY[reg], reg + ' locked write not persistent')
        d.write('CONFIG', 0x0400)
        d.write('EEPROM_UL', 0x8000)
        d.write(reg, programmed)
        for _ in range(2):
            c.equal(d.read_masked('CONFIG', 0x1000), 0x1000, reg + ' Busy CONFIG not read-clear')
            c.equal(d.read_masked('EEPROM_UL', 0x4000), 0x4000, reg + ' Busy mirror not read-clear')
        c.outside(lambda: observe(d, reg), reg + ' programming activation not invented')
        c.outside(lambda: d.write('TLOW', 0x1111), reg + ' prohibited busy-write response unscored')
        d.event('eeprom_program_completed')
        c.equal(d.read_masked('CONFIG', 0x1000), 0, reg + ' programming complete Busy0')
        c.equal(d.read_masked('EEPROM_UL', 0x4000), 0, reg + ' programming complete mirror0')
        reset(d)
        c.equal(observe(d, reg), programmed & mask, reg + ' programmed backing reloaded')
        c.equal(d.read_masked('EEPROM_UL', 0x8000), 0, reg + ' general-call relocks')
        for other in FACTORY:
            if other != reg:
                c.equal(observe(d, other), FACTORY[other], reg + ' preserves other NVM location ' + other)
        d.write('CONFIG', 0x0400)
        d.write(reg, volatile)
        reset(d)
        c.equal(observe(d, reg), programmed & mask, reg + ' subsequent volatile write does not overwrite NVM')
        c.capture(d, reg)
    return c


def config_bit_persistence():
    c = Checks()
    for bit in range(2, 12):
        d = Semantics()
        d.write('CONFIG', 0x0400)
        d.write('EEPROM_UL', 0x8000)
        # This is a symbolic EEPROM-backed CONFIG programming contract. Mode
        # activation under EUN1 is unknown and is deliberately not observed.
        raw = 1 << bit
        d.write('CONFIG', raw)
        d.event('eeprom_program_completed')
        reset(d)
        expected = raw & 0x07FC
        c.equal(d.read_masked('CONFIG', 0x0FFC), expected, 'CONFIG bit' + str(bit) + ' persistence mask')
        c.equal(d.operating_mode, 'shutdown' if expected & 0x0400 else 'continuous', 'Source-backed startup mode')
        c.capture(d, 'CONFIG_bit' + str(bit))
    return c


def por_and_user_image():
    c = Checks()
    image = {'CONFIG': 0x0494, 'THIGH': 0x2400, 'TLOW': 0x1200, 'TEMP_OFFSET': 0xFF80}
    d = Semantics(eeprom_image=image)
    for reg, value in image.items():
        c.equal(observe(d, reg), value, 'Explicit supplied NVM image ' + reg)
    d.event('por_started')
    c.equal(d.read_masked('CONFIG', 0x1000), 0x1000, 'POR Busy CONFIG')
    c.equal(d.read_masked('EEPROM_UL', 0x4000), 0x4000, 'POR Busy mirror')
    for reg, value in [('CONFIG', 0x0200), ('THIGH', 0x1111), ('TLOW', 0x2222)]:
        d.write(reg, value)
    c.outside(lambda: d.write('TEMP_OFFSET', 0x3333), 'POR OFF write response not specified')
    c.outside(lambda: d.write('EEPROM_UL', 0x8000), 'POR EUN write response not specified')
    d.event('por_load_completed')
    for reg, value in image.items():
        c.equal(observe(d, reg), value, 'POR loads supplied backing ' + reg)
    c.equal(d.read_masked('CONFIG', 0x1000), 0, 'POR complete not typical elapsed deadline')
    c.capture(d, 'user_image')
    return c


def one_shot_matrix():
    c = Checks()
    for avg, count in enumerate((1, 8, 32, 64)):
        for conv in range(8):
            d = Semantics()
            config = 0x0C00 | (avg << 5) | (conv << 7)
            d.write('CONFIG', config)
            c.equal(d.read_masked('CONFIG', 0x2000), 0, 'Request alone is not completed DR')
            c.outside(lambda: d.read('CONFIG'), 'Unknown one-shot MOD readback excluded')
            d.event('conversion_started')
            for i in range(count):
                code = 0x1940 if count == 1 else (0x1900 if i % 2 == 0 else 0x1980)
                d.event('conversion_sample_completed', temperature_code=code)
                if i < count - 1:
                    c.equal(d.read_masked('CONFIG', 0x2000), 0, 'N-1 samples cannot set DR')
            c.equal(d.operating_mode, 'shutdown', 'One-shot completes in operational shutdown')
            c.equal(d.read_masked('CONFIG', 0x2000), 0x2000, 'Nth sample yields preclear DR')
            c.equal(d.read_masked('CONFIG', 0x2000), 0, 'CONFIG read clears DR')
            c.equal(d.read('TEMP'), 0x1940, 'Exact accumulated mean; CONV-independent one-shot')
            c.outside(lambda: d.event('conversion_started'), 'Automatic shutdown prevents unrequested restart')
            c.outside(lambda: d.read('CONFIG'), 'Automatic shutdown does not imply numeric MOD1')
            c.capture(d, f'AVG{avg}_CONV{conv}')
    return c


def mode_abort_and_atomic_guards():
    c = Checks()
    d = Semantics()
    d.write('CONFIG', 0x0C20)
    d.event('conversion_started')
    d.event('conversion_sample_completed', temperature_code=0x1980)
    before = copy.deepcopy(d.__dict__)
    c.outside(lambda: d.write('CONFIG', 0x0CA0), 'Active CONV change response not invented')
    c.equal(d.__dict__ == before, True, 'Rejected active reconfiguration is atomic')
    d.write('CONFIG', 0x0420)
    c.equal(d.operating_mode, 'shutdown', 'MOD01 sourced abort')
    c.equal(d.read_masked('CONFIG', 0x2000), 0, 'Partial conversion aborted without false DR')
    c.outside(lambda: d.event('conversion_sample_completed', temperature_code=0x1980), 'No samples after explicit abort')
    d.write('CONFIG', 0x0800)
    c.equal(d.read_masked('CONFIG', 0x0C00), 0, 'MOD10 explicit readback00')
    c.equal(d.operating_mode, 'continuous', 'MOD10 is continuous')
    c.capture(d, 'abort')
    return c


def signed_offset():
    c = Checks()
    for raw, offset, expected in [(0x0100, 0xFF80, 0x0080), (0xFF00, 0x0080, 0xFF80),
                                  (0x7FF0, 0x0100, 0x7FFF), (0x8008, 0xFFF0, 0x8000)]:
        d = Semantics()
        d.write('TEMP_OFFSET', offset)
        d.write('CONFIG', 0x0C00)
        completed(d, raw)
        c.equal(d.read('TEMP'), expected, 'Signed offset addition with sourced saturation')
        c.equal(d.read_masked('CONFIG', 0x2000), 0, 'TEMP read clears DR independently')
        c.capture(d, hex(raw) + '_' + hex(offset))
    return c


def alert_and_therm():
    c = Checks()
    for tna in (0, 1):
        d = Semantics()
        d.write('THIGH', 0xFFF0)  # -0.125C.
        d.write('TLOW', 0xFF00)   # -2C; signed ordering matters.
        d.write('CONFIG', tna << 4)
        completed(d, 0x0080)
        c.equal(d.alert_level(), 0, 'Default POL0 HIGH asserts logical ALERT')
        d.read('TEMP')
        c.equal(d.read_masked('CONFIG', 0xE000), 0x8000, 'TEMP clears DR, retains alert for CONFIG preclear')
        c.equal(d.read_masked('CONFIG', 0xC000), 0x8000 if tna else 0, 'THERM differs from Alert read-clear')
        if tna:
            for code in (0xFFF0, 0xFF00, 0xFF80):
                completed(d, code)
                c.equal(d.read_masked('CONFIG', 0xC000), 0x8000, 'THERM equality/between preserves hysteresis')
            completed(d, 0xFE80)
            c.equal(d.read_masked('CONFIG', 0xC000), 0, 'THERM clears only below signed low')
        else:
            completed(d, 0xFE80)
            c.equal(d.read_masked('CONFIG', 0xC000), 0x4000, 'Signed below-low sets nonzero LOW')
        c.capture(d, 'TNA' + str(tna))
    return c


def data_ready_pin_selection():
    c = Checks()
    for pol in (0, 1):
        for tna in (0, 1):
            d = Semantics()
            d.write('CONFIG', 0x0C04 | (pol << 3) | (tna << 4))
            c.equal(d.alert_level(), 1 - pol, 'Selected DR initial logical polarity')
            completed(d, 0x1900)
            c.equal(d.alert_level(), pol, 'DR_ALERT selects nonzero DR even without threshold alarm')
            c.equal(d.read_masked('CONFIG', 0x2000), 0x2000, 'Both modes return DR preclear')
            c.equal(d.alert_level(), 1 - pol, 'CONFIG clears selected DR in either mode')
            c.capture(d, f'POL{pol}_TNA{tna}')
    return c


def nominal_cycle_table():
    c = Checks()
    table = ((15.5, 125, 500, 1000), (125, 125, 500, 1000), (250, 250, 500, 1000),
             (500, 500, 500, 1000), (1000, 1000, 1000, 1000), (4000, 4000, 4000, 4000),
             (8000, 8000, 8000, 8000), (16000, 16000, 16000, 16000))
    for conv in range(8):
        for avg in range(4):
            d = Semantics()
            d.write('CONFIG', (conv << 7) | (avg << 5))
            c.equal(d.nominal_cc_cycle_ms(), table[conv][avg], 'Table7-7 metadata only; no timing measurement')
            c.capture(d, f'table_CONV{conv}_AVG{avg}')
    return c


SCENARIOS = {'eeprom_roundtrips': eeprom_roundtrips, 'config_bit_persistence': config_bit_persistence,
             'por_and_user_image': por_and_user_image, 'one_shot_matrix': one_shot_matrix,
             'mode_abort_and_atomic_guards': mode_abort_and_atomic_guards, 'signed_offset': signed_offset,
             'alert_and_therm': alert_and_therm, 'data_ready_pin_selection': data_ready_pin_selection,
             'nominal_cycle_table': nominal_cycle_table}

CLAIM_SCENARIOS = {
    'NVM-CONFIG-MASK': ['config_bit_persistence'], 'NVM-BACKED-LOCATIONS': ['eeprom_roundtrips'],
    'NVM-LOCKED-WRITES': ['eeprom_roundtrips'], 'NVM-PROGRAM': ['eeprom_roundtrips'],
    'NVM-POR': ['eeprom_roundtrips', 'por_and_user_image'], 'NVM-BUSY-MIRROR': ['eeprom_roundtrips', 'por_and_user_image'],
    'GENERAL-CALL-RESET': ['eeprom_roundtrips'], 'MODE-ENCODINGS': ['mode_abort_and_atomic_guards', 'one_shot_matrix'],
    'AVERAGE-COUNTS': ['one_shot_matrix'], 'OS-CONV-INDEPENDENT': ['one_shot_matrix'],
    'SIGNED-OFFSET-SATURATION': ['signed_offset'], 'SIGNED-LIMITS': ['alert_and_therm'],
    'READY-READ-CLEAR': ['one_shot_matrix', 'alert_and_therm', 'data_ready_pin_selection'],
    'ALERT-MODE': ['alert_and_therm', 'data_ready_pin_selection'], 'THERM-MODE': ['alert_and_therm'],
    'CC-CYCLE-TABLE': ['nominal_cycle_table'],
}
