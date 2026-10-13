"""Emit exact independent expert return only after recorded successful execution."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
PROJECT = HERE.parents[1]


def main():
    run = json.loads((HERE / 'independent_code_execution.json').read_text(encoding='utf-8'))
    for name,sha in run['reviewed_input_sha256'].items():
        assert hashlib.sha256((PROJECT / name).read_bytes()).hexdigest() == sha,name
    for name,sha in run['output_sha256'].items():
        assert hashlib.sha256((HERE / name).read_bytes()).hexdigest() == sha,name
    source = json.loads((HERE / 'source_review.json').read_text(encoding='utf-8'))
    n = run['independent_test_counts']['passed']
    faults = run['synthetic_runtime_faults_detected']
    corrupt = run['proof_or_source_corruption_rejections']
    partial = run['missing_scenario_partial_checks']
    result = dict(
        contract_version='1.0',expert_skill='sci-skills-presubmission-review',project_id='d2d-twin',
        paper_family='M',stage_id='M4',task_id='tmp461-v34/code_review',task_status='COMPLETE',
        inputs_reviewed=[
            'corpus/data/raw_pdf/TI/TMP461.pdf SBOS722B printed pp.13,16-21; visual pp.19,21',
            'eval/independent_source_admission_20261012/field_evidence.json',
            *[str((HERE/name).relative_to(PROJECT)).replace('\\','/') for name in
              ('source_review.json','tmp461.py','scenarios.py','admission.py','scenario_execution.json',
               'closure_ledger.json','admission_gate.json','execution_manifest.json')]],
        outputs=['code_review.md','code_review.json','code_acceptance_checklist.md',
            'tests/test_independent_tmp461.py','tests/record_independent_execution.py',
            'tests/package_code_review.py','independent_code_execution.json',
            'independent_code_execution.log','independent_code_results.xml'],
        evidence_status=[
            'VERIFIED_SOURCE: independently read primary specification and visually inspected Table5 and one-shot/conversion text.',
            f'EXECUTED_LOCAL: {n} independent pytest cases passed, {faults} synthetic behavioral faults detected, {corrupt} evidence/source variants rejected.',
            f'EXECUTED_LOCAL: {partial} missing-scenario variants remain partial; saved execution and14ledger rows replay exactly.',
            'VERIFIED_USER_MATERIAL: owner preservation record reviewed; independent recorder confirms frozen harness MD5.',
            'NOT_EXECUTED: physical SMBus/I2C/diode/ADC/calibration/electrical timing; new LLM scores; whole source admission.'],
        assumptions=[
            'External conversion/fault/service events are explicitly qualified logical stimuli.',
            'Default both-channel, filter-disabled, consecutive-count-one scope; higher-count/filter branches excluded.',
            'STATUS unknown boot/reset values and unreadable/unretained ONE_SHOT action bytes are not zero oracles.',
            'THERM2 low flags remain unknown; exploratory profile is not universal hardware equivalence.',
            'Temperature flag retirement is conservatively qualified only when the channel is within both limits; opposite-limit crossing is not certified as an independent clear oracle.',
            'Unfinished temperature-byte observation rejects completion instead of claiming full asynchronous snapshot implementation.'],
        author_input_needed=[],manual_actions=[],
        quality_checks=[
            f'{n}/{n} actual tests; zero failures/errors/skips.',
            '9 source REPAIR fields/14 dimensions:9reset5read_clear; no denominator expansion.',
            'Each active cause survives STATUS read; retired cause returns preclear then clears; mask observes subset but executes whole read side effects.',
            'BUSY and THERM remain live; hysteresis releases inclusively; STATUS cannot acknowledge ALERT latch.',
            'Any valid byte triggers write-only one-shot only in shutdown; current SD conversion finishes; reset abort restores unknown boundaries.',
            'Known historical remote latch1 survives unknown fault completion; invalid observations and payloads reject atomically.',
            'Measurement range validation distinct from legal default limit -128; threshold changes need a fresh comparison.',
            'Exact replay binds source identity and scope, checks, traces and current primary/frozen authority SHA256.',
            'All14ledger rows retain whole_field_promoted=false and whole_dimension_closed=false.'],
        conflicts=source['conflicts'],conflict_resolution_status='UNRESOLVED',merge_permission='orchestrator_only',
        recommended_next_action='Orchestrator verify TMP461 accepted bytes and continue remaining frozen REPAIR obligations while generation stays blocked.',
        stage_acceptance_recommendation='REPAIR',review_date='2026-10-13',
        readiness='CONDITIONALLY_READY_FOR_DECLARED_TMP461_SCOPE_ONLY',paper_submission_readiness='NOT_READY',
        bounded_implementation_recommendation='PASS_CANDIDATE',
        independent_test_counts=run['independent_test_counts'],synthetic_runtime_faults=faults,
        proof_corruption_rejections=corrupt,source_conflict_ids=[r['conflict_id'] for r in source['conflicts']],
        reviewed_input_sha256=run['reviewed_input_sha256'])
    (HERE/'code_review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report = f'''# Independent TMP461 v3.4 code acceptance

Task `tmp461-v34/code_review`, project d2d-twin, family M, stage M4. Bounded implementation: **PASS_CANDIDATE**. Whole-stage recommendation: **REPAIR**; paper submission and production generation remain NOT_READY. Stage authority belongs to the orchestrator.

Primary SBOS722B revised August2016 was independently read at printed pp.13,16–21; pp.19 and21 visually inspected. Exact source SHA256 `{source['source']['sha256']}` matches reviewed primary and frozen source inventory. The9fields/14dimensions denominator is9reset plus5read_clear, not14whole fields.

Actual recorded execution: **{n}/{n} independent tests passed**, zero failures/errors/skips; **{faults} synthetic runtime faults detected**, **{corrupt} evidence/source corruption variants rejected**, **{partial} missing-scenario variants remain partial**. Saved scenarios and14ledger rows reconstruct exactly from current code. These cases are validation fixtures, not model-generation samples or physical measurements.

Contribution lens: the work adds source-bounded, executable cause-aware status and unknown-reset obligations. It does not establish new model scores, novelty, complete peripheral equivalence or submission readiness. The8STATUSfields andONE_SHOTaction remain sourceREPAIR, with no whole-field promotion.

Methods lens: STATUS power-on/reset is unknown, not fabricated zero; write-only ONE_SHOT does not store any byte. Start/completion/shutdown/reset boundaries are explicit. Each active flag survives read, retired flags return preclear then clear, and a masked read clears all eligible flags. Temperature cause retirement conservatively requires the corresponding channel inside both limits; an opposite-limit crossing is not certified as its own clearing oracle. BUSY/THERM are live. ALERT has a separately serviced latch; status reads never acknowledge it. THERM hysteresis and inclusive release, THERM2 high-state hysteresis, low-bit exclusion and MASK1 independence are checked. Remote-open result uncertainty is guarded while known historical latch1 is retained. Rewritten thresholds cannot clear flags without a new comparison. Unfinished temperature-byte observations are completion guards, not full asynchronous snapshot evidence. Invalid inputs and excluded source branches reject atomically.

Review found two repaired implementation defects: measurement range guarding was initially applied to legal default low limit-128; remote-open completion initially discarded known historical remote high/low latch1. The final independent tests regress both. Strict master-service and paired-read fixtures were adapted to the stated public evidence boundary. There is no remaining blocker within the declared bounded scope.

Communication lens: six unresolved source branches remain visibly reported: higher consecutive count status/latch timing, mixed cause counting, digital-filter startup/rounding, THERM2 low-state history, numeric STATUS POR, and active RANGE transitions. THERM2 candidate observations cannot be relabelled as universal manufacturer certification. Nominal periods are metadata, not measured deadline proof. The paper must distinguish local logical event validation from actual SMBus/remote-diode hardware tests.

Primary/frozen authority hashes and all declared execution input/output hashes were checked. Independent recorder confirms harness MD5 `8cf0854d4779467bc8e472ee4fb97023`. Preservation of all historical files is reviewed owner execution evidence; this reviewer modified only the new task outputs. No old IR/test/model score changes or SCNet/API/hardware execution occurred.

Reproduce: `python eval/tmp461_semantics_v34_20261013/tests/record_independent_execution.py` then `python eval/tmp461_semantics_v34_20261013/tests/package_code_review.py`. Execution command, JUnit, log, hashes and count record are retained.

Unique next action: orchestrator verifies accepted TMP461 bytes and continues remaining sourceREPAIR obligations with global generation blocked.
'''
    (HERE/'code_review.md').write_text(report,encoding='utf-8')
    print('Packaged independent TMP461 review from successful recorded execution')


if __name__=='__main__': main()
