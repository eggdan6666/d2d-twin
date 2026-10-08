# -*- coding: utf-8 -*-
"""INA219 人工参考实现（金标代码，仅用于校验 testbench，不参评）。

依据 d2d/ir/INA219_gold_ir.json（TI SBOS448G，p.18-24）。
关键语义：
  · 16 位寄存器堆（00h-05h）
  · CONFIGURATION (00h) 上电复位值 399Fh
  · CONFIG.RST (bit 15) 写 1 触发软复位恢复全部寄存器出厂值，且该位自清零（读回恒 0）
  · CALIBRATION (05h) 的 bit 0 为 void bit，硬件强制恒 0（不可写）
  · 01h-04h 为只读测量与状态寄存器，写操作忽略
"""
from base_sensor import BaseVirtualSensor


class INA219_Simulator(BaseVirtualSensor):
    DEFAULTS = {
        0x00: 0x399F,
        0x01: 0x0000,
        0x02: 0x0000,
        0x03: 0x0000,
        0x04: 0x0000,
        0x05: 0x0000,
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
        if addr == 0x00:
            if data & 0x8000:
                # RST 位触发软复位：全部寄存器恢复出厂值
                self.regs = dict(self.DEFAULTS)
            else:
                # RST 自清零，bit 14 可写 (R/W-0)
                self.regs[0x00] = data & 0x7FFF
        elif addr == 0x05:
            # bit 0 void bit 硬件强制恒 0
            self.regs[0x05] = data & 0xFFFE
        # 0x01, 0x02, 0x03, 0x04 为只读，写操作忽略
