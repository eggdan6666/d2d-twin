# Bounded independent acceptance of the source-admission bundle

Task: `semantic-v3/source_acceptance`; expert: `sci-skills-paper-deep-reading`; contract 1.0; project `d2d-twin`, family M, stage M4. This expert does not change stage state.

## Scope and inputs

The input is the existing `independent_source_admission_20261012` package, v2 inventory/core inputs, and local manufacturer PDFs. This is an independent integrity/replay review plus decisive primary-source spot checks. It is **not a second independent judgment of all 572 fields**, vendor authentication of local PDF bytes, a check of current online versions, or hardware timing validation. Local source access included complete relevant pages, surrounding mechanism sections, register tables, and visual rendering of crucial bitmaps.

## Specialist findings

**PASS for the bounded package-integrity, identity, patch-replay and requested spot-check gates. Formal production generation admission remains REPAIR.** No newly discovered factual blocker prevents building a separately scoped candidate event/interface contract. Conditional and disputed aspects cannot become unconditional assertions by virtue of this acceptance.

### Executed integrity and geometry checks

| Check | Independently executed result |
|---|---|
| Bundle payload manifest | All 1,252 declared payload hashes match |
| Proposed input snapshot manifest | All 30 hashes match; its own status remains REVIEWABLE_SNAPSHOT_ONLY |
| Reviewed PDF identities | 21 PDF SHA-256 values match local bytes |
| Field inventory | Exactly 20 chips, 572 unique prior identities; exact correspondence to v2 inventory |
| Seven aspect records | Exactly 4,004 identity/aspect combinations; dimension CSV corresponds bijectively to JSON |
| Verdict counts | 135 PASS, 96 REPAIR, 302 CONDITIONAL, 39 EXCLUDE, unchanged |
| Locator structure/text presence | 5,243 valid page locators; 4,356 nonempty excerpts match source text; 887 locators have empty excerpts |
| Repair replay | All 109 guarded old-value operations replay successfully against v2 IR |
| Final candidate reproduction | After separately reproducing documented commentary/schema packaging, all 20 candidate IRs deep-equal the published copies |
| Candidate geometry | 572 fields within device width, no overlap, all present numeric resets fit the field width |
| Policy mapping | All 572 prior inventory IDs map to candidate field names and corrected geometry |
| Preservation | All 12,563 protected live files match the prior before-hashes; v2 core 44 files and formal IR also unchanged |
| Frozen original harness | MD5 `8cf0854d4779467bc8e472ee4fb97023` |

Text presence supports traceability, not validity of the conclusion attached to the excerpt. Empty excerpt locators were checked for page range/locator structure, not treated as quote matches. The 21-PDF manifest includes the MPU6050 product specification; field locators use the independently hashed register-map source, so only 20 distinct PDFs appear in field locator extraction.

### Direct primary-source spot checks

| Source fact (原文事实 / VERIFIED_SOURCE) | Primary source locator | Acceptance boundary |
|---|---|---|
| TMP117 EUN=0 allows volatile register writes; EUN=1 enables corresponding nonvolatile programming. Writes must wait for Busy to clear; POR also sets Busy. | SNOSD82D, printed/PDF pp.18,30, §7.5.1.2 and Table7-10 | Reject a rule that requires unlocking for ordinary volatile configuration/limit writes. EEPROM completion may be abstracted explicitly; typical 7 ms is not a deterministic measured completion time. |
| TMP117 alert TNA=0 clears HIGH/LOW flags on CONFIG read; therm TNA=1 leaves those flags unaffected by CONFIG read, HIGH follows completed conversions and hysteresis, LOW reads zero. | Printed/PDF pp.16–17,27, §§7.4.4.1–2, Table7-6 | Therm clear comparison is below the LOW limit; do not silently change it to less-than-or-equal. Preclear observation and postclear state need a controlled asserted event. |
| TMP117 DATA_READY clears on TEMP or CONFIG read. MOD=2 reads back as0. MOD1 cannot be stored in EEPROM. | Printed/PDF pp.27–28, Table7-6 and note2 | Do not reuse the alert clear rule for DataReady or program the entire grouped MOD field into EEPROM without masking its unsupported bit. |
| TMP117 high/low thresholds load EEPROM values on reset; factory defaults are declared separately. | Printed/PDF pp.25,29, Table7-3 footnote1, Tables7-8–9 | Do not claim factory numerical defaults for a previously reprogrammed EEPROM image. Existing source conflicts are retained; this check does not resolve them. |
| LIS2DW12 OUT_T_L has TEMP3..TEMP0 in bits7:4 and zero bits3:0. Temperature is left-justified 12-bit data across OUT_T_H/L. | DS11811 Rev9, printed/PDF pp.18,33,35, §3.6, Tables21–23 | Geometry repair and ZERO_3_0 rename are supported; data is dynamic, not a permanent reset snapshot. Table23 prose's “8 least significant bits” does not supersede the explicit bitmap and §3.6 format. |
| TMP461 STATUS and ONE_SHOT have POR N/A; one-shot has no read pointer, write0Fh, and arbitrary write data starts a one-shot. | SBOS722B, printed/PDF p.17, Table4 and note1 | A numerical reset-zero oracle is unsupported. Unknown reset cannot be converted to an assumed hardware zero; abstract event completion remains an explicit assumption. |
| TPS23861 firmware revision command is41h, read-only, FRV[2:0] firmware revision; reset/version symbols are R, not a specified number. | SLUSBX9I, printed/PDF p.77, §7.5.30 | Address repair 0xFE→0x41 supported; no fixed revision value inferred. Source conflict in GENERAL_MASK remains unresolved. |
| TMP100 has full12-bit temperature format at bits15:4, zeros3:0; effective9/10/11/12-bit ADC resolution selects further output zeros. Result is0 until first conversion completes. | SBOS231I, printed/PDF pp.9,16–17, §7.3.1, Tables6–7, resolution Table10 | Geometry15:7 is only the effective default9-bit slice, not the full general format. Variable resolution and conversion epoch must be explicit. |

Crucial bitmaps were visually inspected after local rendering: LIS2DW12 p.35, TMP461 p.17, TMP100 p.16, TMP117 pp.27,30, TPS23861 p.77. Numeric page references above are both printed and PDF physical pages for these checked sources.

## Evidence and execution status

`EXECUTED_LOCAL`: Python integrity/replay/geometry checks and PyMuPDF extraction/rendering. `VERIFIED_USER_MATERIAL`: supplied bundle/candidate copies and prior inventory. `VERIFIED_SOURCE`: bounded primary-PDF statements in the table. `AI_INFERENCE`: recommendation that this package can support a separately validated event/interface candidate. No external API, model inference, hardware operation, historical rescoring or prior-file edit was executed.

## Deliverables

This report and `source_acceptance.json` carry the expert return. Reproducible integrity source, output, all-locator checks, live preservation checks and rendered spot-check pages are in `source_acceptance_scratch/`. Scratch contains derived extraction/rendering files, not edits to original evidence.

## Limitations and risks

The bundle's TMP117, INA3221 and TPS23861 source conflicts remain unresolved and must retain aspect-specific exclusions. A static bitfield repair does not establish dynamic semantics. All 302 CONDITIONAL fields need stated dependencies or a bounded exclusion; all 96 REPAIR labels need implementation/integration acceptance, rather than relabeling to PASS. No absent hardware result can be replaced with a simulated timing claim. Unknown startup/default values and unsupported illegal-input outcomes remain unasserted.

## Quality checks

All requested outputs and bounded checks are complete. The return identifiers match the orchestrator task. The full prior protection baseline still matches after this expert's work. Completeness and semantic certainty remain separate; source facts, abstraction assumptions and unresolved conflicts are not merged. This expert has not changed `.sci-skills` stage state or promoted generation inputs.

## One next action

Implement and validate the explicitly scoped v3 event/interface admission contract against these repaired candidates, keeping unresolved source aspects excluded, before the orchestrator considers a prospective generation-input freeze.
