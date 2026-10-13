# LIS3DH independent manufacturer-source review


## 1. Scope and bibliographic position
DocID17530 Rev 2 (December 2016), ST LIS3DH datasheet, complete 54-page local primary source. PDF SHA-256: `852bfcf1a993f04cc147f26a26612a22fdc307c234f3e53d2c24c850ad421533`. Frozen ledger SHA-256 matches audit manifest: `0905059f5f981f89137533d8b6f34d33cde5b673a05707c6b7141d521bb54711`. This is a bounded source review for M4, not a stage pass or physical certification.


## 2. Research question
Can eight REPAIR fields be implemented with manufacturer-supported clauses without inventing unspecified dynamics?


## 3. Background route
Earlier inventory excluded ST RW and the entire STATUS reset byte too broadly. Repair should recover explicit facts without replacing unknowns with zero.


## 4. Unresolved pain point
Table 47 omits XDA and does not define DA/OR flag-clear read events. A smooth emulator must not conceal these omissions.


## 5. Core source finding
One ST access dimension and seven STATUS reset dimensions have bounded direct source support. Initial STATUS known mask is FE, expected masked value zero; whole-byte zero is unsupported.


## 6. Method
Read full extracted source; visually inspect printed pages16,17,31,37,39,40; verify manufacturer SHA against all eight rows and authority ledger hash; preserve claim IDs and conflicts.


## 7. Mechanisms and source facts
- **C1 VERIFIED_SOURCE** (p.31 Table21; p.37 section8.11 Tables37-38): CTRL_REG4 address23 is RW. ST occupies bits2:1 and default00; legal code storage/readback may be tested while maintaining legal neighboring mode/interface settings. UNSPEC is an old audit exclusion label, not the manufacturer access type.
- **C2 VERIFIED_SOURCE** (p.37 Table39): ST00 disabled, ST01 self-test0, ST10 self-test1. ST11 row is --, not an ordinary legal RW persistence test. Rejecting it at an adapter boundary does not assert silicon ignores or resets that code.
- **C3 VERIFIED_SOURCE** (p.39 Tables46-47; p.31 Table21): STATUS address27 is read-only Output in the summary, but Table47 explicitly gives zero defaults for ZYXOR7 ZOR6 YOR5 XOR4 ZYXDA3 ZDA2 YDA1. Known default maskFE, expected0, only at initial settled boot/default boundary before qualified sample events. Bit0 XDA has no description/default in Table47 and is not part of known reset mask.
- **C4 VERIFIED_SOURCE** (p.17 section3.2.2; pp.10-11 Table4 notes5-7; p.37 Table39): Self-test produces electrostatic acceleration and a physical output difference; the source settling requirement is two samples low-power/normal or eight high-resolution. Legal ST storage is not completion, analog response, sign/amplitude or timing certification. Qualified output sample events with ST nonzero need not be modeled by this bounded task.
- **C5 VERIFIED_SOURCE** (p.39 Table47; p.19 section3.4): YDA/ZDA indicate new data available for their axes, ZYXDA indicates a new set available. Qualified simultaneous XYZ completion in bypass/no-read/no-history-change scope may establish these known bits1. XDA is excluded because its row is absent. No arbitrary partial-axis aggregation oracle follows.
- **C6 VERIFIED_SOURCE** (p.39 Table47; p.37 Table38 BDU): Per-axis overrun indicates newly generated data overwrote previous axis data; ZYXOR indicates a new set overwrote previous set. Two qualified simultaneous XYZ completed samples with BDU0 and no intervening output/status reads support overwrite witness at FE mask. BDU-blocked nonwrites must not be called output overwrites; exact post-read flag history not specified.
- **C7 VERIFIED_SOURCE** (p.40 sections8.16-8.18; p.16 Table10; p.37 Table38 BLE and Table37note1): Acceleration outputs are signed two-complement left-justified. Qualified integer codes use8/10/12 significant bits for low-power/normal/high-resolution respectively. BLE0 lower-addressLSB, BLE1 lower-addressMSB; BLE can activate only high-resolution. Source format clauses are supporting scope, not eight new repaired output fields, not mg-to-code calibration.
- **C8 VERIFIED_SOURCE_WITH_AMBIGUITY** (p.37 Table38 BDU): BDU0 continuous update; BDU1 output registers not updated until MSB and LSB reading. This proves hold-until-both-read boundary, not precise pending/latest/next sample release, per-axis versus whole-XYZ granularity, duplicate-half read policy or post-release STATUS clear behavior.
- **C9 VERIFIED_SOURCE** (p.16 Table10; p.17 Table11; p.35 Table31): Legal LPen/HR pairs are10 low-power,00 normal,01 high-resolution;11 not allowed. ODR0 power-down,1-7 allthree modes,8 low-power only,9 high-resolution/normal1.344kHz or low-power5.376kHz;10-15 undefined. Settled qualified logical sample events do not execute wall-clock turn-on/ODR scheduling or active-history mode transition.
- **C10 ABSTRACTION_ASSUMPTION** (Task evidence boundaries; pp.24-30 digitalinterfaces; pp.10-15 physical/electrical specifications): Register/event adapter only. Use quiescent legal configuration, allaxes enabled, FIFO off/bypass, filter bypass, ST0 for qualified sample scenarios. No actual I2C ACK/frame/SPI/electrical/physical acceleration/self-test/clock certification; out-of-scope errors constrain benchmark input only.
- **C11 VERIFIED_SOURCE_WITH_AMBIGUITY** (p.39 Tables46-47; p.37 Table38; p.40 sections8.16-8.18; p.38 Table41; p.42 section8.22; p.45 section8.26): Reviewed Rev2 STATUS descriptions do not specify how STATUS or any output-byte/pair read clears or preserves DA/OR bits. Explicit INT1/INT2 source-register readclear provisions belong to other registers and cannot be transferred to STATUS. No common-source post-read reset/retention oracle after first observed read.
- **C12 VERIFIED_SOURCE_WITH_AMBIGUITY** (p.39 Table47): ZYXDA and ZYXOR prose refers to XYZ/new set without explicit OR/AND truth table for independently updated/read/disabled axes. Simultaneous allaxis no-read cases have common outcome; partial or mixed-history cases must be excluded or labelled hypothesis.


## 8. Formats and assumptions
For supplied signed n-bit output code s, the supporting left-justified word is `(s mod 2^n) << (16-n)` where n=8/10/12 for LP/normal/HR. This is a representation adapter, not conversion of real acceleration. BLE reversal is permitted only HR. Guard errors constrain accepted benchmark inputs and do not describe silicon response to illegal writes.


## 9. Material and denominator
8 frozen REPAIR fields, 8 dimensions: CTRL_REG4.ST/access; STATUS_REG XOR,YDA,YOR,ZDA,ZOR,ZYXDA,ZYXOR/reset. XDA, output formats and BDU are supporting/excluded clauses, not additional admitted dimensions.


## 10. Proposed experiment matrix (NOT_EXECUTED)
Legal ST writes00/01/10 under legal neighboring settings; ST11 guard; initial FE reset; controlled simultaneous XYZ firstsample/secondoverwrite with BDU0; per-axis known bits and whole knownmask; bit0unknown; output byte representation; unknown post-read STATUS; BDU hold boundary without pending release inference.


## 11. Claim-to-validation recommendations
- `CTRL_REG4.ST` -> C1,C2,C4,C9,C10; exact legal ST00/01/10 RW field storage; rejectST11 atcontractboundary withoutsiliconoracle; preserve legalneighboring settings anddefaultST00; do not claim physicalselftest completion/response
- `STATUS_REG.XOR` -> C3,C5,C6,C10,C11,C12; known initial/reset bit zero beforequalifiedevents; wholeSTATUS knownmaskFE notFF; XDA remainsoutside repairedscope; qualified simultaneousXYZ nonzero DA/OR witness excludesreadhistory; no postread reset/preservation promotion
- `STATUS_REG.YDA` -> C3,C5,C6,C10,C11,C12; known initial/reset bit zero beforequalifiedevents; wholeSTATUS knownmaskFE notFF; XDA remainsoutside repairedscope; qualified simultaneousXYZ nonzero DA/OR witness excludesreadhistory; no postread reset/preservation promotion
- `STATUS_REG.YOR` -> C3,C5,C6,C10,C11,C12; known initial/reset bit zero beforequalifiedevents; wholeSTATUS knownmaskFE notFF; XDA remainsoutside repairedscope; qualified simultaneousXYZ nonzero DA/OR witness excludesreadhistory; no postread reset/preservation promotion
- `STATUS_REG.ZDA` -> C3,C5,C6,C10,C11,C12; known initial/reset bit zero beforequalifiedevents; wholeSTATUS knownmaskFE notFF; XDA remainsoutside repairedscope; qualified simultaneousXYZ nonzero DA/OR witness excludesreadhistory; no postread reset/preservation promotion
- `STATUS_REG.ZOR` -> C3,C5,C6,C10,C11,C12; known initial/reset bit zero beforequalifiedevents; wholeSTATUS knownmaskFE notFF; XDA remainsoutside repairedscope; qualified simultaneousXYZ nonzero DA/OR witness excludesreadhistory; no postread reset/preservation promotion
- `STATUS_REG.ZYXDA` -> C3,C5,C6,C10,C11,C12; known initial/reset bit zero beforequalifiedevents; wholeSTATUS knownmaskFE notFF; XDA remainsoutside repairedscope; qualified simultaneousXYZ nonzero DA/OR witness excludesreadhistory; no postread reset/preservation promotion
- `STATUS_REG.ZYXOR` -> C3,C5,C6,C10,C11,C12; known initial/reset bit zero beforequalifiedevents; wholeSTATUS knownmaskFE notFF; XDA remainsoutside repairedscope; qualified simultaneousXYZ nonzero DA/OR witness excludesreadhistory; no postread reset/preservation promotion


## 12. Conclusion boundary
All source advice remains REPAIR_PENDING_EXECUTION. No field, chip, input version or SCI-Skills stage is declared passed. Code correctness would establish bounded clauses only.


## 13. Source limitations
The source records physical conditions, typical-versus-guaranteed limits and self-test settling requirements. It does not provide the STATUS readclear/aggregate/BDU-release truth tables needed for unconstrained software emulation. These are observed omissions in this version, not official errata.


## 14. Critical assessment and conflicts
- **LIS3DH-C-XDA-OMITTED** (p.39 Tables46-47): XDA bit0 initial/default and dynamic semantics. UNRESOLVED; initial STATUS knownmaskFE and XDA remains unknown throughout common source; no borrowing AUX1DA or sibling-chip facts.
- **LIS3DH-C-STATUS-READ-HISTORY** (p.39 Table47; p.40 sections8.16-8.18; p.38 Table41; p.42 section8.22): STATUS DA/OR clearing or preservation on STATUS/output reads. UNRESOLVED; source common profile ends numeric STATUS oracle at first observed read; thereafter unknown/guard, not zero or preservation. Candidate explicit profiles do not constitute manufacturer verification.
- **LIS3DH-C-AGGREGATE** (p.39 Table47): ZYXDA/ZYXOR for partial-axis/mixed-read histories. UNRESOLVED; support simultaneous XYZ samples only. Do not generalize all-axis witness to OR/AND aggregation.
- **LIS3DH-C-BDU-RELEASE** (p.37 Table38; p.40 sections8.16-8.18): BDU pair reading and blocked sample release selection/granularity. UNRESOLVED; verify hold before complete pair only as supporting bounded clause; post-pair selection and status effect excluded. Deterministic candidate interpretation must be labelled abstraction.
- **LIS3DH-C-ST-PHYSICAL** (p.17 section3.2.2; pp.10-11 Table4notes5-7; p.37 Table39): RW self-test code versus actual physical response/settling. UNRESOLVED as physical capability; use explicit two-bit Table39 for storage, leave response/sign/calibration/executed sample-settling out. Do not claim ST code persistence proves accelerometer self-test.
- **LIS3DH-C-ACTIVE-MODE-HISTORY** (p.16 Table10; p.17 Table11; p.35 Table31; p.37 Table38): Output/STATUS/unread history across active ODR/mode/BLE changes. UNRESOLVED; only quiescent legal setup before qualified samples, disallow active reinterpretation; source turn-on values metadata, not executed timer proof.


## 15. Reusable connection
Separate known reset masks from implementation backing bytes, read observation from subsequent sideeffects, and source facts from explicit candidate profile choices. Cross-register INT readclear is not evidence for STATUS readclear.


## 16. Testable follow-up idea
An official source or hardware trace could distinguish flag-clear/read and aggregation candidates. Minimum falsifiable sequence: qualified XYZ arrivals, partial output reads, STATUS observations, then repeat across axes with BDU0/1. Evidence must identify exact source/device/config; this review does not execute or require hardware.


## Evidence, quality and deliverables
PDF/ledger hashes and denominator checks executed locally. Full PDF text extracted; six critical pages rendered and visually checked. source_review.json emits exact expert contract,12claims,8advice records,6unresolved conflicts. Runtime, admission and physical verification were not executed by this expert. Old assets were read-only.


## One next action
Implement and independently replay the eight bounded repair dimensions while retaining FE-only default oracles and unknown post-read histories before input admission.
