# Expansion IR repair log

Date: 2026-10-10  
Scope: AD5592R, LIS3DH, MPU6050 provisional candidates  
Status: source review passed; simulator and benchmark integration pending

The independent sign-off is archived in `INDEPENDENT_IR_REVIEW_SIGNOFF.md`. The post-repair recheck is archived in `POST_REPAIR_RECHECK.md`; it marks both LIS3DH and MPU6050 **PASS**. All three candidates now require simulator and benchmark integration review before promotion.

## Applied repairs

- **AD5592R**: added `SW_RESET.write_key = 0x5AC` using the frozen schema's `W` access code; represented reserved command-data regions as `UNSPEC`; recorded the 250 microsecond power-up delay and `IO_LOCK` cross-register side effect; retained SPI selector/readback framing outside the direct-register score.
- **LIS3DH**: added I2C/SPI framing metadata; represented fixed-default regions in `CTRL_REG0` and `TEMP_CFG_REG` as `UNSPEC`; marked `STATUS_REG` and six acceleration output bytes as `runtime_value`; marked `CTRL_REG4.ST[1:0]` as `UNSPEC` because value `11` is invalid; documented that BDU/BLE paired-output behavior is outside the direct-register harness.
- **MPU6050**: corrected the 8-bit `PWR_MGMT_1` reset encoding to `0x40`; recorded `DEVICE_RESET` against register-map pp.40-41; retained the local register-map mirror as provisional evidence.
- **Independent-review follow-up**: LIS3DH dynamic output reset assertions were removed and undocumented ODR codes were excluded from scoring; MPU6050 reserved fields, corrected pp.40-41 pointer, and primary-I2C framing metadata were added.

## Evidence and gate

- AI source review: `_setup/ir_drafts/SOURCE_REVIEW.md` and `_setup/ir_drafts/SOURCE_REVIEW_RESULT.json`.
- Frozen harness MD5: `8cf0854d4779467bc8e472ee4fb97023` (unchanged).
- MPU6050 mirror SHA-256: `519650CBC502A3E89DDBA6D6F115734B6C7060D451938C0DC36B6232DAAE7014`.
- None of the three repaired drafts has been copied into `d2d/ir/`.

## Admission gate

All three candidates have source-review PASS. Each still needs a simulator, candidate-specific frozen-harness run, and integration review before promotion to the formal benchmark roster.
