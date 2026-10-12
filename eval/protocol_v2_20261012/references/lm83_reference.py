# -*- coding: utf-8 -*-
"""LM83 人工参考实现（金标代码，仅用于校验 testbench，不参评）。

依据 d2d/ir/LM83_gold_ir.json（§2.0-2.7 p.13-15）。这颗的关键语义：
  · **读写别名**：6 个逻辑寄存器的读地址≠写地址（CONFIG 读 03h/写 09h；LHS 05h/0Bh；
    D2RHS 07h/0Dh；D1RHS 38h/50h；D3RHS 3Ah/52h；TCS 42h/5Ah）——写只读位置不改变内容
  · **位级保留恒 0**：CONFIG 的 D6/D0 原话『A write of 1 will return a 0 when read』；
    SR1 的 D7/D5/D3、SR2 的 D6/D3 同理（都在只读寄存器里）
  · **非零复位值**：四个 HIGH 设定点与 T_CRIT 上电 = 7Fh（127°C）；MID = 01h
  · 保留地址（04h/06h/08h/0Eh-2Fh…）手册未定义读回值 ⇒ 不入断言，本实现按 0 返回
"""
from base_sensor import BaseVirtualSensor


class LM83_Simulator(BaseVirtualSensor):
    # 读地址: (写地址或 None, 复位值, 可写掩码)
    MAP = {
        0x00: (None, 0x00, 0x00),
        0x01: (None, 0x00, 0x00),
        0x02: (None, 0x00, 0x00),
        0x03: (0x09, 0x00, 0xBE),
        0x05: (0x0B, 0x7F, 0xFF),
        0x07: (0x0D, 0x7F, 0xFF),
        0x30: (None, 0x00, 0x00),
        0x31: (None, 0x00, 0x00),
        0x35: (None, 0x00, 0x00),
        0x38: (0x50, 0x7F, 0xFF),
        0x3A: (0x52, 0x7F, 0xFF),
        0x42: (0x5A, 0x7F, 0xFF),
        0xFE: (None, 0x01, 0x00),
        0xFF: (None, 0x00, 0x00),
    }
    WRITE_TO_READ = {w: r for r, (w, _d, _m) in MAP.items() if w}

    def __init__(self):
        super().__init__()
        self.regs = {r: v[1] for r, v in self.MAP.items()}

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        return self.regs.get(addr, 0) & 0xFF

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        target = self.WRITE_TO_READ.get(addr)          # 别名写地址 → 逻辑寄存器
        if target is None:
            if addr in self.MAP:                        # 直接写只读位置：忽略
                return
            return                                      # 未定义/保留地址：忽略
        _, _, mask = self.MAP[target]
        self.regs[target] = (self.regs[target] & ~mask & 0xFF) | (data & mask)
