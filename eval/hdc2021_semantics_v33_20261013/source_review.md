# HDC2021 independent source review

## Scope and inputs

Bounded SCI-Skills paper-deep-reading task `hdc2021-v33/source_review`, project `d2d-twin`, paper family `M`, stage `M4`. This expert supplies source findings and a repair recommendation. Only the orchestrator may merge evidence or change a stage.

The full manufacturer PDF is locally accessible: `corpus/data/raw_pdf/TI/HDC2021.pdf`, SNAS773A, revised June 2020, 48 PDF pages including later packaging addenda. SHA-256 is `bbe3256eb811eb000f871eb3740449bd9ad2adf60db91d859ac433131d6d0a27`, matching all eight frozen HDC2021 REPAIR field records. This review uses the PDF as primary authority; candidate IR and the prior audit are inventories, not substitute authority.

Text was extracted from every PDF page. The functional specification occupies printed pp. 1–38. Critical rendered pages 7, 14, 16, 17, 23, 30 and 31 were visually inspected, including table column alignment and threshold waveforms. No physical measurement or bus execution was performed.

## Specialist findings — bounded 16-section reading card

1. **Bibliographic position.** HDC2021 High-Accuracy, Low-Power Humidity and Temperature Sensor With Assembly Protection Cover, Texas Instruments, SNAS773A. The packaging appendices carry dates in 2025–2026; they do not revise the functional register specification.
2. **Question.** Which of the eight audited repair clauses can become independently replayable register-level checks, and which require explicit candidate interpretation or remain excluded?
3. **Background route.** Datasheet-to-code evaluation needs to distinguish start, completion, clear-on-read, comparator state and electrical pin behavior. A simple storage register model misses these distinctions.
4. **Unresolved pain point.** This manual contains contradictory feature prose and register descriptions. Test success cannot turn a conflicting interpretation into a manufacturer fact.
5. **Core insight.** Restrict common read-clear checks to INT_MODE=0 with relevant enable bits set, create nonzero preconditions, and prevent a new conversion between reads. Keep comparator/threshold alternatives explicitly provisional.
6. **Method.** Read primary sections and register tables; check SHA against the frozen audit; inspect figures; map the eight fields to exact repair dimensions and conditional witness requirements.
7. **Mechanism.** `MEAS_TRIG=1` initiates measurement, self-clears when measurement starts, and must not immediately claim completed data or DR. Completion updates selected channel data. `SOFT_RES=1` initiates reset and self-clears after reset. Pending reset readback is unspecified.
8. **Formulas and assumptions.** Unsigned temperature word `w` gives `165*w/65536 - 40` °C; unsigned humidity word gives `100*w/65536` %RH (pp. 21–22). Unsigned threshold byte `q` uses denominator 256 (pp. 28–29), so comparing `w` with `q<<8` is an exact algebraic candidate when the corresponding threshold interpretation is chosen. Equality behavior and resolution-dependent low-bit alignment are not specified. Use stimuli safely away from equality. The analog humidity hysteresis listed on pp. 5–6 is not a digital Schmitt-band register.
9. **Material.** One manufacturer PDF; eight actual REPAIR fields and eight REPAIR dimensions: one legal encoding, two trigger/completion and five read-clear. No benchmark sample count, model score or full-field admission is changed.
10. **Design and metrics.** Proposed checks require a nonzero latch/DR, return of pre-clear data, second read after no new conversion, sibling preservation, and separate trigger/start/completion observations. These are proposed acceptance checks, not source-task test results.
11. **Evidence chain.** Source facts and their locators are enumerated as C1–C12 in `source_review.json`; the eight `field_closure_advice` entries map those facts to observable checks. Source conflicts below are retained rather than silently corrected.
12. **Conclusion boundary.** Positive mode0 read-clear, legal mode encodings, self-clear at start/reset completion, selected-channel structure and nominal CC values have source support. Candidate interpretations still require labels; actual hardware timing, analog accuracy and full I2C behavior are outside this review.
13. **Author-stated limitations.** The tPOR duration and selected conversion characteristics are specified by design/characterization and not tested in production (pp. 5–7 footnotes). Application examples are expressly outside the component specification (p. 33). Environmental, contaminant and layout effects limit physical accuracy (pp. 4–6, 34–36).
14. **Critical assessment.** A generic reset-to-zero oracle would incorrectly erase documented defaults such as TEMP_THR_L=1 and high thresholds=FF. A universal comparator read-clear oracle and a pin logical OR contradict parts of the manual. None of these problems is resolved by local tests alone.
15. **Reusable connections.** A reusable semantic adapter should expose the event boundary and evidence profile separately from register storage. The previous TMP117/TMP126 results are methodological context only and were not modified or reevaluated here.
16. **Testable follow-up.** Minimum viable repair: eight source-bound witness families with actual local traces, independent negative tests and immutable source hashes. Falsification is any wrong clear target, premature completion, reset-default loss, channel contamination or accepted fabricated witness. Main risk: reproducing one conflicting manual interpretation and overstating it as hardware truth. Novelty is not claimed; no broad literature search was performed in this bounded source task.

## Evidence and execution status

| Clause | Primary source | Supported bounded rule |
| --- | --- | --- |
| STATUS layout | p. 23 Tables 7-15/7-16 | DR bit7; TH6; TL5; HH4; HL3; status mask F8 |
| DR clear | p. 23 §7.6.5 | Any single read of 00,01,02,03 or04 clears DR; RESET clears DR |
| Threshold latch | pp.14–17 Figures7-3…7-6; p.30 Table7-36 | Mode0 latches until Status read; mode1 current-result is a conflicting figure-supported candidate |
| Measurement trigger | p.31 Table7-38; p.18 §7.4.1 | Write1 starts; bit clears at START; completion is later |
| Reset | p.30 Table7-36; p.7 §6.6; p.20 Table7-6 | Completed reset clears trigger and restores documented defaults; no guaranteed pending read |
| CC configuration | p.30 Table7-36 | CC0 one-shot; CC1…7 nominal periods120,60,10,5,1,0.5,0.2 seconds |
| Channels/accuracy | p.31 Table7-38 | MEAS_CONF0 both,1 temperature only;2/3 NA; TACC/HACC0/1/2 valid,3 NA |
| Pin priority | p.12 §7.3.5 | Threshold winner TH>TL>HH>HL; explicitly not logical OR |

`VERIFIED_SOURCE` identifies directly checked manual statements. `EXECUTED_LOCAL` applies only to PDF extraction, hashing and rendering. `AI_INFERENCE` applies to guarded algebraic mappings and candidate interpretations. Runtime, independent tests and physical behavior are `NOT_EXECUTED` by this source task.

An early partial-page reading suggested that 3.5 ms was only a power-up readiness statement. Full review and visual inspection of p. 7 corrected that inference: the 3.5 ms value is in the **MAX** column for Power-On Reset or Software Reset Duration, with the design/characterization footnote. Preserve this as source metadata, never as an executed timing result. Page18 separately says at least3.5 ms after power-up before measurements are ready.

## Conflicts, limitations and risks

Six unresolved source conflicts/ambiguities are returned in the JSON:

- **Comparator clear:** p.23 gives unconditional threshold status-read clear; pp.14–17 describe current-result comparator status. Common profile uses mode0; comparator preservation belongs to an explicit figure candidate.
- **Enable versus status generation:** feature prose conditions status assertion on enabled interrupts; p.25 says Status is unaffected by the enable register. Set all relevant enable bits for the common positive scenario; do not certify disabled-generation behavior.
- **Temperature-low address:** p.15 says0x0C; register map and p.28 say0x0A. Use table candidate mapping and retain the conflict.
- **Humidity-high channel/direction:** p.16 says temperature under the humidity-high threshold; Figure7-5 and register equations describe humidity above high. The latter remains an explicit candidate.
- **Humidity-low channel/name/address:** p.17 names temperature, HIGH and0x0E; Figure7-6 and tables identify humidity LOW0x0C. Keep the competing text visible.
- **DR plus threshold pin composition:** p.12 gives threshold priority and denies logical OR, but its equal-priority DR statement does not give a joint truth table. Use isolated DR-only or threshold-only pin cases; exclude combined-source truth-table assertions.

Additional exclusions are not manufacturer errors: active mode switches, mid-conversion retrigger/configuration changes, pending reset reads, threshold equality, exact output LSBs for9/11/14-bit accuracy, offsets/heater/calibration physics, bus waveforms and elapsed-time accuracy are outside the bounded certified clauses. One-shot versus continuous is not an excuse to invent auto-completion on a register write. CC changes alone should not be reported as tested wall-clock scheduling. Use an explicit measurement trigger to arm the series and logical scheduling events only.

HH/HL/TL nonzero generation from numeric stimuli follows disputed figure/table mappings. A common read-clear claim can consume a qualified logical status event while preserving this generation boundary. Replaying a candidate figure accurately provides bounded evidence for that profile, not resolution of the manual conflict.

## Deliverables and quality checks

Delivered `source_review.json`, this report, full `source_extract.txt`, and local rendered source pages in `source_review_materials/`. JSON includes the exact Expert Contract1.0 identifiers, twelve claims, eight field entries, six unresolved conflicts and explicit excluded claims. Original IR, frozen tests and historical results were not edited.

Recommendation: **REPAIR**. Source reading is complete for the bounded task; runtime validation is pending. Whole-field promotions authorized by this expert: **0**. This report does not advance M4 or authorize formal generation inputs.

## One next action

Implement and independently replay the eight bounded source clauses with exact source binding, retaining candidate profiles and exclusions before input admission.
