# Independent TMP461 v3.4 code acceptance

Task `tmp461-v34/code_review`, project d2d-twin, family M, stage M4. Bounded implementation: **PASS_CANDIDATE**. Whole-stage recommendation: **REPAIR**; paper submission and production generation remain NOT_READY. Stage authority belongs to the orchestrator.

Primary SBOS722B revised August2016 was independently read at printed pp.13,16–21; pp.19 and21 visually inspected. Exact source SHA256 `ad98b47e7b831b44da5cedb8454220cbc2ee0220f32de48d5ebf1e81eb7bf740` matches reviewed primary and frozen source inventory. The9fields/14dimensions denominator is9reset plus5read_clear, not14whole fields.

Actual recorded execution: **135/135 independent tests passed**, zero failures/errors/skips; **8 synthetic runtime faults detected**, **28 evidence/source corruption variants rejected**, **12 missing-scenario variants remain partial**. Saved scenarios and14ledger rows reconstruct exactly from current code. These cases are validation fixtures, not model-generation samples or physical measurements.

Contribution lens: the work adds source-bounded, executable cause-aware status and unknown-reset obligations. It does not establish new model scores, novelty, complete peripheral equivalence or submission readiness. The8STATUSfields andONE_SHOTaction remain sourceREPAIR, with no whole-field promotion.

Methods lens: STATUS power-on/reset is unknown, not fabricated zero; write-only ONE_SHOT does not store any byte. Start/completion/shutdown/reset boundaries are explicit. Each active flag survives read, retired flags return preclear then clear, and a masked read clears all eligible flags. Temperature cause retirement conservatively requires the corresponding channel inside both limits; an opposite-limit crossing is not certified as its own clearing oracle. BUSY/THERM are live. ALERT has a separately serviced latch; status reads never acknowledge it. THERM hysteresis and inclusive release, THERM2 high-state hysteresis, low-bit exclusion and MASK1 independence are checked. Remote-open result uncertainty is guarded while known historical latch1 is retained. Rewritten thresholds cannot clear flags without a new comparison. Unfinished temperature-byte observations are completion guards, not full asynchronous snapshot evidence. Invalid inputs and excluded source branches reject atomically.

Review found two repaired implementation defects: measurement range guarding was initially applied to legal default low limit-128; remote-open completion initially discarded known historical remote high/low latch1. The final independent tests regress both. Strict master-service and paired-read fixtures were adapted to the stated public evidence boundary. There is no remaining blocker within the declared bounded scope.

Communication lens: six unresolved source branches remain visibly reported: higher consecutive count status/latch timing, mixed cause counting, digital-filter startup/rounding, THERM2 low-state history, numeric STATUS POR, and active RANGE transitions. THERM2 candidate observations cannot be relabelled as universal manufacturer certification. Nominal periods are metadata, not measured deadline proof. The paper must distinguish local logical event validation from actual SMBus/remote-diode hardware tests.

Primary/frozen authority hashes and all declared execution input/output hashes were checked. Independent recorder confirms harness MD5 `8cf0854d4779467bc8e472ee4fb97023`. Preservation of all historical files is reviewed owner execution evidence; this reviewer modified only the new task outputs. No old IR/test/model score changes or SCNet/API/hardware execution occurred.

Reproduce: `python eval/tmp461_semantics_v34_20261013/tests/record_independent_execution.py` then `python eval/tmp461_semantics_v34_20261013/tests/package_code_review.py`. Execution command, JUnit, log, hashes and count record are retained.

Unique next action: orchestrator verifies accepted TMP461 bytes and continues remaining sourceREPAIR obligations with global generation blocked.
