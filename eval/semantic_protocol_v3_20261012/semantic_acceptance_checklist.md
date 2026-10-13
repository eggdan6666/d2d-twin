# Bounded independent semantic admission checklist

Scope: d2d-twin / M / M4 / semantic-v3/semantic_acceptance. This is design and code admission of a bounded new semantic prototype, not certification of 572 fields or real hardware.

## Compiler must fail closed

- Preserve exact 572 unique inventory IDs and seven dimensions; validate mask/geometry and source identities before any assertion.
- Source PASS is not executable PASS. A prose rule, absent handler, unsupported condition, conflicting aspect, zero mask, zero comparisons or missing event is not a passing test.
- Reject unknown chip/register/operator/event, malformed payload, duplicate scenarios and stale artifact hashes.
- Every admitted scenario has an explicit source fact, independent expected values, legal stimulus, nonzero state and observable assertions; source annotations cannot invoke arbitrary code.
- Coverage maps only the specific fact/condition exercised, never an entire multi-clause dimension from one passing example.
- Gate remains closed if admitted production facts lack implementation or required repaired fields are unresolved.

## Minimum event scenarios

- TMP117: HIGH/LOW flags nonzero; CONFIG read clears only Alert mode. THERM mode LOW remains zero, HIGH tracks high/low hysteresis. TEMP/CONFIG separately clear Data_Ready.
- TMP117: EUN=0 still updates volatile backed register; EEPROM unchanged, later reset restores independently specified EEPROM image. EUN=1 starts busy program; completion then reset loads programmed values. Writes during busy rejected as outside contract (p18 prohibits them, does not specify ignored response).
- TMP126: Alert_Status single read clears only RC mask; auto-increment preserves. TEMP_RESULT separately clears Data_Ready. Comparator-to-interrupt transition and averaged one-shot completion have explicit events.
- HDC2021: MEAS_TRIG remains pending before start, clears at start; DRDY absent until complete. Each documented output read address clears DRDY.
- Bosch: BME ctrl_hum not effective before ctrl_meas commit; config sleep write accepted. Normal mode config writes are outside guaranteed domain (may be ignored). Both forced encodings complete to sleep, status measuring cleared only completion.
- Negative fixtures: inert storage, eager read-clear, premature complete, ignored EUN/sleep guard, immediate humidity commit, wrong masked flag clear, missing completion must each be detected.

## Evidence and boundaries

Original manufacturer pages directly read for TMP117 PDF17/18/27/28/29/30/31; TMP126 PDF16/18/26-33; HDC2021 PDF15/23-28; BME280 PDF27/28/30; BMP280 PDF24/25/26. Read scope and extraction saved locally. These readings do not replace full prior independent source ledger. Root prototype event payloads are declared abstract inputs; no elapsed physical timing, bus frames, silicon or numerical sensor conversion claim follows.

## Final acceptance prerequisites

Executed independent fixtures with command/log; input source/code hashes; final exact expert contract; named unresolved conflicts and partial coverage. Historical result files and previous protocol directories remain unmodified.

One next action: validate bounded implementation and keep production freeze closed for all unimplemented source obligations.

## Review closure checkpoint (2026-10-13)

Independent runtime/compiler regressions:58PASS. TMP117 nowuses controlled raw16bit completed-measurement codes with signed ordered limits (THIGH0x2000/TLOW0x1800), replacing relation-only injection. Strict threshold equalities are checked; TEMPs digitalrawupdate is distinctfrom physical measurement. Execution-proof guards nowreject missingchecks/count mismatch/failed comparisons/no required events/no nonzero stimulus/wrong-chip lineage. Remaining target-wide obligations keep formalfreeze NOT_ADMITTED.
