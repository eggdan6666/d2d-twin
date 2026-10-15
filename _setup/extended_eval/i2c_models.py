"""Deterministic I2C protocol models used by the extended software tests.

These models are deliberately separate from the frozen register-level
simulators. They exercise bus framing, sub-address auto-increment, reset, and
the stateful output behavior that the original harness cannot express.
"""
from __future__ import annotations


class LIS3DHI2C:
    ADDRESSES = {0x18, 0x19}

    def __init__(self):
        self.regs = {0x0F: 0x33, 0x1E: 0x10, 0x1F: 0x00, 0x20: 0x07, 0x23: 0x00, 0x27: 0x00}
        self.regs.update({a: 0 for a in range(0x28, 0x2E)})
        self._sample = (0, 0, 0)
        self._latched = None
        self._read_axes = set()

    def _check(self, addr7):
        if addr7 not in self.ADDRESSES:
            raise ValueError(f"LIS3DH NACK at 7-bit address 0x{addr7:02x}")

    def _write_one(self, reg, value):
        if reg in (0x0F, 0x27) or 0x28 <= reg <= 0x2D:
            return
        if reg == 0x20 and (value >> 4) > 0x9:
            raise ValueError("unsupported LIS3DH ODR encoding 0xA-0xF")
        self.regs[reg] = value & 0xFF
        if reg == 0x23:
            self._refresh_output()

    def i2c_write(self, addr7, subaddress, data):
        self._check(addr7)
        auto = bool(subaddress & 0x80)
        reg = subaddress & 0x7F
        for value in data:
            self._write_one(reg, value)
            if auto:
                reg += 1

    def _refresh_output(self):
        x, y, z = self._sample
        ble = bool(self.regs[0x23] & 0x40)
        pairs = []
        for value in (x, y, z):
            value &= 0xFFFF
            lo, hi = value & 0xFF, (value >> 8) & 0xFF
            pairs.extend((hi, lo) if ble else (lo, hi))
        for offset, byte in enumerate(pairs):
            self.regs[0x28 + offset] = byte

    def set_sample(self, x, y, z):
        bdu = bool(self.regs[0x23] & 0x80)
        if bdu and self._read_axes:
            self._latched = (x, y, z)
            return
        self._sample = (x, y, z)
        self._refresh_output()

    def i2c_read(self, addr7, subaddress, length):
        self._check(addr7)
        auto = bool(subaddress & 0x80)
        reg = subaddress & 0x7F
        data = []
        for _ in range(length):
            data.append(self.regs.get(reg, 0) & 0xFF)
            if 0x28 <= reg <= 0x2D:
                self._read_axes.add((reg - 0x28) // 2)
            if auto:
                reg += 1
        if len(self._read_axes) == 3 and self._latched is not None:
            self._sample = self._latched
            self._latched = None
            self._read_axes.clear()
            self._refresh_output()
        return bytes(data)


class MPU6050I2C:
    ADDRESSES = {0x68, 0x69}

    def __init__(self):
        self.reset_values = {0x19: 0x00, 0x1A: 0x00, 0x1B: 0x00, 0x1C: 0x00, 0x6B: 0x40, 0x75: 0x68}
        self.reset_values.update({a: 0 for a in range(0x3B, 0x41)})
        self.regs = dict(self.reset_values)
        self.last_transaction = []

    def _check(self, addr7):
        if addr7 not in self.ADDRESSES:
            raise ValueError(f"MPU6050 NACK at 7-bit address 0x{addr7:02x}")

    def _write_one(self, reg, value):
        if reg == 0x75 or 0x3B <= reg <= 0x40:
            return
        if reg == 0x6B and value & 0x80:
            self.regs = dict(self.reset_values)
            return
        self.regs[reg] = value & 0xFF

    def i2c_write(self, addr7, register, data):
        self._check(addr7)
        self.last_transaction = ["START", "AD+W", "ACK", "RA", "ACK"]
        for index, value in enumerate(data):
            self._write_one(register + index, value)
            self.last_transaction.extend(["DATA", "ACK"])
        self.last_transaction.append("STOP")

    def i2c_read(self, addr7, register, length):
        self._check(addr7)
        self.last_transaction = ["START", "AD+W", "ACK", "RA", "ACK", "REPEATED_START", "AD+R", "ACK"]
        data = [self.regs.get(register + index, 0) & 0xFF for index in range(length)]
        for index in range(length):
            self.last_transaction.extend(["DATA", "ACK" if index < length - 1 else "NACK"])
        self.last_transaction.append("STOP")
        return bytes(data)
