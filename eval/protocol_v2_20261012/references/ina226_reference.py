# -*- coding: utf-8 -*-
"""INA226 人工参考实现（金标代码，仅用于校验 testbench，不参评）。

依据 d2d/ir/INA226_gold_ir.json（PDF SBOS547C p.22–26 直读）：
  · RO：01h/02h/03h/04h/FEh/FFh
  · CONFIG(00h)：D15 RST 写 1 ⇒ 全寄存器回默认且自身不保存（p.23 self-clears）；
    D14:12 未命名保留位（POR=100b）不可写 ⇒ 写掩码 0x0FFF
  · CALIBRATION(05h)：D15 未命名保留 ⇒ 0x7FFF
  · MASK_ENABLE(06h)：D9:5 未命名保留、D4:2 为硬件标志 ⇒ 0xFC03
  · 不建模 ADC/告警通路，故 01h–04h 与 AFF/CVRF/OVF 恒为复位值
"""
from base_sensor import BaseVirtualSensor


class INA226_Simulator(BaseVirtualSensor):
    RESET = {
        0x00: 0x4127, 0x01: 0x0000, 0x02: 0x0000, 0x03: 0x0000, 0x04: 0x0000,
        0x05: 0x0000, 0x06: 0x0000, 0x07: 0x0000, 0xFE: 0x5449, 0xFF: 0x2260,
    }
    RO = {0x01, 0x02, 0x03, 0x04, 0xFE, 0xFF}
    WRITE_MASK = {0x00: 0x0FFF, 0x05: 0x7FFF, 0x06: 0xFC03, 0x07: 0xFFFF}
    RST_BIT = 0x8000

    def __init__(self):
        super().__init__()
        self.regs = dict(self.RESET)

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        return self.regs.get(addr, 0) & 0xFFFF

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        if addr in self.RO:
            return
        data &= 0xFFFF
        if addr == 0x00 and (data & self.RST_BIT):
            self.regs = dict(self.RESET)          # 系统复位，RST 位本身不保存
            return
        mask = self.WRITE_MASK.get(addr, 0x0000)
        self.regs[addr] = (self.regs[addr] & ~mask & 0xFFFF) | (data & mask)
