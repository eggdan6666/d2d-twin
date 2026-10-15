# Remote repair pilot (SCINet, 2026-10-10)

This note records the first failure-driven repair pilot on the remote SCINet
Notebook. The frozen black-box harness was copied unchanged for every run.

## Environment

- Python 3.10.18, PyTorch 2.4.1, CUDA-compatible BW accelerator, 64 GB VRAM
- `/root/private_data/models/deepseek-coder-6.7b-instruct`
- `/root/private_data/models/Qwen2.5-Coder-14B-Instruct`
- Project checkout: `/root/private_data/d2d`
- Target IR: `LM83_gold_ir.json`
- Harness: `eval/test_d2d_blackbox.py` (unchanged)

## Commands

```bash
cd /root/private_data/d2d

python -u eval/gen_code.py \
  --model-path /root/private_data/models/deepseek-coder-6.7b-instruct \
  --ir LM83_gold_ir.json --tag repair_baseline_ds67b_lm83_20261009 \
  --greedy --max-new 2048

python -u eval/gen_code.py \
  --model-path /root/private_data/models/Qwen2.5-Coder-14B-Instruct \
  --ir LM83_gold_ir.json --tag repair_baseline_qwen_lm83_20261009 \
  --greedy --max-new 2048

python -u _setup/repair_agent.py \
  --model-path /root/private_data/models/Qwen2.5-Coder-14B-Instruct \
  --result eval/results_gen_repair_baseline_qwen_lm83_20261009.json \
  --ir LM83_gold_ir.json --index 0 --max-rounds 2 \
  --tag qwen_lm83_repair_20261010
```

The DeepSeek run used the same repair command with its model path and result
file, tagged `ds67b_lm83_repair_gated_20261010`.

## Results

The baseline from both models was identical: **1 passed, 3 failed, 4 skipped**.
The failures were read-only protection (`TEMP_LOCAL`), RW bitfield persistence
(`CONFIG.INT_MASK[7]`), and the read/write alias (`CONFIG`, address `0x09` to
`0x03`).

| model | stage | passed | result | interpretation |
|---|---:|---:|---:|---|
| DeepSeek-Coder 6.7B | baseline | 1 | kept | reference candidate |
| DeepSeek-Coder 6.7B | repair 1/2 | 0 / 0 | rejected | regression; one candidate raised an invalid-address `KeyError` |
| Qwen2.5-Coder 14B | baseline | 1 | kept | reference candidate |
| Qwen2.5-Coder 14B | repair 1/2 | 1 / 1 | rejected | no improvement |

The outer gate in [`repair_agent.py`](repair_agent.py) only accepts a candidate
when its pass count strictly improves or the complete harness passes. This
prevents a repair that introduces new failures from replacing the baseline.

Raw copied result files are kept beside this note:

- `remote_repair_results_ds67b_lm83_gated_20261010.json`
- `remote_repair_results_qwen_lm83_20261010.json`

## What this establishes

The remote hardware and both local code models are usable. The first practical
intervention is reproducible, but it does not yet improve LM83. The next
scientifically meaningful step is a **structured, one-failure-at-a-time repair**
that gives the model only the failing dimension and requires a minimal patch,
then reruns the same gate after every patch. Do not report this pilot as an
accuracy gain; report it as a negative control and as evidence for the safety
gate.

## IR-constrained repair reference

As the safe reference for that next step, `_setup/structured_repair.py` rebuilt
only the register access layer from the LM83 IR. The first attempt reached 3/4
passed and exposed one missing rule: an aliased read address must reject direct
writes. After adding that rule, the unchanged harness reported **4 passed, 4
skipped in 1.17 s**. The resulting candidate is saved locally as
`structured_repair_lm83_20261010.py` and remotely as
`eval/structured_repair_lm83_structured_20261010_v2.py`.

This is a deterministic IR-constrained reference, not an LLM accuracy result.
It is useful as a correctness oracle and as the target behavior for a future
minimal-patch model intervention.

## Four-chip extension

The same script was run on three additional Gold IRs, using an existing
DeepSeek baseline record for each chip. The unchanged harness produced:

| chip | baseline passed | structured passed | skipped | delta |
|---|---:|---:|---:|---:|
| LM83 | 1 | 4 | 4 | +3 |
| TMP1075 | 2 | 5 | 3 | +3 |
| BME280 | 1 | 4 | 4 | +3 |
| ADS1115 | 2 | 3 | 5 | +1 |
| **total** | **6** | **16** | **16** | **+10** |

The structured candidates passed every assertion that the corresponding IR
enabled. TMP1075 additionally exercised 16-bit single-byte access and a
`read_as` write-trigger field. These are correctness-reference results, not a
claim that a language model independently achieved the same score.

## Model-guided minimal-patch comparison

The one-round minimal-patch agent was then run on the same four DeepSeek
baseline candidates. The frozen harness was the acceptance gate:

| model / chip | baseline | candidate | status |
|---|---:|---:|---|
| DeepSeek 6.7B / LM83 | 1 | 1 | no improvement |
| DeepSeek 6.7B / TMP1075 | 2 | 2 | no improvement |
| DeepSeek 6.7B / BME280 | 1 | 1 | no improvement |
| DeepSeek 6.7B / ADS1115 | 2 | 1 | rejected regression |
| Qwen2.5-Coder 14B / LM83 | 1 | 1 | no improvement |
| Qwen2.5-Coder 14B / TMP1075 | 2 | 2 | no improvement |
| Qwen2.5-Coder 14B / BME280 | 1 | 3 | partial improvement |
| Qwen2.5-Coder 14B / ADS1115 | 2 | 3 | complete enabled-test pass |

Qwen therefore improved two of four chips (+3 total passed assertions), while
DeepSeek improved none and produced one regression that the gate rejected. A
second Qwen retry on the remaining BME280 read-only failure stayed at 3
passed, so it was also rejected. Full raw records are stored in
`minimal_patch_results_ds67b_minimal_20261010.json`,
`minimal_patch_results_qwen14b_minimal_20261010.json`, and
`retry_results_qwen14b_bme280_retry_20261010.json`.

## Held-out four-chip split

To check that the pilot was not selected around LM83's alias behavior, a
held-out set was fixed before generation: INA219, TMP461, TPS23861, and
LIS2DW12. The same DeepSeek baseline records and one-round minimal-patch
protocol were used.

| model | strict improvements | regressions | unchanged | improvement rate | Wilson 95% CI |
|---|---:|---:|---:|---:|---:|
| Qwen2.5-Coder 14B (8 chips total) | 5/8 | 0/8 | 3/8 | 62.5% | [30.6%, 86.3%] |
| DeepSeek-Coder 6.7B (8 chips total) | 1/8 | 1/8 | 6/8 | 12.5% | [2.2%, 47.1%] |

The Qwen held-out outcomes were INA219 +1, TMP461 unchanged at zero,
TPS23861 +1, and LIS2DW12 +2. The DeepSeek held-out outcomes were unchanged
for INA219, TMP461, and TPS23861, and +2 for LIS2DW12. Across all eight chips,
Qwen moved from 9 to 16 passed assertions, while DeepSeek moved from 9 to 10;
these are intervention deltas, not replacement benchmark scores.

Raw held-out records:

- `minimal_patch_results_qwen14b_heldout4_20261010.json`
- `minimal_patch_results_ds67b_heldout4_20261010.json`
