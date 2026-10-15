# Contract-level repair completion

**Date:** 2026-10-11  
**Scope:** the three formally admitted extension chips (`AD5592R`, `LIS3DH`,
`MPU6050`).

The IR-constrained reference simulators were repaired and validated without
changing the frozen black-box harness:

| Chip | Candidate admission | Extended protocol |
|---|---:|---:|
| AD5592R | PASS (4 passed, 4 skipped) | covered by protocol suite |
| LIS3DH | PASS (3 passed, 5 skipped) | covered by protocol suite |
| MPU6050 | PASS (4 passed, 4 skipped) | covered by protocol suite |
| **Total** | **11 passed, 13 skipped** | **10 passed** |

The local commands were:

```bash
python _setup/run_candidate_admission.py
python _setup/run_extended_protocol_tests.py
```

Both commands completed successfully. The 20-chip integrity check remains
valid (`17` historical baseline plus `3` formal extensions).

The raw model-generated candidates remain preserved as experimental evidence.
Their failures were not silently replaced by the IR reference implementation:
the Qwen/DeepSeek extension generation run remains `45/108` all-green, and the
repair interventions produced no clean `DEVICE_RESET` fix. This separation is
required to keep the paper's model-capability claim valid.

