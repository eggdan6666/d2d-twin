# -*- coding: utf-8 -*-
"""D2D-Twin 基类（MVP 接口 v1）。

被测仿真器必须继承 BaseVirtualSensor 并实现 read_register / write_register。
Testbench 只通过本接口与被测代码交互，保证黑盒性——被测代码内部怎么存、
怎么算，testbench 一概不感知（不 import 其内部符号、不直读 self.regs）。

nbytes 语义（对齐真实 I2C 字节访问）：
  nbytes=2 完整寄存器读写；
  nbytes=1 单字节访问，按器件 IR 的 single_byte_semantics 生效
            （TMP1075: 写只更新 bits 15:8，读只返回 bits 15:8）。
"""


class BaseVirtualSensor:
    REG_WIDTH = 16  # 本基准目标器件寄存器宽度（16 位为主）

    def __init__(self):
        self.regs = {}  # addr(int) -> value(int)；子类可用，testbench 不读

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        raise NotImplementedError

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        raise NotImplementedError
