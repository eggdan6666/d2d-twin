# INA219 independent source-derived acceptance checklist

Read directly: SBOS448G, printed pp. 10, 12–13, 17–24. This checklist predates the implementation review.

1. Table 2 p.18 specifies CONFIG 399F, CALIBRATION/CURRENT/POWER zero; BUS and SHUNT reset are measured quantities without a fixed numeric reset. Full BUS and SHUNT cold reads must reject rather than invent zero.
2. Figure 24 p.23 makes BUS bits15:3 voltage, bit1 CNVR, bit0 OVF. Bit2 is a dash without a fixed reset or preservation oracle. Numeric full-word BUS must remain unavailable; mask 0xFFFB can become available only after qualified completion.
3. CALIBRATION FS0 is explicitly fixed zero in Figure27 footnote, p.24. This does not establish zero for BUS reserved bit2.
4. RST requests a system reset, self-clears and restores documented defaults (Table3 p.19). An explicit reset_completed qualification is required; pending state cannot promise an immediate reset, reset-bit readback or elapsed time.
5. CNVR is set after conversions, averaging and multiplications complete (pp.10/23), not merely conversion_started. External qualified completion is not an ADC/timing test.
6. A changed active mode clears CNVR; MODE0 and MODE4 writes do not. Same-active-mode writes are disputed: p.10 says any CONFIG write; p.23 says a new mode. Main policy must preserve the ambiguity.
7. Power read clears CNVR (p.23). p.10 instead says nonexistent Status read and convert-pin trigger. Preserve this conflict and label any selected named-register policy as source-conditioned.
8. OVF requires qualified current/power range evidence. It is not a voltage-range flag. CALIBRATION math, signed rounding and actual overflow prediction remain outside scope unless independently specified and tested.
9. Test malformed types and out-of-profile events atomically, with unchanged state and trace. Tests may not hard-code the old prototype's fabricated reset or reserved-bit policy.
10. Replayed source and runtime evidence must bind exact expert identity, source hashes, six fields/seven dimensions and execution kind. Missing evidence remains partial. Every whole_field_promoted and whole_dimension_closed stays false.

Independent review readiness: pending actual implementation, fault-oracle runs and evidence replay.

Primary next action: execute independent oracles against the bounded INA219 runtime and preserve unresolved source clauses.
