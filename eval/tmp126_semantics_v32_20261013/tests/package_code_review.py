"""Package a bounded expert return from actually recorded local acceptance."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
PROJECT = HERE.parents[1]


def main():
    run = json.loads((HERE / 'independent_code_execution.json').read_text(encoding='utf-8'))
    for name, sha in run['reviewed_input_sha256'].items():
        assert hashlib.sha256((PROJECT / name).read_bytes()).hexdigest() == sha, name
    result = {
        'contract_version':'1.0', 'expert_skill':'sci-skills-presubmission-review',
        'project_id':'d2d-twin', 'paper_family':'M', 'stage_id':'M4',
        'task_id':'tmp126-v32/code_review', 'task_status':'COMPLETE',
        'inputs_reviewed':[
            'corpus/data/raw_pdf/TI/TMP126.pdf SNIS209C printed pp2,14-17,21,26-32',
            'eval/independent_source_admission_20261012/field_evidence.json',
            'eval/tmp126_semantics_v32_20261013/source_review.json',
            'eval/tmp126_semantics_v32_20261013/tmp126.py',
            'eval/tmp126_semantics_v32_20261013/scenarios.py',
            'eval/tmp126_semantics_v32_20261013/admission.py',
            'eval/tmp126_semantics_v32_20261013/scenario_execution.json',
            'eval/tmp126_semantics_v32_20261013/closure_ledger.json',
            'eval/tmp126_semantics_v32_20261013/admission_gate.json',
            'eval/tmp126_semantics_v32_20261013/execution_manifest.json',
            '_setup/run_tmp126_v32.py'],
        'outputs':['code_review.md','code_review.json','code_acceptance_checklist.md',
                   'tests/test_independent_tmp126.py','tests/record_independent_execution.py',
                   'tests/package_code_review.py','independent_code_execution.json',
                   'independent_code_execution.log','independent_code_results.xml'],
        'evidence_status':[
            'VERIFIED_SOURCE: directly read original SNIS209C pp2,14-17,21,26-32 and verified PDF SHA256.',
            'EXECUTED_LOCAL: 121 independent tests passed; 13 synthetic runtime faults detected; 28 corrupted execution/source variants rejected.',
            'EXECUTED_LOCAL: ten saved scenarios exactly replay; eight bounded ledger rows reconstruct exactly; all recorded input/output SHA256 verified.',
            'VERIFIED_USER_MATERIAL: preservation record states old12563 files/prior1390 archived payloads unchanged; independently checked the frozen harness MD5.',
            'NOT_EXECUTED: physical SPI frames, actual CRC computation, electrical timing, analog measurements, new model generation/rescoring or global production admission.'],
        'assumptions':[
            'Completed-conversion and qualified CRC/slew events are declared atomic digital inputs, not physical measurement or bus proof.',
            'Eight-sample averaging is tested only for exact integral signed14 code means; unknown rounding is excluded atomically.',
            'Common clear proof is single-word/no-increment; disputed body_candidate burst behavior is explicitly exploratory.',
            'Int_Comp table encoding and low-limit interpretation remain declared candidate decisions with unresolved source contradictions.',
            'Deterministic replay establishes local reproducibility with trusted code, not remote attestation.'],
        'author_input_needed':[], 'manual_actions':[],
        'quality_checks':[
            '121/121 local independent pytest cases, zero failure/error/skip.',
            'Nonzero0xA7 flag return-before-clear and0x58 live-status preservation distinguish incorrect readclear implementations.',
            'TEMP clears DR only; comparator1tointerrupt0 clears nonzero whole status and logical ALERT.',
            'AVG8, automatic MODE1, readzeroONE_SHOT, restart/discard, shutdownabort and exactsignedmean checked.',
            'Invalid words/events/register identities and ambiguous transactions reject without state mutation.',
            '13 source-derived oracle/fault pairs each pass reference and reject deliberate synthetic implementation fault.',
            '28 false/corrupt execution/source variants rejected; eight missing required scenarios yield PARTIAL, never promotion.',
            'Ten saved scenarios/85 checks include8 nominalmetadata and2 exploratory checks, not85 independent physical measurements.',
            'Eight original REPAIR fields/eight dimensions remain whole_dimension_closed=false and whole_field_promoted=false.',
            'Execution input/output hashes match current bytes; frozen harness MD5 is8cf0854d4779467bc8e472ee4fb97023.'],
        'conflicts':[
            {'conflict_id':'TMP126_SOURCE_SIX_CONFLICTS','type':'SOURCE_INTERNAL',
             'claim':'Burstclear, CRC_CONFIG, negative slew, comparator encoding, enable-disable response and low-limit naming remain unresolved.',
             'source_or_locator':'source_review.json six conflicts; SNIS209C pp2,13,16-17,26-30',
             'resolution':'Retain explicit common/exploratory profiles and exclusions; no official erratum or full field certification.'},
            {'conflict_id':'GLOBAL_PRODUCTION_ADMISSION_OPEN','type':'SCOPE',
             'claim':'These eight bounded TMP126 obligations do not admit all20chips/572fields.',
             'source_or_locator':'admission_gate.json and original independent source signoff',
             'resolution':'production_generation_ready=false; M4 stage remains under orchestrator authority.'}],
        'conflict_resolution_status':'UNRESOLVED', 'merge_permission':'orchestrator_only',
        'recommended_next_action':'Orchestrator verifies exact accepted bytes and scope, then handles HDC2021 eight REPAIR fields while retaining global generation block.',
        'stage_acceptance_recommendation':'REPAIR', 'review_date':'2026-10-13',
        'readiness':'CONDITIONALLY_READY_FOR_DECLARED_TMP126_SCOPE_ONLY',
        'paper_submission_readiness':'NOT_READY', 'bounded_implementation_recommendation':'PASS_CANDIDATE',
        'independent_test_counts':run['independent_test_counts'],
        'synthetic_runtime_faults':13, 'proof_corruption_rejections':28,
        'reviewed_input_sha256':run['reviewed_input_sha256'],
    }
    (HERE / 'code_review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    report = '''# Independent TMP126 v3.2 code acceptance

Task `tmp126-v32/code_review`, project `d2d-twin`, family M, stage M4. **Bounded implementation: PASS_CANDIDATE. Whole-stage recommendation: REPAIR. Production generation and submission remain NOT_READY.**

The source-derived checklist was written before reviewing runtime code. Primary local PDF SNIS209C revised June2022 SHA-256 `6d9bab59b2814422d7bc1dff8fbd203df26e92ee40075b613c1f1fbb59eddfef` was independently read at printed pp2,14-17,21,26-32. Expected RC/live masks, signed data format, averaging count and event transitions come from these pages, not from candidate rule outputs.

Actual saved execution: **121/121 independent CPU tests passed**, zero failures/errors/skips. **13 synthetic runtime faults** were detected by source-derived oracles. **28 corrupted or fabricated execution/source variants** were rejected. Eight missing required-scenario variants stayed PARTIAL. These are validation fixtures, not LLM sample outcomes.

The ten saved owner scenarios replayed exactly; the eight-row bounded closure ledger reconstructed exactly; execution-manifest input/output SHA-256 matches were independently verified. The owner scenarios total85 checks, including8 source-table metadata checks and2 explicitly exploratory body-policy checks. They are not85 physical measurements. Original eight source REPAIR fields/eight dimensions remain unpromoted.

Contribution lens: the improvement supplies independently executable temporal checks for eight known TMP126 semantic defects. It does not show new model accuracy, novelty against literature, physical chip equivalence or a complete datasheet emulator. No submission-level contribution claim was accepted here.

Methods lens: nonzero flags are returned before0xA7 readclear, live0x58 bits survive, and TEMP read clears DR only. Qualified CRC failure discards writes. Comparator-to-interrupt transition clears pre-existing nonzero flags/live bits and logical ALERT; same-mode writes preserve state. Eight-sample signed averaging, restart/discard, readzeroONE_SHOT, MODE1 completion and abort were tested separately. Malformed payloads and out-of-scope transactions reject atomically. Admission binds exact source advice, source PDF SHA, frozen original field inventory, scenario identity, trace/check content and deterministic replay. Reviewed code had no remaining blocker within the declared bounded scope.

Communication lens: six source conflicts are visibly retained. Single/no-increment statusclear is the common positive scope. Burstclear behavior in body_candidate is exploratory only. Comparator encoding/low-limit naming retain candidate labels; active disable timing, CRC_CONFIG, physical frames and numerical slew are excluded. The current output correctly separates nominal metadata, digital event checks and exploratory checks. This separation must survive any paper revision.

Issues repaired during review: source_scope_guards initially attempted an active-alert enable change that its own common scope excludes; the owner removed this setup write. Admission initially did not rehash the reviewed primary PDF; the owner added path/SHA binding. Averaging scenario was strengthened to a distinct signed exact-grid stimulus so a last-sample implementation cannot pass. Final independent evidence refers only to the corrected current bytes.

Remaining major limitation (source_review.json/admission_gate.json): source contradictions and physical omissions prevent whole-field certification and global production generation. Minimum repair is to retain the existing exclusions and continue outstanding source obligations. Resolving manufacturer contradictions or adding physical evidence is outside this task and must not be claimed complete.

The preservation artifact records12563 old inventory files and1390 prior archived payloads unchanged; that is reviewed owner execution evidence. The independent recorder separately verified the frozen harness MD5 `8cf0854d4779467bc8e472ee4fb97023`. No historical model score was computed by this review.

Reproduce with `python eval/tmp126_semantics_v32_20261013/tests/record_independent_execution.py`. Exact executed command, XML, log, input hashes and counts are in independent_code_execution.json. Repackage this review only after that record succeeds on the accepted owner manifest.

Unique next action: orchestrator verifies the accepted TMP126 bytes and implements HDC2021 eight outstanding REPAIR fields, preserving the global generation block. No author environment or hardware action is required for that bounded next task.
'''
    (HERE / 'code_review.md').write_text(report, encoding='utf-8')
    print('Packaged code review from verified execution')


if __name__ == '__main__':
    main()
