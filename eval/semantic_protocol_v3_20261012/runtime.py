"""Bounded digital event prototypes; not an emulator of all device functions.

Events represent completed digital actions. They do not simulate elapsed time,
analog signals or physical bus frames. Unimplemented operations fail closed.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'independent_source_admission_20261012'


class OutsideContract(ValueError):
    """Benchmark operation has no oracle in this bounded profile."""


def number(value):
    return int(value, 0) if isinstance(value, str) else int(value)


def geometry(bits):
    hi, lo = (list(map(int, bits.split(':'))) if ':' in bits else [int(bits)] * 2)
    if lo < 0 or hi < lo:
        raise ValueError(bits)
    return ((1 << (hi - lo + 1)) - 1) << lo, lo


class Semantics:
    supported = {'TMP117', 'TMP126', 'HDC2021', 'BME280', 'BMP280'}

    def __init__(self, chip):
        if chip not in self.supported:
            raise OutsideContract('No event prototype for ' + chip)
        self.chip = chip
        self.ir = json.loads((SOURCE / 'candidate_ir' / (chip + '_gold_ir.json')).read_text(encoding='utf-8'))
        self.registers = {r['name']: r for r in self.ir['registers']}
        self.fields = {(r['name'], f['name']): f for r in self.ir['registers'] for f in r['fields']}
        self.values = {}
        self.known = {}
        for name, reg in self.registers.items():
            value = mask = 0
            for f in reg['fields']:
                if f.get('reset') is not None:
                    m, lo = geometry(f['bits'])
                    value |= (number(f['reset']) << lo) & m
                    mask |= m
            self.values[name], self.known[name] = value, mask
        self.phase = 'idle'
        self.trace = []
        self.pending = None
        self.conversions = 0
        self.nvm = {}
        if chip == 'TMP117':
            # Explicit factory-image scenario, not arbitrary EEPROM contents.
            self.nvm = {r: self.values[r] for r in ('CONFIG', 'THIGH', 'TLOW', 'TEMP_OFFSET')}
            self.known['DEVICE_ID'] &= 0x0FFF  # Revision nibble is not certified.
        self.active_humidity = 0

    def peek(self, reg):
        """Diagnostic state only; never a replacement for device read assertions."""
        return self.values[reg]

    def field(self, reg, name):
        mask, lo = geometry(self.fields[reg, name]['bits'])
        if self.known[reg] & mask != mask:
            raise OutsideContract('Unknown field value: ' + reg + '.' + name)
        return (self.values[reg] & mask) >> lo

    def _field(self, reg, name, value):
        mask, lo = geometry(self.fields[reg, name]['bits'])
        if value < 0 or value > mask >> lo:
            raise OutsideContract('Value outside field width')
        self.values[reg] = (self.values[reg] & ~mask) | (value << lo)
        self.known[reg] |= mask

    def _rw(self, reg, value):
        mask = 0
        for f in self.registers[reg]['fields']:
            if f.get('access') == 'RW':
                mask |= geometry(f['bits'])[0]
        self.values[reg] = (self.values[reg] & ~mask) | (value & mask)
        self.known[reg] |= mask

    def _busy(self, value):
        self._field('CONFIG', 'EEPROM_BUSY', value)
        self._field('EEPROM_UL', 'EEPROM_BUSY', value)

    def write(self, reg, value):
        if reg not in self.registers or not isinstance(value, int) or not 0 <= value < 1 << self.ir['reg_width']:
            raise OutsideContract('Unknown register or invalid width')
        self.trace.append({'chip': self.chip, 'op': 'write', 'register': reg, 'value': value})
        if self.chip == 'TMP117':
            if self.phase == 'por_loading' and reg in ('CONFIG', 'THIGH', 'TLOW'):
                return  # Sourced POR write-ignore, not programming-busy behavior.
            if self.phase == 'programming':
                raise OutsideContract('Writes during EEPROM programming are prohibited; no response oracle')
            if reg == 'EEPROM_UL':
                self._field(reg, 'EUN', (value >> 15) & 1)
                return
            if reg not in self.nvm:
                raise OutsideContract('Only mapped EEPROM-backed scratch writes implemented')
            if reg == 'CONFIG' and value & 2:
                raise OutsideContract('SOFT_RESET source conflict retained')
            if reg == 'CONFIG' and ((value >> 10) & 3) not in (0, 2):
                raise OutsideContract('Shutdown/one-shot transition not implemented in this alert profile')
            if reg == 'CONFIG' and value & 0xF001:
                raise OutsideContract('Use sourced writable CONFIG bits and reserved-zero baseline')
            self._rw(reg, value)
            if reg == 'CONFIG' and self.field('CONFIG', 'MOD') == 2:
                self._field('CONFIG', 'MOD', 0)
            if self.field('EEPROM_UL', 'EUN'):
                if reg == 'CONFIG':
                    nv = (self.nvm[reg] & ~0x07FC) | (value & 0x07FC)
                else:
                    nv = self.values[reg]
                self.pending = (reg, nv)
                self.phase = 'programming'
                self._busy(1)
            return
        if self.chip == 'TMP126':
            if reg != 'CONFIG':
                raise OutsideContract('Only CONFIG writes implemented')
            if value & 0x100:
                raise OutsideContract('Reset completion not implemented')
            if value & 0xFE40:
                raise OutsideContract('Reserved-zero input constraint')
            old_mode = self.field('CONFIG', 'INT_COMP')
            self._rw(reg, value)
            if old_mode == 1 and self.field('CONFIG', 'INT_COMP') == 0:
                self.values['ALERT_STATUS'] = 0
            if value & 0x10:
                self._field('CONFIG', 'ONE_SHOT', 0)  # Defined readback, not completion.
                self.phase, self.conversions = 'converting', 0
            elif self.field('CONFIG', 'MODE') == 1:
                self.phase, self.conversions = 'idle', 0
            return
        if self.chip == 'HDC2021':
            if reg != 'MEAS_CONFIG' or self.field('DEVICE_CONFIG', 'CC') != 0:
                raise OutsideContract('Only one-shot MEAS_CONFIG writes implemented')
            if (value >> 6) & 3 == 3 or (value >> 4) & 3 == 3 or value & 0x0E:
                raise OutsideContract('Use legal baseline resolutions, default reserved/channel bits')
            if self.phase != 'idle':
                raise OutsideContract('Retrigger during an active measurement not implemented')
            self._rw(reg, value)
            if value & 1:
                self.phase = 'start_requested'
            return
        # Bosch profile uses sleep + no pending transition as a stimulus guard.
        if self.phase != 'idle':
            raise OutsideContract('Writes during pending Bosch measurement/transition are outside profile')
        if reg == 'config':
            if self.field('ctrl_meas', 'mode') != 0:
                raise OutsideContract('Normal-mode write may be ignored; no deterministic write oracle')
            if value & 2 or ((value >> 2) & 7) > 4:
                raise OutsideContract('Reserved/filter encoding excluded')
            self._rw(reg, value)
        elif reg == 'ctrl_hum' and self.chip == 'BME280':
            if value & ~7 or value > 5 or self.field('ctrl_meas', 'mode') != 0:
                raise OutsideContract('Humidity writes require legal sleep baseline')
            self._rw(reg, value)
        elif reg == 'ctrl_meas':
            if (value >> 5) > 5 or ((value >> 2) & 7) > 5:
                raise OutsideContract('Oversampling encoding excluded')
            self._rw(reg, value)
            if self.chip == 'BME280':
                self.active_humidity = self.field('ctrl_hum', 'osrs_h')
            if value & 3 in (1, 2):
                self.phase = 'converting'
                self._field('status', 'measuring', 1)
        else:
            raise OutsideContract('Bosch write not implemented in profile')

    def read(self, reg, transaction='single', auto_increment=False):
        if transaction not in ('single', 'burst') or not isinstance(auto_increment, bool):
            raise OutsideContract('Unknown read transaction')
        width_mask = (1 << self.ir['reg_width']) - 1
        if reg not in self.values or self.known[reg] != width_mask:
            raise OutsideContract('Unknown register bits cannot be returned as fabricated zero')
        before = self.values[reg]
        if self.chip == 'TMP117':
            if reg in ('CONFIG', 'TEMP'):
                self._field('CONFIG', 'DATA_READY', 0)
            if reg == 'CONFIG' and self.field('CONFIG', 'TNA') == 0:
                self._field('CONFIG', 'HIGH_ALERT', 0)
                self._field('CONFIG', 'LOW_ALERT', 0)
        elif self.chip == 'TMP126':
            if reg == 'ALERT_STATUS' and transaction == 'single' and not auto_increment:
                self.values[reg] &= ~0xA7  # RC flags only; live condition status retained.
            if reg == 'TEMP_RESULT':
                self._field('ALERT_STATUS', 'DATA_READY_FLAG', 0)
        elif self.chip == 'HDC2021' and reg in ('TEMP_LOW', 'TEMP_HIGH', 'HUM_LOW', 'HUM_HIGH', 'STATUS'):
            self._field('STATUS', 'DRDY_STATUS', 0)
        self.trace.append({'chip': self.chip, 'op': 'read', 'register': reg, 'value': before,
                           'transaction': transaction, 'auto_increment': auto_increment})
        return before

    def event(self, name, **payload):
        allowed = {'qualifying_conversion_completed': {'temperature_code'}, 'qualifying_flag_event': {'fields'}}
        if set(payload) != allowed.get(name, set()):
            raise OutsideContract('Unknown or missing event payload')
        self.trace.append({'chip': self.chip, 'op': 'event', 'name': name, 'payload': payload})
        if self.chip == 'TMP117':
            if name == 'por_started' and self.phase == 'idle':
                self.phase = 'por_loading'
                self._field('EEPROM_UL', 'EUN', 0)
                self._busy(1)
            elif name == 'por_load_completed' and self.phase == 'por_loading':
                for reg, value in self.nvm.items():
                    self.values[reg] = (value & 0x07FC) if reg == 'CONFIG' else value
                self._busy(0)
                self.phase = 'idle'
            elif name == 'eeprom_program_completed' and self.phase == 'programming':
                reg, value = self.pending
                self.nvm[reg] = value
                self.pending = None
                self._busy(0)
                self.phase = 'idle'
            elif (name == 'qualifying_conversion_completed' and self.phase == 'idle'
                  and not self.field('EEPROM_UL', 'EUN') and self.field('CONFIG', 'MOD') == 0):
                code = payload['temperature_code']
                if type(code) is not int or not 0 <= code <= 0xFFFF:
                    raise OutsideContract('Completed digital temperature code must be16 bits')
                signed = lambda value: value - 0x10000 if value & 0x8000 else value
                low, high = signed(self.values['TLOW']), signed(self.values['THIGH'])
                if low >= high:
                    raise OutsideContract('Ordered low/high limits required by this event profile')
                temperature = signed(code)
                relation = 'above_high' if temperature > high else 'below_low' if temperature < low else 'between'
                self._field('TEMP', 'T', code)
                self._field('CONFIG', 'DATA_READY', 1)
                if self.field('CONFIG', 'TNA'):
                    if relation != 'between':
                        self._field('CONFIG', 'HIGH_ALERT', int(relation == 'above_high'))
                    self._field('CONFIG', 'LOW_ALERT', 0)
                else:
                    if relation == 'above_high':
                        self._field('CONFIG', 'HIGH_ALERT', 1)
                    if relation == 'below_low':
                        self._field('CONFIG', 'LOW_ALERT', 1)
            else:
                raise OutsideContract('Unsupported TMP117 event or phase')
        elif self.chip == 'TMP126':
            if name == 'qualifying_flag_event':
                fields = payload.get('fields', [])
                if (not isinstance(fields, list) or not fields or len(set(fields)) != len(fields)
                        or any(f not in {'CRC_FLAG', 'SLEW_FLAG', 'THIGH_FLAG', 'TLOW_FLAG'} for f in fields)):
                    raise OutsideContract('Only named qualifying RC flag events supported')
                for f in fields:
                    self._field('ALERT_STATUS', f, 1)
            elif name == 'conversion_sample_completed' and self.phase == 'converting':
                self.conversions += 1
                required = 8 if self.field('CONFIG', 'AVG') else 1
                if self.conversions == required:
                    self._field('ALERT_STATUS', 'DATA_READY_FLAG', 1)
                    self._field('CONFIG', 'MODE', 1)
                    self.phase = 'idle'
            else:
                raise OutsideContract('Unsupported TMP126 event or phase')
        elif self.chip == 'HDC2021':
            if name == 'measurement_started' and self.phase == 'start_requested':
                self._field('MEAS_CONFIG', 'MEAS_TRIG', 0)
                self.phase = 'converting'
            elif name == 'conversion_completed' and self.phase == 'converting':
                self._field('STATUS', 'DRDY_STATUS', 1)
                self.phase = 'idle'
            else:
                raise OutsideContract('Unsupported HDC2021 event or phase')
        elif name == 'measurement_completed' and self.phase == 'converting':
            self._field('status', 'measuring', 0)
            self._field('ctrl_meas', 'mode', 0)
            self.phase = 'idle'
        else:
            raise OutsideContract('Unsupported Bosch event or phase')
