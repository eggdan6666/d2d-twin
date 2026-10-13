"""Produce the exact expert return only from an actual successful recorded run."""
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
    tests = run['independent_test_counts']['passed']
    faults = run['synthetic_runtime_faults_detected']
    corrupt = run['proof_or_source_corruption_rejections']
    partial = run['missing_scenario_partial_checks']
    source_conflicts = [r['conflict_id'] for r in source['conflicts']]
    result = {
        'contract_version':'1.0','expert_skill':'sci-skills-presubmission-review',
        'project_id':'d2d-twin','paper_family':'M','stage_id':'M4','task_id':'hdc2021-v33/code_review',
        'task_status':'COMPLETE',
        'inputs_reviewed':[
            'corpus/data/raw_pdf/TI/HDC2021.pdf SNAS773A printed pp7,12-17,20-31; visually checked pp12,23',
            'eval/independent_source_admission_20261012/field_evidence.json',
            'eval/hdc2021_semantics_v33_20261013/source_review.json',
            'eval/hdc2021_semantics_v33_20261013/hdc2021.py',
            'eval/hdc2021_semantics_v33_20261013/scenarios.py',
            'eval/hdc2021_semantics_v33_20261013/admission.py',
            'eval/hdc2021_semantics_v33_20261013/scenario_execution.json',
            'eval/hdc2021_semantics_v33_20261013/closure_ledger.json',
            'eval/hdc2021_semantics_v33_20261013/admission_gate.json',
            'eval/hdc2021_semantics_v33_20261013/execution_manifest.json'],
        'outputs':['code_review.md','code_review.json','code_acceptance_checklist.md',
            'tests/test_independent_hdc2021.py','tests/record_independent_execution.py','tests/package_code_review.py',
            'independent_code_execution.json','independent_code_execution.log','independent_code_results.xml'],
        'evidence_status':[
            'VERIFIED_SOURCE: primary source directly read; original SHA-256 independently matches source review and frozen authority.',
            f'EXECUTED_LOCAL: {tests} independent tests passed; {faults} source-derived synthetic faults detected; {corrupt} corruption/relabel variants rejected.',
            f'EXECUTED_LOCAL: {partial} missing-scenario variants remain partial; saved scenario checks/traces replay exactly and eight closure rows reconstruct exactly.',
            'VERIFIED_USER_MATERIAL: reviewed owner preservation record; independent recorder separately verifies frozen harness MD5.',
            'NOT_EXECUTED: physical I2C transactions, ADC/humidity response, actual conversion/reset deadlines, new model generation, full field/source certification.'],
        'assumptions':[
            'Completed-word events are externally qualified atomic digital inputs, not ADC quantization or timing evidence.',
            'Threshold mapping follows explicit table/figure candidate preconditions where prose conflicts.',
            'INT_MODE=0 common read-clear; comparator read preservation is exploratory only.',
            'Unknown reserved/status bits are masked or excluded, not assumed zero.',
            'Deterministic replay binds declared evidence to trusted local code; it is not remote attestation.'],
        'author_input_needed':[],'manual_actions':[],
        'quality_checks':[
            f'{tests}/{tests} actual independent pytest cases, zero failures/errors/skips.',
            'Nonzero STATUS0xF8 returned before clear; each result-byte read clears DR only.',
            'MEAS_TRIG self-clear at START is distinguished from DATA_READY at COMPLETION.',
            'Temperature-only retains humidity; seven CC encodings require an initial trigger before periodic events.',
            'Dirty reset completes separately and restores nonzero TEMP_THR_L=1 and high thresholds=255.',
            'Pin priority uses highest enabled TH>TL>HH>HL, rather than OR of active lower flags; mixed DR tie guarded.',
            'Source identity/authority, scenario identity, checks/trace/type integrity and accepted source advice bound by replay.',
            f'{faults} fault/oracle pairs detect meaningful counterimplementations; {corrupt} corrupted/relabelled evidence variants rejected.',
            'Eight REPAIR fields/eight dimensions remain whole_field_promoted=false and whole_dimension_closed=false.',
            'Execution manifest hashes match current input/output bytes; frozen harness MD5 remains8cf0854d4779467bc8e472ee4fb97023.'],
        'conflicts':source['conflicts'] + [{
            'conflict_id':'GLOBAL_PRODUCTION_ADMISSION_OPEN','type':'SCOPE',
            'claim':'Eight bounded HDC2021 obligations do not admit20chips/572fields or make the manuscript submission-ready.',
            'source_or_locator':'admission_gate.json and independent source signoff',
            'resolution':'Retain production_generation_ready=false and stage authority with orchestrator.'}],
        'conflict_resolution_status':'UNRESOLVED','merge_permission':'orchestrator_only',
        'recommended_next_action':'Orchestrator verifies exact accepted HDC2021 bytes and handles TMP461 nine REPAIR fields/fourteen dimensions with global admission retained.',
        'stage_acceptance_recommendation':'REPAIR','review_date':'2026-10-13',
        'readiness':'CONDITIONALLY_READY_FOR_DECLARED_HDC2021_SCOPE_ONLY',
        'paper_submission_readiness':'NOT_READY','bounded_implementation_recommendation':'PASS_CANDIDATE',
        'independent_test_counts':run['independent_test_counts'],'synthetic_runtime_faults':faults,
        'proof_corruption_rejections':corrupt,'source_conflict_ids':source_conflicts,
        'reviewed_input_sha256':run['reviewed_input_sha256'],
    }
    (HERE / 'code_review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report = f'''# Independent HDC2021 v3.3 code acceptance

Task `hdc2021-v33/code_review`, project `d2d-twin`, family M, stage M4. **Bounded implementation: PASS_CANDIDATE. Whole-stage recommendation: REPAIR. Production generation and paper submission remain NOT_READY.**

The source-derived checklist was authored before runtime review. Original SNAS773A revised June2020 was directly read at printed pp7,12–17,20–31 and visually inspected at pp12,23. Its independently computed SHA-256 is `{source['source']['sha256']}`. Six primary-source conflicts remain unresolved; no official erratum is asserted.

Actual recorded local execution: **{tests}/{tests} independent tests passed**, with zero failures/errors/skips. **{faults} synthetic runtime faults** were caught by source-derived oracles; **{corrupt} fabricated/corrupted/relabelled evidence variants** were rejected. **{partial} missing-scenario variants** remained partial. These are validation fixtures, not LLM-performance samples or physical measurements. The twelve saved owner scenarios exactly replayed, the eight-row closure ledger reconstructed exactly, and all accepted manifest input/output SHA-256 values matched current bytes.

Contribution lens: the bounded improvement makes eight known HDC2021 semantic obligations independently executable. It supplies event and evidence checks; it establishes neither new model performance nor complete peripheral equivalence. Novelty or submission-level contribution was not accepted by this specialist review.

Methods lens: nonzero latched STATUS is returned before clear; data reads clear DR only. Start/request/completion/reset boundaries are distinct. Trigger clearing at measurement start cannot be mistaken for conversion completion. Channel retention, continuous arming, dirty reset and nonzero defaults are checked. Unknown bit observations and malformed payloads reject atomically. Priority pin tests distinguish highest enabled threshold from incorrectly OR-ing lower active flags. Source authority is rehashed and evidence content exactly replayed; a count-only PASS cannot pass. Reviewed code has no remaining blocker within the declared bounded scope.

Communication lens: status generation when disabled, comparator STATUS reads, threshold address/channel prose and mixed DR/threshold priority are explicitly source-conflicted. Common positive latch tests use relevant enables set. Table/figure threshold preconditions and comparator policy remain candidate interpretations. Comparator/threshold exploratory witnesses cannot be relabelled as unconflicted manufacturer facts. Nominal timing metadata, event checks and candidate observations must remain distinct in any paper revision.

Issue repaired during review: standalone closure now asserts expert contract identities in addition to canonical accepted-file matching. Accepted package bytes are also bounded by execution/artifact manifests; neither is remote attestation. No fabricated physical evidence or silent source promotion was found. Early fixture signatures were adapted to the final public read API; they are not implementation defects.

Remaining major limitation at source_review.json/admission_gate.json: six manufacturer-source contradictions, no actual I2C frame validation, no ADC/calibration/elapsed-time test, and excluded peak-detector behavior. Minimum repair is to retain these scope restrictions and continue unresolved field obligations. Whole fields, all572source fields and full M4 are not promoted.

The preservation record is reviewed owner-run evidence. The independent recorder separately confirms frozen harness MD5 `8cf0854d4779467bc8e472ee4fb97023`. No original IR or historical model result was modified or rescored by this review.

Reproduce actual independent evidence with `python eval/hdc2021_semantics_v33_20261013/tests/record_independent_execution.py`. Executed command, JUnit XML, log, input hashes and exact counts are retained locally.

Unique next action: orchestrator verifies the accepted HDC2021 bytes and handles TMP461 nine REPAIR fields/fourteen dimensions while keeping global generation blocked. This bounded continuation needs no author hardware purchase.
'''
    (HERE / 'code_review.md').write_text(report,encoding='utf-8')
    print('Packaged independent review from successful recorded execution')


if __name__ == '__main__':
    main()
