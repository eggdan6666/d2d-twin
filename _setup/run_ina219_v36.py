"""INA219 bounded witnesses and immutable lineage, without production freeze."""
import hashlib
import json
from pathlib import Path
import platform
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'eval/ina219_semantics_v36_20261013'
sys.path.insert(0,str(OUT))
from admission import build_closure,produce_witness
from scenarios import SCENARIOS


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf-8'))
def write(n,v): (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    start=time.monotonic(); old=[]
    for directory,manifest in [('independent_source_admission_20261012','audit_bundle_manifest.json'),
        ('semantic_protocol_v3_20261012','artifact_manifest.json'),('tmp117_semantics_v31_20261013','artifact_manifest.json'),('tmp126_semantics_v32_20261013','artifact_manifest.json'),('hdc2021_semantics_v33_20261013','artifact_manifest.json'),('tmp461_semantics_v34_20261013','artifact_manifest.json'),('lis3dh_semantics_v35_20261013','artifact_manifest.json')]:
        base=ROOT/'eval'/directory
        for rel,expected in load(base/manifest)['files'].items():
            p=(base/rel).resolve()
            assert p.is_relative_to(base.resolve()) and sha(p)==expected,rel
            old.append((p,expected))
    protected=load(ROOT/'eval/independent_source_admission_20261012/protected_files_before.json')
    for rel,expected in protected.items():
        p=(ROOT/rel).resolve()
        assert p.is_relative_to(ROOT.resolve()) and sha(p)==expected,rel
        old.append((p,expected))
    pdf=ROOT/'corpus/data/raw_pdf/TI/INA219.pdf'
    review=load(OUT/'source_review.json'); assert sha(pdf)==review['source']['sha256']
    inputpaths=[OUT/n for n in ('ina219.py','scenarios.py','admission.py','source_review.json')]+[pdf,ROOT/'_setup/run_ina219_v36.py']
    inputs={p.relative_to(ROOT).as_posix():sha(p) for p in inputpaths}
    results={n:produce_witness(n) for n in SCENARIOS}
    closure=build_closure(review,results)
    write('scenario_execution.json',results); write('closure_ledger.json',closure)
    write('admission_gate.json',{'ina219_task_status':'BOUNDED_SCOPE_COMPLETE','target_repair_fields':6,
        'target_repair_dimensions':7,'bounded_dimensions_verified':sum(r['assessment']=='BOUNDED_CLAUSES_VERIFIED' for r in closure),
        'whole_fields_promoted':0,'production_generation_ready':False,'scientific_readiness':'NOT_READY',
        'global_source_admission':'NOT_ADMITTED','unresolved_source_conflicts':len(review['conflicts']),
        'scenario_count':len(results),'exploratory_scenarios':['candidate_read_clear','mode_clear_boundaries'],
        'physical_i2c_adc_or_timing_verified':False})
    for p,expected in old: assert sha(p)==expected,'Previously protected payload changed: '+str(p)
    for rel,expected in inputs.items(): assert sha(ROOT/rel)==expected,'Run input changed'
    write('preservation_verification.json',{'status':'UNCHANGED','old_inventory_files':len(protected),
        'prior_archive_payloads':len(old)-len(protected),'harness_md5':hashlib.md5((ROOT/'d2d/eval/test_d2d_blackbox.py').read_bytes()).hexdigest(),
        'historical_model_generation_or_rescoring':False,'scnet_used':False})
    assert load(OUT/'preservation_verification.json')['harness_md5']=='8cf0854d4779467bc8e472ee4fb97023'
    write('execution_manifest.json',{'protocol':'3.6-ina219-20261013','execution_date':'2026-10-14','status':'EXECUTED_LOCAL_NOT_PRODUCTION_FREEZE',
        'python':platform.python_version(),'command':'python _setup/run_ina219_v36.py','elapsed_seconds':time.monotonic()-start,
        'input_sha256':inputs,'scenario_count':len(results),'check_count':sum(r['check_count'] for r in results.values()),
        'source_table_metadata_checks':results['nominal_adc_table']['check_count'],
        'exploratory_checks':sum(results[n]['check_count'] for n in ('candidate_read_clear','mode_clear_boundaries')),
        'output_sha256':{n:sha(OUT/n) for n in ('scenario_execution.json','closure_ledger.json','admission_gate.json','preservation_verification.json')}})
    print('INA219:',len(results),'scenarios;',sum(r['check_count'] for r in results.values()),'checks;7 bounded dimensions;0 whole-field promotions.')


if __name__=='__main__': main()
