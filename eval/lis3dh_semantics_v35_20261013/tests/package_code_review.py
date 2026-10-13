"""Emit an expert return only after actual independent execution and input replay."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
PROJECT=HERE.parents[1]


def main():
    run=json.loads((HERE/'independent_code_execution.json').read_text(encoding='utf-8'))
    for name,sha in run['reviewed_input_sha256'].items():
        assert hashlib.sha256((PROJECT/name).read_bytes()).hexdigest()==sha,name
    for name,sha in run['output_sha256'].items():
        assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==sha,name
    source=json.loads((HERE/'source_review.json').read_text(encoding='utf-8'))
    n=run['independent_test_counts']['passed']
    faults=run['synthetic_runtime_faults_detected']
    corrupt=run['proof_or_source_corruption_rejections']
    partial=run['missing_scenario_partial_checks']
    result=dict(contract_version='1.0',expert_skill='sci-skills-presubmission-review',
        project_id='d2d-twin',paper_family='M',stage_id='M4',task_id='lis3dh-v35/code_review',
        task_status='COMPLETE',
        inputs_reviewed=['corpus/data/raw_pdf/ST/LIS3DH.pdf DocID17530 Rev2 printed pp11,16-17,31-32,37,39-40; visual37/39',
            'eval/independent_source_admission_20261012/field_evidence.json',
            *[(HERE/name).relative_to(PROJECT).as_posix() for name in
            ('source_review.json','lis3dh.py','scenarios.py','admission.py','scenario_execution.json',
            'closure_ledger.json','admission_gate.json','execution_manifest.json')]],
        outputs=['code_review.md','code_review.json','code_acceptance_checklist.md',
            'tests/test_independent_lis3dh.py','tests/record_independent_execution.py',
            'tests/package_code_review.py','independent_code_execution.json',
            'independent_code_execution.log','independent_code_results.xml'],
        evidence_status=['VERIFIED_SOURCE: primary specification independently read; tables37-39 and46-47 visually inspected.',
            f'EXECUTED_LOCAL: {n} independent tests passed; {faults} synthetic faults detected; {corrupt} proof/source corruption variants rejected.',
            f'EXECUTED_LOCAL: {partial} missing-scenario fixtures remain partial; saved scenario and eight closure rows replay exactly.',
            'VERIFIED_USER_MATERIAL: historical preservation record reviewed; recorder independently confirms frozen harness MD5.',
            'NOT_EXECUTED: real I2C/SPI, MEMS acceleration, physical self-test, clock timing, model generation or whole source admission.'],
        assumptions=['Primary source does not define XDA reset/event oracle: known STATUS maskFE in both profiles.',
            'Main coherent sample events are supplied logical stimuli, not physical measurements; seven-bit status knowledge ends at first status/output observation.',
            'Candidate ANY aggregate and two distinct output-byte consumption rules are explicit hypotheses; no manufacturer promotion.',
            'Only settled legal mode, all-axis, FIFO/filter-bypass stimuli; ST physical responses, active mode histories and BDU pending selection excluded.',
            'Strict precision-grid stimuli are scoped input qualification rather than evidence of all physical output low bits.'],
        author_input_needed=[],manual_actions=[],
        quality_checks=[f'{n}/{n} actual tests; zero errors/failures/skips.',
            'Exactly eight source REPAIR fields/eight dimensions: oneSTaccess andsevenSTATUSreset.',
            'ST00/01/10 RW persistence preserves legal adjacent controls; ST11 rejects atomically.',
            'Cold STATUS FE zero, XDA unknown, dynamic outputs unknown; no full-byte fabrication.',
            'Controlled coherent pre-read DA/overrun witnesses; first main status/output read invalidates subsequent numeric status knowledge.',
            'Normal/high-resolution/low-power source-format scoped stimuli; malformed/outside-profile operations reject without trace/state mutation.',
            'Candidate paired reads, both orders, repeated half reads, partial masked reads, other-axis preservation and interleaved samples tested.',
            'Source PDF and frozen field authority rehashed; altered identities, claims, traces/checks and execution-kind relabelling rejected.',
            'All eight ledger rows keep whole_field_promoted=false and whole_dimension_closed=false.'],
        conflicts=source['conflicts'],conflict_resolution_status='UNRESOLVED',merge_permission='orchestrator_only',
        recommended_next_action='Orchestrator verify the accepted LIS3DH bytes and continue remaining frozen REPAIR obligations while formal generation stays blocked.',
        stage_acceptance_recommendation='REPAIR',review_date='2026-10-13',
        readiness='CONDITIONALLY_READY_FOR_DECLARED_LIS3DH_SCOPE_ONLY',paper_submission_readiness='NOT_READY',
        bounded_implementation_recommendation='PASS_CANDIDATE',
        independent_test_counts=run['independent_test_counts'],synthetic_runtime_faults=faults,
        proof_corruption_rejections=corrupt,source_conflict_ids=[r['conflict_id'] for r in source['conflicts']],
        reviewed_input_sha256=run['reviewed_input_sha256'])
    (HERE/'code_review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report=f'''# Independent LIS3DH v3.5 implementation acceptance

Task `lis3dh-v35/code_review`, project d2d-twin, family M, stage M4. Bounded implementation recommendation: **PASS_CANDIDATE**. Stage recommendation: **REPAIR**. Paper submission and formal generation remain **NOT_READY**; only the orchestrator controls stage state.

The primary ST DocID17530 Rev2 was independently read at printed pp11,16–17,31–32,37,39–40. Tables37–39 and46–47 were visually inspected; the missing XDA description/default is visibly absent in Table47. Source SHA256 `{source['source']['sha256']}` matches the reviewed source/frozen inventory. The denominator is8fields/8dimensions: CTRL_REG4.ST access plus seven documented STATUS reset bits. XDA and output fields remain outside repaired inventory.

Actual recorded execution: **{n}/{n} independent tests passed**, zero errors/failures/skips; **{faults} deliberate behavioral faults detected**, **{corrupt} proof/source corruption variants rejected**, **{partial} missing-scenario variants remain partial**. Saved scenario results and8closure rows replay exactly from accepted current code. Tests are fixtures, not LLM samples or hardware observations.

Contribution lens: source-bounded digital behavior and unknown-state guards improve executable rigor. This work does not prove a complete accelerometer twin, physical self-test, real-bus equivalence, higher model accuracy, novelty or submission readiness. No whole-field promotion occurs.

Methods lens: source ST codes00/01/10 persist with legal neighboring controls, while undefined11 is an atomic contract rejection without a silicon response claim. Initial/reset STATUS maskFE has seven documented zero bits; bit0 remains unknown in both profiles. Dynamic output bytes start unknown. Qualified coherent samples expose source-bounded pre-read DA/overrun bits and format-restricted supplied words. Main-profile output/STATUS observations invalidate subsequent STATUS knowledge because Rev2 supplies no clear trigger truth table; full cold/postevent STATUS reads cannot invent XDA. Candidate two-distinct-byte axis consumption and ANY aggregate rules are checked independently but explicitly remain hypotheses. Repeated half-reads, read-order permutations, interleaved samples, partial masks, other-axis preservation, BDU pending guards and illegal configurations are exercised. Reset is an externally qualified power-on completion event, not an invented software reset command.

Runtime subset review found no remaining defects within declared scope. Two initial mutant fixture overrides needed the runtime's optional read arguments; these were corrected before recorded acceptance. Source conflict review changed early planned full-byte sample expectations to FE-only masked witnesses, retaining XDA unknown throughout. The implementation did not need weakening to match tests.

Communication lens: six source gaps remain explicit: missingXDA, STATUS read history, partial-axis aggregation, BDU pending/release, self-test physical response and active mode history. ODR metadata discrepancy is also guarded. A rejected operation denotes no oracle in this benchmark scope, not a predicted silicon error. Precision-grid inputs, external overwrite qualifiers and post-read unknown status must remain visible in any paper claims.

Independent execution verifies primary/frozen authority hashes and all recorded input/output bytes. The frozen harness MD5 is `8cf0854d4779467bc8e472ee4fb97023`. Historical preservation is owner-recorded evidence reviewed independently; this expert modified only the new checklist/tests/report outputs. No old IR/harness/model-result changes or SCNet/API/physical execution occurred.

Reproduce with `python eval/lis3dh_semantics_v35_20261013/tests/record_independent_execution.py`, then `python eval/lis3dh_semantics_v35_20261013/tests/package_code_review.py`. The command, JUnit, log, exact hashes and counts are retained.

Primary next action: orchestrator verify these accepted bytes and continue remaining frozen REPAIR obligations while formal generation remains blocked.
'''
    (HERE/'code_review.md').write_text(report,encoding='utf-8')
    print(json.dumps({'independent_tests':n,'runtime_faults':faults,'corruption_rejections':corrupt}))


if __name__=='__main__':main()
