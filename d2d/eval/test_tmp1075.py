# -*- coding: utf-8 -*-
"""D2D-Twin IR 驱动的黑盒断言 testbench（MVP）。

被测对象：tmp1075_simulator.<DEVICE>_Simulator（由 Coder 模型生成）。
所有断言从金标 IR 派生——换一款芯片只需换 ir/*.json，本文件零改动复用。
断言层级（对齐计划书模块四）：
  ①接口级  被测类继承 BaseVirtualSensor
  ②默认值级 上电读出 == IR.reset
  ③权限级  RO 寄存器写脏数据保持不变
  ④位域级  RW 字段写全 1 读回全 1（read_as 位除外）
  ⑤语义级  OS 读恒 0；单字节访问只碰 bits 15:8
"""
import importlib
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent
while not (ROOT / "ir" / "TMP1075_gold_ir.json").exists() and ROOT.parent != ROOT:
    ROOT = ROOT.parent          # 兼容任意深度沙盒：向上找项目根（含 ir/ 的那层）
sys.path.insert(0, str(ROOT / "rtl"))
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from base_sensor import BaseVirtualSensor  # noqa: E402

IR = json.load(open(ROOT / "ir" / "TMP1075_gold_ir.json", encoding="utf-8"))
DEVICE = IR["device"]
REGS = {r["name"]: r for r in IR["registers"]}


def u16(v):
    return int(v) & 0xFFFF


def bits_of(spec):
    parts = [int(x) for x in spec.split(":")]
    if len(parts) == 1:
        return parts[0], parts[0]
    return parts[0], parts[1]


@pytest.fixture(scope="module")
def sensor():
    sim = importlib.import_module("tmp1075_simulator")
    cls = getattr(sim, f"{DEVICE}_Simulator", None)
    if cls is None:
        pytest.fail(f"被测模块缺少 {DEVICE}_Simulator 类")
    inst = cls()
    assert isinstance(inst, BaseVirtualSensor), "必须继承 base_sensor.BaseVirtualSensor"
    return inst


def test_reset_values(sensor):
    """②上电默认值：每寄存器读出 == IR.reset"""
    for r in IR["registers"]:
        got = u16(sensor.read_register(int(r["addr"], 16)))
        exp = int(r["reset"], 16)
        assert got == exp, f"{r['name']}({r['addr']}) 复位值期望 {exp:#06x}，实得 {got:#06x}"


def test_readonly_protection(sensor):
    """③RO 寄存器写脏数据后保持 reset 值"""
    dirty = 0xA5A5
    for r in IR["registers"]:
        if r["access"] != "RO":
            continue
        rst = int(r["reset"], 16)
        sensor.write_register(int(r["addr"], 16), dirty)
        got = u16(sensor.read_register(int(r["addr"], 16)))
        assert got == rst, f"{r['name']} 是 RO：写 {dirty:#06x} 后应保持 {rst:#06x}，实得 {got:#06x}"


def test_rw_field_persistence(sensor):
    """④每个 RW 字段：写全 1 后读回该字段全 1，其余位不受影响；read_as 位按标注"""
    for r in IR["registers"]:
        if r["access"] == "RO":
            continue
        addr = int(r["addr"], 16)
        rst = int(r["reset"], 16)
        for f in r["fields"]:
            if f["access"] != "RW":
                continue
            hi, lo = bits_of(f["bits"])
            width = hi - lo + 1
            fmask = ((1 << width) - 1) << lo
            sensor.write_register(addr, rst | fmask)
            got = u16(sensor.read_register(addr))
            exp = f["read_as"] if f.get("read_as") is not None else (1 << width) - 1
            act = (got >> lo) & ((1 << width) - 1)
            assert act == exp, (
                f"{r['name']}.{f['name']}[{f['bits']}] 写全 1 后读回 {act}，期望 {exp}"
                f"（整寄存器 {got:#06x}）")
            sensor.write_register(addr, rst)


def test_os_bit_reads_as_zero(sensor):
    """⑤OS 位：写 1 启动单次转换，读恒 0（Table 7-8 明文）"""
    f = {x["name"]: x for x in REGS["CFGR"]["fields"]}["OS"]
    if f.get("read_as") is None:
        pytest.skip("IR 未标注 OS read_as")
    addr = int(REGS["CFGR"]["addr"], 16)
    rst = int(REGS["CFGR"]["reset"], 16)
    sensor.write_register(addr, rst | 0x8000)
    got = u16(sensor.read_register(addr))
    assert (got >> 15) & 1 == 0, f"OS 位写 1 后读回应 0，实得 {got:#06x}"
    sensor.write_register(addr, rst)


def test_single_byte_semantics(sensor):
    """⑤单字节访问：写只更新 bits 15:8，读只返回 bits 15:8"""
    sem = IR.get("single_byte_semantics", {})
    if not sem or sem.get("applies_to") == "none":
        pytest.skip("IR 未启用单字节语义")
    addr = int(REGS["CFGR"]["addr"], 16)
    rst = int(REGS["CFGR"]["reset"], 16)
    sensor.write_register(addr, rst)
    sensor.write_register(addr, 0x40, nbytes=1)  # 0x40=R[1:0] 高位，刻意避开 bit15=OS（读恒 0 会自清）
    full = u16(sensor.read_register(addr, nbytes=2))
    exp = (0x40 << 8) | (rst & 0xFF)
    assert full == exp, f"单字节写 0x40 后整寄存器期望 {exp:#06x}，实得 {full:#06x}"
    high = sensor.read_register(addr, nbytes=1)
    assert high == (full >> 8) & 0xFF, f"单字节读应返回 bits 15:8（{(full>>8)&0xFF:#04x}），实得 {high:#04x}"
    sensor.write_register(addr, rst)
