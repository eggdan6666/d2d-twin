# -*- coding: utf-8 -*-
"""TMP102 人工参考实现（金标代码，仅用于校验 testbench，不参评）。"""
from base_sensor import BaseVirtualSensor


class TMP102_Simulator(BaseVirtualSensor):
    RESET = {0x00: 0x0000, 0x01: 0x60A0, 0x02: 0x4B00, 0x03: 0x5000}
    RO = {0x00}
    # RW 寄存器内的只读位：CONFIG 的 R1/R0/AL（写忽略）+ CONFIG/TLOW/THIGH 低 4 位保留（硬连 0）
    RO_MASKS = {0x01: (1 << 14) | (1 << 13) | (1 << 5) | 0xF,
                0x02: 0xF, 0x03: 0xF}

    def __init__(self):
        super().__init__()
        self.regs = dict(self.RESET)

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        return self.regs.get(addr, 0) & 0xFFFF

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        if addr in self.RO:
            return
        data &= 0xFFFF
        ro = self.RO_MASKS.get(addr, 0)
        self.regs[addr] = (data & ~ro & 0xFFFF) | (self.regs[addr] & ro)
