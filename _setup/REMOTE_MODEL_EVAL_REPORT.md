# Remote model generation evaluation report

**Run date:** 2026-10-10 (Asia/Shanghai)  
**Purpose:** evaluate the first three formally admitted extension IRs with the two models available on the SCNet DCU node.  
**Scope:** generated Python digital-twin code executed against the frozen `d2d/eval/test_d2d_blackbox.py` harness.

## Models, data, and reproducibility

The run used the following local checkpoints on the remote node:

- `Qwen2.5-Coder-14B-Instruct` (`qwen14b`)
- `deepseek-coder-6.7b-instruct` (`ds67b`)

The evaluated formal Gold IRs were `AD5592R`, `LIS3DH`, and `MPU6050`.  For each model/chip pair, generation used temperature `0.7` and seeds `1,2,3`. Qwen14B produced 8 samples per seed (24 per pair); DeepSeek-Coder 6.7B produced 4 samples per seed (12 per pair). The complete run therefore contains **108 generated samples**.

The remote command family was:

```bash
python eval/gen_code.py \
  --model-path <local-checkpoint> \
  --ir ir/<CHIP>_gold_ir.json \
  --tag <model>_<chip>_20261010 \
  --n <8-or-4> --temperature 0.7 --seeds 1,2,3 --max-new <configured-limit>
```

The raw JSON outputs and the complete launcher log are preserved in [`_setup/remote_model_eval/`](./remote_model_eval/). `summary.json` is a machine-readable aggregation of the raw records.

## Results

`All-green` means that the generated simulator returned `rc=0` for the frozen black-box test run. It is a strict sample-level pass: every assertion in that run passed.  It does not mean that a model generated production-ready code for every untested protocol behavior.

| Model | Chip | Samples | All-green | Pass rate | Mean passed assertions |
|---|---:|---:|---:|---:|---:|
| Qwen2.5-Coder-14B | AD5592R | 24 | 24 | **100.0%** | 4.00 |
| Qwen2.5-Coder-14B | LIS3DH | 24 | 9 | **37.5%** | 2.38 |
| Qwen2.5-Coder-14B | MPU6050 | 24 | 0 | **0.0%** | 2.29 |
| DeepSeek-Coder-6.7B | AD5592R | 12 | 12 | **100.0%** | 4.00 |
| DeepSeek-Coder-6.7B | LIS3DH | 12 | 0 | **0.0%** | 1.83 |
| DeepSeek-Coder-6.7B | MPU6050 | 12 | 0 | **0.0%** | 2.00 |

Across all 108 samples, **45 passed (41.7%)**. AD5592R is solved by both evaluated models under this harness. LIS3DH is partially solved by Qwen14B but not by DeepSeek-Coder. MPU6050 remains unsolved for both models.

## Failure localization

The failures are concentrated in concrete register semantics rather than in the test runner:

- **LIS3DH / Qwen14B:** the 15 failing samples are all `test_readonly_protection` failures, involving one or more of `OUT_X_L`, `WHO_AM_I`, and `STATUS_REG`.
- **LIS3DH / DeepSeek-Coder:** all 12 samples fail `test_readonly_protection`; the same read-only register family dominates, with one additional sample exposing reset/field behavior (`CTRL_REG0`, `SDO_PU_DISC`).
- **MPU6050 / Qwen14B:** 22/24 samples fail read-only protection for `ACCEL_XOUT_H`; 19/24 also fail the `PWR_MGMT_1.DEVICE_RESET` write-trigger assertion.
- **MPU6050 / DeepSeek-Coder:** 11/12 fail read-only protection and 10/12 fail the `DEVICE_RESET` write-trigger assertion. Two samples additionally expose field-persistence problems (`SMPLRT_DIV` or `YG_ST`).

This pattern is useful evidence for the paper: scaling from 6.7B to 14B improves LIS3DH substantially, but does not eliminate the MPU6050 failure cluster. The result supports reporting per-register failure taxonomy instead of a single aggregate score.

## Interpretation and limits

The extension IRs had already passed the independent source review and post-repair recheck before this run. The observed failures therefore belong to generated implementations under the frozen contract, not to an unreviewed Gold IR. The separate extended I2C/SPI protocol suite is recorded in [`_setup/EXTENDED_PROTOCOL_REPORT.md`](./EXTENDED_PROTOCOL_REPORT.md); it was not silently mixed into the 108-sample model-generation score.

The next analysis should keep the raw outputs fixed and classify each failed sample by register contract (`RO`, reset value, write-one trigger, reserved bits, and protocol metadata). Do not revise the harness or convert failed generated code into a pass without a separately documented repair experiment.

