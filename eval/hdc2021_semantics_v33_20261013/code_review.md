# Independent HDC2021 v3.3 code acceptance

Task `hdc2021-v33/code_review`, project `d2d-twin`, family M, stage M4. **Bounded implementation: PASS_CANDIDATE. Whole-stage recommendation: REPAIR. Production generation and paper submission remain NOT_READY.**

The source-derived checklist was authored before runtime review. Original SNAS773A revised June2020 was directly read at printed pp7,12–17,20–31 and visually inspected at pp12,23. Its independently computed SHA-256 is `bbe3256eb811eb000f871eb3740449bd9ad2adf60db91d859ac433131d6d0a27`. Six primary-source conflicts remain unresolved; no official erratum is asserted.

Actual recorded local execution: **135/135 independent tests passed**, with zero failures/errors/skips. **11 synthetic runtime faults** were caught by source-derived oracles; **29 fabricated/corrupted/relabelled evidence variants** were rejected. **11 missing-scenario variants** remained partial. These are validation fixtures, not LLM-performance samples or physical measurements. The twelve saved owner scenarios exactly replayed, the eight-row closure ledger reconstructed exactly, and all accepted manifest input/output SHA-256 values matched current bytes.

Contribution lens: the bounded improvement makes eight known HDC2021 semantic obligations independently executable. It supplies event and evidence checks; it establishes neither new model performance nor complete peripheral equivalence. Novelty or submission-level contribution was not accepted by this specialist review.

Methods lens: nonzero latched STATUS is returned before clear; data reads clear DR only. Start/request/completion/reset boundaries are distinct. Trigger clearing at measurement start cannot be mistaken for conversion completion. Channel retention, continuous arming, dirty reset and nonzero defaults are checked. Unknown bit observations and malformed payloads reject atomically. Priority pin tests distinguish highest enabled threshold from incorrectly OR-ing lower active flags. Source authority is rehashed and evidence content exactly replayed; a count-only PASS cannot pass. Reviewed code has no remaining blocker within the declared bounded scope.

Communication lens: status generation when disabled, comparator STATUS reads, threshold address/channel prose and mixed DR/threshold priority are explicitly source-conflicted. Common positive latch tests use relevant enables set. Table/figure threshold preconditions and comparator policy remain candidate interpretations. Comparator/threshold exploratory witnesses cannot be relabelled as unconflicted manufacturer facts. Nominal timing metadata, event checks and candidate observations must remain distinct in any paper revision.

Issue repaired during review: standalone closure now asserts expert contract identities in addition to canonical accepted-file matching. Accepted package bytes are also bounded by execution/artifact manifests; neither is remote attestation. No fabricated physical evidence or silent source promotion was found. Early fixture signatures were adapted to the final public read API; they are not implementation defects.

Remaining major limitation at source_review.json/admission_gate.json: six manufacturer-source contradictions, no actual I2C frame validation, no ADC/calibration/elapsed-time test, and excluded peak-detector behavior. Minimum repair is to retain these scope restrictions and continue unresolved field obligations. Whole fields, all572source fields and full M4 are not promoted.

The preservation record is reviewed owner-run evidence. The independent recorder separately confirms frozen harness MD5 `8cf0854d4779467bc8e472ee4fb97023`. No original IR or historical model result was modified or rescored by this review.

Reproduce actual independent evidence with `python eval/hdc2021_semantics_v33_20261013/tests/record_independent_execution.py`. Executed command, JUnit XML, log, input hashes and exact counts are retained locally.

Unique next action: orchestrator verifies the accepted HDC2021 bytes and handles TMP461 nine REPAIR fields/fourteen dimensions while keeping global generation blocked. This bounded continuation needs no author hardware purchase.
