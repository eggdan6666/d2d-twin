# Independent TMP126 v3.2 code acceptance

Task `tmp126-v32/code_review`, project `d2d-twin`, family M, stage M4. **Bounded implementation: PASS_CANDIDATE. Whole-stage recommendation: REPAIR. Production generation and submission remain NOT_READY.**

The source-derived checklist was written before reviewing runtime code. Primary local PDF SNIS209C revised June2022 SHA-256 `6d9bab59b2814422d7bc1dff8fbd203df26e92ee40075b613c1f1fbb59eddfef` was independently read at printed pp2,14-17,21,26-32. Expected RC/live masks, signed data format, averaging count and event transitions come from these pages, not from candidate rule outputs.

Actual saved execution: **121/121 independent CPU tests passed**, zero failures/errors/skips. **13 synthetic runtime faults** were detected by source-derived oracles. **28 corrupted or fabricated execution/source variants** were rejected. Eight missing required-scenario variants stayed PARTIAL. These are validation fixtures, not LLM sample outcomes.

The ten saved owner scenarios replayed exactly; the eight-row bounded closure ledger reconstructed exactly; execution-manifest input/output SHA-256 matches were independently verified. The owner scenarios total85 checks, including8 source-table metadata checks and2 explicitly exploratory body-policy checks. They are not85 physical measurements. Original eight source REPAIR fields/eight dimensions remain unpromoted.

Contribution lens: the improvement supplies independently executable temporal checks for eight known TMP126 semantic defects. It does not show new model accuracy, novelty against literature, physical chip equivalence or a complete datasheet emulator. No submission-level contribution claim was accepted here.

Methods lens: nonzero flags are returned before0xA7 readclear, live0x58 bits survive, and TEMP read clears DR only. Qualified CRC failure discards writes. Comparator-to-interrupt transition clears pre-existing nonzero flags/live bits and logical ALERT; same-mode writes preserve state. Eight-sample signed averaging, restart/discard, readzeroONE_SHOT, MODE1 completion and abort were tested separately. Malformed payloads and out-of-scope transactions reject atomically. Admission binds exact source advice, source PDF SHA, frozen original field inventory, scenario identity, trace/check content and deterministic replay. Reviewed code had no remaining blocker within the declared bounded scope.

Communication lens: six source conflicts are visibly retained. Single/no-increment statusclear is the common positive scope. Burstclear behavior in body_candidate is exploratory only. Comparator encoding/low-limit naming retain candidate labels; active disable timing, CRC_CONFIG, physical frames and numerical slew are excluded. The current output correctly separates nominal metadata, digital event checks and exploratory checks. This separation must survive any paper revision.

Issues repaired during review: source_scope_guards initially attempted an active-alert enable change that its own common scope excludes; the owner removed this setup write. Admission initially did not rehash the reviewed primary PDF; the owner added path/SHA binding. Averaging scenario was strengthened to a distinct signed exact-grid stimulus so a last-sample implementation cannot pass. Final independent evidence refers only to the corrected current bytes.

Remaining major limitation (source_review.json/admission_gate.json): source contradictions and physical omissions prevent whole-field certification and global production generation. Minimum repair is to retain the existing exclusions and continue outstanding source obligations. Resolving manufacturer contradictions or adding physical evidence is outside this task and must not be claimed complete.

The preservation artifact records12563 old inventory files and1390 prior archived payloads unchanged; that is reviewed owner execution evidence. The independent recorder separately verified the frozen harness MD5 `8cf0854d4779467bc8e472ee4fb97023`. No historical model score was computed by this review.

Reproduce with `python eval/tmp126_semantics_v32_20261013/tests/record_independent_execution.py`. Exact executed command, XML, log, input hashes and counts are in independent_code_execution.json. Repackage this review only after that record succeeds on the accepted owner manifest.

Unique next action: orchestrator verifies the accepted TMP126 bytes and implements HDC2021 eight outstanding REPAIR fields, preserving the global generation block. No author environment or hardware action is required for that bounded next task.
