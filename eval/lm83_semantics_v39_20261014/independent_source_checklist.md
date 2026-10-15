# LM83 v39 independent source checklist

Authored from original PDF and pinned Linux source before reading any implementation or tests. Expert: sci-skills-paper-deep-reading; project d2d-twin, M4, task lm83-v39/source_review. Source review is not board validation.

1. Freeze eight original field identities with overall REPAIR; selected dimensions are eight CONDITIONAL read_clear rules. There are zero REPAIR dimensions. Retain the other 24 CONDITIONAL rules and zero whole-field promotions.
2. Check SR1@0x02: D2CRIT bit1, D2RHIGH bit4, LCRIT bit0, LHIGH bit6; SR2@0x35: D1CRIT bit0, D1RHIGH bit7, D3CRIT bit1, D3RHIGH bit4.
3. Read SR1 clears only SR1 selected flags; read SR2 clears only SR2 selected flags. Preserve untouched register identity/value. Do not certify the other three OPEN fields through this eight-field task.
4. Enforce SR1 reserved mask 0xA8 and SR2 mask 0x48. Do not treat named OPEN bits as reserved.
5. Report pre-clear state, then apply clear, then repeat read with no intervening qualified conversion. Pre-clear read ordering is an explicit transaction abstraction inferred from the diagram, not timing measured on silicon.
6. Admit only the conflict-safe condition: selected latched flag, a completed conversion retiring its fault, then a same-register read, and no new corresponding conversion between observations. HIGH retirement is <= corresponding HIGH; CRIT retirement is strictly < T_CRIT.
7. Keep persistent-fault figure_clear as a separately labelled source interpretation. Figure 6 depicts clear on read while fault remains and pin remains asserted, but §1.3 prose puts flag reset behind below-threshold condition. Preserve C01 unresolved; do not mark this interpretation universal manufacturer fact.
8. After figure_clear, sample alone does not reassert; only qualified completion of the corresponding channel with over-limit converted result can reassert. Unrelated channels and mere host reads do not act as conversions. A conversion may happen arbitrarily close to a read: no positive minimum delay is promised.
9. With stable thresholds, unchanged mask/inversion, output enabled, and an established persistent over-limit converted result, a read alone does not release the asserted output. Global pins aggregate contributors; no release if another qualified source remains. Masked outputs and INT inversion are separate cases.
10. Do not silently equate CRIT equality with below. Retaining an already asserted CRIT at equality is a conservative profile assumption; no measured boundary evidence exists.
11. History order (acknowledge read before retiring conversion versus retiring conversion before acknowledge) is not fully defined by source prose/diagrams for all combinations. Label the implemented acknowledgement-history profile; limit certified cases to retiring conversion then read.
12. Timing metadata must retain electrical table 460 ms typical / 600 ms maximum under table operating conditions, §1.1 approximately 480 ms round / approximately 120 ms per channel, and §1.2 approximately 60 ms from sample to conversion completion. Never 'completion + 60 ms'. These are source metadata, not model measurements.
13. Note 10 ties the all-temperature timing specification to temperature data updates, and reads yield last result independent of conversion state. Do not report every flag/pin event bound as universally 0..600 ms without phase, continuously running conversion, stable operating conditions and profile assumptions.
14. Linux source corroborates addresses, field maps, volatile statuses, two separate reads and reserved masks; it does not validate physical flags-under-fault, pin latch or timing.
15. Preserve formal Gold, old Harness, frozen ledger and protected files; this expert writes only its sandbox. Any source review passes are advice to the orchestrator.

Evidence locators: PDF5/printed4 conversion-time table; PDF9/printed8 Notes6/7/10 and §1.1; PDF10/printed9 §1.2–1.4 Figures4–7 (visually inspected); PDF11/printed10 §1.4; PDF12/printed11 §1.9; PDF14/printed13 §2.1; PDF15/printed14 §2.3/§2.5; PDF16/printed15 §2.5. Linux commit 24a19b953e2a3d0ea5a8c4951a0ab8f32720c907, local SHA256 c388209e03ef84c7a3b43590e21720c6e26cac27061831550446ffee1048f680, lines50–51,82–96,150–173,201–218,250–266,378–380.

Next action: orchestrator freezes the conservative and figure-backed profiles with separate claim statuses before implementation acceptance.
