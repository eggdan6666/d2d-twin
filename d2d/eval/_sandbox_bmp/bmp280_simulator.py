# -*- coding: utf-8 -*-
"""BMP280 人工参考实现（金标代码，仅用于校验 testbench，不参评）。"""
from base_sensor import BaseVirtualSensor


class BMP280_Simulator(BaseVirtualSensor):
    REG_WIDTH = 8
    RESET = {0xD0: 0x58, 0xE0: 0x00, 0xF3: 0x00, 0xF4: 0x00, 0xF5: 0x00,
             0xF7: 0x80, 0xF8: 0x00, 0xF9: 0x00,
             0xFA: 0x80, 0xFB: 0x00, 0xFC: 0x00}
    RO = {0xD0, 0xF3, 0xF7, 0xF8, 0xF9, 0xFA, 0xFB, 0xFC}

    def __init__(self):
        super().__init__()
        self.regs = dict(self.RESET)

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        return self.regs.get(addr, 0) & 0xFF   # 8 位器件，nbytes 无特殊语义

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        if addr in self.RO:
            return
        data &= 0xFF
        if addr == 0xE0:                        # 软复位键：0xB6 生效，其余无效果，读恒 0
            if data == 0xB6:
                self.regs = dict(self.RESET)
            return
        self.regs[addr] = data
