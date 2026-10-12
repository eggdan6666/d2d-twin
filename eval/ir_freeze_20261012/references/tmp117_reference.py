# -*- coding: utf-8 -*-
"""TMP117 人工参考实现（金标代码，仅用于校验 testbench，不参评）。

依据 d2d/ir/TMP117_gold_ir.json（PDF §7.6 p.25-29）：
  · 只读寄存器：00h TEMP（复位 8000h 非零）、0Fh DEVICE_ID（0117h）
  · CONFIG：bit15:12 只读标志（未建模 read-to-clear，见 IR Q2）、bit11:2 可写、bit1 SOFT_RESET 写 1
    触发全寄存器回默认且该位不存储（读恒 0）、bit0 保留读 0
  · EEPROM_UL：仅 bit15 EUN 可写，其余 15 位读 0
  · EEPROM1-3：整字可写；EUN 写 gating 不建模（IR Q3）
"""
from base_sensor import BaseVirtualSensor


class TMP117_Simulator(BaseVirtualSensor):
    RESET = {
        0x00: 0x8000, 0x01: 0x0220, 0x02: 0x6000, 0x03: 0x8000, 0x04: 0x0000,
        0x05: 0x0000, 0x06: 0x0000, 0x07: 0x0000, 0x08: 0x0000, 0x0F: 0x0117,
    }
    RO = {0x00, 0x0F}
    WRITE_MASK = {
        0x01: 0x0FFC,          # bit11:2 可写；bit15:12 只读标志、bit1 自清零、bit0 保留
        0x02: 0xFFFF, 0x03: 0xFFFF,
        0x04: 0x8000,          # 只有 EUN 可写
        0x05: 0xFFFF, 0x06: 0xFFFF, 0x07: 0xFFFF, 0x08: 0xFFFF,
    }
    SOFT_RESET_BIT = 0x0002
    READ_CLEAR_FLAGS = 0xF000     # HIGH_ALERT/LOW_ALERT/DATA_READY：读 CONFIG 或 TEMP 即清除
                                  # （EEPROM_BUSY 不在此列，它随 EEPROM 编程结束而变）

    def __init__(self):
        super().__init__()
        self.regs = dict(self.RESET)

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        v = self.regs.get(addr, 0) & 0xFFFF
        if addr in (0x00, 0x01):
            self.regs[0x01] = self.regs.get(0x01, 0) & ~self.READ_CLEAR_FLAGS
        return v

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        if addr in self.RO:
            return
        data &= 0xFFFF
        if addr == 0x01 and (data & self.SOFT_RESET_BIT):
            self.regs = dict(self.RESET)     # 2ms 软复位：全部回默认，SOFT_RESET 位本身不存储
            return
        mask = self.WRITE_MASK.get(addr, 0xFFFF)
        self.regs[addr] = (self.regs[addr] & ~mask & 0xFFFF) | (data & mask)
