"""TMP117 source-scoped digital semantics, separate from every frozen version.

Events are abstract completion boundaries, not elapsed-time/silicon simulation.
Unspecified averaging rounding and mode readback remain outside the oracle.
"""
import hashlib
import json
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE.parent / 'semantic_protocol_v3_20261012/runtime.py'
BASE_MANIFEST = HERE.parent / 'semantic_protocol_v3_20261012/artifact_manifest.json'
expected = json.loads(BASE_MANIFEST.read_text(encoding='utf-8'))['files']['runtime.py']
if hashlib.sha256(BASE_PATH.read_bytes()).hexdigest() != expected:
    raise ValueError('Frozen v3 base runtime changed')
_base = types.ModuleType('_frozen_tmp117_base_v3')
_base.__file__ = str(BASE_PATH)
# Read-only import avoids writing bytecode into the frozen artifact directory.
exec(compile(BASE_PATH.read_bytes(), str(BASE_PATH), 'exec'), _base.__dict__)
OutsideContract = _base.OutsideContract

PERSIST_MASK = 0x07FC
CONFIG_WRITE_MASK = 0x0FFC
AVG_COUNTS = (1, 8, 32, 64)
CC_CYCLE_MS = ((15.5, 125, 500, 1000), (125, 125, 500, 1000),
               (250, 250, 500, 1000), (500, 500, 500, 1000),
               (1000, 1000, 1000, 1000), (4000, 4000, 4000, 4000),
               (8000, 8000, 8000, 8000), (16000, 16000, 16000, 16000))


def signed(value):
    return value - 0x10000 if value & 0x8000 else value


def word(value):
    if type(value) is not int or not 0 <= value <= 0xFFFF:
        raise OutsideContract('Expected unsigned16 digital word')
    return value


class Semantics(_base.Semantics):
    """Four mapped EEPROM-backed registers plus controlled measurement events."""

    def __init__(self, chip='TMP117', eeprom_image=None):
        if chip != 'TMP117':
            raise OutsideContract('This version implements TMP117 only')
        super().__init__(chip)
        if eeprom_image is not None:
            if not isinstance(eeprom_image, dict) or set(eeprom_image) != set(self.nvm):
                raise OutsideContract('Supply all four mapped EEPROM locations')
            image = {k: word(v) for k, v in eeprom_image.items()}
            if image['CONFIG'] & ~PERSIST_MASK:
                raise OutsideContract('EEPROM image contains nonpersistent CONFIG bits')
            self.nvm = image.copy()
            for reg, value in self.nvm.items():
                self.values[reg] = value
        self.image_kind = 'factory_declared' if eeprom_image is None else 'explicit_user_image'
        self.operating_mode = 'shutdown' if self.values['CONFIG'] & 0x0400 else 'continuous'
        self.conversion_state = 'idle'
        self.samples = []
        self.required_samples = None
        self.offset_at_start = None
        self.reload_required = set()
        self.trace = []

    def _trace(self, op, **details):
        self.trace.append({'chip': 'TMP117', 'op': op, **details})

    def nominal_cc_cycle_ms(self):
        """Table7-7 metadata; not a simulated or guaranteed completion deadline."""
        return CC_CYCLE_MS[self.field('CONFIG', 'CONV')][self.field('CONFIG', 'AVG')]

    def alert_level(self):
        """Abstract digital ALERT level, excluding electrical/SMBus timing."""
        if self.phase != 'idle':
            raise OutsideContract('ALERT during memory loading/programming not admitted')
        if self.field('CONFIG', 'DR_ALERT'):
            asserted = bool(self.field('CONFIG', 'DATA_READY'))
        elif self.field('CONFIG', 'TNA'):
            asserted = bool(self.field('CONFIG', 'HIGH_ALERT'))
        else:
            asserted = bool(self.field('CONFIG', 'HIGH_ALERT') or self.field('CONFIG', 'LOW_ALERT'))
        return int(asserted) if self.field('CONFIG', 'POL') else int(not asserted)

    def write(self, reg, value):
        word(value)
        if type(reg) is not str or reg not in self.registers:
            raise OutsideContract('Unmapped register')
        if self.phase == 'programming':
            raise OutsideContract('All I2C writes prohibited during EEPROM programming')
        if self.phase == 'por_loading':
            if reg not in ('CONFIG', 'THIGH', 'TLOW'):
                raise OutsideContract('POR write-ignore not specified for this address')
            self._trace('write', register=reg, value=value, outcome='por_ignored')
            return
        if reg == 'EEPROM_UL':
            if value & 0x7FFF:
                raise OutsideContract('Unlock writes use only EUN in this profile')
            if self.conversion_state != 'idle':
                raise OutsideContract('Do not unlock or change programming gate during conversion')
            self._field(reg, 'EUN', value >> 15)
            self._trace('write', register=reg, value=value)
            return
        if reg not in self.nvm:
            raise OutsideContract('Only CONFIG/THIGH/TLOW/TEMP_OFFSET software writes supported')
        mod = (value >> 10) & 3 if reg == 'CONFIG' else None
        if reg == 'CONFIG' and value & ~CONFIG_WRITE_MASK:
            raise OutsideContract('Soft-reset conflict, reserved and status bits excluded from stimuli')
        if self.conversion_state != 'idle':
            # Explicit MOD01 abort is sourced; changing schedule/retrigger is not.
            old_controls = self.values['CONFIG'] & 0x03FC
            if (reg != 'CONFIG' or mod != 1 or value & 0x03FC != old_controls
                    or self.field('EEPROM_UL', 'EUN')):
                raise OutsideContract('Mid-conversion write/retrigger has no admitted oracle')
        unlocked = bool(self.field('EEPROM_UL', 'EUN'))
        if not unlocked and reg == 'CONFIG':
            old_tna_known = bool(self.known['CONFIG'] & 0x0010)
            tna_changed = not old_tna_known or bool(value & 0x0010) != bool(self.values['CONFIG'] & 0x0010)
            alerts_known_clear = self.known['CONFIG'] & 0xC000 == 0xC000 and self.values['CONFIG'] & 0xC000 == 0
            if tna_changed and not alerts_known_clear:
                raise OutsideContract('Alert-history mode-switch effects are outside this profile')
        if unlocked:
            new_nvm = value & PERSIST_MASK if reg == 'CONFIG' else value
            self.pending = reg, new_nvm
            self.phase = 'programming'
            self.reload_required.add(reg)
            # Activation/readback during programming is not specified. Only Busy
            # is scored until the programmed data are explicitly reloaded.
            self.known[reg] &= ~(CONFIG_WRITE_MASK if reg == 'CONFIG' else 0xFFFF)
            if reg == 'CONFIG':
                self.operating_mode = 'unknown_until_reload'
            self._busy(1)
        else:
            self._rw(reg, value)
            self.reload_required.discard(reg)
            if reg == 'CONFIG':
                if mod == 2:
                    self._field('CONFIG', 'MOD', 0)
                    self.operating_mode = 'continuous'
                elif mod == 0:
                    self.operating_mode = 'continuous'
                elif mod == 1:
                    self.operating_mode = 'shutdown'
                    self.conversion_state = 'idle'
                    self.samples = []
                    self.required_samples = None
                else:
                    self.operating_mode = 'one_shot'
                    self.conversion_state = 'requested'
                    self.samples = []
                    # No numeric MOD readback oracle while/after one-shot.
                    self.known['CONFIG'] &= ~0x0C00
                if self.field('CONFIG', 'TNA'):
                    self._field('CONFIG', 'LOW_ALERT', 0)
        self._trace('write', register=reg, value=value)

    def read(self, reg):
        return self.read_masked(reg, 0xFFFF)

    def read_masked(self, reg, mask):
        if (type(reg) is not str or type(mask) is not int or not 0 < mask <= 0xFFFF
                or reg not in self.values):
            raise OutsideContract('Nonzero valid observation mask required')
        if self.phase == 'por_loading':
            allowed = 0x1000 if reg == 'CONFIG' else 0x4000 if reg == 'EEPROM_UL' else 0
            if mask & ~allowed:
                raise OutsideContract('Only sourced Busy observations admitted during POR load')
        if self.known[reg] & mask != mask:
            raise OutsideContract('Unknown readback bits excluded')
        value = self.values[reg] & mask
        if reg in ('CONFIG', 'TEMP'):
            self._field('CONFIG', 'DATA_READY', 0)
        if reg == 'CONFIG':
            if not self.known['CONFIG'] & 0x0010:
                self.known['CONFIG'] &= ~0xC000  # TNA activation while programming unknown.
            elif self.field('CONFIG', 'TNA') == 0:
                self._field('CONFIG', 'HIGH_ALERT', 0)
                self._field('CONFIG', 'LOW_ALERT', 0)
        self._trace('read', register=reg, mask=mask, value=value)
        return value

    def _begin_load(self):
        self.phase = 'por_loading'
        self._field('EEPROM_UL', 'EUN', 0)
        self._busy(1)
        self.conversion_state = 'idle'
        self.samples = []
        self.required_samples = None

    def _finish_load(self):
        for name, reg in self.registers.items():
            value = mask = 0
            for f in reg['fields']:
                if f.get('reset') is not None:
                    m, lo = _base.geometry(f['bits'])
                    value |= (_base.number(f['reset']) << lo) & m
                    mask |= m
            self.values[name], self.known[name] = value, mask
        for reg, value in self.nvm.items():
            self.values[reg] = value
        self.known['DEVICE_ID'] &= 0x0FFF
        self._busy(0)
        self.phase = 'idle'
        self.operating_mode = 'shutdown' if self.nvm['CONFIG'] & 0x0400 else 'continuous'
        self.reload_required.clear()

    def _alert_update(self, temperature):
        low, high = signed(self.values['TLOW']), signed(self.values['THIGH'])
        if self.field('CONFIG', 'TNA'):
            if temperature > high:
                self._field('CONFIG', 'HIGH_ALERT', 1)
            elif temperature < low:
                self._field('CONFIG', 'HIGH_ALERT', 0)
            self._field('CONFIG', 'LOW_ALERT', 0)
        else:
            if temperature > high:
                self._field('CONFIG', 'HIGH_ALERT', 1)
            if temperature < low:
                self._field('CONFIG', 'LOW_ALERT', 1)

    def event(self, name, **payload):
        required = {'temperature_code'} if name == 'conversion_sample_completed' else set()
        if set(payload) != required:
            raise OutsideContract('Unexpected/missing event payload')
        if name in ('por_started', 'general_call_reset_started'):
            if self.phase != 'idle':
                raise OutsideContract('Reset while programming/loading excluded')
            self._begin_load()
        elif name == 'por_load_completed':
            if self.phase != 'por_loading':
                raise OutsideContract('No pending POR load')
            self._finish_load()
        elif name == 'eeprom_program_completed':
            if self.phase != 'programming' or self.pending is None:
                raise OutsideContract('No pending EEPROM program')
            reg, value = self.pending
            self.nvm[reg] = value
            self.pending = None
            self.phase = 'idle'
            self._busy(0)
        elif name == 'conversion_started':
            if (self.phase != 'idle' or self.field('EEPROM_UL', 'EUN') or self.reload_required
                    or self.operating_mode == 'shutdown' or self.conversion_state == 'running'):
                raise OutsideContract('No legal conversion start in current state')
            avg = self.field('CONFIG', 'AVG')
            offset = signed(self.values['TEMP_OFFSET'])
            if avg and offset:
                raise OutsideContract('Nonzero offset plus averaging pipeline ordering not certified')
            if signed(self.values['TLOW']) >= signed(self.values['THIGH']):
                raise OutsideContract('Ordered threshold profile required')
            self.required_samples = AVG_COUNTS[avg]
            self.offset_at_start = offset
            self.samples = []
            self.conversion_state = 'running'
        elif name == 'conversion_sample_completed':
            code = word(payload['temperature_code'])
            if self.phase != 'idle' or self.conversion_state != 'running' or self.field('EEPROM_UL', 'EUN'):
                raise OutsideContract('No active conversion')
            proposed = self.samples + [signed(code)]
            if len(proposed) == self.required_samples:
                total = sum(proposed)
                if total % self.required_samples:
                    raise OutsideContract('Fractional averaging rounding not specified')
                mean = total // self.required_samples
                result = max(-32768, min(32767, mean + self.offset_at_start))
                self.samples = proposed
                self._field('TEMP', 'T', result & 0xFFFF)
                self._field('CONFIG', 'DATA_READY', 1)
                self._alert_update(result)
                self.conversion_state = 'idle'
                if self.operating_mode == 'one_shot':
                    self.operating_mode = 'shutdown'
                    self.known['CONFIG'] &= ~0x0C00
            else:
                self.samples = proposed
        else:
            raise OutsideContract('Unsupported TMP117 event')
        self._trace('event', name=name, payload=payload)
