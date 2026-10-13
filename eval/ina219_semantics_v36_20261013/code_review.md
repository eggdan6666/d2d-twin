# Independent INA219 v3.6 implementation acceptance

Task `ina219-v36/code_review`, project d2d-twin, family M, stage M4. Bounded implementation recommendation **PASS_CANDIDATE**; stage recommendation **REPAIR**, full paper submission **NOT_READY**. Only the orchestrator may change stage state.

Original TI SBOS448G technical pp.9–13,17–24 were read independently before implementation. Source SHA256 `58004eda854d07478e6fc6f4398c114f60a3bcf18d4877471c7c1a306d1fa1cb` matches reviewed bytes. Table2 supplies CONFIG399F and CALIBRATION/CURRENT/POWER0 but no fixed numeric BUS/SHUNT reset. Figure24 supplies no reserved-bit2 value. All six REPAIR fields and seven dimensions retain the frozen inventory.

Actual recorded execution: **193/193 independent tests passed**, zero errors/failures/skips, **13 deliberate behavioral faults detected**, **30 proof/source corruption variants rejected**. **10 required-scenario omissions remain partial**, while **1 optional metadata-support omission leaves all bounded rows verified**; these categories derive from source advice and claim mappings. The source advice, accepted scenarios and seven-row closure replay exactly. These are test fixtures and supplied logical stimuli, not hardware observations or model samples.

Contribution lens: executable unknown-state guards and conditional event semantics improve local benchmark rigor. They do not establish complete device equivalence, real-bus behavior, higher model accuracy, novelty or submission readiness.

Methods lens: BUS and SHUNT begin unknown. Reserved bit2 remains outside every numeric oracle. Explicit reset completion restores known defaults while rejecting pending reads and unsupported deadlines. CNVR completion includes the whole externally qualified conversion/averaging/multiplication sequence; modes0/4 preserve known CNVR, changed active modes clear, disputed same-mode active writes invalidate it. The conflicting p10 Status/convert-pin references are retained rather than silently treated as official errata. Main BUS/POWER reads end CNVR knowledge; the p23 POWER-clear branch is an explicitly source-conditioned candidate. OVF is based on qualified math range, never raw voltage exceeding a chosen threshold; no-overflow clearing, arithmetic rounding and signed-power outcomes remain outside scope. CAL bit0 explicitly zero is not borrowed to define BUS bit2. The pre-first-programming zero guarantee is not generalized to later nonzero-to-zero calibration writes: CURRENT/POWER remain unknown even after supplied zero-calibration completion until a qualified reset; an independent instant-zero mutant is rejected.

Communication lens: source contradictions and source omissions stay visible in the runtime and return contract. A scope guard means this benchmark has no oracle, not that silicon rejects the transaction. Logical settled register access and nominal timing metadata do not certify the source's4us write-update behavior, averaging timer, I2C framing or analog accuracy. Every whole-field and whole-dimension promotion stays false.

Execution evidence includes command, JUnit, log and input/output hashes. The frozen harness independently matches MD5 `8cf0854d4779467bc8e472ee4fb97023`. This expert edited only new checklist/tests/report outputs; no historical IR, frozen harness or model results were changed.

Reproduce with `python eval/ina219_semantics_v36_20261013/tests/record_independent_execution.py`, followed by `python eval/ina219_semantics_v36_20261013/tests/package_code_review.py`.

Primary next action: orchestrator verify accepted INA219 bytes and continue remaining frozen REPAIR obligations while formal generation remains blocked.
