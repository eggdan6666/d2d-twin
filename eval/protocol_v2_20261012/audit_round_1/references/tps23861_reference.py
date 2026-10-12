# -*- coding: utf-8 -*-
"""TPS23861 人工参考实现（金标代码，仅用于校验 testbench，不参评）。

依据 d2d/ir/TPS23861_gold_ir.json（§7.5 p.45-46 + 各详情表 POR VALUE）。三处关键语义：
  · **Clear-on-Read 别名地址**：读 03h/05h/07h/09h/0Bh 返回同一份数据但把该寄存器整体清零
    （详情表原文：『a read at each location returns the same register data with the exception
    that the Clear-on-Read command clears all bits of the register』）
  · 17h 的 `-` 无功能位与 `R` ROM 位、27h 高 4 位 ROM ⇒ 写不进、读回复位值
  · 40h 低 4 位手册 RST STATE 标 `-`（复位值未定义）⇒ IR 用 UNSPEC，不判分；本实现按可写存储
    处理只是参考实现的自由选择，不影响任何断言
  · 18h/19h/1Ah 纯写命令：写被接受但无可读回状态，故不留存
"""
from base_sensor import BaseVirtualSensor


class TPS23861_Simulator(BaseVirtualSensor):
    RESET = {
        0x00: 0x80,
        0x02: 0x00, 0x04: 0x00, 0x06: 0x00, 0x08: 0x00, 0x0A: 0x30,
        0x0C: 0x00, 0x0D: 0x00, 0x0E: 0x00, 0x0F: 0x00, 0x10: 0x00,
        0x17: 0x80, 0x18: 0x00, 0x19: 0x00, 0x1A: 0x00,
        0x27: 0x00, 0x2C: 0x00, 0x40: 0x00, 0xFE: 0x00,
    }
    RO = {0x00, 0x02, 0x04, 0x06, 0x08, 0x0A, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x2C, 0xFE}
    WRITE_MASK = {0x17: 0x91, 0x27: 0x0F, 0x40: 0xFF}
    WO = {0x18, 0x19, 0x1A}
    COR = {0x03: 0x02, 0x05: 0x04, 0x07: 0x06, 0x09: 0x08, 0x0B: 0x0A}

    def __init__(self):
        super().__init__()
        self.regs = dict(self.RESET)

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        if addr in self.COR:                       # 读即清别名地址
            target = self.COR[addr]
            v = self.regs.get(target, 0) & 0xFF
            self.regs[target] = 0                 # clears all bits
            return v
        if addr in self.WO:
            return 0                               # 纯写命令无可读回状态
        return self.regs.get(addr, 0) & 0xFF

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        if addr in self.WO or addr in self.RO or addr not in self.WRITE_MASK:
            return                                 # 只读/纯写/未定义地址：不改变状态
        mask = self.WRITE_MASK[addr]
        self.regs[addr] = (self.regs[addr] & ~mask & 0xFF) | (data & mask)
