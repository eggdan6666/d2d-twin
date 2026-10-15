# -*- coding: utf-8 -*-
"""Structured write_register-only patch interface for DEVICE_RESET."""
from __future__ import annotations

import argparse
import ast
import difflib
import json
import pathlib
import re

from repair_agent import load_model, run_harness, PROJECT_ROOT


def extract_method(text: str) -> str | None:
    m = re.search(r"```python\s*\n(.*?)```", text, re.S)
    raw = m.group(1) if m else text
    lines = raw.strip("\n").splitlines()
    start = next((i for i, x in enumerate(lines) if x.lstrip().startswith("def write_register")), None)
    if start is None:
        return None
    body = lines[start:]
    # Normalize a top-level returned method to class indentation.
    if body and not body[0].startswith("    "):
        body = ["    " + x if x else x for x in body]
    # Keep only this method; discard accidental second definitions.
    cut = next((i for i, x in enumerate(body[1:], 1) if x.startswith("    def ")), len(body))
    return "\n".join(body[:cut]).rstrip() + "\n"


def replace_method(source: str, method: str) -> str | None:
    lines = source.splitlines()
    start = next((i for i, x in enumerate(lines) if x.startswith("    def write_register")), None)
    if start is None:
        return None
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("    def ")), len(lines))
    new_lines = method.rstrip("\n").splitlines()
    return "\n".join(lines[:start] + new_lines + lines[end:]) + "\n"


def method_scope(method: str) -> dict:
    # The method may use generic self.regs iteration; explicit unrelated
    # register literals are disallowed by this endpoint.
    tokens = re.findall(r"0x[0-9A-Fa-f]+", method)
    allowed = {"0x6B", "0x80", "0x40", "0x7F", "0x00", "0xFF", "0xFFFF", "0xFF00", "0x00FF"}
    bad = sorted(set(t for t in tokens if t.upper() not in {x.upper() for x in allowed}))
    try:
        ast.parse("class X:\n" + "\n".join("    " + x[4:] if x.startswith("    ") else "    " + x for x in method.splitlines()))
        syntax_ok = True
    except SyntaxError:
        syntax_ok = False
    return {"scope_ok": syntax_ok and not bad, "syntax_ok": syntax_ok, "explicit_literals": tokens, "disallowed_literals": bad}


def prompt_for(device: str, reg: dict, method: str, trace: str) -> str:
    return f'''Return only one Python method named write_register for {device}_Simulator.
Do not return a class, imports, prose, or any other method.

This is a structured patch endpoint. The caller will replace ONLY the existing
write_register method with your returned method. Preserve all behavior outside
address 0x6B. Implement only the IR-defined PWR_MGMT_1.DEVICE_RESET trigger:
when the DEVICE_RESET bit is written, restore the documented reset state and
clear the trigger bit as required. Do not add explicit addresses for other
registers; use existing self.regs state generically if needed. Preserve RO,
bitfield, alias, and nbytes behavior unrelated to this field.

Relevant IR register:
```json
{json.dumps(reg, ensure_ascii=False, indent=1)}
```

Current write_register method:
```python
{method}
```

DEVICE_RESET failure evidence:
```text
{trace}
```
'''


def trigger_register(ir: dict) -> dict:
    for r in ir.get("registers", []):
        if "PWR_MGMT_1" in r.get("name", "") or any("DEVICE_RESET" in f.get("name", "") for f in r.get("fields", [])):
            return r
    return {}


def trigger_trace(tail: str) -> str:
    return "\n".join(x for x in tail.splitlines() if "DEVICE_RESET" in x or "PWR_MGMT_1" in x) or tail[-1200:]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--model-path', required=True)
    ap.add_argument('--tag', required=True)
    ap.add_argument('--items', nargs='+', required=True)
    args = ap.parse_args()
    tokenizer, model = load_model(args.model_path)
    import torch
    results = []
    for item in args.items:
        chip, result_file, idx_s = item.split(':', 2)
        idx = int(idx_s)
        records = json.loads((PROJECT_ROOT / 'eval' / result_file).read_text(encoding='utf-8'))
        baseline_code = records[idx]['code']
        ir_name = f'{chip}_gold_ir.json'
        ir = json.loads((PROJECT_ROOT / 'ir' / ir_name).read_text(encoding='utf-8'))
        base_method = extract_method(baseline_code)
        tag = f'{args.tag}_{chip.lower()}_{idx}'
        baseline = run_harness(baseline_code, ir_name, tag, 0)
        if not base_method:
            results.append({'chip': chip, 'index': idx, 'status': 'no_baseline_method', 'baseline': baseline})
            continue
        prompt = prompt_for(chip, trigger_register(ir), base_method, trigger_trace(baseline['tail']))
        messages = [{'role': 'system', 'content': 'You return only structured Python method patches.'}, {'role': 'user', 'content': prompt}]
        encoded = tokenizer(tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True), return_tensors='pt', add_special_tokens=False).to('cuda')
        with torch.no_grad():
            generated = model.generate(**encoded, max_new_tokens=1600, do_sample=False, pad_token_id=tokenizer.eos_token_id)
        raw = tokenizer.decode(generated[0][encoded.input_ids.shape[1]:], skip_special_tokens=True)
        method = extract_method(raw)
        if not method:
            results.append({'chip': chip, 'index': idx, 'status': 'no_method', 'baseline': baseline, 'raw_tail': raw[-4000:]})
            continue
        scope = method_scope(method)
        patched = replace_method(baseline_code, method)
        if not patched:
            results.append({'chip': chip, 'index': idx, 'status': 'replace_failed', 'baseline': baseline, 'scope': scope})
            continue
        checked = run_harness(patched, ir_name, tag, 1)
        if not scope['scope_ok']:
            status = 'scope_reject'
        elif checked['rc'] == 0:
            status = 'clean_success'
        elif checked['passed'] > baseline['passed']:
            status = 'scoped_partial'
        else:
            status = 'scoped_no_improvement'
        results.append({'chip': chip, 'index': idx, 'status': status, 'baseline': baseline, 'candidate': checked, 'scope': scope, 'method': method})
        print(chip, idx, status, 'baseline=', baseline['passed'], 'candidate=', checked['passed'], 'scope_ok=', scope['scope_ok'])
    out = PROJECT_ROOT / 'eval' / f'structured_patch_results_{args.tag}.json'
    out.write_text(json.dumps({'model_path': args.model_path, 'focus': 'PWR_MGMT_1.DEVICE_RESET', 'interface': 'write_register_method_only', 'results': results}, ensure_ascii=False, indent=2), encoding='utf-8')
    print('output:', out)


if __name__ == '__main__':
    raise SystemExit(main())
