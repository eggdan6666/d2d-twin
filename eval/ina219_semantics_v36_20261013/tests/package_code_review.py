"""Exact expert return after real tests and evidence replay; no stage authority."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
PROJECT = HERE.parents[1]


def main():
    run = json.loads((HERE / 'independent_code_execution.json').read_text(encoding='utf-8'))
    for name, sha in run['reviewed_input_sha256'].items():
        assert hashlib.sha256((PROJECT / name).read_bytes()).hexdigest() == sha, name
    for name, sha in run['output_sha256'].items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == sha, name
    source = json.loads((HERE / 'source_review.json').read_text(encoding='utf-8'))
    n = run['independent_test_counts']['passed']
    faults = run['synthetic_runtime_faults_detected']
    corrupt = run['proof_or_source_corruption_rejections']
    partial = run['missing_scenario_partial_checks']
    optional = run['optional_supporting_scenario_checks']
    result = dict(contract_version='1.0', expert_skill='sci-skills-presubmission-review',
        project_id='d2d-twin', paper_family='M', stage_id='M4', task_id='ina219-v36/code_review',
        task_status='COMPLETE',
        inputs_reviewed=['corpus/data/raw_pdf/TI/INA219.pdf SBOS448G printed pp.9–13,17–24 independently read',
            'eval/independent_source_admission_20261012/field_evidence.json',
            *[(HERE / name).relative_to(PROJECT).as_posix() for name in
              ('source_review.json', 'ina219.py', 'scenarios.py', 'admission.py', 'scenario_execution.json',
               'closure_ledger.json', 'admission_gate.json', 'execution_manifest.json')]],
        outputs=['code_review.md', 'code_review.json', 'code_acceptance_checklist.md',
            'tests/test_independent_ina219.py', 'tests/record_independent_execution.py',
            'tests/package_code_review.py', 'independent_code_execution.json',
            'independent_code_execution.log', 'independent_code_results.xml'],
        evidence_status=['VERIFIED_SOURCE: original primary specification read independently before implementation.',
            f'EXECUTED_LOCAL: {n} independent tests passed; {faults} synthetic faults detected; {corrupt} proof/source corruption variants rejected.',
            'EXECUTED_LOCAL: accepted saved scenarios and seven closure rows replay exactly; source PDF and frozen authority rehashed.',
            f'EXECUTED_LOCAL: {partial} required-scenario omissions retain partial closure; {optional} optional supporting-scenario omission leaves bounded rows verified.',
            'VERIFIED_USER_MATERIAL: owner preservation record reviewed and frozen harness independently rehashed.',
            'NOT_EXECUTED: analog ADC, I2C electrical traffic, calibration arithmetic, timing, model generation and formal full-source admission.'],
        assumptions=['Logical completed-sequence and reset events are externally supplied qualifications.',
            'SHUNT/BUS cold values and BUS bit2 stay unknown; knownmask0 never asserts numeric zero.',
            'Conflicting CNVR reads and same-mode writes invalidate main knowledge; named-register detail is candidate policy.',
            'Only qualified math-overflow sets1; no fabricated no-overflow or clear promise.',
            'Previously programmed calibration cleared to0 does not restore an immediate numeric CURRENT/POWER oracle; qualified reset restores known zero.',
            'Nominal metadata and exact scoped supplied raw words do not establish physical ADC results.'],
        author_input_needed=[], manual_actions=[],
        quality_checks=[f'{n}/{n} actual tests, zero errors/failures/skips.',
            'Exactly six source REPAIR fields/seven dimensions retained without changing frozen authority.',
            'Defined defaults separated from unspecified SHUNT/BUS reset and reserved bit2.',
            'RST pending blocks numeric promises; completed reset restores only documented defaults.',
            'Calibration pre-first-programming zero guarantee is not generalized to nonzero-to-zero histories; an injected instant-zero fault is detected.',
            'CNVR whole-completion, active-mode changes, power-down/ADC-off exceptions and candidate crossread checked.',
            'Source-derived faults and altered evidence identities, traces, checks, hashes and execution kinds rejected.',
            'Every whole_field_promoted and whole_dimension_closed remains false.'],
        conflicts=source['conflicts'], conflict_resolution_status='UNRESOLVED', merge_permission='orchestrator_only',
        recommended_next_action='Orchestrator verify accepted INA219 bytes and continue remaining frozen REPAIR obligations while formal generation stays blocked.',
        stage_acceptance_recommendation='REPAIR', review_date='2026-10-14',
        readiness='CONDITIONALLY_READY_FOR_DECLARED_INA219_SCOPE_ONLY', paper_submission_readiness='NOT_READY',
        bounded_implementation_recommendation='PASS_CANDIDATE',
        independent_test_counts=run['independent_test_counts'], synthetic_runtime_faults=faults,
        proof_corruption_rejections=corrupt,
        missing_scenario_partial_checks=partial,
        optional_supporting_scenario_checks=optional,
        source_conflict_ids=[r['conflict_id'] for r in source['conflicts']],
        reviewed_input_sha256=run['reviewed_input_sha256'])
    (HERE / 'code_review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    report = f'''# Independent INA219 v3.6 implementation acceptance

Task `ina219-v36/code_review`, project d2d-twin, family M, stage M4. Bounded implementation recommendation **PASS_CANDIDATE**; stage recommendation **REPAIR**, full paper submission **NOT_READY**. Only the orchestrator may change stage state.

Original TI SBOS448G technical pp.9–13,17–24 were read independently before implementation. Source SHA256 `{source['source']['sha256']}` matches reviewed bytes. Table2 supplies CONFIG399F and CALIBRATION/CURRENT/POWER0 but no fixed numeric BUS/SHUNT reset. Figure24 supplies no reserved-bit2 value. All six REPAIR fields and seven dimensions retain the frozen inventory.

Actual recorded execution: **{n}/{n} independent tests passed**, zero errors/failures/skips, **{faults} deliberate behavioral faults detected**, **{corrupt} proof/source corruption variants rejected**. **{partial} required-scenario omissions remain partial**, while **{optional} optional metadata-support omission leaves all bounded rows verified**; these categories derive from source advice and claim mappings. The source advice, accepted scenarios and seven-row closure replay exactly. These are test fixtures and supplied logical stimuli, not hardware observations or model samples.

Contribution lens: executable unknown-state guards and conditional event semantics improve local benchmark rigor. They do not establish complete device equivalence, real-bus behavior, higher model accuracy, novelty or submission readiness.

Methods lens: BUS and SHUNT begin unknown. Reserved bit2 remains outside every numeric oracle. Explicit reset completion restores known defaults while rejecting pending reads and unsupported deadlines. CNVR completion includes the whole externally qualified conversion/averaging/multiplication sequence; modes0/4 preserve known CNVR, changed active modes clear, disputed same-mode active writes invalidate it. The conflicting p10 Status/convert-pin references are retained rather than silently treated as official errata. Main BUS/POWER reads end CNVR knowledge; the p23 POWER-clear branch is an explicitly source-conditioned candidate. OVF is based on qualified math range, never raw voltage exceeding a chosen threshold; no-overflow clearing, arithmetic rounding and signed-power outcomes remain outside scope. CAL bit0 explicitly zero is not borrowed to define BUS bit2. The pre-first-programming zero guarantee is not generalized to later nonzero-to-zero calibration writes: CURRENT/POWER remain unknown even after supplied zero-calibration completion until a qualified reset; an independent instant-zero mutant is rejected.

Communication lens: source contradictions and source omissions stay visible in the runtime and return contract. A scope guard means this benchmark has no oracle, not that silicon rejects the transaction. Logical settled register access and nominal timing metadata do not certify the source's4us write-update behavior, averaging timer, I2C framing or analog accuracy. Every whole-field and whole-dimension promotion stays false.

Execution evidence includes command, JUnit, log and input/output hashes. The frozen harness independently matches MD5 `8cf0854d4779467bc8e472ee4fb97023`. This expert edited only new checklist/tests/report outputs; no historical IR, frozen harness or model results were changed.

Reproduce with `python eval/ina219_semantics_v36_20261013/tests/record_independent_execution.py`, followed by `python eval/ina219_semantics_v36_20261013/tests/package_code_review.py`.

Primary next action: orchestrator verify accepted INA219 bytes and continue remaining frozen REPAIR obligations while formal generation remains blocked.
'''
    (HERE / 'code_review.md').write_text(report, encoding='utf-8')
    print(json.dumps({'independent_tests': n, 'runtime_faults': faults, 'corruption_rejections': corrupt}))


if __name__ == '__main__':
    main()
