"""Build actual clause witnesses, immutable lineage and scoped TMP117 gate."""
import hashlib
import json
from pathlib import Path
import platform
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'eval/tmp117_semantics_v31_20261013'
sys.path.insert(0,str(OUT))
from admission import build_closure, produce_witness
from scenarios import SCENARIOS


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(name,value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    start=time.monotonic()
    source=ROOT/'eval/independent_source_admission_20261012'
    previous=ROOT/'eval/semantic_protocol_v3_20261012'
    old=[]
    for base,manifest in [(source,load(source/'audit_bundle_manifest.json')),
                          (previous,load(previous/'artifact_manifest.json'))]:
        for relative,expected in manifest['files'].items():
            path=(base/relative).resolve()
            assert path.is_relative_to(base.resolve()) and sha(path)==expected,relative
            old.append((path,expected))
    review=load(OUT/'source_review.json')
    pdf=ROOT/'corpus/data/raw_pdf/TI/TMP117.pdf'
    assert sha(pdf)==review['inputs_reviewed'][0]['sha256']
    inputpaths=[OUT/'tmp117.py',OUT/'scenarios.py',OUT/'admission.py',OUT/'source_review.json',
                ROOT/'_setup/run_tmp117_v31.py',pdf,
                previous/'artifact_manifest.json',source/'audit_bundle_manifest.json']
    inputs={p.relative_to(ROOT).as_posix():sha(p) for p in inputpaths}
    results={}
    for name,fn in SCENARIOS.items():
        results[name]=produce_witness(name)
    closure=build_closure(review,results)
    write('scenario_execution.json',results)
    write('closure_ledger.json',closure)
    write('admission_gate.json',{'tmp117_task_status':'BOUNDED_SCOPE_COMPLETE',
        'implemented_scenarios':len(results),'source_claims_with_witnesses':16,
        'target_repair_fields':15,'target_repair_dimensions':16,
        'bounded_dimensions_verified':sum(r['assessment']=='BOUNDED_CLAUSES_VERIFIED' for r in closure),
        'whole_fields_promoted':0,'production_generation_ready':False,'scientific_readiness':'NOT_READY',
        'remaining_scope':'Unspecified/excluded TMP117 behavior and remaining19-chip implementation; exact future generation context'})
    for path,expected in old:
        assert sha(path)==expected,'Previously frozen payload changed'
    for rel,expected in inputs.items():
        assert sha(ROOT/rel)==expected,'Current run input changed'
    write('execution_manifest.json',{'protocol':'3.1-tmp117-20261013','client_date':'2026-10-13',
        'status':'EXECUTED_LOCAL_NOT_PRODUCTION_FREEZE','python':platform.python_version(),
        'command':'python _setup/run_tmp117_v31.py','elapsed_seconds':time.monotonic()-start,
        'input_sha256':inputs,'previous_payloads_verified':len(old),'scenario_count':len(results),
        'check_count':sum(r['check_count'] for r in results.values()),
        'physical_timing_verified':False,'model_generation_or_rescoring':False,
        'output_sha256':{n:sha(OUT/n) for n in ['scenario_execution.json','closure_ledger.json','admission_gate.json']}})
    print('TMP117 scoped witnesses:',len(results),'scenarios;',sum(r['check_count'] for r in results.values()),'checks;16 scoped dimensions;0 whole-field promotions.')


if __name__=='__main__':
    main()
