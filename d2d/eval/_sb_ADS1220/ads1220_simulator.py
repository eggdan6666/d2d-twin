# -*- coding: utf-8 -*-
"""ADS1220 人工参考实现（金标代码，仅用于校验 testbench，不参评）。

正对照芯片：四个 8 位配置寄存器、位域全 R/W-0、复位全 00h，没有 RO 寄存器、没有只读位、
没有写触发位、没有 write-only 软复位键 ⇒ 行为等价于一个纯寄存器堆。
这颗的存在是为了证明复杂芯片上的低分不是断言写坏了。
"""
from base_sensor import BaseVirtualSensor


class ADS1220_Simulator(BaseVirtualSensor):
    RESET = {0x00: 0x00, 0x01: 0x00, 0x02: 0x00, 0x03: 0x00}
    RO = set()

    def __init__(self):
        super().__init__()
        self.regs = dict(self.RESET)

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        return self.regs.get(addr, 0) & 0xFF

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        if addr in self.RO:
            return
        self.regs[addr] = data & 0xFF
