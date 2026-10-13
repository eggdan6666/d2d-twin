# Independent TMP126 bounded acceptance checklist

Reviewer task `tmp126-v32/code_review`; project `d2d-twin`, family M, stage M4. Source inspected directly: local TI TMP126 SNIS209C, July 2021 revised June 2022; SHA-256 `6d9bab59b2814422d7bc1dff8fbd203df26e92ee40075b613c1f1fbb59eddfef`, 49 PDF pages. Printed pages equal PDF page numbers in the inspected section.

- Printed pp27–28 Table 8-7: exercise nonzero CRC/Slew/THigh/TLow/Data_Ready flags (mask `0xA7`) and live status bits (`0x58`) separately. Read returns preclear flags and clears only flags under the qualified transaction. Live bits must survive read. No zero-only proof accepted.
- Printed p27 introductory restriction: a single register read without auto increment clears status. Auto increment and repeated transactions are excluded from positive clear proof. Preserve the revision-history inconsistency in source review.
- Printed p28 Table 8-7 and p14 §8.4.1: temperature-result read clears Data_Ready only; other flags and live status remain.
- Printed p16 §8.4.4.1: comparator-to-interrupt change immediately clears Alert_Status and resets logical ALERT. Same-mode writes must not manufacture this transition.
- Printed p29 Table 8-8: Int_Comp `0=interrupt`, `1=comparator`; p17 prose conflicts and is not silently corrected as an official erratum.
- Printed p15 §8.4.3, p29 Table 8-8: One_Shot always reads zero, starts/restarts conversion, discards incomplete conversion, completes with Mode=1 and Data_Ready=1. AVG=1 requires eight conversions, including one-shot. Exact average arithmetic needs its declared digital input scope and exclusions.
- Printed p29 Table 8-8: conversion period codes 0..7 map to nominal 6 ms, 31.25 ms, 62.5 ms, 125 ms, 250 ms, 500 ms, 1 s, 2 s. This is metadata, not measured physical timing.
- Invalid event/write payloads must reject atomically, without changing runtime state. SPI frames, CRC generation, analog measurements and physical time are outside the bounded digital model.
- Admission must bind the original eight REPAIR-field identities and dimensions, accepted source advice, PDF hashes and trace/check identities, and independently replay recorded scenarios. Fabricated equal actual/expected values or misplaced source claims must fail.
- Whole-field promotion, whole-dimension closure and whole-project production admission remain false. No historical model score is recomputed in this task.

This checklist precedes implementation review; execution results are recorded separately after the runtime exists.
