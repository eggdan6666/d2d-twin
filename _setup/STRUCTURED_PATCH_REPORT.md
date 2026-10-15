# Structured `write_register` patch experiment

**Date:** 2026-10-11  
**Interface:** the model returned only a `write_register` method; the runner
replaced that method in the existing candidate, then applied a literal-scope
audit and the unchanged frozen Harness.

## Results

| Model | Samples | Scope accepted | Partial improvement | Clean green |
|---|---:|---:|---:|---:|
| Qwen2.5-Coder-14B | 3 | 1/3 | 1/3 | 0/3 |
| DeepSeek-Coder-6.7B | 3 | 3/3 | 2/3 | 0/3 |

Scope acceptance allows only the `0x6B` trigger path plus generic masks and
reset-state operations; explicit unrelated register literals are rejected.
The raw runner JSON contains its initial conservative audit; the counts below
use a post-hoc re-audit that allows generic masks (`0xFF`, `0xFF00`, `0x00FF`)
while continuing to reject unrelated register addresses.
Qwen produced two broad method rewrites that touched other register literals.
DeepSeek stayed within the method scope, but its candidates reached only
3 passed assertions and never passed the complete enabled test set.

The structured interface reduced unrelated full-file rewrites, but it did not
produce a clean `DEVICE_RESET` repair: **0/6 candidates were fully green**.
This is a negative intervention result and should remain separate from the
108-sample generation benchmark.

Raw records:

- [`structured_patch_results_qwen_structured_20261011.json`](./remote_model_eval/structured_patch_results_qwen_structured_20261011.json)
- [`structured_patch_results_ds67b_structured_20261011.json`](./remote_model_eval/structured_patch_results_ds67b_structured_20261011.json)
- [`qwen_structured_20261011.log`](./remote_model_eval/qwen_structured_20261011.log)
- [`ds67b_structured_20261011.log`](./remote_model_eval/ds67b_structured_20261011.log)

