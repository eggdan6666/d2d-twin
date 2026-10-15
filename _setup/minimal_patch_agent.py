# -*- coding: utf-8 -*-
"""Batch one-round, failure-driven minimal-patch evaluation.

The model sees one existing generated candidate, its frozen-harness failures,
and the IR. Every output is evaluated with the unchanged harness and retained
only as an evidence record; this script never overwrites benchmark results.
"""
from __future__ import annotations

import argparse
import json
import pathlib

from repair_agent import extract_code, load_model, run_harness, PROJECT_ROOT


def prompt_for(device, ir, code, failure_tail):
    return f'''Repair only the demonstrated failures in this {device} peripheral emulator.
Return exactly one complete Python code block and nothing else.

This is a MINIMAL PATCH task. Preserve every behavior that already passes.
Do not redesign the class, add undocumented registers, change reset values, or
modify the test harness. Implement only behavior explicitly supported by the
IR. Pay special attention to RO protection, writable bit masks, read/write
aliases, read_as values, and single-byte semantics when present in the IR.
The outer evaluator will reject any candidate that loses passing tests.

IR:
```json
{json.dumps(ir, ensure_ascii=False, indent=1)}
```

Current candidate:
```python
{code}
```

Frozen harness failure trace:
```text
{failure_tail}
```
'''


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--model-path', required=True)
    ap.add_argument('--tag', default='minimal_patch')
    ap.add_argument('--max-new', type=int, default=2048)
    ap.add_argument('--items', nargs='+', required=True,
                    help='triples CHIP:RESULT_JSON:INDEX')
    args = ap.parse_args()

    tokenizer, model = load_model(args.model_path)
    import torch
    all_results = []
    for item in args.items:
        chip, result_file, index_s = item.split(':', 2)
        index = int(index_s)
        records = json.loads((PROJECT_ROOT / 'eval' / result_file).read_text(encoding='utf-8'))
        baseline_code = records[index]['code']
        ir_name = f'{chip}_gold_ir.json'
        ir = json.loads((PROJECT_ROOT / 'ir' / ir_name).read_text(encoding='utf-8'))
        run_tag = f'{args.tag}_{chip.lower()}'
        baseline = run_harness(baseline_code, ir_name, run_tag, 0)
        messages = [
            {'role': 'system', 'content': 'You are an expert embedded-systems repair engineer.'},
            {'role': 'user', 'content': prompt_for(chip, ir, baseline_code, baseline['tail'])},
        ]
        text_in = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        encoded = tokenizer(text_in, return_tensors='pt', add_special_tokens=False).to('cuda')
        with torch.no_grad():
            generated = model.generate(**encoded, max_new_tokens=args.max_new,
                                       do_sample=False, pad_token_id=tokenizer.eos_token_id)
        raw = tokenizer.decode(generated[0][encoded.input_ids.shape[1]:], skip_special_tokens=True)
        candidate = extract_code(raw)
        if candidate:
            checked = run_harness(candidate, ir_name, run_tag, 1)
            status = 'improved' if checked['passed'] > baseline['passed'] else ('green' if checked['rc'] == 0 else 'not_improved')
            rec = {'chip': chip, 'source': result_file, 'index': index,
                   'status': status, 'baseline': baseline, 'candidate': checked}
        else:
            rec = {'chip': chip, 'source': result_file, 'index': index,
                   'status': 'no_code', 'baseline': baseline, 'raw_tail': raw[-5000:]}
        all_results.append(rec)
        print(chip, rec['status'], 'baseline=', baseline['passed'],
              'candidate=', rec.get('candidate', {}).get('passed'))

    out = PROJECT_ROOT / 'eval' / f'minimal_patch_results_{args.tag}.json'
    out.write_text(json.dumps({'model_path': args.model_path, 'results': all_results},
                              ensure_ascii=False, indent=2), encoding='utf-8')
    print('output:', out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
