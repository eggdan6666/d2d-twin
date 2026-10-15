# Independent IR review sign-off

Reviewer: Codex independent IR reviewer
Date: 2026-10-10
Review scope: AD5592R / LIS3DH / MPU6050

## Sign-off matrix

| Candidate | Address/reset | Fields/access | Stateful semantics | Source identity | Decision |
|---|---|---|---|---|---|
| AD5592R | **PASS** — selectors 0x1/0x2/0x3/0x4/0x5/0x6/0xF and resets 0x000/0x000/0x000/0x000/0x000/0x0FF/0x000 match the control-register summary and detail tables (PDF pp.35-42, 50). | **PASS** — every listed functional and reserved field has the PDF bit range, default, and access policy; reserved regions are explicitly UNSPEC/set-to-zero (PDF pp.36-42, 50). | **PASS** — 16-bit SPI word, bit-15 control/DAC split, selector bits 14:11, reserved bits 10:9, and 16-clock read/write timing match the PDF; 250 microsecond reset/power-up wait, software reset key, and IO_LOCK behavior are recorded (PDF pp.25-27, 33, 39, 50-51). | **PASS** — AD5592R Rev. H, register-map pages match the local PDF (PDF pp.1, 35-52). | **PASS** |
| LIS3DH | **REPAIR** — map addresses and ordinary reset values match, but `STATUS_REG` and all six `OUT_*` registers are currently assigned reset `0x00` although the PDF map marks them `Output`; their dynamic reset is unspecified. Keep `runtime_value: true`, remove/omit those register reset assertions, and omit `OUT_* .DATA.reset` (PDF pp.31, 39-40). | **REPAIR** — listed field ranges/access/defaults match. Add an explicit unsupported/unspecified policy for undocumented `CTRL_REG1.ODR` codes `0xA-0xF`; Table 31 defines only `0x0-0x9` (PDF p.35). `CTRL_REG4.ST=11` is correctly identified as invalid/unspecified (PDF p.37). | **PASS** for the recorded fixed-bit, dynamic-output, BDU/BLE, and ST annotations; I2C/SPI bit positions and auto-increment framing are correct (PDF pp.24-30, 34, 37-40). | **PASS** — ST LIS3DH DocID17530 Rev.2 is the local PDF (PDF pp.1, 31-40). | **REPAIR** |
| MPU6050 | **REPAIR** — all listed addresses and reset values match the mirror; reserved bits in included registers are missing from the IR: `CONFIG[7:6]`, `GYRO_CONFIG[2:0]`, `ACCEL_CONFIG[2:0]`, and `PWR_MGMT_1[4]` must be represented as reserved/UNSPEC with reset 0 (PDF pp.6, 8, 13-15, 40). | **REPAIR** — functional fields and `DEVICE_RESET.read_as=0` match, but the four reserved regions above are omitted. | **REPAIR** — accelerometer `runtime_value` annotations and `DEVICE_RESET` auto-clear semantics are correct, but the candidate's note points to pp.42-43; the actual `PWR_MGMT_1` detail is on pp.40-41. The IR also has no primary-I2C frame metadata. Add the I2C START/AD+R/W/ACK/RA/DATA/repeated-START/STOP sequence and burst auto-increment rules, or explicitly mark protocol framing unsupported (supplemental local Product Specification pp.33-37). | **PASS** — local SHA-256 is `519650CBC502A3E89DDBA6D6F115734B6C7060D451938C0DC36B6232DAAE7014`; PDF p.1 identifies `RM-MPU-6000A-00`, Revision 4.2, release 08/19/2013, and pp.2-4 corroborate the same identity. | **REPAIR** |

## Field-level audit

### AD5592R — PASS

| Register | Candidate value | PDF verification |
|---|---|---|
| `DAC_RD` | `addr=0x1`, `RW`, `reset=0x0000`; `DAC_RD_EN[4:3]`, `DAC_CH_SEL[2:0]`, `RESERVED[10:5]` | Matches Table 13 and Table 15, including channel codes 000-111 and defaults (PDF pp.35-37). |
| `ADC_SEQ` | `addr=0x2`, `RW`, `reset=0x0000`; `REP[9]`, `TEMP[8]`, `ADC_CH_MASK[7:0]`, `RESERVED[10]` | Matches Table 13 and Table 16; channel bits 7:0 and repetition/temperature bits are all default 0 (PDF pp.35, 37-38). |
| `GEN_CTRL_REG` | `addr=0x3`, `RW`, `reset=0x0000`; functional bits `[9]`, `[8]`, `[7]`, `[6]`, `[5]`, `[4]`, reserved `[10]` and `[3:0]` | Matches Table 17, including IO_LOCK, ALL_DAC, range selections, and reserved set-zero policy (PDF pp.35, 38-39). |
| `ADC_CONFIG` | `addr=0x4`, `RW`, `reset=0x0000`; `ADC_PIN_MASK[7:0]`, `RESERVED[10:8]` | Matches Table 18 (PDF pp.35, 39-40). |
| `DAC_CONFIG` | `addr=0x5`, `RW`, `reset=0x0000`; `DAC_PIN_MASK[7:0]`, `RESERVED[10:8]` | Matches Table 19 (PDF pp.35, 40-41). |
| `PULLDWN_CONFIG` | `addr=0x6`, `RW`, `reset=0x00FF`; `PULL_DWN_MASK[7:0]` reset 255, `RESERVED[10:8]` | Matches Table 20: all eight pull-down bits default 1 (PDF pp.35, 41-42). |
| `SW_RESET` | `addr=0xF`, `W`, `reset=0x0000`; `SW_RESET_CODE[10:0]`, `write_key=0x5AC` | `0x5AC` is binary `10110101100`, exactly the Table 28 reset key; software reset restores all registers and I/O defaults and blocks writes for up to 250 microseconds (PDF pp.33, 50). |

Protocol and side effects: the 16-bit SPI input shift register and control/DAC split are correct: bit 15 selects control versus DAC write, control selector is bits 14:11, bits 10:9 are reserved, and the next 16 clocks carry readback after the readback selector write (PDF pp.26-27). `IO_LOCK=1` blocks later I/O configuration writes (PDF p.39). The excluded DAC/ADC readback payload formats are correctly left outside the direct-register subset, with their formats documented on pp.51-52.

### LIS3DH — REPAIR

All functional address/access/bit/default entries below match the PDF unless a repair is called out.

| Register | Candidate value | PDF verification / required action |
|---|---|---|
| `WHO_AM_I` | `0x0F`, `RO`, `0x33`, `ID[7:0]` | Exact match; fixed ID `00110011` (PDF pp.31, 34). |
| `CTRL_REG0` | `0x1E`, `RW`, `0x10`; `SDO_PU_DISC[7]`, fixed bits `[6]`, `[5]`, `[4]`, `[3:0]` | Exact match. Bits 0-6 must remain at defaults; UNSPEC plus the recorded fixed-default text is appropriate (PDF p.34). |
| `TEMP_CFG_REG` | `0x1F`, `RW`, `0x00`; `ADC_EN[7]`, `TEMP_EN[6]`, fixed `[5:0]` | Exact match (PDF pp.31, 34). |
| `CTRL_REG1` | `0x20`, `RW`, `0x07`; `ODR[7:4]`, `LPen[3]`, `Zen/Yen/Xen[2:0]` | Ranges/defaults match Table 29-31 (PDF pp.31, 35). **Repair:** Table 31 lists codes `0000` through `1001`; current IR has no policy for `1010`-`1111`. Add an `unsupported/UNSPEC` legal-value annotation or explicitly exclude those encodings from scoring (PDF p.35). |
| `CTRL_REG4` | `0x23`, `RW`, `0x00`; `BDU[7]`, `BLE[6]`, `FS[5:4]`, `HR[3]`, `ST[2:1]`, `SIM[0]` | Exact match. `ST=00/01/10` are the documented modes and `ST=11` is the undocumented/invalid row; current UNSPEC annotation is correct (PDF p.37). |
| `STATUS_REG` | `0x27`, `RO`, current `reset=0x00`, `runtime_value=true` | **Repair:** the address map gives default `Output`, not a reset byte. Correct register metadata is `runtime_value=true` with register reset omitted/unspecified; individual status flags do have default 0 in Table 47 (PDF pp.31, 39). |
| `OUT_X_L/H`, `OUT_Y_L/H`, `OUT_Z_L/H` | `0x28-0x2D`, `RO`, current `reset=0x00`, `runtime_value=true`, `DATA[7:0]` reset 0 | **Repair:** the address map marks each as `Output` and the description only defines live two's-complement left-justified data. Correct register and `DATA` field reset is omitted/unspecified; retain `runtime_value=true` (PDF pp.31, 40). |

Protocol audit: I2C addresses `0x18/0x19` and SA0 selection are correct (PDF p.25); the 8-bit sub-address MSB enables auto-increment (PDF pp.25-26). SPI bit 0 is R/W (`0` write, `1` read), bit 1 is MS (`0` fixed address, `1` auto-increment), bits 7:2 are the register address, and single transfers use 16 clocks with additional 8-clock blocks for multi-byte transfers (PDF pp.27-30). The candidate's bit-position metadata matches these rules. BDU/BLE paired-output behavior is correctly recorded as out of direct-register scoring, and no `read_as` or write key is warranted for this subset (PDF pp.37, 40).

### MPU6050 — REPAIR

| Register | Candidate value | PDF verification / required action |
|---|---|---|
| `SMPLRT_DIV` | `0x19`, `RW`, `0x00`, field `[7:0]` | Exact match (PDF pp.6, 11-12). |
| `CONFIG` | `0x1A`, `RW`, `0x00`, `EXT_SYNC_SET[5:3]`, `DLPF_CFG[2:0]` | Functional fields match. **Repair:** add reserved `[7:6]`, reset 0, UNSPEC/set-zero policy (PDF pp.6, 8, 13). |
| `GYRO_CONFIG` | `0x1B`, `RW`, `0x00`, `XG_ST[7]`, `YG_ST[6]`, `ZG_ST[5]`, `FS_SEL[4:3]` | Functional fields and defaults match. **Repair:** add reserved `[2:0]`, reset 0, UNSPEC/set-zero policy (PDF pp.6, 14). |
| `ACCEL_CONFIG` | `0x1C`, `RW`, `0x00`, `XA_ST[7]`, `YA_ST[6]`, `ZA_ST[5]`, `AFS_SEL[4:3]` | Functional fields and defaults match. **Repair:** add the table's reserved `[2:0]`, reset 0, UNSPEC/set-zero policy (PDF pp.6, 15-16). |
| `ACCEL_XOUT_H/L`, `ACCEL_YOUT_H/L`, `ACCEL_ZOUT_H/L` | `0x3B-0x40`, `RO`, `0x00`, `runtime_value=true`, byte fields `[7:0]` | Exact match. The map gives reset 0 for all registers other than 107 and 117, while p.29 defines live user-facing shadow copies updated at the sample rate; `runtime_value=true` is correct (PDF pp.7-8, 29). |
| `PWR_MGMT_1` | `0x6B`, `RW`, `0x40`; `DEVICE_RESET[7]` `RW`, `read_as=0`; `SLEEP[6]=1`, `CYCLE[5]=0`, `TEMP_DIS[3]=0`, `CLKSEL[2:0]=0` | Functional fields, reset 0x40, and auto-clear/read-as-0 reset trigger match. **Repair:** add reserved bit `[4]`, reset 0, UNSPEC; correct the candidate's page pointer from pp.42-43 to pp.40-41 (PDF pp.8, 40-41). |
| `WHO_AM_I` | `0x75`, `RO`, `0x68`; `WHO_AM_I[6:1]=52`, hard-coded `ZERO_7[7]`/`ZERO_0[0]` | Exact match: upper six address bits, AD0 excluded, bits 7 and 0 hard-coded zero (PDF pp.8, 45). |

Protocol audit: the 7-bit addresses `0x68` and `0x69` are correct (`b110100X`, AD0 selects the LSB) (PDF pp.5, 45; supplemental Product Specification p.33). **Repair:** the candidate has no protocol-frame block. For MPU6050 I2C, record START → `AD+W` (W=0) → ACK → register address → ACK → data bytes → ACK → STOP for writes; reads use START → `AD+W` → register address → repeated START → `AD+R` (R=1) → ACK/data → NACK → STOP, with burst auto-increment (supplemental Product Specification pp.35-36). MPU6050 does not support the primary SPI frame; SPI is MPU6000-only (supplemental Product Specification pp.8, 33, 37).

## MPU6050 mirror identity

The local mirror is accepted as the reproducibility artifact: its SHA-256 is exactly `519650CBC502A3E89DDBA6D6F115734B6C7060D451938C0DC36B6232DAAE7014`, and PDF p.1 states `RM-MPU-6000A-00`, Revision 4.2, release date 08/19/2013. The revision history on p.4 includes Revision 4.2 dated 08/19/2013; the register map and WHO_AM_I details are on pp.6-8 and 45. This identity check passes even though the candidate still needs the IR repairs above.

For MPU6050, record whether the local mirror with SHA-256
`519650CBC502A3E89DDBA6D6F115734B6C7060D451938C0DC36B6232DAAE7014`
is accepted as the reproducibility artifact.

**Promotion decision:** I confirm that only rows marked PASS may be copied into `d2d/ir/`. On this review, only AD5592R is eligible; LIS3DH and MPU6050 remain REPAIR.

Signature/name: Codex independent IR reviewer
