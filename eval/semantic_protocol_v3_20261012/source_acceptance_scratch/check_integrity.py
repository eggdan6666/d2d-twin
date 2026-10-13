from pathlib import Path
import json,hashlib,collections,csv,copy,re,sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[3]
B=ROOT/'eval/independent_source_admission_20261012'
V=ROOT/'eval/protocol_v2_20261012'
S=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text('utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
for name in ['audit_bundle_manifest.json','input_freeze_candidate_manifest.json']:
    d=read(B/name); bad=[n for n,h in d['files'].items() if not (B/n).is_file() or sha(B/n)!=h]
    checks[name]={'count':len(d['files']),'mismatches':bad}
sources=read(B/'reviewed_source_manifest.json')['sources']
checks['source_hashes']={'count':len(sources),'mismatches':[x['source_path'] for x in sources if sha(ROOT/x['source_path'])!=x['sha256']]}
rows=read(B/'field_evidence.json'); key=lambda x:(x['chip'],x['register'],x['field'])
inv=read(V/'field_policy_inventory.json'); dims=['reset','access','legal_encoding','read_clear','trigger_completion','conditional_write','reserved_policy']
assert {key(x) for x in rows}=={key(x) for x in inv}
assert len(rows)==len({key(x) for x in rows})==572
assert all(set(x['dimensions'])==set(dims) for x in rows)
ds=list(csv.DictReader((B/'dimension_evidence.csv').open(encoding='utf-8-sig',newline='')))
assert len(ds)==4004 and {(r['chip'],r['register'],r['field'],r['dimension']) for r in ds}=={(*key(r),d) for r in rows for d in dims}
checks['identity_correspondence']={'chips':len({r['chip'] for r in rows}),'fields':len(rows),'dimensions':len(ds),'overall_status':dict(collections.Counter(r['overall_status'] for r in rows))}
candidates={p.stem.replace('_gold_ir',''):read(p) for p in (V/'ir').glob('*_gold_ir.json')}
patches=read(B/'applied_candidate_patches.json'); patch_checks=[]
for p in patches:
    c=p['chip'];target=candidates[c]
    if p.get('register'):target=next(r for r in target['registers'] if r['name']==p['register'])
    if p.get('field'):target=next(f for f in target['fields'] if f['name']==p['field'])
    prop=p['property'].split('.')
    for k in prop[:-1]:target=target[k]
    k=prop[-1];old=target.get(k)
    if k=='source_default_admission' and old is None and isinstance(p.get('old'),dict):
        assert target.get('reset')==p['old']['field_reset']
        assert next(r for r in candidates[c]['registers'] if r['name']==p['register']).get('reset')==p['old']['register_reset']
    else:assert old==p.get('old'),p
    if p.get('op')=='remove':target.pop(k,None)
    else:target[k]=p.get('new')
    patch_checks.append({'chip':c,'register':p.get('register'),'field':p.get('field'),'property':p['property'],'old_value_match':True})
annotations=read(B/'legacy_ir_annotations.json')
for a in annotations:
    target=candidates[a['chip']]
    if a.get('register'):target=next(r for r in target['registers'] if r['name']==a['register'])
    if a.get('field'):target=next(f for f in target['fields'] if f['name']==a['field'])
    assert target[a['path']]==a['content']
    if not a.get('register'):target.pop(a['path'])
    else:target[a['path']]='Historical source-conflict wording withheld: see the independently reviewed source facts and conditional rules in field_evidence.json; no official manufacturer erratum was verified.'
differences=[];geometry=[]
for c,ir in candidates.items():
    final=read(B/'candidate_ir'/f'{c}_gold_ir.json')
    # Packaging-only schema/provenance additions are not one of the 109 attribute repairs.
    expected=copy.deepcopy(final)
    for k in ['schema','schema_note','base_schema','source_admission']:expected.pop(k,None)
    actual=copy.deepcopy(ir);actual.pop('schema',None)
    if actual!=expected:differences.append(c)
    for r in final['registers']:
        occupied=0
        for f in r.get('fields',[]):
            z=[int(a) for a in f['bits'].split(':')];hi,lo=z[0],z[-1]
            assert 0<=lo<=hi<final.get('reg_width',16),(c,r['name'],f)
            mask=((1<<(hi-lo+1))-1)<<lo;assert not occupied&mask;occupied|=mask
            if f.get('reset') is not None:assert 0<=f['reset']<(1<<(hi-lo+1))
            geometry.append((c,r['name'],f['name'],f['bits']))
checks['patch_replay']={'operations':len(patches),'matched_old_values':len(patch_checks),'post_packaging_deep_diff_chips':differences,'geometry_fields':len(geometry),'valid_nonoverlap':True}
policy=read(B/'candidate_source_policy.json')['field_rules'];candidate_ids={(c,r,f) for c,r,f,b in geometry}
assert len(policy)==572 and {key(x) for x in policy}==candidate_ids
assert {x['inventory_field_id'] for x in policy}=={'.'.join(key(x)) for x in inv}
checks['policy_mapping']={'candidate_identities':572,'prior_inventory_ids':572,'geometry_matches':all(tuple([x['chip'],x['register'],x['field'],x['bits']]) in geometry for x in policy)}
before=read(B/'protected_files_before.json');after=read(B/'protected_files_after.json')
checks['protected_snapshot_records']={'count':len(before),'record_changes':[p for p in before if before[p]!=after.get(p)]}
core=read(V/'protocol_manifest.json');checks['v2_current_core']={'count':len(core['files']),'mismatches':[p for p,h in core['files'].items() if sha(V/p)!=h]}
checks['formal_current_ir']={'count':20,'mismatches':[str(p.relative_to(ROOT)) for p in (ROOT/'d2d/ir').glob('*_gold_ir.json') if str(p.relative_to(ROOT)).replace('\\','/') in before and sha(p)!=before[str(p.relative_to(ROOT)).replace('\\','/')]]}
checks['harness_md5']=hashlib.md5((ROOT/'d2d/eval/test_d2d_blackbox.py').read_bytes()).hexdigest()
(S/'integrity_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(checks,ensure_ascii=False,indent=2))
