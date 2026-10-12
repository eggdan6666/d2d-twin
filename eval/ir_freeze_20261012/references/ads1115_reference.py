# -*- coding: utf-8 -*-
"""ADS1115 人工参考实现（金标代码，仅用于校验 testbench，不参评）。

依据 d2d/ir/ADS1115_gold_ir.json（TI SBAS444D，p.24-28）。
关键语义：
  · 16 位寄存器堆（00h-03h）
  · CONFIG (01h) 上电复位值 8583h
  · LO_THRESH (02h) 上电复位值 8000h
  · HI_THRESH (03h) 上电复位值 7FFFh
  · CONVERSION (00h) 为只读寄存器，复位值 0000h，写操作忽略
"""
from base_sensor import BaseVirtualSensor


class ADS1115_Simulator(BaseVirtualSensor):
    DEFAULTS = {
        0x00: 0x0000,
        0x01: 0x8583,
        0x02: 0x8000,
        0x03: 0x7FFF,
    }

    def __init__(self):
        super().__init__()
        self.regs = dict(self.DEFAULTS)

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        val = self.regs.get(addr, 0) & 0xFFFF
        if nbytes == 1:
            return (val >> 8) & 0xFF
        return val

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        data &= 0xFFFF
        if addr in (0x01, 0x02, 0x03):
            self.regs[addr] = data
        # 0x00 is RO: ignore
