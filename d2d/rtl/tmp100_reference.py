# -*- coding: utf-8 -*-
"""TMP100 人工参考实现（金标代码，仅用于校验 testbench，不参评）。

按 d2d/ir/TMP100_gold_ir.json 编码。三处关键语义：
  1. CONFIG 是 8 位寄存器，复位总线读回 0x80（内部位全 0，但 OS/ALERT 上电读 1）；
  2. 默认分辨率 R1R0=00 → 温度与阈值寄存器只有 bits[15:7] 可存，bits[6:0] 硬连 0
     （手册：『For 9-, 10-, or 11-bit resolution, the MSBs ... unused least significant bits
     equal to zero』）——这是 TMP100 与 TMP102（12 位、R1R0 只读）的实质差异；
  3. 8 位寄存器被 2 字节读时按 IR 约定仍返回该 8 位值（见 IR open_questions Q2）。
"""
from base_sensor import BaseVirtualSensor


class TMP100_Simulator(BaseVirtualSensor):
    WIDTH_8BIT = {0x01}
    RESET = {0x00: 0x0000, 0x01: 0x0080, 0x02: 0x4B00, 0x03: 0x5000}
    RO = {0x00}
    # RW 寄存器内可存储的位：CONFIG 全 8 位可写；阈值只有高 9 位可写，低 7 位硬连 0
    WRITE_MASK = {0x01: 0x00FF, 0x02: 0xFF80, 0x03: 0xFF80}

    def __init__(self):
        super().__init__()
        self.regs = dict(self.RESET)

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        val = self.regs.get(addr, 0)
        if addr in self.WIDTH_8BIT:
            return val & 0xFF
        return (val >> 8) & 0xFF if nbytes == 1 else val & 0xFFFF

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        if addr in self.RO:
            return
        mask = self.WRITE_MASK.get(addr, 0xFFFF)
        if addr not in self.WIDTH_8BIT and nbytes == 1:
            data = (data << 8) | (self.regs[addr] & 0x00FF)
            mask &= 0xFF00
        self.regs[addr] = (self.regs[addr] & ~mask & 0xFFFF) | (data & mask)
