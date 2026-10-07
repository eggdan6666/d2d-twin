# -*- coding: utf-8 -*-
"""LIS2DW12 人工参考实现（金标代码，仅用于校验 testbench，不参评）。

依据 d2d/ir/LIS2DW12_gold_ir.json（PDF p.33-55 直读；解析稿有损不可用）：
  · 8 位寄存器芯片（reg_width=8）
  · RO：0Dh/0Eh/0Fh/26h/27h/2Fh/38h；WHO_AM_I 复位 0x44（非零）
  · CTRL2(21h)：bit6 SOFT_RESET 写 1 触发全寄存器回默认且自身不保存（读恒 0）；
    bit5 位图只写 0 且脚注『must be set to 0』——无访问码列 ⇒ C 档，本实现按硬连 0
  · WAKE_UP_SRC(38h)：bit5..0 是锁存标志，读该寄存器即清除（ST 的 latched 语义）；
    bit7:6 位图写 0 ⇒ C 档
"""
from base_sensor import BaseVirtualSensor


class LIS2DW12_Simulator(BaseVirtualSensor):
    REG_WIDTH = 8
    RESET = {
        0x0D: 0x00, 0x0E: 0x00, 0x0F: 0x44, 0x20: 0x00, 0x21: 0x04,
        0x23: 0x00, 0x24: 0x00, 0x26: 0x00, 0x27: 0x00, 0x2E: 0x00,
        0x2F: 0x00, 0x38: 0x00, 0x3C: 0x00, 0x3D: 0x00, 0x3E: 0x00,
    }
    RO = {0x0D, 0x0E, 0x0F, 0x26, 0x27, 0x2F, 0x38}
    READ_CLEAR = {0x38: 0x3F}          # FF_IA/SLEEP_STATE_IA/WU_IA/X_WU/Y_WU/Z_WU 读清除
    WRITE_MASK = {
        0x20: 0xFF,
        0x21: 0xBF,                    # 1011_1111：bit6 SOFT_RESET 自清零不存储、bit5 文档要求保持 0，其余可写
        0x23: 0xFF, 0x24: 0xFF, 0x2E: 0xFF,
        0x3C: 0xFF, 0x3D: 0xFF, 0x3E: 0xFF,
    }
    SOFT_RESET_BIT = 0x40              # CTRL2[6]

    def __init__(self):
        super().__init__()
        self.regs = dict(self.RESET)

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        v = self.regs.get(addr, 0) & 0xFF
        m = self.READ_CLEAR.get(addr)
        if m:
            self.regs[addr] = v & ~m & 0xFF     # 本次返回旧值，之后标志位清零
        return v

    def _soft_reset(self):
        self.regs = dict(self.RESET)

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        if addr in self.RO:
            return
        data &= 0xFF
        if addr == 0x21 and (data & self.SOFT_RESET_BIT):
            self._soft_reset()                   # 写 1 复位，该位读回恒 0
            return
        mask = self.WRITE_MASK.get(addr, 0x00)
        self.regs[addr] = (self.regs[addr] & ~mask & 0xFF) | (data & mask)
