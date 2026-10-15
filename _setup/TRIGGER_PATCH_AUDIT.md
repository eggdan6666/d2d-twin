# DEVICE_RESET intervention patch audit

The 2026-10-11 trigger-only probe was audited against the baseline code in the
raw result records. A trigger-only success is accepted only when the changed
code is confined to `PWR_MGMT_1` (`0x6B`) trigger handling and does not add
unrelated RO or field behavior.

## Audit outcome

| Model | Sample | Gate outcome | Patch scope | Clean trigger success |
|---|---:|---|---|---|
| Qwen2.5-Coder-14B | seed 1 | unchanged | added RO guards for `0x3B`-`0x40` | no |
| Qwen2.5-Coder-14B | seed 2 | improved to `4 passed` | added RO guards for `0x3B`-`0x40` | no; improvement is RO-related |
| Qwen2.5-Coder-14B | seed 3 | improved to `3 passed` | changed only `0x6B` reset helper, but trigger assertion remained unresolved | no |
| DeepSeek-Coder-6.7B | seed 1 | regression | rewrote class/register contract | no; rejected |
| DeepSeek-Coder-6.7B | seed 2 | regression | rewrote class/register contract | no; rejected |
| DeepSeek-Coder-6.7B | seed 3 | improved to `3 passed` | changed `0x6B` but also left RO failure | no |

Therefore the apparent `2/3` Qwen and `1/3` DeepSeek improvement rates must not
be reported as `DEVICE_RESET` repair accuracy. After scope audit, the number of
clean trigger successes is **0/6**. The outer pytest gate and this patch-scope
audit jointly prevent unrelated RO fixes or regressions from being counted as
trigger repair.

Raw inputs:

- [`dimension_trigger_results_qwen_trigger_stability_20261011.json`](./remote_model_eval/dimension_trigger_results_qwen_trigger_stability_20261011.json)
- [`dimension_trigger_results_ds67b_trigger_stability_20261011.json`](./remote_model_eval/dimension_trigger_results_ds67b_trigger_stability_20261011.json)

## Constrained prompt rerun (2026-10-11)

A second experiment exposed only the `PWR_MGMT_1.DEVICE_RESET` register field
and applied an automatic diff-scope gate. The gate allowed changes only around
address `0x6B` and rejected candidates touching other register addresses or
rewriting the simulator contract.

| Model | Samples | Scope accepted | Clean success |
|---|---:|---:|---:|
| Qwen2.5-Coder-14B | 3 | 0/3 | 0/3 |
| DeepSeek-Coder-6.7B | 3 | 1/3 | 0/3 |

The one DeepSeek scope-accepted candidate stayed at 3 passed and therefore did
not improve the gate. The other two DeepSeek candidates were broad rewrites and
were rejected. This confirms that the bottleneck is not merely prompt wording:
the models need a structured patch interface or a stronger constrained decoder
to make a clean trigger-only change.

Raw constrained-run records:

- [`scoped_trigger_results_qwen_scoped_trigger_20261011.json`](./remote_model_eval/scoped_trigger_results_qwen_scoped_trigger_20261011.json)
- [`scoped_trigger_results_ds67b_scoped_trigger_20261011.json`](./remote_model_eval/scoped_trigger_results_ds67b_scoped_trigger_20261011.json)

