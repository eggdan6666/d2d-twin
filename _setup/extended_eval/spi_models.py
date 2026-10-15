"""AD5592R SPI protocol model for the extended software tests."""
from __future__ import annotations


class AD5592RSPI:
    RESET = {0x1: 0x0000, 0x2: 0x0000, 0x3: 0x0000, 0x4: 0x0000, 0x5: 0x0000, 0x6: 0x00FF}
    CONFIG_READ_AND_LDAC = 0x7
    IO_CONFIG_REGS = {0x4, 0x5, 0x6}

    def __init__(self):
        self.regs = dict(self.RESET)
        self.time_us = 0
        self.readback_selector = None
        self.io_locked = False
        self.last_dac_write = None

    def advance_time_us(self, amount):
        self.time_us += amount

    def _require_ready(self):
        if self.time_us < 250:
            raise RuntimeError("AD5592R write attempted during 250 us power-up interval")

    @staticmethod
    def _word(data):
        if len(data) != 2:
            raise ValueError("AD5592R SPI transfer must be exactly 16 bits")
        return (data[0] << 8) | data[1]

    def _control_write(self, selector, payload):
        if selector == 0xF:
            if payload == 0x5AC:
                self.regs = dict(self.RESET)
                self.io_locked = False
            return
        # Control words reserve data bits 10:9; they are forced to zero.
        payload &= 0x7FF
        payload &= ~((1 << 10) | (1 << 9))
        if self.io_locked and selector in self.IO_CONFIG_REGS:
            return
        if selector == 0x3:
            self.regs[selector] = payload
            self.io_locked = bool(payload & (1 << 7))
            return
        if selector in self.RESET:
            self.regs[selector] = payload

    def spi_transfer(self, data):
        """Transfer one 16-bit word and return one 16-bit response word."""
        self._require_ready()
        word = self._word(data)
        if self.readback_selector is not None:
            selector = self.readback_selector
            self.readback_selector = None
            value = self.regs.get(selector, 0) & 0xFFFF
            return bytes([(value >> 8) & 0xFF, value & 0xFF])
        if word & 0x8000:
            channel = (word >> 12) & 0x7
            self.last_dac_write = (channel, word & 0x0FFF)
            return b"\x00\x00"
        selector = (word >> 11) & 0xF
        payload = word & 0x7FF
        if selector == self.CONFIG_READ_AND_LDAC and (payload & (1 << 6)):
            self.readback_selector = (payload >> 2) & 0xF
        self._control_write(selector, payload)
        return b"\x00\x00"
