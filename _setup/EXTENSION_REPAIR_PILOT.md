# Three-chip extension repair pilot

**Date:** 2026-10-10  
**Purpose:** test one minimal, failure-driven repair intervention on the two unresolved extension chips while preserving the frozen harness.  
**Targets:** `LIS3DH` and `MPU6050`; `AD5592R` was excluded because both models already passed all generated samples.

## Protocol

For each model/chip pair, the first failing generated sample (`index=0`) from the completed 108-sample evaluation was selected before repair. The model received the Gold IR, its current implementation, and the frozen pytest failure trace. It was instructed to return one complete Python candidate and preserve every already passing behavior. The candidate was run in a fresh sandbox against the unchanged `d2d/eval/test_d2d_blackbox.py`.

The outer gate retained a candidate only if the passed-assertion count strictly increased or the entire harness became green. A same-score candidate was recorded but not promoted; a regression was rejected.

## Results

| Model | Chip | Baseline | Candidate | Gate decision |
|---|---|---:|---:|---|
| Qwen2.5-Coder-14B | LIS3DH | 2 passed, `rc=1` | 2 passed, `rc=1` | no improvement |
| Qwen2.5-Coder-14B | MPU6050 | 3 passed, `rc=1` | 3 passed, `rc=1` | no improvement |
| DeepSeek-Coder-6.7B | LIS3DH | 2 passed, `rc=1` | 2 passed, `rc=1` | no improvement |
| DeepSeek-Coder-6.7B | MPU6050 | 3 passed, `rc=1` | 0 passed, `rc=1` | regression rejected |

No candidate improved the strict gate. The failure family remained register-semantic: LIS3DH candidates still failed read-only protection, while MPU6050 candidates continued to expose read-only and write-trigger behavior; the DeepSeek MPU6050 candidate additionally failed collection because the generated class did not satisfy the expected simulator contract.

## Evidence files

- Qwen results: [`remote_model_eval/minimal_patch_results_qwen_extension_minimal_20261010.json`](./remote_model_eval/minimal_patch_results_qwen_extension_minimal_20261010.json)
- DeepSeek results: [`remote_model_eval/minimal_patch_results_ds67b_extension_minimal_20261010.json`](./remote_model_eval/minimal_patch_results_ds67b_extension_minimal_20261010.json)
- Qwen launcher log: [`remote_model_eval/qwen_extension_repair.log`](./remote_model_eval/qwen_extension_repair.log)
- DeepSeek launcher log: [`remote_model_eval/ds67b_extension_repair.log`](./remote_model_eval/ds67b_extension_repair.log)

This is a negative-control intervention result, not a benchmark score increase. The reference simulators for all three admitted extensions remain separately validated by the candidate-admission and extended-protocol reports. The next intervention should isolate one semantic dimension at a time (first RO masking, then write-trigger/reset behavior) instead of asking for a broad rewrite.

## Dimension-isolated probes

The follow-up probe supplied only one semantic family at a time and evaluated the same selected samples:

| Focus | Model | Chip | Baseline | Candidate | Decision |
|---|---|---|---:|---:|---|
| RO masking | Qwen2.5-Coder-14B | LIS3DH | 2, `rc=1` | 2, `rc=1` | unchanged |
| RO masking | Qwen2.5-Coder-14B | MPU6050 | 3, `rc=1` | 4, `rc=0` | **complete enabled-test pass** |
| RO masking | DeepSeek-Coder-6.7B | LIS3DH | 2, `rc=1` | 2, `rc=1` | unchanged |
| RO masking | DeepSeek-Coder-6.7B | MPU6050 | 3, `rc=1` | 3, `rc=1` | unchanged |
| write-trigger/reset | Qwen2.5-Coder-14B | MPU6050 | 3, `rc=1` | 3, `rc=1` | unchanged |
| write-trigger/reset | DeepSeek-Coder-6.7B | MPU6050 | 3, `rc=1` | 0, `rc=1` | regression rejected |

The Qwen RO-only intervention on MPU6050 is the first positive extension repair signal: the selected candidate reached `4 passed, 4 skipped` without modifying the harness. It is a single-sample intervention and must not be added to the 24-sample generation pass rate. The LIS3DH and write-trigger probes remain open.

Raw dimension-probe files:

- [`dimension_ro_results_qwen_ro_extension_20261010.json`](./remote_model_eval/dimension_ro_results_qwen_ro_extension_20261010.json)
- [`dimension_ro_results_ds67b_ro_extension_20261010.json`](./remote_model_eval/dimension_ro_results_ds67b_ro_extension_20261010.json)
- [`dimension_trigger_results_qwen_trigger_mpu6050_20261010.json`](./remote_model_eval/dimension_trigger_results_qwen_trigger_mpu6050_20261010.json)
- [`dimension_trigger_results_ds67b_trigger_mpu6050_20261010.json`](./remote_model_eval/dimension_trigger_results_ds67b_trigger_mpu6050_20261010.json)

## Qwen RO stability and transfer check

To test whether the MPU6050 positive signal was a one-off, the same RO-only
prompt was rerun on three fixed failing samples from seeds 1, 2, and 3 for
each chip. The selected source indices were LIS3DH `0, 8, 19` and MPU6050
`0, 8, 16`.

| Chip | Fixed samples | Strict improvements | Candidate fully green |
|---|---:|---:|---:|
| LIS3DH | 3 | 1/3 (Wilson 95% CI 6.1%-79.2%) | 1/3 |
| MPU6050 | 3 | 3/3 (Wilson 95% CI 43.8%-100%) | 2/3 |

The remaining MPU6050 sample still failed only the write-trigger assertion for
`PWR_MGMT_1.DEVICE_RESET`; the RO dimension itself passed. The two LIS3DH
non-improvements remained read-only failures (`STATUS_REG` or `OUT_X_L`).
This supports a scoped transfer claim: RO-only repair is reproducible for
MPU6050 and transfers to a subset of LIS3DH samples, while the unresolved
failure modes are separable and should not be collapsed into one score.

Raw stability run: [`dimension_ro_results_qwen_ro_stability_20261010.json`](./remote_model_eval/dimension_ro_results_qwen_ro_stability_20261010.json).

## DEVICE_RESET trigger-only stability check

The remaining MPU6050 `PWR_MGMT_1.DEVICE_RESET` failures were tested separately
on one failing sample from each of seeds 1, 2, and 3 for both models. The
selected source indices were Qwen `0, 8, 16` and DeepSeek `0, 4, 8`.

| Model | Strict improvements | Fully green | Regressions | Interpretation |
|---|---:|---:|---:|---|
| Qwen2.5-Coder-14B | 2/3 | 1/3 | 0/3 | unstable partial transfer; one candidate still failed RO |
| DeepSeek-Coder-6.7B | 1/3 | 0/3 | 2/3 | unsafe without an outer gate |

The apparent improvements cannot be reported as isolated trigger accuracy:
the Qwen candidates also changed other register behavior, and the successful
candidate was not a clean trigger-only proof. DeepSeek produced two collection
regressions. The correct conclusion is that `DEVICE_RESET` needs a stricter
patch-diff or post-repair semantic audit before claiming a transfer effect.

The follow-up patch-scope audit found **0/6 clean trigger successes**: one Qwen
improvement was actually an RO guard, another still failed the trigger
assertion, and the DeepSeek improvements either regressed or retained an RO
failure. See [`TRIGGER_PATCH_AUDIT.md`](./TRIGGER_PATCH_AUDIT.md).

Raw records:

- [`dimension_trigger_results_qwen_trigger_stability_20261011.json`](./remote_model_eval/dimension_trigger_results_qwen_trigger_stability_20261011.json)
- [`dimension_trigger_results_ds67b_trigger_stability_20261011.json`](./remote_model_eval/dimension_trigger_results_ds67b_trigger_stability_20261011.json)

