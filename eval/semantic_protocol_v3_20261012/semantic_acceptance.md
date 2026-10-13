# Independent bounded semantic acceptance

Project d2d-twin; family M; stage M4; task semantic-v3/semantic_acceptance. Review completed 2026-10-13. Directory/version retains the established 20261012 identifier. This is an independent AI review, not a human signature, manufacturer certification, physical experiment or a peer-review decision.

**Decision: bounded prototype checks acceptable; global source/production admission remains REPAIR / NOT_READY.** No whole source dimension is closed, no repaired field promoted, and no new generation should start from this version.

## Scope and inputs

Read the SCI-Skills presubmission-review expert and its required contract/evidence/stage/local-adapter resources; the independent source signoff, candidate policy, candidate IR, and new runtime/compiler/scenarios/build script. Directly read original TMP117 SNOSD82D pp17-18/27-31, TMP126 SNIS209C pp16/18/26-33, HDC2021 SNAS773A pp15/23-32, BME280 cover revision1.24 (February2024, BST-BME280-DS001-24) pp27-28/30 and BMP280 register pages24-26. Five original PDF SHA-256 identities match the candidate source lock. BME280 cover identifies1.24, while the inspected internal pages retain footer BST-BME280-DS001-23 Revision_1.23_012022; this cover/footer discrepancy is retained, not interpreted as an official erratum or silently resolved. Detailed direct-page extracts are retained as a bounded review working record. Source review of all572 fields belongs to the separate independent source ledger, not this execution review.

The target is a five-chip digital event prototype. Explicit event hooks represent qualifying completed digital actions; they do not measure conversion duration, analog thresholds, silicon behavior or bus frames. TMP117 uses a declared factory EEPROM image and controlled completed-measurement raw-code event with ordered signed limits. BME active humidity is an explicitly labeled abstract observation hook.

## Specialist findings

|Lens / severity|Evidence and consequence|Minimum repair or boundary|
|---|---|---|
|Contribution / MAJOR|Eight scenarios and61 checks (54 numeric comparisons,7 scope guards) demonstrate executable conditional semantics, not new model capability or full device emulation.|Describe the artifact as semantic validation infrastructure; preserve historical scores and avoid an accuracy-improvement claim.|
|Methods / BLOCKER|The4004-dimension closure ledger reports24 partial dimensions,2361 pending,820 source-excluded and799 not-applicable; every whole_dimension_closed remains false.|Retain NOT_ADMITTED. Implement and independently validate remaining admitted obligations before a new production freeze.|
|Methods / MAJOR|Scalar register reads/events omit protocol frames, numerical sensor outputs, broad operating modes and physical timing. Runtime supported-chip membership does not admit all chip functions.|Scope assertions to exact clauses and event assumptions. Do not count a known reset or partial read-clear example as all seven source dimensions complete.|
|Methods / MODERATE|Execution-link compilation initially trusted caller PASS/assertion-count claims without complete check/trace records. Independent fault cases exposed absent required events/nonzero stimuli and wrong-chip lineage; these guards were repaired and rechecked.|Repaired guard tests pass; maintain actual local logs and hashes. Structured records and hashes provide local provenance, not remote execution attestation.|
|Communication / MAJOR|Original source conflicts including TMP117 reset/EEPROM/revision, INA3221 and TPS23861 remain unresolved.|Continue to disclose conflicts and excluded aspects; never label selected interpretations official errata.|

Dangerous source mismatches were explicitly avoided: TMP117 p18 prohibits writes during EEPROM programming without defining an ignored-write response; the prototype excludes the operation. Bosch normal-mode config writes may be ignored, so the profile excludes a deterministic response assertion. TMP117 Alert and THERM read-clear behaviors differ; HDC trigger start differs from measurement completion. Shutdown/one-shot TMP117 modes and reserved TMP126 write stimuli are excluded in the bounded profile instead of given speculative behavior.

## Evidence and execution status

Independent tests are in tests/test_independent_semantics.py. The retained independent log and manifest record58 passing cases at this review checkpoint. Seven synthetic fault fixtures are detected: eager humidity commit, inappropriate alert clear on TEMP, inert no-event storage, programming while EUN locked, premature HDC ready, missing HDC data-read clear, and premature averaged-conversion completion. These are synthetic mutation checks, not empirical model results.

Positive and negative scenarios independently check TMP117 conditional alert/THERM semantics and volatile-vs-programmed EEPROM/POR/busy; TMP126 transaction-sensitive clear and eighth-sample one-shot completion; every documented HDC cross-clear address with a nonzero witness; both Bosch forced encodings on both devices; config sleep guards; unknown-event/payload/chip guards; unknown revision/empty-register rejection; six source mapping tamper cases; failed/vacuous scenario rejection; conflict-aspect rejection; and hash/path traversal rejection. A controlled raw measurement code updates TEMP; no temperature measurement or numeric conversion is inferred from a prior reset value.

The root local run records8 scenarios61 checks (54 numeric comparisons,7 scope guards). These support bounded partial clauses only. The independent run manifest stores input code/test hashes; final orchestrator packaging must rerun combined tests and preserve current hashes if code changes after this checkpoint. Earlier source verdicts remain135PASS/96REPAIR/302CONDITIONAL/39EXCLUDE.

## Deliverables and limitations

Deliverables: this review, semantic_acceptance.json, semantic_acceptance_checklist.md, independent tests, independent_semantic_execution.log and independent_semantic_execution.json. No previous frozen harness, formal IR, historical model result, old v2 file or authoritative project stage was modified by this review. This review does not independently audit every preserved12563-file hash; that integrity claim belongs to the source/orchestrator manifests.

Readiness is NOT_READY for production input freezing. The prototype intentionally keeps production_generation_ready=false even with a supplied generation context; it is not yet a general predicate capable of accepting a finished full protocol. The ledger is a repair queue and partial demonstration record. Source-defined exclusions do not automatically justify excluding broad required functions from the final benchmark target.

## Quality checks and one next action

Source facts were checked in five original PDFs, scenario expectations are independent literals/conditions rather than copied model/reference outputs, malformed/unsupported operations fail closed within tested profiles, no all572 execution certificate is issued, and local fault/check logs are retained. Manuscript source claims and target-wide closure still require further work.

**One next action:** implement the first explicitly queued unclosed semantic obligation in a new bounded repair cycle, validate nonzero/negative fixtures independently, and keep formal generation input freezing blocked until the declared target obligations are admitted.
