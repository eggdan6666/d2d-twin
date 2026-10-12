# -*- coding: utf-8 -*-
"""HDC2021 人工参考实现（金标代码，仅用于校验 testbench，不参评）。

依据 d2d/ir/HDC2021_gold_ir.json（PDF §7.6 p.20-32）：
  · 8 位寄存器；测量/状态/MAX/ID 全只读（ID 复位值非零）
  · 0x0E bit7 SOFT_RES：写 1 → 全部寄存器回默认值，该位自清零（读恒 0）
  · 0x07 INTERRUPT_ENABLE 低 3 位、0x04 STATUS 低 3 位：TI 的 TYPE 列空白，按现行保留位约定编成硬连 0
  · 0x0F bit3 名为 RES 但手册标 R/W → 可写（与 INA3221 Mask/Enable bit15 同例）
"""
from base_sensor import BaseVirtualSensor


class HDC2021_Simulator(BaseVirtualSensor):
    RESET = {
        0x00: 0x00, 0x01: 0x00, 0x02: 0x00, 0x03: 0x00, 0x04: 0x00, 0x05: 0x00, 0x06: 0x00,
        0x07: 0x00, 0x08: 0x00, 0x09: 0x00,
        0x0A: 0x01, 0x0B: 0xFF, 0x0C: 0x00, 0x0D: 0xFF,
        0x0E: 0x00, 0x0F: 0x00,
        0xFC: 0x49, 0xFD: 0x54, 0xFE: 0xD0, 0xFF: 0x07,
    }
    RO = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0xFC, 0xFD, 0xFE, 0xFF}
    WRITE_MASK = {0x07: 0xF8, 0x08: 0xFF, 0x09: 0xFF, 0x0A: 0xFF, 0x0B: 0xFF,
                  0x0C: 0xFF, 0x0D: 0xFF, 0x0E: 0x7F, 0x0F: 0xFF}
    SOFT_RES_BIT = 0x80

    def __init__(self):
        super().__init__()
        self.regs = dict(self.RESET)

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        return self.regs.get(addr, 0) & 0xFF

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        if addr in self.RO:
            return
        data &= 0xFF
        if addr == 0x0E and (data & self.SOFT_RES_BIT):
            self.regs = dict(self.RESET)      # 软复位：全部回默认，SOFT_RES 本身不存储
            return
        mask = self.WRITE_MASK.get(addr, 0xFF)
        self.regs[addr] = (self.regs[addr] & ~mask & 0xFF) | (data & mask)
