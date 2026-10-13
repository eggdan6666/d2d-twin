# INA219 independent primary-source review

Status: COMPLETE / recommendation REPAIR. Scope:6fields7repairdimensions. No whole-field promotions.

## 1. Bibliographic position

TI INA219 manufacturer datasheet SBOS448G, August2008/revisedDecember2015. Full local38page PDF including newer package addenda. This is register-source review, not a research-paper novelty review.

## 2. Research question

Can six REPAIR fields/seven repair dimensions become safe bounded logical assertions without inventing POR measurement values or resolving conflicting prose by fiat?

## 3. Background route

Frozen independent audit records20chips572fields. INA219 subset independently rechecked against manufacturer source and SHA-bound ledger.

## 4. Unresolved pain point

BUS/SHUNT measurement POR unknown; reserved bit2 unknown; reset pending timing unknown. CNVR read-clear prose conflicts.

## 5. Core insight

An exclusion/unknown guard is a legitimate repaired assertion boundary. Passing that guard is not a numeric hardware guarantee or a whole-field promotion.

## 6. Method overview

Extract complete PDF; inspect pin list, conflicting CNVR prose, reset summary, register diagram and ADC tables; verify exact PDF/ledger hash and field/dimension identity.

## 7. Mechanism logic

Reset request and qualified reset completion are separate. CNVR completion follows all averaging/multiplication. Qualified OVF set is separate from computing arithmetic overflow. Ambiguous reads erase CNVR knownness in common source.

## 8. Formulas and assumptions

BUS code is rawBD times4mV; SHUNT encoded signed word times10uV. Current=SHUNT×CAL/4096 and Power=CURRENT×BUS/5000 are source equations, but rounding, clipping and signed power histories remain outside this task. No physical conversion accuracy inferred.

## 9. Material and benchmark

Manufacturer PDF SHA256 58004eda854d07478e6fc6f4398c114f60a3bcf18d4877471c7c1a306d1fa1cb. Frozen ledger SHA256 0905059f5f981f89137533d8b6f34d33cde5b673a05707c6b7141d521bb54711. Six fields7dimensions, not a new model benchmark.

## 10. Design and validation

Recommend dirty-reset completion/unknown masks; BUSreserved exclusion; all16 ADC code aliases; CNVR pre/post ambiguous read; same-mode active rewrite unknown; qualified overflow set. Implementation/testing not executed by source reviewer.

## 11. Experiment-to-claim chain

No physical experiment performed. Exact claim IDs and printed/PDF page locators in source_review.json. All runtime results require independent later execution.

Calibration scope clarification (independent recheck2026-10-14): p12 section8.5 and p18 Table2 footnote2 support CURRENT/POWER0 in the pre-first-programming history following POR or qualified reset completion. They do not specify immediate output clearing when previously programmed nonzero CAL is later written0. Such a write is not itself a completed ADC/multiplication or reset event. Keep CURRENT/POWER unknown after later clearing until qualified reset in this bounded common profile. This is a conservative scope restriction, not an official erratum and not a new repaired field/dimension.

## 12. Conclusion boundary

SOURCE_FACT: documented defaults and reset completion; SOURCE_OMISSION: measurement POR/reserved value; CONFLICTING_SOURCE: CNVR read rule. Whole-field promotion0; formal input not admitted.

## 13. Author-stated limitations

Datasheet electrical characteristics/ADC scaling do not certify proposed logical emulator. Application examples are not TI component specifications (p25).

## 14. Critical assessment

p10 names nonexistent Status register and convert pin; p23 Power clear differs. These are recorded contradictions, not claimed official errata. No candidate branch may silently replace the main common profile.

## 15. Reusable knowledge

Separate storage from knownness, source uncertainty from implementation failure, supporting dynamic clauses from repaired denominator, qualified events from measured hardware behavior.

## 16. Testable follow-up

After local bounded verification, resolve CNVR rules through official clarification or controlled hardware observations before broader promotion. No innovation claim without wider literature search.

## Claim-level unresolved conflicts

**INA219-C-CNVR-READ**: CNVR clear read register. UNRESOLVED; common profile numeric CNVR valid only before ambiguous BUS/POWER read; after read mark unknown. register_detail_candidate POWER clear remains candidate. Locators: p10 section8.3.1, p18 Table2, p23 section8.6.3.2

**INA219-C-CNVR-SAME-MODE**: CNVR on same active-mode CONFIG write. UNRESOLVED; changed active modes clear is common; same-mode active rewrite invalidates CNVR. Trigger start is supported independently. Locators: p10 section8.3.1, p23 section8.6.3.2

**INA219-C-CONVERT-PIN**: Single-shot convert pin and Status register mentioned in general prose. UNRESOLVED; do not invent convert-pin API or label possible copied prose an official erratum. Locators: p3 Pin Functions, p9 section8.3.1, p10 section8.3.1, p18 Table2

**INA219-C-RESET-PENDING**: Reset-in-progress readback and latency. UNRESOLVED; explicit qualified reset_completed event, no numeric reads while pending. Locators: p19 Table3

**INA219-C-BUS-RESERVED**: BUS reserved bit2 value and software policy. UNRESOLVED; knownmask bit2 zero means exclusion, not bit value0. No write-persistence/value oracle. Locators: p18 Table2, p23 Figure24

**INA219-C-OVF-CLEAR-ARITHMETIC**: OVF clearing and out-of-range current/power representation. UNRESOLVED; certify qualified overflow sets1 only; overflowFalse/clearing, arithmetic overflow representations, rounding and signed power excluded. Locators: p12 Equations4-5, p23 OVF and Current/Power definitions

**INA219-C-SEQUENCE-ABSTRACTION**: ADC/average/multiplication completion supplied as logical event. UNRESOLVED; only qualified supplied settled result; excludes sample scheduling, incomplete-average results, analog accuracy and I2C electrical behavior. Locators: p9 section8.3.1, p10 section8.3.1, p20 Tables5-6, p23 CNVR

Primary next action: Implement and independently execute INA219 bounded common-source reset/unknown guards while keeping formal generation input NOT_ADMITTED.
