# First expansion IR review log

Date: 2026-10-10

These files are review drafts only. They are intentionally outside `d2d/ir/` and are not admitted to the frozen benchmark.

| Candidate | Source evidence | Draft scope | Status | Blocking item |
|---|---|---|---|---|
| AD5592R | `corpus/data/raw_pdf/ADI/ad5592r.pdf`, Register Map pp. 35-52 | 7 control selectors, 16-bit SPI command framing | source-review PASS; simulator pending | Add a simulator and run the frozen harness before promotion |
| LIS3DH | `corpus/data/raw_pdf/ST/LIS3DH.pdf`, mapping pp. 31-32 and descriptions pp. 33-40 | WHO_AM_I, control registers, status, X/Y/Z output bytes | independent recheck PASS; simulator pending | Implement simulator and run candidate-specific frozen-harness tests |
| MPU6050 | `corpus/data/raw_pdf/InvenSense/MPU6050.pdf`, plus `corpus/data/raw_pdf/InvenSense/MPU-6000-Register-Map1_mirror.pdf`, RM-MPU-6000A-00 Rev. 4.2 | WHO_AM_I, power, sampling, filter, gyro/accel configuration and accelerometer output MVP | independent recheck PASS; simulator pending | Implement simulator and run candidate-specific frozen-harness tests |

## Admission rule

Do not copy any draft into `d2d/ir/` until two reviewers independently confirm: register address, access type, reset value, field bit range, and any read side effect. For stateful devices, add at least one explicit black-box assertion for each side effect before admission.

The MPU6050 mirror reviewed here is tracked by SHA-256 `519650CBC502A3E89DDBA6D6F115734B6C7060D451938C0DC36B6232DAAE7014`; this identifies the local artifact but does not by itself prove byte-for-byte equivalence to the official source.

## Evidence notes

- AD5592R is not a conventional byte-addressed register device. The repaired draft adds the `0x5AC` software-reset key, marks reserved command-data bits as `UNSPEC`, and keeps DAC write/readback framing out of the MVP until the frozen harness can represent it without changing the interface.
- LIS3DH has a clear byte register map. The repaired draft adds I2C/SPI framing metadata, fixed-default `UNSPEC` regions, runtime annotations for status/output registers, and excludes invalid self-test encoding and BDU/BLE pair semantics from direct-register scoring.
- MPU6050 now has a local 46-page Revision 4.2 mirror and an official InvenSense/TDK URL recorded in the draft. Its 8-bit `PWR_MGMT_1` reset is corrected to `0x40`; the mirror, checksum and register-level claims still require independent confirmation.

## Next review action

The independent sign-off and post-repair recheck are archived at `_setup/ir_drafts/INDEPENDENT_IR_REVIEW_SIGNOFF.md` and `_setup/ir_drafts/POST_REPAIR_RECHECK.md`. Implement simulators for the three source-approved candidates and run candidate-specific frozen-harness tests before promoting any candidate into `d2d/ir/`.
