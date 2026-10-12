# -*- coding: utf-8 -*-
"""BME280 人工参考实现（金标代码，仅用于校验 testbench，不参评）。"""
from base_sensor import BaseVirtualSensor


class BME280_Simulator(BaseVirtualSensor):
    REG_WIDTH = 8
    RESET = {0xD0: 0x60, 0xE0: 0x00, 0xF2: 0x00, 0xF3: 0x00, 0xF4: 0x00, 0xF5: 0x00,
             0xF7: 0x80, 0xF8: 0x00, 0xF9: 0x00,
             0xFA: 0x80, 0xFB: 0x00, 0xFC: 0x00,
             0xFD: 0x80, 0xFE: 0x00}
    RO = {0xD0, 0xF3, 0xF7, 0xF8, 0xF9, 0xFA, 0xFB, 0xFC, 0xFD, 0xFE}
    # RW 寄存器内的硬连 0 位：ctrl_hum bits7:3
    RO_MASKS = {0xF2: 0xF8}

    def __init__(self):
        super().__init__()
        self.regs = dict(self.RESET)

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        return self.regs.get(addr, 0) & 0xFF

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        if addr in self.RO:
            return
        data &= 0xFF
        if addr == 0xE0:                        # 软复位键：0xB6 生效，其余无效果，读恒 0
            if data == 0xB6:
                self.regs = dict(self.RESET)
            return
        ro = self.RO_MASKS.get(addr, 0)
        self.regs[addr] = (data & ~ro & 0xFF) | (self.regs[addr] & ro)
