# Local Model Expansion Plan

## Deployment mode

All new model weights are downloaded to the SCNet DCU node and loaded locally by `d2d/eval/gen_code.py`. No remote inference API is used. The Windows workstation stores prompts, manifests, results, and logs only.

## Model matrix

| Role | Model | Status | Reason |
|---|---|---|---|
| Existing control | Qwen2.5-Coder-14B-Instruct | present on SCNet | Historical 14B control |
| Existing control | DeepSeek-Coder-6.7B-Instruct | present on SCNet | Historical 6.7B control |
| First new model | Qwen2.5-Coder-3B-Instruct | **downloaded and smoke-tested** | Fits the remaining SCNet quota; first new local arm |
| Deferred model | Qwen2.5-Coder-7B-Instruct | deferred | About 15 GB of safetensors; current 50 GB quota cannot hold it safely |
| Deferred model | DeepSeek-Coder-V2-Lite-Instruct | deferred | About 31.4 GB of safetensors; requires quota expansion or cleanup |

All three models have now completed the 20-chip exploratory screening, each with 240 samples. These results are kept separate from the historical 612-run tables. The verified 14B export is stored under `eval/expansion_qwen14b/`, and the descriptive comparison and provenance audit are under `eval/model_comparison_20chip/`.

## Sampling protocol

### Balanced screening arm

- 20 formal chips in the current IR roster (the protocol scales to 32 when the remaining IRs are admitted);
- seeds `1,2,3`;
- `--n 4` per seed, therefore 12 samples per chip/model;
- `temperature=0.7`, `top_p=0.9`, `top_k=40`;
- target protocol: identical prompt, IR revision, harness hash, and `max-new` for every model. Per-run input hashes were not saved for the earlier arms, so exact runtime input identity remains unverified.

For the current Qwen-3B run this gives 240 samples (20 × 3 × 4). A future 32-chip run gives 384 samples per model.

Verified raw results: Qwen-3B 22/240 (9.2%), DeepSeek-6.7B 25/240 (10.4%), Qwen-14B 48/240 (20.0%). The earlier screenshot-based 38/240 figure was a reading error and is superseded. DeepSeek is a cross-family control, not an intermediate point on a Qwen parameter-scale curve.

The SCNet export differs from current local IRs for eight chips: seven annotation changes and one semantic correction (INA3221). Archive scoring and current-revision scoring must be retained separately. Publication claims require the provenance audit and revision sensitivity checks, rather than aggregate counts alone.

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

The first download gate passed on 2026-10-11: Qwen2.5-Coder-3B-Instruct completed ModelScope `SIZE_CHECK PASS`, occupies about 5.8 GB, and left about 3.3 GB free. The SCNet runtime requires `/opt/conda/bin/python` plus `LD_LIBRARY_PATH=/opt/dtk-25.04.1/hip/lib:/opt/dtk-25.04.1/lib:$LD_LIBRARY_PATH`.

The 20-chip Qwen-3B screening completed with 240 generated samples. The raw JSON files and the derived summary are under `eval/expansion_qwen3b/`; the aggregate was 22/240 fully green (9.2%) with 239/240 code blocks extracted (99.6%). This is a separate expansion result, not a replacement for the historical model tables.

## Acceptance gate

Each new model must pass a one-chip smoke test, then the 32-chip screening arm. A model is admitted to the comparison table only when its raw outputs, generation configuration, logs, and result JSON are archived together.
