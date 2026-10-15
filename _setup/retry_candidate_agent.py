# -*- coding: utf-8 -*-
"""One focused retry from a previously evaluated model candidate."""
from __future__ import annotations
import argparse, json
from repair_agent import extract_code, load_model, run_harness, PROJECT_ROOT


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model-path', required=True)
    ap.add_argument('--prior', required=True)
    ap.add_argument('--chip', required=True)
    ap.add_argument('--tag', required=True)
    ap.add_argument('--max-new', type=int, default=1024)
    a = ap.parse_args()
    d = json.loads((PROJECT_ROOT / 'eval' / a.prior).read_text(encoding='utf-8'))
    row = next(x for x in d['results'] if x['chip'] == a.chip)
    code = row['candidate']['code']
    ir_name = f'{a.chip}_gold_ir.json'
    ir = json.loads((PROJECT_ROOT / 'ir' / ir_name).read_text(encoding='utf-8'))
    base = run_harness(code, ir_name, a.tag, 0)
    prompt = f'''Make one minimal repair to this {a.chip} emulator.
Return exactly one complete Python code block. Preserve the {base['passed']} passing
tests and fix only the failures in the trace. Do not redesign code, add registers,
change resets, or modify the harness. Follow the IR exactly, including RO masks,
field access, aliases, read_as and single-byte semantics.
IR:\n```json\n{json.dumps(ir,ensure_ascii=False,indent=1)}\n```
Current candidate:\n```python\n{code}\n```
Failure trace:\n```text\n{base['tail']}\n```'''
    tok, model = load_model(a.model_path)
    import torch
    msg=[{'role':'system','content':'You are an embedded-systems repair engineer.'},{'role':'user','content':prompt}]
    text=tok.apply_chat_template(msg,tokenize=False,add_generation_prompt=True)
    enc=tok(text,return_tensors='pt',add_special_tokens=False).to('cuda')
    with torch.no_grad():
        out=model.generate(**enc,max_new_tokens=a.max_new,do_sample=False,pad_token_id=tok.eos_token_id)
    raw=tok.decode(out[0][enc.input_ids.shape[1]:],skip_special_tokens=True)
    cand=extract_code(raw)
    checked=run_harness(cand,ir_name,a.tag,1) if cand else {'rc':-1,'passed':0,'tail':raw[-5000:]}
    result={'chip':a.chip,'prior':a.prior,'baseline':base,'candidate':checked}
    outp=PROJECT_ROOT/'eval'/f'retry_results_{a.tag}.json'
    outp.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'output':str(outp),'baseline_passed':base['passed'],'candidate_passed':checked.get('passed'),'rc':checked.get('rc')},ensure_ascii=False))

if __name__=='__main__': main()
