# Independent HDC2021 code acceptance checklist

Task: `hdc2021-v33/code_review`; project `d2d-twin`; bounded M4 review.
The reviewer directly read SNAS773A (December 2019, revised June 2020), printed pages 7, 12–17, 20–31; page 12 was also rendered and visually inspected. These are source-derived digital checks, not physical measurements or new model-performance samples.

1. **Nonzero read effects:** in clear-on-read mode, return pre-read STATUS bits 7:3, then clear them. Reading any of TEMP_LOW/HIGH or HUM_LOW/HIGH clears DRDY only (p.23/Table 7-16). Do not certify blank-type STATUS reserved bits 2:0; use mask 0xF8.
2. **Threshold history:** high/low tests must first produce nonzero flags and return to neutral. Latch mode retains flags until STATUS read. Comparator updates with the current conversion, but active comparator STATUS-read behavior conflicts between p.23 and pp.14–17 figures; common profile must guard, figure candidate must be labelled exploratory.
3. **Start is not completion:** MEAS_TRIG starts a single or continuous measurement and clears when measurement starts, not when measurement completes (p.31/Table 7-38). DRDY and result updates require a separate conversion-completed event.
4. **Channel and accuracy scope:** MEAS_CONF 00 allows both channels, 01 temperature only, 10/11 are NA; TACC/HACC 11 are NA. Digital input words do not certify analog quantization, accuracy, or elapsed time. Humidity data must remain unchanged in temperature-only mode.
5. **Reset completion:** SOFT_RES self-clears after reset (p.30/Table 7-36), with nominal reset duration 3.5 ms (p.7). Do not pretend write completion is reset completion. Dirty data, thresholds, and control state must restore after a distinct reset-completed event, including TEMP_THR_L=1 and high thresholds=0xFF (p.20).
6. **Interrupt pin:** p.12 explicitly forbids OR of enabled threshold bits; highest enabled TH > TL > HH > HL wins, irrespective of which lower flag is active. DRDY/threshold tied priority is ambiguous; common profile must exclude mixed active pin outcomes. Pin output enable and polarity follow p.30; p.25 states interrupt-enable writes do not change STATUS.
7. **Atomic exclusions:** unknown events/registers, reserved encodings, invalid word types/ranges, absent/extra channel data, reset-pending access, and unsupported live reconfiguration must reject before any state or trace change. Source exclusions are prototype scope guards, not claims that silicon rejects transactions.
8. **Admission:** exact source identity and eight original REPAIR field/dimension obligations must be bound to evidence. Fake PASS, count-only records, altered traces/checks/scenario IDs and source metadata must fail replay. Missing witnesses must remain partial. No whole-field or global stage promotion.

Source conflicts retained: comparator STATUS-read context; enable/status-generation wording; humidity prose labels/addresses vs figures and register tables; reset/ADC timing is not simulated. All must remain visible in reports and closure scope.

Primary next action: execute these independent checks against the new runtime and replay gate when the implementation is available.
