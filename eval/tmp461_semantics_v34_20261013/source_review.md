# TMP461 independent source review, v3.4

Date: 2026-10-13. Task: `tmp461-v34/source_review`. This is an independent source specialist return; only the SCI-Skills orchestrator may change stage status.

## Scope and inputs

Full local primary manufacturer PDF: `corpus/data/raw_pdf/TI/TMP461.pdf`, SBOS722B, June 2015 / revised August 2016, 38 PDF pages. Functional specification printed pp. 1-29; package/addenda/disclaimer PDF pp. 30-38 (addendum 19-Mar-2026, materials 18-Jun-2025). SHA-256 `ad98b47e7b831b44da5cedb8454220cbc2ee0220f32de48d5ebf1e81eb7bf740` matches every frozen TMP461 REPAIR record. The frozen `field_evidence.json` hash is `0905059f5f981f89137533d8b6f34d33cde5b673a05707c6b7141d521bb54711`; checked against its audit manifest. Candidate IR is not manufacturer authority.

Exactly nine REPAIR fields / fourteen REPAIR dimensions: ONE_SHOT.START reset; eight STATUS fields reset; LHIGH/LLOW/RHIGH/RLOW/OPEN additionally read_clear. Denominator = 9 reset + 5 read_clear. Trigger behavior and pin hooks are supporting executable clauses, not additional frozen REPAIR dimensions.

All 38 pages were extracted/read. Critical printed pp. 10,12,13,17,19,21 were rendered and visually inspected. Local PyMuPDF was already available. No old IR/harness/result writes, API calls, SCNet execution or physical test occurred in this review.

## Specialist findings and standard reading card

1. **Bibliographic position (原文事实 / VERIFIED_SOURCE).** Manufacturer component specification, not a research experiment. Core version SBOS722B; later packaging pages do not supersede register semantics.
2. **Question.** Can a register-level emulator preserve the difference between undefined power-on state, live conversion/thermal state, condition-qualified status latches, and separately serviced ALERT?
3. **Background.** Local and remote temperature channels share ADC/control but use distinct limits and result bytes; pin 7 switches ALERT/THERM2; pin 4 is THERM.
4. **Unresolved pain point (AI分析 / AI_INFERENCE).** A zero-filled dictionary and unconditional STATUS read-clear give plausible but incorrect outputs. The frozen N/A reset facts prohibit asserting power-on zero.
5. **Core insight.** Track a known-bit mask and independently track current causes, historical status latches and ALERT latch. Read-clear depends on mode and cause retirement.
6. **Method.** Use source-grounded register access and qualified logical conversion/fault/service events. No analog signal or elapsed-time fidelity is claimed.
7. **Mechanism.** Table 4 p.17 sets STATUS POR=N/A; ONE_SHOT is write-only, POR=N/A, X bits. Table 5 p.19 BUSY is live, bits 6:2 are qualified latches in ALERT, bits 1:0 are automatic thermal comparators. In THERM2 only OPEN remains read-clear latched. A STATUS read clears retired flag causes, never the ALERT output latch.
8. **Formulas.** Normal result temperature = signed8(high) + (low >> 4)/16 C; extended = unsigned8(high)-64+(low >>4)/16 C (Tables 1/2 pp.10-11). RANGE changes result format at the next conversion, not immediately. Thermal assertion is strict T>limit; thermal release is T<=limit-hysteresis (p.19). Hysteresis is unsigned integer degree difference, not extended offset or signed temperature. Digital remote filter is a four/eight sample moving average (p.12), but initialization and nonintegral rounding are not specified.
9. **Material.** One exact manufacturer source and nine frozen evidence records; no extra chips, generation samples or hardware cohort.
10. **Design and acceptance.** Before read-clear, produce a nonzero source-qualified flag. Read while cause persists must preserve it; then return inside, read pre-clear value, and verify the next read clears only eligible flags. Separate masked pin, status and master-service checks. Default CONAL=1 and filter disabled provide a common-source intersection.
11. **Evidence chain.** See claim C1-C13 in JSON; every bounded clause has printed page/table/section locators. Source recommendation is pending actual runtime/testing, not execution PASS.
12. **Conclusion boundary.** These facts permit bounded logical clauses only. No whole field promotion, no formal generation input approval, no reset-value zero oracle for STATUS/ONE_SHOT.
13. **Source-stated limits.** Device ambient specified -40..125 C, remote-diode practical range differs from representable extended codes (p.10). Physical bus/electrical/analog limits require real measurements; applications pp.23-28 explicitly carry manufacturer validation caveats.
14. **Critical assessment.** Retain ambiguities below; avoid silent correction, universal exact timing, undefined reset fabrication and treating the benchmark event as an actual SMBus service transaction.
15. **Reusable connection (AI分析).** A partial-state logical oracle can distinguish unknown defaults from controlled post-conversion values and can maintain causal proof for destructive reads.
16. **Testable follow-up idea (研究假设 / RESEARCH_HYPOTHESIS).** Compare generators' unconditional read-clear failures against cause-aware modeling using positive-before-read traces. Required evidence: independent mutated implementations and field-bound actual replay; falsifier: no difference on bounded clauses. Minimum version: this chip's five conditional flags; risk: source ambiguities outside the default-filter/default-CONAL envelope. No novelty claim.

## Source-supported executable clauses

- **Unknown POR**: STATUS all bits have no numeric POR guarantee. ONE_SHOT has no readable value and does not store the written byte. A runtime may carry internal zero bytes only with a zero known mask; a read must not certify this as observed zero. General-call reset restores the same unknown-POR boundary.
- **One-shot**: p.21 writing *any* byte at 0x0F when SD=1 starts one conversion/comparison cycle of enabled LEN/REN channels. Completion updates results and returns shutdown. BUSY starts at conversion and retires on completion. Active retransmission and SD=0 trigger behavior lack a supported outcome and should be excluded.
- **ALERT read-clear**: p.19 cause-qualified mask0x7C. Return pre-clear byte, then clear only retired causes. Persisting high/low/open causes remain. Temperature/result/CONFIG reads are not STATUS read-clear operations.
- **ALERT pin**: p.19 pin latch stays asserted after STATUS clears. Only a qualified master servicing the sensor device address when flags reset and causes gone clears it. Ordinary register read is not proof of an electrical SMBus alert-response transaction.
- **THERM state**: RTHRM/LTHRM auto-retire at <=THERM_limit-HYS; STATUS read cannot destroy a thermal comparator or BUSY. Active-low THERM combines local/remote thermal causes.
- **THERM2**: high flags follow high-limit hysteresis; low causes do not affect pin7. OPEN remains latched and read-clear only after functional remote connection. MASK1 only affects ALERT, never THERM2. Unqualified active mode-switch low-bit value is excluded.
- **Supporting defaults**: read/write CONFIG03/09, conversion-rate04/0A, distinct limit aliases Table4. Default rate08=16SPS and one-shot per-channel15ms typ/17ms max are metadata, not local elapsed-time proof.

## Limitations and unresolved source branches

| ID | Branch | Source basis and bounded treatment |
|---|---|---|
| TMP461-C-CONAL-STATUS | p.19 any-high-flag latch language vs pp.13/21 programmed consecutive ALERT pin filtering | No exact status-vs-latch timing rule at CONAL>1. Common CONAL01; other implementations require explicit candidate classification. |
| TMP461-C-CONAL-SOURCES | Consecutive count switching channels/high-low causes and OPEN contribution | pp.13/21 do not specify those truth tables. Do not infer any OR-union or OPEN count behavior at higher count. |
| TMP461-C-FILTER-HISTORY | Initial/changed digital filter history and nonintegral rounding | p.12 Figures11/12 identify moving averages but no exact startup/reset/rounding algorithm. Common DF00; fully primed integral candidate sequences can be separate, not source certification. |
| TMP461-C-THERM2-LOW-STATE | LLOW/RLOW after mode change or old ALERT history | p.19 says low flags no effect on THERM2 and lowbit generated in ALERT, but no transition status-value contract. Scope THERM2 pin/high/OPEN clauses; retain low unknown/excluded as appropriate. |
| TMP461-C-POR-STATUS | Table4 N/A vs Table5 flags reset by POR wording | POR retires latches but Table4 gives no whole numeric STATUS default. Keep full reset known mask00 rather than silently manufacturing STATUS00. Controlled conversion establishes a new known state, not a POR oracle. |
| TMP461-C-RANGE-TRANSITION | Limits/old results interpretation during RANGE change and conversion boundary | p.10 says data format at next conversion; no complete mixed oldresult/newlimits transition oracle. Configure RANGE/limits quiescently, establish new conversion before comparisons; exclude active-range transition. |

Other deliberate exclusions: physical remote fault voltage/sampling timing, exact threshold equality for alert latches, active config/history transitions, midflight one-shot retrigger, per-channel intermediate conversion ordering, calibration/offset/eta physics, out-of-range saturation/electrical behavior, actual general-call/SMBus frames and deadlines. Fault retirement is a qualified logical functional connection event; no pin-voltage conclusion.

## Quality checks and evidence status

VERIFIED_SOURCE: complete exact PDF; six critical visual pages; identity and source-record hash binding; 9/14 denominator checked. EXECUTED_LOCAL: PDF extraction/rendering, SHA-256/count verification. NOT_EXECUTED: implementation regression/admission/hardware, deliberately left to independent runtime reviewer and orchestrator. Source conflicts remain UNRESOLVED. No task/stage advancement authorized.

## One next action

Implement and independently replay the nine fields' fourteen bounded dimensions using these source clauses and explicit exclusions before the orchestrator considers any input admission.
