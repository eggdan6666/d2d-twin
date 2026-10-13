"""Verify signed evidence bytes and inventory only the scoped new archive."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'eval/lis3dh_semantics_v35_20261013'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(p.read_text(encoding='utf-8'))


def main():
    independent=load(OUT/'independent_code_execution.json')
    for rel,expected in independent['reviewed_input_sha256'].items():
        assert sha(ROOT/rel)==expected,'Independent reviewed input changed: '+rel
    for name,expected in independent['output_sha256'].items():
        assert sha(OUT/name)==expected,'Independent output changed'
    final=load(OUT/'regression_manifest.json')
    for rel,expected in final['input_sha256'].items(): assert sha(ROOT/rel)==expected,rel
    for name,expected in final['output_sha256'].items(): assert sha(OUT/name)==expected,name
    assert final['passed']==independent['independent_test_counts']['passed'] and final['passed']>0
    gate=load(OUT/'admission_gate.json')
    assert gate['bounded_dimensions_verified']==8 and gate['whole_fields_promoted']==0
    assert gate['global_source_admission']=='NOT_ADMITTED' and not gate['production_generation_ready']
    files={}
    for p in sorted(OUT.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(OUT)
        if set(rel.parts)&{'__pycache__','.pytest_cache','source_review_materials','code_review_scratch'}: continue
        if rel.as_posix()=='artifact_manifest.json': continue
        files[rel.as_posix()]=sha(p)
    helpers={p.relative_to(ROOT).as_posix():sha(p) for p in
        [ROOT/'_setup'/n for n in ('run_lis3dh_v35.py','package_lis3dh_v35.py','archive_lis3dh_v35.py')]}
    (OUT/'artifact_manifest.json').write_text(json.dumps({'status':'BOUNDED_CANDIDATE_ARCHIVE_NOT_PRODUCTION_FREEZE',
        'client_date':'2026-10-13','production_generation_ready':False,'files':files,'helper_sha256':helpers},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Archive verified:',len(files),'payload files;',sum((OUT/r).stat().st_size for r in files),'bytes')


if __name__=='__main__': main()
