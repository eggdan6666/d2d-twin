# Independent LIS3DH v3.5 implementation acceptance

Task `lis3dh-v35/code_review`, project d2d-twin, family M, stage M4. Bounded implementation recommendation: **PASS_CANDIDATE**. Stage recommendation: **REPAIR**. Paper submission and formal generation remain **NOT_READY**; only the orchestrator controls stage state.

The primary ST DocID17530 Rev2 was independently read at printed pp11,16–17,31–32,37,39–40. Tables37–39 and46–47 were visually inspected; the missing XDA description/default is visibly absent in Table47. Source SHA256 `852bfcf1a993f04cc147f26a26612a22fdc307c234f3e53d2c24c850ad421533` matches the reviewed source/frozen inventory. The denominator is8fields/8dimensions: CTRL_REG4.ST access plus seven documented STATUS reset bits. XDA and output fields remain outside repaired inventory.

Actual recorded execution: **173/173 independent tests passed**, zero errors/failures/skips; **9 deliberate behavioral faults detected**, **28 proof/source corruption variants rejected**, **9 missing-scenario variants remain partial**. Saved scenario results and8closure rows replay exactly from accepted current code. Tests are fixtures, not LLM samples or hardware observations.

Contribution lens: source-bounded digital behavior and unknown-state guards improve executable rigor. This work does not prove a complete accelerometer twin, physical self-test, real-bus equivalence, higher model accuracy, novelty or submission readiness. No whole-field promotion occurs.

Methods lens: source ST codes00/01/10 persist with legal neighboring controls, while undefined11 is an atomic contract rejection without a silicon response claim. Initial/reset STATUS maskFE has seven documented zero bits; bit0 remains unknown in both profiles. Dynamic output bytes start unknown. Qualified coherent samples expose source-bounded pre-read DA/overrun bits and format-restricted supplied words. Main-profile output/STATUS observations invalidate subsequent STATUS knowledge because Rev2 supplies no clear trigger truth table; full cold/postevent STATUS reads cannot invent XDA. Candidate two-distinct-byte axis consumption and ANY aggregate rules are checked independently but explicitly remain hypotheses. Repeated half-reads, read-order permutations, interleaved samples, partial masks, other-axis preservation, BDU pending guards and illegal configurations are exercised. Reset is an externally qualified power-on completion event, not an invented software reset command.

Runtime subset review found no remaining defects within declared scope. Two initial mutant fixture overrides needed the runtime's optional read arguments; these were corrected before recorded acceptance. Source conflict review changed early planned full-byte sample expectations to FE-only masked witnesses, retaining XDA unknown throughout. The implementation did not need weakening to match tests.

Communication lens: six source gaps remain explicit: missingXDA, STATUS read history, partial-axis aggregation, BDU pending/release, self-test physical response and active mode history. ODR metadata discrepancy is also guarded. A rejected operation denotes no oracle in this benchmark scope, not a predicted silicon error. Precision-grid inputs, external overwrite qualifiers and post-read unknown status must remain visible in any paper claims.

Independent execution verifies primary/frozen authority hashes and all recorded input/output bytes. The frozen harness MD5 is `8cf0854d4779467bc8e472ee4fb97023`. Historical preservation is owner-recorded evidence reviewed independently; this expert modified only the new checklist/tests/report outputs. No old IR/harness/model-result changes or SCNet/API/physical execution occurred.

Reproduce with `python eval/lis3dh_semantics_v35_20261013/tests/record_independent_execution.py`, then `python eval/lis3dh_semantics_v35_20261013/tests/package_code_review.py`. The command, JUnit, log, exact hashes and counts are retained.

Primary next action: orchestrator verify these accepted bytes and continue remaining frozen REPAIR obligations while formal generation remains blocked.
