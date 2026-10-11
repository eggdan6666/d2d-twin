# Local Model Expansion Plan

## Deployment mode

All new model weights are downloaded to the SCNet DCU node and loaded locally by `d2d/eval/gen_code.py`. No remote inference API is used. The Windows workstation stores prompts, manifests, results, and logs only.

## Model matrix

| Role | Model | Status | Reason |
|---|---|---|---|
| Existing control | Qwen2.5-Coder-14B-Instruct | present on SCNet | Historical 14B control |
| Existing control | DeepSeek-Coder-6.7B-Instruct | present on SCNet | Historical 6.7B control |
| First new model | Qwen2.5-Coder-7B-Instruct | download after quota check | Same-family scale control; about 15 GB of safetensors |
| Second new model | DeepSeek-Coder-V2-Lite-Instruct | optional, download only after cleanup/quantization plan | MoE comparison; 16B total/2.4B active, about 31.4 GB of safetensors |

The two existing models remain the historical comparison arm. New models are first evaluated on the 32-chip roster; their scores are not merged into the historical 612-run tables.

## Sampling protocol

### Balanced screening arm

- 32 chips per model;
- seeds `1,2,3`;
- `--n 4` per seed, therefore 12 samples per chip/model;
- `temperature=0.7`, `top_p=0.9`, `top_k=40`;
- identical prompt, IR revision, harness MD5, and `max-new` for every model.

This gives 384 samples per model and 1,536 samples for four models.

### Confirmatory arm

For the eight hardest chips, rerun only after the screening results are frozen:

- seeds `1,2,3`;
- `--n 8` per seed, therefore 24 samples per chip/model;
- preserve the original raw generations and do not replace screening results.

The evaluator's `--n` value is per seed, not the total. Every run manifest must record model revision, tokenizer revision, seed, temperature, prompt hash, IR hash, harness MD5, and SCNet machine identifier.

## Download gate

Before downloading any new model on SCNet, run:

```bash
df -h /root/private_data
du -sh /root/private_data/models/* 2>/dev/null | sort -h
```

Do not start a download if the model plus temporary download space would exceed the 50G quota. Download one model at a time, verify checksums, then serve/evaluate it before considering the next model.

## Acceptance gate

Each new model must pass a one-chip smoke test, then the 32-chip screening arm. A model is admitted to the comparison table only when its raw outputs, generation configuration, logs, and result JSON are archived together.
