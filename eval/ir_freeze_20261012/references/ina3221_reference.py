# -*- coding: utf-8 -*-
"""INA3221 人工参考实现（金标代码，仅用于校验 testbench，不参评）。

依据 d2d/ir/INA3221_gold_ir.json（PDF p.24-37 原文）：
  · RO：01h-06h、0Dh（测量值）、FEh/FFh（ID，复位值非零）
  · 写掩码逐寄存器给：告警门限保留低 3 位为 0、累加门限保留 bit0、电源有效限保留 bit15 与低 3 位
  · CONFIG 的 RST(bit15)：写 1 → 全部寄存器回默认值，且该位自清零（读恒 0）
  · Mask/Enable 的 read-clear 语义 MVP 不建模（见 IR Q2），其余按手册逐位 R/W
"""
from base_sensor import BaseVirtualSensor


class INA3221_Simulator(BaseVirtualSensor):
    RESET = {
        0x00: 0x7127,
        0x01: 0x0000, 0x02: 0x0000, 0x03: 0x0000, 0x04: 0x0000, 0x05: 0x0000, 0x06: 0x0000,
        0x07: 0x7FF8, 0x08: 0x7FF8, 0x09: 0x7FF8, 0x0A: 0x7FF8, 0x0B: 0x7FF8, 0x0C: 0x7FF8,
        0x0D: 0x0000, 0x0E: 0x7FFE, 0x0F: 0x0002,
        0x10: 0x2710, 0x11: 0x2328,
        0xFE: 0x5449, 0xFF: 0x3220,
    }
    RO = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x0D, 0xFE, 0xFF}
    WRITE_MASK = {
        0x00: 0x7FFF,             # RST 不存储（自清零）
        0x07: 0xFFFF, 0x08: 0xFFFF, 0x09: 0xFFFF, 0x0A: 0xFFFF, 0x0B: 0xFFFF, 0x0C: 0xFFFF,
        # 手册 p.31-32 逐位标 bits 2-0 Reserved **R/W** 0h ⇒ 这 3 位可写（金标纠正，见 IR tier=B）
        0x0E: 0xFFFE,
        0x0F: 0xFC00,             # 只有 bit15(标 R/W 的 Reserved) + SCC1-3 + WEN + CEN 可写
        0x10: 0x7FF8, 0x11: 0x7FF8,
    }
    RST_BIT = 0x8000
    READ_CLEAR = {0x0F: 0x03F1}   # CF3-1/SF/WF3-1/CVRF：读 Mask/Enable 即清除（§8.2.16）
                                  # PVF/TCF 不在内——原文明说它们不随读清除

    def __init__(self):
        super().__init__()
        self.regs = dict(self.RESET)

    def _soft_reset(self):
        self.regs = dict(self.RESET)

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        v = self.regs.get(addr, 0) & 0xFFFF
        m = self.READ_CLEAR.get(addr)
        if m:
            self.regs[addr] = v & ~m          # 读清零：本次返回旧值，之后标志位归 0
        return v

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        if addr in self.RO:
            return
        data &= 0xFFFF
        if addr == 0x00 and (data & self.RST_BIT):
            self._soft_reset()
            return
        mask = self.WRITE_MASK.get(addr, 0xFFFF)
        self.regs[addr] = (self.regs[addr] & ~mask & 0xFFFF) | (data & mask)
