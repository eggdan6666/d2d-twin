# -*- coding: utf-8 -*-
"""D2D-Twin 通用黑盒断言 testbench（芯片无关，全部断言由 IR 派生）。

选择被测芯片：环境变量 D2D_IR 指定 ir/ 下的金标文件名（默认 TMP1075_gold_ir.json）。
被测模块：tmp1075_simulator.py 风格命名——<小写device>_simulator.py，
          类名 <Device>_Simulator，必须继承 base_sensor.BaseVirtualSensor。

断言层（全部由 IR 注解驱动，换芯片零代码改动）：
  ①接口级    继承检查
  ②默认值级  非运行时寄存器上电读出 == IR.reset（runtime_value:true 的跳过）
  ③权限级    RO 寄存器写脏数据后逐位不变（前后快照，兼容运行时值）
  ④位域级    RW 字段写全 1 读回全 1（带 read_as 的写触发/自清零位不在此列，交 ⑤）
  ⑤语义级    W 寄存器：非键写入无副作用；写键值 → 全部寄存器回复位值（软复位）

两个字段级注解（2026-10-07 加，均为**保持既有分母**设计——不用就等同于不存在）：
  · access:"UNSPEC"   手册既没给访问码、也没说读回值的保留位。不判分，但把模型行为
                       （写全 1 后读回什么）**记录**进 d2d_diag.json。Q0 保留位约定因此
                       可以在 strict / relax / unspec 三档间离线重判，不烧 GPU。
  · read_action:"clear" 读该寄存器即清除的硬件标志（read-to-clear）。③/⑤ 在比快照前
                       会把这类位掩掉——否则"读一次拿 before"这个动作本身就把位清了，
                       会把忠实实现的器件误判成错（实测触发条件：寄存器级 RO 或非零复位的
                       RO 位内含 read-clear；现有 6 颗都恰好不满足，故默认不影响分数）。
"""
import atexit
import importlib
import json
import os
import pathlib
import sys

import pytest

IR_NAME = os.environ.get("D2D_IR", "TMP1075_gold_ir.json")
DIAG_ON = bool(os.environ.get("D2D_DIAG"))
ROOT = pathlib.Path(__file__).resolve().parent
while not (ROOT / "ir" / IR_NAME).exists() and ROOT.parent != ROOT:
    ROOT = ROOT.parent          # 兼容任意深度沙盒：向上找项目根
sys.path.insert(0, str(ROOT / "rtl"))
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from base_sensor import BaseVirtualSensor  # noqa: E402

IR = json.load(open(ROOT / "ir" / IR_NAME, encoding="utf-8"))
DEVICE = IR["device"]
MASK = (1 << IR.get("reg_width", 16)) - 1
REGS = {r["name"]: r for r in IR["registers"]}

_DIAG = {"chip": DEVICE, "unspecified_bits": [], "read_clear_observed": []}


def _flush_diag():
    if DIAG_ON:
        with open(pathlib.Path(__file__).parent / "d2d_diag.json", "w", encoding="utf-8") as f:
            json.dump(_DIAG, f, ensure_ascii=False, indent=1)


atexit.register(_flush_diag)


def read_clear_mask(reg):
    """该寄存器里『读即清除』的位（字段级 read_action:clear）。"""
    m = 0
    for f in reg.get("fields", []):
        if f.get("read_action") == "clear":
            hi, lo, fm = amask(f["bits"])
            m |= fm
    return m & MASK



def amask(spec):
    """'15:4'/'8' -> (hi, lo, 字段掩码)"""
    parts = [int(x) for x in spec.split(":")]
    hi = parts[0]
    lo = parts[-1]
    return hi, lo, ((1 << (hi - lo + 1)) - 1) << lo


@pytest.fixture(scope="module")
def sensor():
    sim = importlib.import_module(f"{DEVICE.lower()}_simulator")
    cls = getattr(sim, f"{DEVICE}_Simulator", None)
    if cls is None:
        pytest.fail(f"被测模块缺少 {DEVICE}_Simulator 类")
    inst = cls()
    assert isinstance(inst, BaseVirtualSensor), "必须继承 base_sensor.BaseVirtualSensor"
    return inst


def snapshot(sensor):
    """按 IR 地址表拍快照（跳过 write-only 寄存器——读它们超出黑盒契约）"""
    return {r["name"]: int(sensor.read_register(int(r["addr"], 16))) & MASK
            for r in IR["registers"] if r["access"] != "W"}


def test_reset_values(sensor):
    """②可读寄存器上电 == IR.reset（runtime_value 与 write-only 跳过）"""
    for r in IR["registers"]:
        if r.get("runtime_value") or r["access"] == "W":
            continue
        got = int(sensor.read_register(int(r["addr"], 16))) & MASK
        exp = int(r["reset"], 16)
        assert got == exp, f"{r['name']}({r['addr']}) 复位值期望 {exp:#0{IR['reg_width']//4+2}x}，实得 {got:#x}"


def test_readonly_protection(sensor):
    """③RO 寄存器写脏数据后快照不变（前后对比，兼容运行时值与读清零位）"""
    dirty = 0xA5A5 & MASK
    for r in IR["registers"]:
        if r["access"] != "RO":
            continue
        addr = int(r["addr"], 16)
        rc_mask = read_clear_mask(r)
        before = int(sensor.read_register(addr)) & MASK
        if rc_mask:
            before2 = int(sensor.read_register(addr)) & MASK   # 读清零：第二次读才是稳定基线
            _DIAG["read_clear_observed"].append(
                {"reg": r["name"], "before_first": hex(before), "before_second": hex(before2)})
            before = before2
        sensor.write_register(addr, dirty)
        after = int(sensor.read_register(addr)) & MASK
        if rc_mask:
            after = int(sensor.read_register(addr)) & MASK
        assert (after & ~rc_mask) == (before & ~rc_mask), \
            f"{r['name']} 是 RO：写脏数据后 {before:#x} → {after:#x}"


def wtarget(r):
    """该寄存器该往哪个地址写：有读写别名的芯片（LM83 类）写地址≠读地址。"""
    return int(r.get("write_addr", r["addr"]), 16)


def test_rw_field_persistence(sensor):
    """④每个 RW 字段：写全 1 读回全 1；read_as 位按标注；UNSPEC 位只记录不判分"""
    for r in IR["registers"]:
        if r["access"] != "RW":
            continue
        addr = int(r["addr"], 16)
        wa = wtarget(r)
        rst = int(r["reset"], 16)
        for f in r["fields"]:
            if f["access"] == "UNSPEC":
                hi, lo, fmask = amask(f["bits"])
                sensor.write_register(wa, MASK)
                got = int(sensor.read_register(addr)) & MASK
                act = (got >> lo) & ((1 << (hi - lo + 1)) - 1)
                sensor.write_register(wa, rst)
                _DIAG["unspecified_bits"].append(
                    {"reg": r["name"], "field": f["name"], "bits": f["bits"],
                     "written": "all1", "readback": act, "readback_hex": hex(got)})
                continue
            if f["access"] != "RW":
                continue
            if f.get("read_as") is not None:
                continue      # 带 read_as 的写触发/自清零位归断言⑤管；④再查一次会把同一缺陷计两遍
            hi, lo, fmask = amask(f["bits"])
            sensor.write_register(wa, rst | fmask)
            got = int(sensor.read_register(addr)) & MASK
            exp = f["read_as"] if f.get("read_as") is not None else (1 << (hi - lo + 1)) - 1
            act = (got >> lo) & ((1 << (hi - lo + 1)) - 1)
            assert act == exp, (
                f"{r['name']}.{f['name']}[{f['bits']}] 写全 1 后读回 {act}，期望 {exp}"
                f"（整寄存器 {got:#x}）")
            sensor.write_register(wa, rst)
        # RW 寄存器内的 RO 位保护：写全 1 后，只读字段必须保持复位值
        # （钓把 R1/R0/AL 这类只读位当可写存储的模型）
        for f in r["fields"]:
            if f["access"] != "RO" or r["access"] != "RW":
                continue
            if f.get("read_action") == "clear":
                _DIAG["read_clear_observed"].append(
                    {"reg": r["name"], "field": f["name"], "skipped": "读清零位不参与复位值断言"})
                continue
            hi, lo, fmask = amask(f["bits"])
            sensor.write_register(wa, MASK)
            got = int(sensor.read_register(addr)) & MASK
            exp = f["read_as"] if f.get("read_as") is not None else f.get("reset", 0)
            act = (got >> lo) & ((1 << (hi - lo + 1)) - 1)
            assert act == exp, (
                f"{r['name']}.{f['name']}[{f['bits']}] 是 RW 寄存器内的 RO 位："
                f"写全 1 后读回 {act}，期望复位值 {exp}（整寄存器 {got:#x}）")
        sensor.write_register(wa, rst)


def test_write_trigger_fields(sensor):
    """⑤IR 标 read_as 的写触发位（如 TMP1075 OS）：写 1 后读回必须等于 read_as"""
    triggers = [(rn, f) for rn, r in REGS.items() for f in r["fields"]
                if f["access"] == "RW" and f.get("read_as") is not None]
    if not triggers:
        pytest.skip("IR 无写触发位")
    for rn, f in triggers:
        r = REGS[rn]
        addr = int(r["addr"], 16)
        rst = int(r["reset"], 16)
        hi, lo, fmask = amask(f["bits"])
        sensor.write_register(addr, rst | fmask)
        got = int(sensor.read_register(addr)) & MASK
        act = (got >> lo) & ((1 << (hi - lo + 1)) - 1)
        assert act == f["read_as"], f"{rn}.{f['name']} 写触发后读回 {act}，期望 {f['read_as']}"
        sensor.write_register(addr, rst)


def test_single_byte_semantics(sensor):
    """⑤单字节语义（IR.single_byte_semantics 驱动）：写只更新高字节，读只返回高字节。
    IR 需给 test_register（要求其高字节 bit0 是普通 RW 位，避开 read_as 触发位）。"""
    sem = IR.get("single_byte_semantics") or {}
    rn = sem.get("test_register")
    if not rn or sem.get("applies_to") in ("none", None):
        pytest.skip("IR 未启用单字节语义")
    r = REGS[rn]
    addr = int(r["addr"], 16)
    rst = int(r["reset"], 16)
    sensor.write_register(addr, rst)
    sensor.write_register(addr, 0x01, nbytes=1)
    full = int(sensor.read_register(addr, nbytes=2)) & MASK
    exp = (0x01 << 8) | (rst & 0xFF)
    assert full == exp, f"单字节写 0x01 后整寄存器期望 {exp:#x}，实得 {full:#x}"
    high = sensor.read_register(addr, nbytes=1)
    assert high == (full >> 8) & 0xFF, f"单字节读应返回高字节 {full>>8:#x}，实得 {high:#x}"
    sensor.write_register(addr, rst)


def test_read_write_alias(sensor):
    """⑦读写别名寄存器（LM83 类：同一逻辑寄存器读地址≠写地址）。

    由 IR 的 write_addr 注解触发，**没标就该测试自动 skip** ⇒ 不加这个注解的芯片分母不变。
    两条断言：① 写别名地址必须能从主（读）地址读回；② 写主地址不得改变内容（那是只读位置）。
    模型几乎必然只实现一个地址——这是前面 9 颗芯片钓不到的维度。
    """
    aliased = [(n, r) for n, r in REGS.items() if r.get("write_addr")]
    if not aliased:
        pytest.skip("IR 无读写别名寄存器")
    dirty = 0x5A & MASK
    for name, r in aliased:
        ra, wa = int(r["addr"], 16), int(r["write_addr"], 16)
        rst = int(r["reset"], 16)
        ro_mask = 0
        for f in r.get("fields", []):
            if f["access"] != "RW":
                _, _, fm = amask(f["bits"])
                ro_mask |= fm
        writable = (MASK & ~ro_mask) or MASK
        # ① 写别名地址 → 主地址读回一致（只比可写位）
        sensor.write_register(wa, (rst & ~writable) | (dirty & writable))
        got = int(sensor.read_register(ra)) & MASK
        exp = (rst & ~writable) | (dirty & writable)
        assert (got & writable) == (exp & writable), \
            f"{name}: 写别名地址 {wa:#04x} 后从 {ra:#04x} 读回 {got:#x}，期望 {exp:#x}"
        sensor.write_register(wa, rst)
        # ② 写主（只读）地址不得改变内容
        before = int(sensor.read_register(ra)) & MASK
        sensor.write_register(ra, 0xFF & MASK)
        after = int(sensor.read_register(ra)) & MASK
        assert after == before, \
            f"{name}: 主地址 {ra:#04x} 是只读位置，写脏数据却把 {before:#x} 改成 {after:#x}"
        sensor.write_register(wa, rst)


def test_write_only_reset_key(sensor):
    """⑤W 寄存器软复位键：非键写入无副作用；写键值 → 全部寄存器回复位"""
    wo = [(n, r) for n, r in REGS.items() if r["access"] == "W"]
    if not wo:
        pytest.skip("IR 无 write-only 寄存器")
    for name, r in wo:
        addr = int(r["addr"], 16)
        key = int(r["write_key"], 16)
        garbage = key ^ 0xFF & MASK or 0x01
        before = snapshot(sensor)
        sensor.write_register(addr, garbage)
        assert snapshot(sensor) == before, \
            f"{name} 写非键值 {garbage:#x} 不应产生任何效果"
        sensor.write_register(addr, key)
        after = snapshot(sensor)
        for rn, rr in REGS.items():
            if rr.get("runtime_value") or rr["access"] == "W":
                continue
            exp = int(rr["reset"], 16)
            assert after[rn] == exp, \
                f"写 {name}=键值 后 {rn} 应回复位 {exp:#x}，实得 {after[rn]:#x}"
            # 恢复现场由下一个测试的上电语义不保证——软复位本身就是恢复
