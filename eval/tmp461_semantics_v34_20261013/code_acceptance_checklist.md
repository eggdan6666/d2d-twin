# Independent TMP461 code acceptance checklist

Direct primary source: SBOS722B, printed pp. 13, 16–21; pp. 19 and 21 visually inspected.

- Table 4 STATUS POR is N/A; retain unknown bits at constructor and reset. ONE_SHOT is write-only, undefined, and does not retain any written byte.
- Any byte starts one-shot only while shutdown (p.21); BUSY follows explicit conversion start/completion; SD written during conversion takes effect after completion (pp.13,20).
- Five ALERT flags (0x7C) are sticky until STATUS read with the individual cause absent (p.19 prose). Capture preclear value. Active causes persist. Table footnote's unqualified wording remains a source conflict.
- Reading any masked part of STATUS is a whole-register read for side effects; mask only limits what is observed. BUSY and THERM bits are never read-clear.
- ALERT interrupt latch is independent from flags: STATUS read cannot acknowledge it. Qualified master device-address interrupt service resets latch only after flags reset and causes absent. No physical SMBus ARA implementation claim.
- THERM bits are live hysteresis outputs (p.19), preserving state inside the band and clearing at or below limit minus hysteresis. THERM2 ambiguous low-bit behaviors require candidate-only scope.
- Invalid byte, mask, event, profile, duplicate start, unsupported mode/encoding, unknown-state observations reject without mutations.
- Recompute scenario witness checks and traces exactly. Reject fabricated PASS, stale hashes, changed source advice, missing/extra scenarios, malformed types, relabelled source authority.
- Nine REPAIR fields and fourteen repair dimensions remain bounded clauses only. No whole-field, stage, physical, model-score, or source-authority promotion.

Primary next action: execute independent source-derived tests against the completed runtime and admission replay.
