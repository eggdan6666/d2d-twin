"""Source-derived event scenarios with explicit, bounded clause coverage."""
from runtime import OutsideContract, Semantics


class Checks:
    def __init__(self):
        self.records = []

    def equal(self, actual, expected, clause):
        self.records.append({'clause': clause, 'actual': actual, 'expected': expected})
        assert actual == expected, f'{clause}: got {actual:#x}, expected {expected:#x}'

    def excluded(self, action, clause):
        try:
            action()
        except OutsideContract:
            self.records.append({'clause': clause, 'outside_contract': True})
        else:
            raise AssertionError('Undefined operation admitted: ' + clause)


def tmp117_eeprom(factory=Semantics):
    d, c = factory('TMP117'), Checks()
    # Nonfactory scratch value is lost on POR with EUN=0.
    d.write('THIGH', 0x1234)
    c.equal(d.read('THIGH'), 0x1234, 'EUN0 permits volatile scratch write')
    d.event('por_started')
    c.equal(d.read('CONFIG') & 0x1000, 0x1000, 'POR load busy in CONFIG')
    c.equal(d.read('EEPROM_UL') & 0x4000, 0x4000, 'POR busy mirror')
    d.write('THIGH', 0x5678)
    d.event('por_load_completed')
    c.equal(d.read('THIGH'), 0x6000, 'POR reloads factory NVM; POR write ignored')
    d.write('EEPROM_UL', 0x8000)
    d.write('THIGH', 0x2345)
    c.equal(d.read('CONFIG') & 0x1000, 0x1000, 'Programming sets Busy')
    c.equal(d.read('EEPROM_UL') & 0x4000, 0x4000, 'Programming busy mirror')
    c.excluded(lambda: d.write('TLOW', 0x4567), 'No response oracle for prohibited programming-busy write')
    d.event('eeprom_program_completed')
    c.equal(d.read('CONFIG') & 0x1000, 0, 'Busy clears only on explicit completion')
    c.equal(d.read('EEPROM_UL') & 0x4000, 0, 'Completion clears Busy mirror')
    d.write('EEPROM_UL', 0)
    d.write('THIGH', 0x3456)
    d.event('por_started')
    d.event('por_load_completed')
    c.equal(d.read('THIGH'), 0x2345, 'POR restores programmed NVM instead of last volatile value')
    c.equal(d.read('EEPROM_UL') & 0x8000, 0, 'POR locks EEPROM')
    return d, c


def tmp117_flags(factory=Semantics):
    d, c = factory('TMP117'), Checks()
    d.write('THIGH', 0x2000)
    d.write('TLOW', 0x1800)
    d.event('qualifying_conversion_completed', temperature_code=0x2100)
    c.equal(d.read('CONFIG') & 0xE000, 0xA000, 'Alert CONFIG returns nonzero preclear HIGH+DR')
    c.equal(d.read('CONFIG') & 0xE000, 0, 'Alert CONFIG clears HIGH+DR')
    d.event('qualifying_conversion_completed', temperature_code=0x1700)
    d.read('TEMP')
    c.equal(d.read('CONFIG') & 0xE000, 0x4000, 'TEMP clears DR but retains LOW for CONFIG preclear return')
    d.write('CONFIG', 0x0230)  # Factory configuration + TNA=1.
    d.event('qualifying_conversion_completed', temperature_code=0x2100)
    c.equal(d.read('CONFIG') & 0xC000, 0x8000, 'THERM nonzero HIGH and LOW=0')
    c.equal(d.read('CONFIG') & 0xC000, 0x8000, 'THERM CONFIG read does not clear HIGH')
    d.event('qualifying_conversion_completed', temperature_code=0x1900)
    c.equal(d.read('CONFIG') & 0xC000, 0x8000, 'THERM hysteresis retains HIGH between limits')
    d.event('qualifying_conversion_completed', temperature_code=0x1700)
    c.equal(d.read('CONFIG') & 0xC000, 0, 'THERM clears HIGH after qualifying below-low conversion')
    return d, c


def tmp126_read_clear(factory=Semantics):
    d, c = factory('TMP126'), Checks()
    d.event('qualifying_flag_event', fields=['CRC_FLAG', 'SLEW_FLAG', 'THIGH_FLAG', 'TLOW_FLAG'])
    c.equal(d.read('ALERT_STATUS', auto_increment=True) & 0xA6, 0xA6, 'Auto-increment returns nonzero flags')
    c.equal(d.read('ALERT_STATUS', transaction='burst', auto_increment=True) & 0xA6, 0xA6, 'Auto-increment preserves flags')
    c.equal(d.read('ALERT_STATUS') & 0xA6, 0xA6, 'Single read returns preclear flags')
    c.equal(d.read('ALERT_STATUS') & 0xA6, 0, 'Single read without increment clears flags')
    d.write('CONFIG', 0x0016)
    d.event('conversion_sample_completed')
    c.equal(d.read('ALERT_STATUS', auto_increment=True) & 1, 1, 'Completed one-shot produces nonzero DR')
    d.read('TEMP_RESULT')
    c.equal(d.read('ALERT_STATUS', auto_increment=True) & 1, 0, 'TEMP_RESULT read clears DR across registers')
    d.write('CONFIG', 0x0026)
    d.event('qualifying_flag_event', fields=['CRC_FLAG'])
    d.write('CONFIG', 0x0006)
    c.equal(d.read('ALERT_STATUS', auto_increment=True), 0, 'Comparator to interrupt clears Alert_Status')
    return d, c


def tmp126_average(factory=Semantics):
    d, c = factory('TMP126'), Checks()
    d.write('CONFIG', 0x0096)  # AVG=1, ONE_SHOT=1, MODE=0.
    c.equal(d.read('CONFIG') & 0x18, 0, 'ONE_SHOT readback zero does not mean completed')
    for _ in range(7):
        d.event('conversion_sample_completed')
    c.equal(d.read('ALERT_STATUS', auto_increment=True) & 1, 0, 'Seven conversions do not complete eight-sample average')
    c.equal(d.read('CONFIG') & 8, 0, 'MODE remains active before completion')
    d.event('conversion_sample_completed')
    c.equal(d.read('ALERT_STATUS', auto_increment=True) & 1, 1, 'Eighth conversion sets DR')
    c.equal(d.read('CONFIG') & 8, 8, 'Completed one-shot returns to shutdown')
    return d, c


def hdc_start_complete(factory=Semantics):
    d, c = factory('HDC2021'), Checks()
    d.write('MEAS_CONFIG', 1)
    c.equal(d.read('STATUS') & 0x80, 0, 'Trigger request is not data ready')
    c.excluded(lambda: d.event('conversion_completed'), 'Completion cannot precede start')
    d.event('measurement_started')
    c.equal(d.read('MEAS_CONFIG') & 1, 0, 'Trigger self-clears at measurement start')
    c.equal(d.read('STATUS') & 0x80, 0, 'Started conversion has not completed')
    d.event('conversion_completed')
    c.equal(d.read('STATUS') & 0x80, 0x80, 'STATUS returns nonzero preclear DRDY')
    c.equal(d.read('STATUS') & 0x80, 0, 'STATUS clears DRDY')
    return d, c


def hdc_cross_read(factory=Semantics):
    all_records, all_trace = [], []
    for reg in ('TEMP_LOW', 'TEMP_HIGH', 'HUM_LOW', 'HUM_HIGH'):
        d, c = factory('HDC2021'), Checks()
        d.write('MEAS_CONFIG', 1)
        d.event('measurement_started')
        d.event('conversion_completed')
        # Single production read, no diagnostic peek used as oracle.
        d.read(reg)
        c.equal(d.read('STATUS') & 0x80, 0, reg + ' read clears DRDY')
        all_records.extend(c.records)
        all_trace.extend(d.trace)
    d.trace, c.records = all_trace, all_records
    return d, c


def bosch_commit(factory=Semantics):
    d, c = factory('BME280'), Checks()
    d.write('ctrl_hum', 2)
    c.equal(d.read('ctrl_hum') & 7, 2, 'Humidity register receives new setting')
    # Active setting is an explicit abstract observation hook, not a silicon register.
    c.equal(d.active_humidity, 0, 'Humidity setting inactive before ctrl_meas commit')
    d.write('ctrl_meas', 0x24)
    c.equal(d.active_humidity, 2, 'ctrl_meas commits pending humidity')
    d.write('config', 0x04)
    c.equal(d.read('config') & 0x1C, 4, 'Legal config write in sleep persists')
    d.write('ctrl_meas', 0x27)
    c.excluded(lambda: d.write('config', 0x08), 'Normal config writes may be ignored; no deterministic response oracle')
    return d, c


def bosch_forced(factory=Semantics):
    all_records, all_trace = [], []
    for chip in ('BME280', 'BMP280'):
        for mode in (1, 2):
            d, c = factory(chip), Checks()
            d.write('ctrl_meas', 0x24 | mode)
            c.equal(d.read('status') & 8, 8, 'Forced measurement is pending')
            c.excluded(lambda: d.write('config', 0x04), 'No config stimulus during pending measurement')
            d.event('measurement_completed')
            c.equal(d.read('status') & 8, 0, 'Completed measurement is not pending')
            c.equal(d.read('ctrl_meas') & 3, 0, 'Both forced codes return to sleep on completion')
            all_records.extend(c.records)
            all_trace.extend(d.trace)
    d.trace, c.records = all_trace, all_records
    return d, c


SCENARIOS = {
    'tmp117_eeprom': tmp117_eeprom, 'tmp117_flags': tmp117_flags,
    'tmp126_read_clear': tmp126_read_clear, 'tmp126_average': tmp126_average,
    'hdc_start_complete': hdc_start_complete, 'hdc_cross_read': hdc_cross_read,
    'bosch_commit': bosch_commit, 'bosch_forced': bosch_forced,
}
