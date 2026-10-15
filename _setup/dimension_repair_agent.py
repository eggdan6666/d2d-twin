# -*- coding: utf-8 -*-
"""One-dimension repair probe for the frozen D2D-Twin harness."""
from __future__ import annotations

import argparse
import json
import pathlib
import re

from repair_agent import extract_code, load_model, run_harness, PROJECT_ROOT


def focus_trace(tail: str, focus: str) -> str:
    lines = []
    terms = ("RO", "WHO_", "OUT_", "STATUS", "ACCEL_") if focus == "RO" else ("DEVICE_RESET", "PWR_", "TRIGGER", "SELF", "写触发")
    for line in tail.splitlines():
        if "AssertionError:" in line and any(x in line for x in terms):
            lines.append(line)
    return "\n".join(lines) or tail[-2000:]


def prompt_for(device, ir, code, trace, focus):
    if focus == "RO":
        rule = "For every register or field marked RO in the IR, writes must leave its stored value unchanged."
        title = "read-only (RO) protection"
    else:
        rule = "Implement only the IR-defined write-trigger or self-clearing behavior shown by the failure trace; do not alter ordinary RW or RO behavior."
        title = "write-trigger/reset semantics"
    return f'''Repair ONLY {title} in this {device} register emulator.
Return exactly one complete Python code block and nothing else.

Do not change reset values, writable fields, write-trigger behavior, aliases,
protocol behavior, or the test harness. Do not add undocumented registers.
Preserve every behavior that already passes. {rule} The outer evaluator
will reject regressions. This is a controlled one-dimension intervention.

IR:
```json
{json.dumps(ir, ensure_ascii=False, indent=1)}
```

Current candidate:
```python
{code}
```

RO-only failure evidence:
```text
{trace}
```
'''


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--model-path', required=True)
    ap.add_argument('--tag', required=True)
    ap.add_argument('--items', nargs='+', required=True)
    ap.add_argument('--focus', choices=['RO', 'TRIGGER'], default='RO')
    ap.add_argument('--max-new', type=int, default=2048)
    args = ap.parse_args()
    tokenizer, model = load_model(args.model_path)
    import torch
    out = []
    for item in args.items:
        chip, result_file, index_s = item.split(':', 2)
        index = int(index_s)
        records = json.loads((PROJECT_ROOT / 'eval' / result_file).read_text(encoding='utf-8'))
        code = records[index]['code']
        ir_name = f'{chip}_gold_ir.json'
        ir = json.loads((PROJECT_ROOT / 'ir' / ir_name).read_text(encoding='utf-8'))
        tag = f'{args.tag}_{chip.lower()}'
        baseline = run_harness(code, ir_name, tag, 0)
        messages = [
            {'role': 'system', 'content': 'You are an embedded register semantics repair engineer.'},
            {'role': 'user', 'content': prompt_for(chip, ir, code, focus_trace(baseline['tail'], args.focus), args.focus)},
        ]
        text_in = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        encoded = tokenizer(text_in, return_tensors='pt', add_special_tokens=False).to('cuda')
        with torch.no_grad():
            generated = model.generate(**encoded, max_new_tokens=args.max_new,
                                       do_sample=False, pad_token_id=tokenizer.eos_token_id)
        raw = tokenizer.decode(generated[0][encoded.input_ids.shape[1]:], skip_special_tokens=True)
        candidate = extract_code(raw)
        if candidate:
            checked = run_harness(candidate, ir_name, tag, 1)
            status = 'improved' if checked['passed'] > baseline['passed'] else ('green' if checked['rc'] == 0 else ('regression' if checked['passed'] < baseline['passed'] else 'unchanged'))
            out.append({'chip': chip, 'status': status, 'baseline': baseline, 'candidate': checked})
            print(chip, status, 'baseline=', baseline['passed'], 'candidate=', checked['passed'])
        else:
            out.append({'chip': chip, 'status': 'no_code', 'baseline': baseline, 'raw_tail': raw[-5000:]})
            print(chip, 'no_code')
    output = PROJECT_ROOT / 'eval' / f'dimension_{args.focus.lower()}_results_{args.tag}.json'
    output.write_text(json.dumps({'model_path': args.model_path, 'focus': args.focus, 'results': out}, ensure_ascii=False, indent=2), encoding='utf-8')
    print('output:', output)


if __name__ == '__main__':
    raise SystemExit(main())
