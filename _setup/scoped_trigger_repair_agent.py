# -*- coding: utf-8 -*-
"""Scope-audited DEVICE_RESET repair probe."""
from __future__ import annotations

import argparse
import difflib
import json
import pathlib
import re

from repair_agent import extract_code, load_model, run_harness, PROJECT_ROOT


def trigger_register(ir: dict) -> dict:
    for reg in ir.get("registers", []):
        if "PWR_MGMT_1" in reg.get("name", "") or any("DEVICE_RESET" in f.get("name", "") for f in reg.get("fields", [])):
            return reg
    return {}


def trigger_trace(tail: str) -> str:
    lines = [x for x in tail.splitlines() if "DEVICE_RESET" in x or "PWR_MGMT_1" in x]
    return "\n".join(lines) or tail[-1500:]


def scope_audit(before: str, after: str) -> dict:
    diff = list(difflib.unified_diff(before.splitlines(), after.splitlines(), n=0))
    changed = [x for x in diff if x.startswith(("+", "-")) and not x.startswith(("+++", "---"))]
    changed_text = "\n".join(changed)
    allowed_terms = ("0x6B", "0x80", "DEVICE_RESET", "PWR_MGMT_1", "reset_device", "self-clearing", "self clearing")
    disallowed_addr = re.findall(r"0x(?:19|1A|1B|1C|3B|3C|3D|3E|3F|40|75)\b", changed_text, re.I)
    disallowed_names = [x for x in ("ACCEL_", "WHO_AM_I", "SMPLRT_DIV", "GYRO_CONFIG", "CONFIG", "ACCEL_CONFIG") if x in changed_text]
    unrelated = disallowed_addr + disallowed_names
    return {"scope_ok": not unrelated and any(t in changed_text for t in allowed_terms), "changed_lines": len(changed), "unrelated_tokens": sorted(set(unrelated)), "diff": changed[:80]}


def prompt_for(device: str, reg: dict, code: str, trace: str) -> str:
    return f'''You are applying a surgical patch to a {device} register emulator.
Return exactly one complete Python code block and nothing else.

ONLY repair the DEVICE_RESET write-trigger semantics in PWR_MGMT_1. A valid
patch may change only the write path for address 0x6B and the minimal helper
needed to clear DEVICE_RESET after the trigger. Do not change any other address,
register, reset value, RO behavior, bitfield, alias, nbytes rule, class shape,
or protocol behavior. Preserve all existing code and passing tests.

The outer evaluator will reject any candidate whose code diff touches unrelated
registers. The candidate must pass the unchanged frozen harness.

Relevant IR register only:
```json
{json.dumps(reg, ensure_ascii=False, indent=1)}
```

Current implementation:
```python
{code}
```

DEVICE_RESET failure evidence only:
```text
{trace}
```
'''


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--model-path', required=True)
    ap.add_argument('--tag', required=True)
    ap.add_argument('--items', nargs='+', required=True)
    args = ap.parse_args()
    tokenizer, model = load_model(args.model_path)
    import torch
    output = []
    for item in args.items:
        chip, result_file, index_s = item.split(':', 2)
        idx = int(index_s)
        records = json.loads((PROJECT_ROOT / 'eval' / result_file).read_text(encoding='utf-8'))
        baseline_code = records[idx]['code']
        ir_name = f'{chip}_gold_ir.json'
        ir = json.loads((PROJECT_ROOT / 'ir' / ir_name).read_text(encoding='utf-8'))
        tag = f'{args.tag}_{chip.lower()}_{idx}'
        baseline = run_harness(baseline_code, ir_name, tag, 0)
        messages = [
            {'role': 'system', 'content': 'You are a conservative embedded-systems patch engineer.'},
            {'role': 'user', 'content': prompt_for(chip, trigger_register(ir), baseline_code, trigger_trace(baseline['tail']))},
        ]
        encoded = tokenizer(tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True), return_tensors='pt', add_special_tokens=False).to('cuda')
        with torch.no_grad():
            generated = model.generate(**encoded, max_new_tokens=2048, do_sample=False, pad_token_id=tokenizer.eos_token_id)
        raw = tokenizer.decode(generated[0][encoded.input_ids.shape[1]:], skip_special_tokens=True)
        candidate = extract_code(raw)
        if not candidate:
            output.append({'chip': chip, 'index': idx, 'status': 'no_code', 'baseline': baseline, 'raw_tail': raw[-4000:]})
            print(chip, idx, 'no_code')
            continue
        checked = run_harness(candidate, ir_name, tag, 1)
        audit = scope_audit(baseline_code, candidate)
        if not audit['scope_ok']:
            status = 'scope_reject'
        elif checked['rc'] == 0:
            status = 'clean_success'
        elif checked['passed'] > baseline['passed']:
            status = 'scoped_partial'
        else:
            status = 'scoped_no_improvement'
        output.append({'chip': chip, 'index': idx, 'status': status, 'baseline': baseline, 'candidate': checked, 'scope_audit': audit})
        print(chip, idx, status, 'baseline=', baseline['passed'], 'candidate=', checked['passed'], 'scope_ok=', audit['scope_ok'])
    out_path = PROJECT_ROOT / 'eval' / f'scoped_trigger_results_{args.tag}.json'
    out_path.write_text(json.dumps({'model_path': args.model_path, 'focus': 'PWR_MGMT_1.DEVICE_RESET', 'results': output}, ensure_ascii=False, indent=2), encoding='utf-8')
    print('output:', out_path)


if __name__ == '__main__':
    raise SystemExit(main())
