# -*- coding: utf-8 -*-
"""Failure-driven repair loop for D2D-Twin.

This utility is deliberately separate from the frozen benchmark harness. It
loads one stored generation, asks a local code model to repair it from the
pytest failure trace, and re-runs the unchanged harness in a fresh sandbox.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time


ROOT = pathlib.Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT / "d2d" if (ROOT / "d2d" / "ir").exists() else ROOT
BASE_FILE = PROJECT_ROOT / "rtl" / "base_sensor.py"
TEST_FILE = PROJECT_ROOT / "eval" / "test_d2d_blackbox.py"


def extract_code(text: str) -> str | None:
    match = re.search(r"```python\s*\n(.*?)```", text, re.S)
    if not match:
        match = re.search(r"```\s*\n(.*?)```", text, re.S)
    return (match.group(1).rstrip() + "\n") if match else None


def run_harness(code: str, ir_name: str, tag: str, round_id: int) -> dict:
    ir = json.loads((PROJECT_ROOT / "ir" / ir_name).read_text(encoding="utf-8"))
    device = ir["device"]
    sandbox = PROJECT_ROOT / "eval" / f"_repair_sandbox_{tag}_{round_id}"
    if sandbox.exists():
        shutil.rmtree(sandbox)
    sandbox.mkdir(parents=True)
    shutil.copy2(BASE_FILE, sandbox / "base_sensor.py")
    shutil.copy2(TEST_FILE, sandbox / "test_d2d_blackbox.py")
    (sandbox / f"{device.lower()}_simulator.py").write_text(code, encoding="utf-8")
    env = dict(os.environ, D2D_IR=ir_name, PYTHONIOENCODING="utf-8")
    started = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "test_d2d_blackbox.py", "-q", "--tb=line"],
        cwd=sandbox, env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=180,
    )
    output = (proc.stdout + "\n" + proc.stderr).strip()
    match = re.search(r"(\d+) passed", output)
    return {
        "round": round_id,
        "rc": proc.returncode,
        "passed": int(match.group(1)) if match else 0,
        "elapsed_s": round(time.perf_counter() - started, 2),
        "tail": output[-5000:],
        "code": code,
        "sandbox": str(sandbox),
    }


def repair_prompt(device: str, ir: dict, code: str, failure_tail: str, round_id: int) -> str:
    return f"""You are repairing a Python register-level peripheral emulator.

This is repair round {round_id}. Return exactly one complete Python code block.
Do not modify the test harness, invent undocumented behavior, remove assertions,
or explain the answer outside the code block. Preserve all behavior that already
passes. Fix only the failures demonstrated by the pytest trace.

Never add registers, addresses, fields, or side effects that are absent from the
IR. Keep every IR address and reset value exact. A candidate that loses passing
tests must be rejected by the outer test gate.

The class must be {device}_Simulator(BaseVirtualSensor), use only the standard
library, and implement the provided IR. Pay special attention to RO masking,
RW bitfield preservation, write_addr aliases, read_as side effects, cor_addr,
and nbytes semantics when they appear in the IR.

## IR
```json
{json.dumps(ir, ensure_ascii=False, indent=1)}
```

## Current implementation
```python
{code}
```

## Frozen Harness failure trace
```text
{failure_tail}
```
"""


def load_model(model_path: str):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    kwargs = dict(attn_implementation="eager")
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_path, dtype=torch.bfloat16, **kwargs
        )
    except TypeError:
        model = AutoModelForCausalLM.from_pretrained(
            model_path, torch_dtype=torch.bfloat16, **kwargs
        )
    model.eval().to("cuda")
    return tokenizer, model


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", required=True)
    parser.add_argument("--result", required=True)
    parser.add_argument("--ir", required=True)
    parser.add_argument("--index", type=int, default=0)
    parser.add_argument("--max-rounds", type=int, default=2)
    parser.add_argument("--tag", default="repair")
    args = parser.parse_args()

    records = json.loads(pathlib.Path(args.result).read_text(encoding="utf-8"))
    record = records[args.index]
    code = record.get("code")
    if not code:
        raise SystemExit("Selected record has no extracted code")
    ir = json.loads((PROJECT_ROOT / "ir" / args.ir).read_text(encoding="utf-8"))
    device = ir["device"]
    output_path = PROJECT_ROOT / "eval" / f"repair_results_{args.tag}.json"
    results = [{"stage": "baseline", **run_harness(code, args.ir, args.tag, 0)}]
    tokenizer, model = load_model(args.model_path)

    best = results[0]
    for round_id in range(1, args.max_rounds + 1):
        previous = best
        prompt = repair_prompt(device, ir, code, previous["tail"], round_id)
        messages = [
            {"role": "system", "content": "You are an expert embedded-systems code repair engineer."},
            {"role": "user", "content": prompt},
        ]
        text_in = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        encoded = tokenizer(text_in, return_tensors="pt", add_special_tokens=False).to("cuda")
        import torch
        with torch.no_grad():
            generated = model.generate(
                **encoded,
                max_new_tokens=2048,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
        raw = tokenizer.decode(
            generated[0][encoded.input_ids.shape[1]:], skip_special_tokens=True
        )
        candidate = extract_code(raw)
        if not candidate:
            results.append({"stage": f"repair_{round_id}", "rc": -1, "passed": 0,
                            "tail": raw[-5000:], "code": None})
            break
        checked = run_harness(candidate, args.ir, args.tag, round_id)
        checked["stage"] = f"repair_{round_id}"
        results.append(checked)
        # Keep the incumbent on ties: an equal pass count can still hide new
        # collection errors or regressions in dimensions not summarized by
        # the first pytest line. A repair must strictly improve the gate, or
        # finish the whole harness successfully.
        if checked["passed"] > best["passed"] or checked["rc"] == 0:
            best = checked
            code = candidate
        if best["rc"] == 0:
            break

    output_path.write_text(json.dumps({
        "model_path": args.model_path,
        "result_source": args.result,
        "ir": args.ir,
        "selected_index": args.index,
        "results": results,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "output": str(output_path),
        "stages": [{k: r.get(k) for k in ("stage", "rc", "passed", "elapsed_s")}
                   for r in results],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
