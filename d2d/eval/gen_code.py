# -*- coding: utf-8 -*-
"""D2D-Twin codegen 评测器（MVP）。

流程：加载 Coder 模型 → 用 [基类 + 金标 IR + 任务书] 构造 prompt → 生成 n 份
tmp1075_simulator.py → 每份放进独立沙盒跑 pytest（test_tmp1075.py）→
记 pass 数与失败明细 → results_gen_<tag>.json。

用法（d2d/ 为根）：
  python eval/gen_code.py --model-path /root/private_data/models/Qwen2.5-Coder-14B-Instruct \
         --tag smokes1 --greedy            # 贪心冒烟 1 份
  python eval/gen_code.py ... --n 4 --temperature 0.7 --seeds 1,2,3
"""
import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys
import time

EVAL = pathlib.Path(__file__).resolve().parent
ROOT = EVAL.parent
BASE_FILE = ROOT / "rtl" / "base_sensor.py"
TEST_FILE = EVAL / "test_d2d_blackbox.py"

SYSTEM = ("You are an expert embedded-systems engineer. You write precise, "
          "minimal, production-quality Python. Output exactly one Python code block.")

USER_TMPL = """Implement a virtual (simulated) I2C sensor as a Python class.

## Task
Write class `{device}_Simulator(BaseVirtualSensor)` that behaviorally simulates the device described by the IR below.

## Base class (must inherit; do not modify)
```python
{base_src}```

## Device IR (ground truth extracted from the datasheet)
```json
{ir}
```

## Hard requirements
0. The code block MUST be self-contained: start with `from base_sensor import BaseVirtualSensor` plus any other imports you need. It will be saved to a file alone and imported by a test.
1. After __init__, every register must read exactly its IR "reset" value.
2. Registers with access "RO" must ignore writes (value unchanged).
3. RW fields store written data. A field with "read_as" must always read back that value no matter what is written.
4. nbytes=1 access must follow IR.single_byte_semantics: a 1-byte write updates only bits 15:8; a 1-byte read returns only bits 15:8.
5. Standard library only. No printing. Class name exactly `{device}_Simulator`.

Output a single ```python code block with the complete implementation."""


def strip_reset(node):
    """递归删掉 reset 字段——**只用于构造 prompt，判据侧仍用完整 IR**。
    Q1 实验：复位值 0/144 失败到底是"从手册抽取"还是"照我们给的 IR 转录"。"""
    if isinstance(node, dict):
        return {k: strip_reset(v) for k, v in node.items() if k != "reset"}
    if isinstance(node, list):
        return [strip_reset(v) for v in node]
    return node


def build_prompt(ir, strip=False):
    base_src = BASE_FILE.read_text(encoding="utf-8")
    body = strip_reset(ir) if strip else ir
    return USER_TMPL.format(device=ir["device"], base_src=base_src,
                            ir=json.dumps(body, ensure_ascii=False, indent=1))


def extract_code(text):
    m = re.search(r"```python\s*\n(.*?)```", text, re.S)
    if not m:
        m = re.search(r"```\s*\n(.*?)```", text, re.S)
    return m.group(1).rstrip() + "\n" if m else None


def run_pytest(sandbox: pathlib.Path, ir_name: str):
    import os as _os
    env = dict(_os.environ, D2D_IR=ir_name)
    r = subprocess.run([sys.executable, "-m", "pytest", "test_d2d_blackbox.py", "-q", "--tb=line"],
                       cwd=str(sandbox), capture_output=True, text=True, timeout=120, env=env)
    tail = (r.stdout + "\n" + r.stderr)[-1500:]
    m = re.search(r"(\d+) passed", tail)
    return {"rc": r.returncode, "passed": int(m.group(1)) if m else 0, "tail": tail}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-path", required=True)
    ap.add_argument("--ir", default="TMP1075_gold_ir.json", help="ir/ 下的金标文件名")
    ap.add_argument("--tag", default="gen")
    ap.add_argument("--greedy", action="store_true", help="贪心冒烟：单样本 temp=0")
    ap.add_argument("--n", type=int, default=4, help="每 seed 采样数（temp>0 时）")
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--seeds", default="1")
    ap.add_argument("--max-new", type=int, default=2048)
    ap.add_argument("--strip-reset", action="store_true",
                    help="prompt 里不给 reset 字段（判据侧仍用完整 IR）——Q1 抽取 vs 转录实验用")
    a = ap.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    ir_file = ROOT / "ir" / a.ir
    ir = json.load(open(ir_file, encoding="utf-8"))
    device = ir["device"]
    module_name = f"{device.lower()}_simulator"
    prompt = build_prompt(ir, a.strip_reset)
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}]

    tok = AutoTokenizer.from_pretrained(a.model_path)
    kw = dict(attn_implementation="eager")
    try:  # transformers >=4.56 用 dtype，4.51 用 torch_dtype
        net = AutoModelForCausalLM.from_pretrained(a.model_path, dtype=torch.bfloat16, **kw)
    except TypeError:
        net = AutoModelForCausalLM.from_pretrained(a.model_path, torch_dtype=torch.bfloat16, **kw)
    net.eval().to("cuda")
    print(f"模型就绪 | eos={tok.eos_token!r} | device={device}", flush=True)

    if a.greedy:
        seeds, n, temp = [0], 1, 0.0
    else:
        seeds, n, temp = [int(s) for s in a.seeds.split(",")], a.n, a.temperature

    out_file = EVAL / f"results_gen_{a.tag}.json"
    results = []

    def snapshot():
        json.dump(results, open(out_file, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    t0 = time.time()
    for seed in seeds:
        torch.manual_seed(seed)
        for i in range(n):
            text_in = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
            enc = tok(text_in, return_tensors="pt", add_special_tokens=False).to("cuda")
            kw_gen = dict(max_new_tokens=a.max_new, pad_token_id=tok.eos_token_id,
                          do_sample=temp > 0)
            if temp > 0:
                kw_gen.update(temperature=temp, top_p=0.9, top_k=40)
            with torch.no_grad():
                g = net.generate(**enc, **kw_gen)
            raw = tok.decode(g[0][enc.input_ids.shape[1]:], skip_special_tokens=True)
            code = extract_code(raw)
            rec = {"seed": seed, "i": i, "gen_s": round(time.time() - t0, 1),
                   "code_extracted": code is not None}
            if code:
                sandbox = EVAL / f"_sandbox_{a.tag}_{seed}_{i}"
                sandbox.mkdir(exist_ok=True)
                shutil.copy(BASE_FILE, sandbox / "base_sensor.py")
                shutil.copy(TEST_FILE, sandbox / "test_d2d_blackbox.py")
                (sandbox / f"{module_name}.py").write_text(code, encoding="utf-8")
                rec.update(run_pytest(sandbox, a.ir))
            else:
                rec.update({"rc": -1, "passed": 0, "tail": raw[-800:]})
            rec["code"] = code
            results.append(rec)
            snapshot()
            print(f"[{seed}][{i}] rc={rec['rc']} passed={rec['passed']} "
                  f"({rec.get('gen_s', 0)}s)", flush=True)
    ok = sum(1 for r in results if r["rc"] == 0)
    print(f"\n== gen {a.tag}: pytest 全绿 {ok}/{len(results)} | 明细 {out_file} ==", flush=True)


if __name__ == "__main__":
    main()
