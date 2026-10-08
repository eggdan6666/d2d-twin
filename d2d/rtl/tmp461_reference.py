# -*- coding: utf-8 -*-
"""TMP461 人工参考实现（金标代码，仅用于校验 testbench，不参评）。

依据 d2d/ir/TMP461_gold_ir.json（TI SBOS722B，§8.6 Register Map p.17-23）。
关键语义：
  · 读写别名：6 组寄存器读地址≠写地址（CONFIG 读 03h/写 09h；CONV_RATE 04h/0Ah；
    LOCAL_HIGH_LIMIT 05h/0Bh；LOCAL_LOW_LIMIT 06h/0Ch；
    REMOTE_HIGH_LIMIT_HIGH 07h/0Dh；REMOTE_LOW_LIMIT_HIGH 08h/0Eh）
    写只读地址不改变内容；写写别名地址更新对应逻辑寄存器。
  · 读即清零（Read-to-Clear）：
    STATUS (02h) 的 D6-D2 位为告警/断线标志，读该寄存器后这 5 个标志清零。
  · 只写触发：
    ONE_SHOT (0Fh) 为只写寄存器，写任意值启动单次转换，读该地址无效。
  · 掩码保护与保留位：
    - CONFIG (03h): 可写位 D7, D6, D5, D2 (掩码 0xE4)，其余保留恒 0
    - CONV_RATE (04h): 可写位 D3-D0 (掩码 0x0F)
    - REMOTE_OFFSET_LOW (12h): 可写位 D7-D4 (掩码 0xF0)
    - REMOTE_HIGH_LIMIT_LOW (13h): 可写位 D7-D4 (掩码 0xF0)
    - REMOTE_LOW_LIMIT_LOW (14h): 可写位 D7-D4 (掩码 0xF0)
    - CHANNEL_ENABLE (16h): 可写位 D1-D0 (掩码 0x03)
    - CONSECUTIVE_ALERT (22h): 可写位 D3-D1 (掩码 0x0E)，D0 固定恒 1 (0x01)
    - DIGITAL_FILTER (24h): 可写位 D1-D0 (掩码 0x03)
"""
from base_sensor import BaseVirtualSensor


class TMP461_Simulator(BaseVirtualSensor):
    # 读地址: (写地址或 None, 复位值, 可写掩码)
    MAP = {
        0x00: (None, 0x00, 0x00),      # TEMP_LOCAL_HIGH
        0x01: (None, 0x00, 0x00),      # TEMP_REMOTE_HIGH
        0x02: (None, 0x00, 0x00),      # STATUS (D6-D2 读即清)
        0x03: (0x09, 0x00, 0xE4),      # CONFIG
        0x04: (0x0A, 0x08, 0x0F),      # CONV_RATE
        0x05: (0x0B, 0x7F, 0xFF),      # LOCAL_HIGH_LIMIT
        0x06: (0x0C, 0x80, 0xFF),      # LOCAL_LOW_LIMIT
        0x07: (0x0D, 0x7F, 0xFF),      # REMOTE_HIGH_LIMIT_HIGH
        0x08: (0x0E, 0x80, 0xFF),      # REMOTE_LOW_LIMIT_HIGH
        0x0F: (0x0F, 0x00, 0x00),      # ONE_SHOT (W-only)
        0x10: (None, 0x00, 0x00),      # TEMP_REMOTE_LOW
        0x11: (0x11, 0x00, 0xFF),      # REMOTE_OFFSET_HIGH
        0x12: (0x12, 0x00, 0xF0),      # REMOTE_OFFSET_LOW
        0x13: (0x13, 0xF0, 0xF0),      # REMOTE_HIGH_LIMIT_LOW
        0x14: (0x14, 0x00, 0xF0),      # REMOTE_LOW_LIMIT_LOW
        0x15: (None, 0x00, 0x00),      # TEMP_LOCAL_LOW
        0x16: (0x16, 0x03, 0x03),      # CHANNEL_ENABLE
        0x19: (0x19, 0x7F, 0xFF),      # REMOTE_THERM_LIMIT
        0x20: (0x20, 0x7F, 0xFF),      # LOCAL_THERM_LIMIT
        0x21: (0x21, 0x0A, 0xFF),      # THERM_HYSTERESIS
        0x22: (0x22, 0x01, 0x0E),      # CONSECUTIVE_ALERT (D0 固定 1)
        0x23: (0x23, 0x00, 0xFF),      # N_FACTOR
        0x24: (0x24, 0x00, 0x03),      # DIGITAL_FILTER
        0xFE: (None, 0x55, 0x00),      # MANUFACTURER_ID
    }
    WRITE_TO_READ = {w: r for r, (w, _d, _m) in MAP.items() if w}

    def __init__(self):
        super().__init__()
        self.regs = {r: v[1] for r, v in self.MAP.items()}

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        val = self.regs.get(addr, 0) & 0xFF
        if addr == 0x02:
            self.regs[0x02] &= ~0x7C   # D6-D2 读即清
        return val

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        if addr == 0x0F:
            return                      # ONE_SHOT 软触发，不存数据
        target = self.WRITE_TO_READ.get(addr)
        if target is None:
            return                      # 写只读位置或未定义地址：忽略
        _, _, mask = self.MAP[target]
        base = self.regs[target]
        if target == 0x22:
            self.regs[target] = ((base & ~mask & 0xFF) | (data & mask) | 0x01) & 0xFF
        else:
            self.regs[target] = ((base & ~mask & 0xFF) | (data & mask)) & 0xFF
