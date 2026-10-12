# -*- coding: utf-8 -*-
"""TMP126 人工参考实现（金标代码，仅用于校验 testbench，不参评）。

依据 d2d/ir/TMP126_gold_ir.json（PDF §8.6 p.26-33，Revision C 直读）：
  · RO 寄存器 00h/01h/02h：写忽略
  · 02h ALERT_STATUS：CRC/Slew/THigh/TLow/Data_Ready 五个标志位读即清除（手册逐位标 RC），
    掩码 0x00B7
  · CONFIG(03h)：bit15:9 与 bit6 是文档明示的 R-0 保留位；bit8「Resets」写 1 触发全寄存器回
    默认且自身不保存（读恒 0）；bit4 One_Shot 同样自清零
  · 05h/06h/08h：可写位域在 15:2 / 14:2，低 2 位与 08h 的 bit15 是 R-0 保留位
"""
from base_sensor import BaseVirtualSensor


class TMP126_Simulator(BaseVirtualSensor):
    RESET = {
        0x00: 0x0000, 0x01: 0x0000, 0x02: 0x0000, 0x03: 0x0006, 0x04: 0x0016,
        0x05: 0xF380, 0x06: 0x2A80, 0x07: 0x0A0A, 0x08: 0x0500,
    }
    RO = {0x00, 0x01, 0x02}
    READ_CLEAR = {0x02: 0x00B7}          # bit7,5,2,1,0 = CRC/Slew/THigh/TLow/Data_Ready 标志
    WRITE_MASK = {
        0x03: 0x00AF,                    # AVG|INT_COMP|MODE|CONV_PERIOD；bit8/bit4 自清零不存储
        0x04: 0x001F,                    # 5 个 Alert_En；bit15:5 保留读 0
        0x05: 0xFFFC,                    # TLow_Limit[13:0] 占 15:2，低 2 位读 0
        0x06: 0xFFFC,
        0x07: 0xFFFF,                    # 两个 8-bit 迟滞字段
        0x08: 0x7FFC,                    # Slew_Rate_Limit[12:0] 占 14:2；bit15 与 1:0 读 0
    }
    RESETS_BIT = 0x0100                  # CONFIG[8]
    ONE_SHOT_BIT = 0x0010                # CONFIG[4]

    def __init__(self):
        super().__init__()
        self.regs = dict(self.RESET)

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        v = self.regs.get(addr, 0) & 0xFFFF
        m = self.READ_CLEAR.get(addr)
        if m:
            self.regs[addr] = v & ~m & 0xFFFF     # 本次返回旧值，之后标志位清零
        return v

    def _soft_reset(self):
        self.regs = dict(self.RESET)

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        if addr in self.RO:
            return
        data &= 0xFFFF
        if addr == 0x03 and (data & self.RESETS_BIT):
            self._soft_reset()                     # 写 1 触发复位，该位读回恒 0
            return
        mask = self.WRITE_MASK.get(addr, 0xFFFF)
        if addr == 0x03:
            mask &= ~self.ONE_SHOT_BIT             # One_Shot 触发动作但不存储
        self.regs[addr] = (self.regs[addr] & ~mask & 0xFFFF) | (data & mask)
