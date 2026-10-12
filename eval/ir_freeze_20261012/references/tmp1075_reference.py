# -*- coding: utf-8 -*-
"""TMP1075 人工参考实现（金标代码）。

作用不是被测，而是校验 testbench 本身：把本文件放进沙盒改名为
tmp1075_simulator.py 跑 pytest，6 个测试必须全绿——
否则是 testbench/IR 有 bug，先修 harness 再评 Coder 模型。
"""
from base_sensor import BaseVirtualSensor


class TMP1075_Simulator(BaseVirtualSensor):
    RESET = {0x00: 0x0000, 0x01: 0x00FF, 0x02: 0x4B00, 0x03: 0x5000, 0x0F: 0x7500}
    RO = {0x00, 0x0F}

    def __init__(self):
        super().__init__()
        self.regs = dict(self.RESET)

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        v = self.regs.get(addr, 0) & 0xFFFF
        if nbytes == 1:
            return (v >> 8) & 0xFF
        return v

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        if addr in self.RO:
            return
        if nbytes == 1:
            data = (data & 0xFF) << 8 | (self.regs.get(addr, 0) & 0xFF)
        data &= 0xFFFF
        if addr == 0x01:                      # CFGR: OS 位写 1 触发转换后自清，读恒 0
            data &= ~(1 << 15) & 0xFFFF
        self.regs[addr] = data
