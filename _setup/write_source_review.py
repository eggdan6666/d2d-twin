from pathlib import Path
import json
out=Path('_setup/ir_drafts/SOURCE_REVIEW.md')
text=r'''# Gold IR Source Review: AD5592R and LIS3DH

- **Contract:** SCI-Skills Expert Contract 1.0
- **Project:** d2d-twin
- **Paper family:** M
- **Stage:** M4 (expansion subtask only; no global stage change)
- **Task:** `expansion-ir-source-review-20261010`
- **Status:** COMPLETE / provisional source review
- **Review boundary:** AI source review of two provisional drafts. This is not an independent human double review, and neither draft is promoted to `d2d/ir/`.

## scope_and_inputs

Reviewed the full text of the supplied PDFs, with page-level rendered checks for the register tables that had extraction ambiguity, the two provisional JSON drafts, and the frozen black-box harness. The PDF evidence is primary-source material; the harness evidence is an executed local file check.

| Input | Locations reviewed |
|---|---|
| `_setup/ir_drafts/AD5592R_draft_ir.json` | whole draft |
| `corpus/data/raw_pdf/ADI/ad5592r.pdf` | pp. 25-29 (reset, SPI/readback), 35-43 (control map and reserved fields), 50-52 (software reset and readback formats) |
| `_setup/ir_drafts/LIS3DH_draft_ir.json` | whole draft |
| `corpus/data/raw_pdf/ST/LIS3DH.pdf` | pp. 24-30 (I2C/SPI framing), 31 (address/default map), 34-40 (CTRL_REG0, controls, status and output registers) |
| `d2d/eval/test_d2d_blackbox.py` | whole assertion path relevant to `addr`, `reset`, `runtime_value`, `access`, `read_as`, `write_key`, and direct read/write calls |

## specialist_findings

### AD5592R

1. **Software reset is not currently wired to the harness semantic test (REPAIR, high confidence).** AD5592R Rev. H Table 28 states that `SW_RESET` bits `[10:0]` accept `10110101100`, which is `0x5AC`, and the operation resets the device (PDF p. 50; reset behavior also described on pp. 25 and 33). The draft marks the register `WO` but has no `write_key`. The frozen harness only runs `test_write_only_reset_key` when a `WO` register also supplies `write_key`; without it, this semantic dimension is skipped. **Fix:** add `write_key: "0x5AC"` to the draft and keep the selector address `0xF` separate from the 16-bit wire framing.

2. **Reserved bits are omitted from the represented fields (REPAIR, high confidence).** The source explicitly identifies reserved bits in `DAC_RD` `[10:5]` (p. 36), `ADC_SEQ` bit 10 (p. 37), `GEN_CTRL_REG` bit 10 and `[3:0]` (pp. 38-39), and the configuration registers on pp. 39-42. The draft only lists functional fields. This means the current harness cannot observe or diagnose a model that incorrectly stores or changes reserved command bits. **Fix:** represent each omitted region as `UNSPEC` when the source only says “set to 0” without a readback guarantee; use `RO` with reset 0 only where the chosen IR semantics deliberately assert fixed readback. Do not silently treat these bits as ordinary `RW`.

3. **The selector address is not a bus register address (REPAIR, high confidence).** The source defines a 16-bit SPI word: bit 15 selects control-register versus DAC write, bits `[14:11]` select the control register, bits `[10:9]` are reserved for control writes, and bits `[8:0]` carry register data (p. 26). The draft correctly warns that `addr` is a selector, but the direct harness calls `read_register(int(addr, 16))` and `write_register(...)`; it does not exercise SYNC/SCLK framing, the bit-15 mode bit, or the two-transaction readback sequence. Readback requires a configuration-register selection write followed by the next 16 clocks (p. 27), while DAC/ADC readback formats are specified on pp. 51-52. **Fix:** retain this candidate as a logical-selector IR only, or add an explicit SPI command adapter before claiming transport fidelity; keep `DAC_WR`, `ADC_RESULT`, and `DAC_DATA_RD` excluded until that adapter exists.

4. **Reset timing and cross-register side effects are not represented (REPAIR, medium confidence).** Power-up configuration takes 250 microseconds and writes must not occur during that interval (p. 27). The asynchronous reset and software reset restore all registers and I/O defaults (pp. 25, 33). `GEN_CTRL_REG.IO_LOCK` causes later writes to I/O configuration registers to be ignored (p. 29 and Table 17, p. 38). **Fix:** add reset timing/side-effect metadata or an explicit exclusion; add a stateful test if inter-register lock behavior is within the expansion scope.

5. **Verified items.** The selector values and functional bit positions in the current seven-register subset agree with Tables 13-20 and 28 (pp. 35-42, 50); `PULLDWN_CONFIG` reset `0x00FF` agrees with Table 13/Table 20 (pp. 35, 41-42). These checks do not establish completeness of the candidate.

### LIS3DH

1. **Transport framing is absent from the IR (REPAIR, high confidence).** I2C uses a 7-bit SAD `001100xb`, giving 0x18 or 0x19 according to SA0; the sub-address MSB enables auto-increment for multi-byte access (pp. 24-26). SPI uses bit 0 for read/write, bit 1 for multi-byte address increment, and bits `[7:2]` for the register address (pp. 27-30). The draft's I2C addresses are correct, but it does not encode these framing rules. The frozen harness's direct register API cannot test them. **Fix:** add explicit `address_encoding` metadata and keep framing out of the score until a protocol adapter is available.

2. **CTRL_REG0 fixed-default bits are under-specified (REPAIR, high confidence).** Table 25 and its note state that only bit 7 (`SDO_PU_DISC`) is functional; bits 0-6 must remain at their default value for correct operation, with reset `00010000` (p. 34; visually checked). The draft lists only bit 7 and a prose note. A model could therefore accept invalid writes to bit 4 or the other fixed bits without being diagnosed. **Fix:** add bit-level fixed-default fields for bits 0-6 (bit 4 reset 1, the rest reset 0), using `RO` only if fixed readback is an intended assertion; otherwise use `UNSPEC` plus an explicit “must write default” constraint.

3. **TEMP_CFG_REG fixed bits are omitted (REPAIR, high confidence).** Table 27 shows `ADC_EN` bit 7 and `TEMP_EN` bit 6, with bits 5-0 fixed at zero (p. 34). The draft lists the two enables only. **Fix:** represent the fixed region as `UNSPEC` or fixed `RO` fields under the same policy as CTRL_REG0.

4. **Dynamic status and output registers are incorrectly treated as static reset-zero registers (REPAIR, high confidence).** The address map labels `STATUS_REG` and `OUT_X/Y/Z_{L,H}` as `Output` rather than giving reset values (p. 31). The register descriptions define availability/overrun flags and live two's-complement, left-justified acceleration outputs (pp. 39-40). The draft assigns reset `0x00` and does not set `runtime_value`. The current harness therefore attempts a static reset assertion for values that are runtime outputs. **Fix:** set `runtime_value: true` for `STATUS_REG` and all six acceleration output bytes (and for auxiliary output registers if they are later added). Keep output-pair behavior separate from scalar register reset claims.

5. **CTRL_REG4 self-test encoding contains an undefined combination (REPAIR, high confidence).** Table 39 maps `ST[1:0]` values `00` to normal, `01` and `10` to self-test modes, and `11` to an invalid/blank entry (p. 37). The draft marks the entire field `RW`; the harness writes all ones to every `RW` field. **Fix:** mark `ST` `UNSPEC` until the IR/harness supports legal-value constraints, or add a legal-values annotation and a dedicated test. Do not score `11` as ordinary persistence.

6. **Multi-byte output semantics are not representable by independent byte reads (REPAIR, medium confidence).** `CTRL_REG4.BDU` controls whether output updates wait for both MSB and LSB reads, and `BLE` selects byte order (p. 37); the output values are paired at pp. 40. **Fix:** add pair/endianness metadata or exclude BDU/BLE behavior from the current direct-register contract. Do not infer an atomic two-byte guarantee from six independent `read_register` calls.

7. **Verified items.** `WHO_AM_I=0x33`, addresses 0x0F/0x1E/0x1F/0x20/0x23/0x27/0x28-0x2D, and reset values for the listed static controls agree with Table 21 and Tables 24-47 (pp. 31, 34-40). No explicit read-to-clear behavior was found for `STATUS_REG` on p. 39; the draft should keep `read_action` unset unless another source establishes it.

## evidence_and_execution_status

- `VERIFIED_SOURCE`: register addresses, defaults, bit positions, transport framing, reset key, and dynamic-output labels were checked against the cited PDF pages.
- `VERIFIED_USER_MATERIAL`: both provisional JSON drafts and the frozen harness were read from the workspace.
- `EXECUTED_LOCAL`: rendered page checks were performed for LIS3DH pp. 31 and 34 and AD5592R pp. 35-38; JSON/harness files were parsed/read locally.
- `EXECUTED_LOCAL`: frozen harness MD5 is `8cf0854d4779467bc8e472ee4fb97023`.
- `AI_INFERENCE`: recommendations about whether to encode reserved/fixed bits as `RO` versus `UNSPEC`, and the need for a transport adapter, follow from the source/harness boundary and are not claims about silicon behavior beyond the cited text.
- No external API, remote model, credential, or package installation was used.

## deliverables

- `_setup/ir_drafts/SOURCE_REVIEW.md` (this report)
- `_setup/ir_drafts/SOURCE_REVIEW_RESULT.json` (contract-complete expert result)
- No draft JSON and no frozen harness was edited.

## limitations_and_risks

- The review is an AI source review, not an independent human double review.
- The current harness is a direct register API and cannot validate electrical SPI/I2C waveforms, command framing, timing, FIFO behavior, BDU atomicity, or sensor physics.
- AD5592R and LIS3DH remain provisional; adding them to the formal roster before the listed repairs risks inflating coverage while leaving untested semantics and static/dynamic mismatches.
- `MPU6050` was outside this bounded review and remains blocked on its missing independent Register Map source.

## quality_checks

- [x] PDF text extraction completed for both source files.
- [x] Ambiguous register tables visually checked at page level.
- [x] Draft schema fields compared with harness branches.
- [x] Frozen harness hash recorded; no harness edit performed.
- [x] Source review does not claim independent human review or formal stage passage.

## one_next_action

Repair the two provisional drafts exactly against the findings above (starting with AD5592R `write_key`/reserved-bit policy and LIS3DH `runtime_value`/fixed-bit/self-test annotations), then obtain a separate human field-by-field review before any promotion into `d2d/ir/`.
'''
out.write_text(text,encoding='utf-8')
result={
'contract_version':'1.0',
'expert_skill':'sci-skills-paper-deep-reading',
'project_id':'d2d-twin',
'paper_family':'M',
'stage_id':'M4',
'task_id':'expansion-ir-source-review-20261010',
'task_status':'COMPLETE',
'inputs_reviewed':[
 {'path':'_setup/ir_drafts/AD5592R_draft_ir.json','scope':'whole draft'},
 {'path':'_setup/ir_drafts/LIS3DH_draft_ir.json','scope':'whole draft'},
 {'path':'corpus/data/raw_pdf/ADI/ad5592r.pdf','locators':'pp. 25-29, 35-43, 50-52'},
 {'path':'corpus/data/raw_pdf/ST/LIS3DH.pdf','locators':'pp. 24-31, 34-40'},
 {'path':'d2d/eval/test_d2d_blackbox.py','scope':'whole relevant assertion path'}],
'outputs':[
 {'path':'_setup/ir_drafts/SOURCE_REVIEW.md','type':'specialist-review'},
 {'path':'_setup/ir_drafts/SOURCE_REVIEW_RESULT.json','type':'expert-result'}],
'evidence_status':[
 {'label':'VERIFIED_SOURCE','claim':'Register addresses/defaults/bit positions/transport framing/reset key/dynamic labels checked against cited PDF pages.'},
 {'label':'VERIFIED_USER_MATERIAL','claim':'Drafts and frozen harness read from workspace.'},
 {'label':'EXECUTED_LOCAL','claim':'Selected PDF pages rendered and inspected; frozen harness MD5 recorded as 8cf0854d4779467bc8e472ee4fb97023.'},
 {'label':'AI_INFERENCE','claim':'RO versus UNSPEC and transport-adapter recommendations are analysis of source/harness boundary.'}],
'assumptions':[
 'Harness addr values are logical direct-register addresses; they do not imply wire-level SPI/I2C validation.',
 'A dynamic/output register should not be scored as a static reset value unless the IR explicitly freezes that behavior.'
],
'author_input_needed':[
 'Choose and document the reserved/fixed-bit policy (RO assertion versus UNSPEC diagnostic) for both drafts.',
 'Provide a separate human field-by-field review before promotion.',
 'Decide whether transport framing and multi-byte semantics are out of scope for M4 or require a protocol adapter.'
],
'manual_actions':[
 'A second human reviewer should compare each recommended field change with the rendered source pages and sign the review log.'
],
'quality_checks':[
 {'check':'Selected source tables rendered and visually inspected','status':'PASS'},
 {'check':'Draft-to-harness branch comparison','status':'PASS'},
 {'check':'Frozen harness unchanged; MD5 8cf0854d4779467bc8e472ee4fb97023','status':'PASS'},
 {'check':'No formal roster admission performed','status':'PASS'}],
'conflicts':[],
'conflict_resolution_status':'NOT_REQUIRED',
'merge_permission':'orchestrator_only',
'recommended_next_action':'Repair the two provisional drafts from SOURCE_REVIEW.md, then obtain separate human field-by-field review before promotion into d2d/ir.',
'stage_acceptance_recommendation':'REPAIR'
}
Path('_setup/ir_drafts/SOURCE_REVIEW_RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(out)
print('_setup/ir_drafts/SOURCE_REVIEW_RESULT.json')
