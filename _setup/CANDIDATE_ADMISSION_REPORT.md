# Candidate IR simulator admission report

Date: 2026-10-10  
Scope: source-approved provisional candidates  
Harness: copied frozen `d2d/eval/test_d2d_blackbox.py`  
Formal `d2d/ir/` and `d2d/rtl/` were not modified.

## Results

| Candidate | Result | Pytest summary | Log |
|---|---|---|---|
| AD5592R | PASS | 4 passed, 4 skipped | `_setup/candidate_runs/AD5592R/pytest.log` |
| LIS3DH | PASS | 3 passed, 5 skipped | `_setup/candidate_runs/LIS3DH/pytest.log` |
| MPU6050 | PASS | 4 passed, 4 skipped | `_setup/candidate_runs/MPU6050/pytest.log` |

The machine-readable summary is `_setup/candidate_runs/summary.json`. The reproducible runner is `_setup/run_candidate_admission.py`; it creates an isolated sandbox for each candidate and copies the frozen harness into that sandbox.

## Interpretation

The passing assertions establish that the candidate simulators satisfy the currently expressible register-level IR contract: reset values where applicable, RO protection, RW persistence, UNSPEC handling, and write-trigger/reset behavior. Skipped assertions are expected for dimensions not represented by each candidate IR or by the direct-register harness, including physical SPI/I2C framing, BDU/BLE paired-output atomicity, timing, FIFO, and sensor dynamics.

Following the source sign-off and this candidate run, the three IRs and reference simulators were promoted into the formal 20-chip roster on 2026-10-10. The historical model comparison remains a 17-chip baseline; the three new chips have no model-generation pass-rate entries yet. Protocol extensions are supplemental software evidence and do not claim electrical-level validation.
