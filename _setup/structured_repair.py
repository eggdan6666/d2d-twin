# -*- coding: utf-8 -*-
"""IR-constrained fallback repair for one generated peripheral emulator.

This is intentionally deterministic: it uses only the frozen IR to rebuild
the register access layer, so it can serve as a safe reference candidate when
free-form LLM repair regresses. It does not modify the benchmark harness.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys


def bits_mask(spec: str) -> int:
    p = [int(x) for x in spec.split(":")]
    hi, lo = p[0], p[-1]
    return ((1 << (hi - lo + 1)) - 1) << lo


def intv(x) -> int:
    return int(x, 16) if isinstance(x, str) else int(x)


def render(ir: dict) -> str:
    device = ir["device"]
    mask = (1 << ir.get("reg_width", 16)) - 1
    regs = {intv(r["addr"]): intv(r.get("reset", 0)) for r in ir["registers"]}
    ro = [intv(r["addr"]) for r in ir["registers"] if r["access"] == "RO"]
    aliases = {
        intv(r["write_addr"]): intv(r["addr"])
        for r in ir["registers"] if r.get("write_addr")
    }
    aliased_reads = sorted(aliases.values())
    writable = {}
    read_as = {}
    for r in ir["registers"]:
        if r["access"] != "RW":
            continue
        m = 0
        for f in r.get("fields", []):
            if f.get("access") == "RW":
                m |= bits_mask(f["bits"])
        writable[intv(r["addr"])] = m & mask
        forced = []
        for f in r.get("fields", []):
            if f.get("read_as") is not None:
                forced.append((bits_mask(f["bits"]), int(f["read_as"])))
        if forced:
            read_as[intv(r["addr"])] = forced
    for r in ir["registers"]:
        forced = []
        for f in r.get("fields", []):
            if f.get("read_as") is not None:
                forced.append((bits_mask(f["bits"]), int(f["read_as"])))
        if forced:
            read_as[intv(r["addr"])] = forced

    def fmt_map(m):
        return "{\n" + "\n".join(f"            0x{k:02X}: 0x{v:X}," for k, v in sorted(m.items())) + "\n        }"

    return f'''from base_sensor import BaseVirtualSensor

class {device}_Simulator(BaseVirtualSensor):
    def __init__(self):
        super().__init__()
        self.regs = {fmt_map(regs)}
        self._ro_addrs = {sorted(ro)!r}
        self._write_to_read = {aliases!r}
        self._aliased_reads = {aliased_reads!r}
        self._writable_masks = {writable!r}
        self._read_as = {read_as!r}

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        if addr not in self.regs:
            return 0
        value = self.regs[addr] & {mask:#x}
        for field_mask, forced in self._read_as.get(addr, []):
            value = (value & ~field_mask) | (forced & field_mask)
        if nbytes == 1:
            return ((value >> 8) & 0xFF) if {ir.get('reg_width', 16)} > 8 else (value & 0xFF)
        return value

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        if addr in self._aliased_reads:
            return
        addr = self._write_to_read.get(addr, addr)
        if addr not in self.regs or addr in self._ro_addrs:
            return
        writable = self._writable_masks.get(addr, {mask:#x})
        if nbytes == 1 and {ir.get('reg_width', 16)} > 8:
            value = ((data & 0xFF) << 8) | (self.regs[addr] & 0xFF)
        else:
            value = data & 0xFF if nbytes == 1 else data & {mask:#x}
        self.regs[addr] = ((self.regs[addr] & ~writable) | (value & writable)) & {mask:#x}
'''


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--ir", required=True)
    ap.add_argument("--tag", default="structured")
    args = ap.parse_args()
    root = pathlib.Path(args.project)
    ir = json.loads((root / "ir" / args.ir).read_text(encoding="utf-8"))
    code = render(ir)
    sandbox = root / "eval" / f"_structured_sandbox_{args.tag}"
    if sandbox.exists():
        import shutil
        shutil.rmtree(sandbox)
    sandbox.mkdir(parents=True)
    import shutil
    shutil.copy2(root / "rtl" / "base_sensor.py", sandbox / "base_sensor.py")
    shutil.copy2(root / "eval" / "test_d2d_blackbox.py", sandbox / "test_d2d_blackbox.py")
    (sandbox / f"{ir['device'].lower()}_simulator.py").write_text(code, encoding="utf-8")
    p = subprocess.run(
        [sys.executable, "-m", "pytest", "test_d2d_blackbox.py", "-q", "--tb=line"],
        cwd=sandbox, env={**__import__("os").environ, "D2D_IR": args.ir},
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    print(p.stdout + p.stderr)
    out = root / "eval" / f"structured_repair_{args.tag}.py"
    out.write_text(code, encoding="utf-8")
    print(f"candidate: {out}")
    return p.returncode


if __name__ == "__main__":
    raise SystemExit(main())
