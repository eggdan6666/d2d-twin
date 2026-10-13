"""Consolidate source reviews, create prospective inputs, check protected histories."""
from pathlib import Path
import json,hashlib,csv,collections,copy,re,datetime
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[1]
BASE=ROOT/'eval/protocol_v2_20261012'
PARTS=['source_root','source_adc_monitor','source_motion_io','source_power_thermal']
DIMS=['reset','access','legal_encoding','read_clear','trigger_completion','conditional_write','reserved_policy']
STATUS={'PASS','REPAIR','CONDITIONAL','EXCLUDE'}

def read(p): return json.loads(p.read_text(encoding='utf-8'))
def dump(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def rel(p): return str(p.relative_to(ROOT)).replace('\\','/')
def key(x): return x['chip'],x['register'],x['field']
def sources_flat(x):
    if isinstance(x,list): return x
    if 'sources' in x: return x['sources']
    return list(x.values())

rows=[]; findings=[]; patches=[]; gaps=[]; sources=[]; returns=[]; tasks=[]
for name in PARTS:
    p=OUT/'partitions'/name
    a=read(p/'fields.json'); rows+=a
    findings+=read(p/'findings.json'); patches+=read(p/'ir_patches.json'); gaps+=read(p/'register_gaps.json')
    sources+=sources_flat(read(p/'sources.json'))
    ret=read(p/'expert_return.json'); returns.append(ret)
    required=['contract_version','expert_skill','project_id','paper_family','stage_id','task_id','task_status','inputs_reviewed','outputs','evidence_status','assumptions','author_input_needed','manual_actions','quality_checks','conflicts','conflict_resolution_status','merge_permission','recommended_next_action','stage_acceptance_recommendation']
    assert all(x in ret for x in required),(name,'missing return contract')
    assert ret['contract_version']=='1.0' and ret['project_id']=='d2d-twin' and ret['paper_family']=='M' and ret['stage_id']=='M4' and ret['merge_permission']=='orchestrator_only',(name,'identity mismatch')
    assert ret['task_id']==name or ret['task_id'].endswith('/'+name),(name,'task mismatch')
    tasks.append({'contract_version':'1.0','project_id':'d2d-twin','paper_family':'M','stage_id':'M4','task_id':name,'expert_skill':ret['expert_skill'],'task_summary':'Independent manufacturer-source admission for assigned register fields','inputs':['seven requested v2 documents','original local manufacturer PDFs','field inventory for assigned chips'],'expected_outputs':['fields.json','findings.json','sources.json','ir_patches.json','register_gaps.json','REVIEW.md','expert_return.json'],'evidence_boundaries':['local original PDFs only','manufacturer facts distinct from abstractions and source conflicts','no historical model results as source evidence','write only in new review directory'],'acceptance_checks':['all assigned fields accounted exactly once','seven dimensions and source locators per field','file SHA256 and manual/printed page identity retained'],'known_missing_items':[],'manual_operation_allowed':False,'optional_adapters_allowed':['local-python','local-file-import','local-document-rendering'],'stage_authority':'sci-skills','dispatch_status':'VERIFIED'})

inventory=read(BASE/'field_policy_inventory.json'); expected={key(x) for x in inventory}
assert len(rows)==572 and len(set(key(x) for x in rows))==572
assert {key(x) for x in rows}==expected
rows.sort(key=key)
fingerprints={}; verified_sources=[]
for s in sources:
    path=s.get('source_path',s.get('path'))
    assert path and (ROOT/path).is_file(),s
    claimed=s.get('sha256',s.get('source_sha256'))
    actual=sha(ROOT/path); assert actual==claimed,(path,'source hash mismatch')
    ss=copy.deepcopy(s); ss['source_path']=path; ss['sha256']=actual
    if path not in fingerprints: verified_sources.append(ss)
    fingerprints[path]=actual

text_cache={}
def page_text(path,n):
    import fitz
    if path not in text_cache:
        with fitz.open(ROOT/path) as doc: text_cache[path]=[p.get_text()+'\n'+p.get_text(sort=True) for p in doc]
    assert isinstance(n,int) and 1<=n<=len(text_cache[path]),(path,n)
    return text_cache[path][n-1]

quote_checks=[]; dimension_count=0
for row in rows:
    assert row['overall_status'] in STATUS and all(d in row['dimensions'] for d in DIMS),key(row)
    path=row['source_path']; assert fingerprints.get(path)==row['source_sha256'],key(row)
    assert row.get('manual_version'),key(row)
    for name in DIMS:
        d=row['dimensions'][name]; dimension_count+=1
        assert d['status'] in STATUS and 'fact' in d and 'candidate_rule' in d and 'evidence_class' in d and d.get('locators'),(key(row),name)
        for l in d['locators']:
            n=l['pdf_page']; lp=l.get('source_path',path)
            t=page_text(lp,n)
            assert l.get('printed_page') is not None and any(l.get(x) for x in ['table','section','table_or_section']),(key(row),name,l)
            q=l.get('excerpt','')
            if q:
                norm=lambda v: re.sub(r'\s+','',v).casefold()
                quote_checks.append({'field':'.'.join(key(row)),'dimension':name,'pdf_page':n,'source_path':lp,'excerpt':q,'matched':norm(q) in norm(t)})

dump(OUT/'field_evidence.json',rows)
dump(OUT/'reviewed_source_manifest.json',{'source_boundary':'Local manufacturer PDFs supplied by repository; current vendor website bytes and official errata not checked','sources':verified_sources,'preflight_warning':'prepare.py initial filename match for MPU6050 is product specification; actual register review uses separately hashed original manufacturer RM mirror, recorded here and in each field.'})
dump(OUT/'source_excerpt_checks.json',quote_checks)
dump(OUT/'expert_returns.json',returns);dump(OUT/'expert_tasks.json',tasks)
dump(OUT/'register_scope_gaps.json',gaps)
dump(OUT/'revision_candidates.json',{'status':'CANDIDATE_NOT_PROMOTED','source_protocol_version':'2.0-candidate-20261012.1','findings':findings,'ir_patches':patches,'scope_gaps':gaps,'rule':'No conflict is resolved by a majority vote or a reference score. Candidate rules need a separately implemented prospective harness.'})

def writer(p,fields,data):
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)

fieldcsv=[];dimcsv=[]
for r in rows:
    v={k:r.get(k) for k in ['chip','register','field','bits','overall_status','manual_version','source_path','source_sha256']}
    v.update({d:r['dimensions'][d]['status'] for d in DIMS});fieldcsv.append(v)
    for d in DIMS:
        x=r['dimensions'][d]; dimcsv.append({**{k:r.get(k) for k in ['chip','register','field','bits','manual_version','source_path','source_sha256']},'dimension':d,'status':x['status'],'applicable':x.get('applicable','unspecified'),'evidence_class':x['evidence_class'],'manufacturer_fact':x['fact'],'candidate_rule':json.dumps(x['candidate_rule'],ensure_ascii=False),'locators':json.dumps(x['locators'],ensure_ascii=False)})
writer(OUT/'field_verdicts.csv',list(fieldcsv[0]),fieldcsv)
writer(OUT/'dimension_evidence.csv',list(dimcsv[0]),dimcsv)
counts=collections.Counter(r['overall_status'] for r in rows)
perchip=[]
for chip in sorted({x['chip'] for x in rows}):
    cc=collections.Counter(x['overall_status'] for x in rows if x['chip']==chip)
    perchip.append({'chip':chip,'fields':sum(cc.values()),**{s:cc[s] for s in ['PASS','REPAIR','CONDITIONAL','EXCLUDE']}})
writer(OUT/'per_chip_verdicts.csv',list(perchip[0]),perchip)

# Preserve operation records separately from unique final attribute changes.
raw_patch_count=len(patches); duplicate_patches=[]; unique=[]; seen={}
for p in patches:
    pk=(p['chip'],p.get('register'),p.get('field'),p['property'],p.get('op','replace'),json.dumps(p.get('old'),sort_keys=True,ensure_ascii=False),json.dumps(p.get('new'),sort_keys=True,ensure_ascii=False))
    if pk in seen:
        duplicate_patches.append({'duplicate_operation':p,'same_final_change_index':seen[pk]})
    else: seen[pk]=len(unique);unique.append(p)
patches=unique
dump(OUT/'duplicate_candidate_patch_records.json',duplicate_patches)
# Candidate copies are intentionally incompatible with old unconditional assertions.
candidate={p.stem.replace('_gold_ir',''):read(p) for p in (BASE/'ir').glob('*_gold_ir.json')}
applied=[]
for p in patches:
    c=p['chip']; rn=p.get('register'); fn=p.get('field'); prop=p['property']
    target=candidate[c]
    if rn: target=next(r for r in target['registers'] if r['name']==rn)
    if fn: target=next(f for f in target['fields'] if f['name']==fn)
    if '.' in prop:
        parts=prop.split('.')
        for part in parts[:-1]: target=target[part]
        prop=parts[-1]
    old=target.get(prop)
    if prop=='source_default_admission' and old is None and isinstance(p.get('old'),dict):
        ctx=p['old']; assert target.get('reset')==ctx['field_reset']
        parent=next(r for r in candidate[c]['registers'] if r['name']==rn)
        assert parent.get('reset')==ctx['register_reset']
    else: assert old==p.get('old'),('patch old value mismatch',p,old)
    if p.get('op')=='remove': target.pop(prop,None)
    else: target[prop]=p.get('new')
    applied.append({**p,'applied_to':f'candidate_ir/{c}_gold_ir.json'})

legacy=[];postconditions=[]
rename_map={(p['chip'],p.get('register'),p.get('field')):p['new'] for p in patches if p['property']=='name' and p.get('field')}
for chip,ir in candidate.items():
    for k in ['proofread_record','source_repair_note','schema_note']:
        if k in ir: legacy.append({'chip':chip,'path':k,'content':ir.pop(k),'reason':'historical commentary withheld from generation prompt; source conflicts are declared in the new evidence policy'})
    for r in ir['registers']:
        # Legacy desc text is retained in audit, but unsupported "official erratum" tone is removed from input.
        targets=[r]+r.get('fields',[])
        for t in targets:
            for k in ['desc','tier_evidence']:
                if isinstance(t.get(k),str) and re.search('erratum|errata|笔误|误标|勘误',t[k],re.I) and not re.search(r'no official|not official',t[k],re.I):
                    legacy.append({'chip':chip,'register':r['name'],'field':t.get('name') if t is not r else None,'path':k,'content':t[k],'reason':'unsupported erratum terminology excluded from source facts'})
                    t[k]='Historical source-conflict wording withheld: see the independently reviewed source facts and conditional rules in field_evidence.json; no official manufacturer erratum was verified.'
        occupied=0
        for f in r.get('fields',[]):
            bits=[int(x) for x in f['bits'].split(':')];hi,lo=bits[0],bits[-1]
            assert hi>=lo>=0 and hi<ir.get('reg_width',16),(chip,r['name'],f)
            m=((1<<(hi-lo+1))-1)<<lo
            assert occupied&m==0,('overlapping fields after patches',chip,r['name'],f)
            occupied|=m
            if f.get('reset') is not None: assert 0<=f['reset']<(1<<(hi-lo+1)),(chip,r['name'],f)
        postconditions.append({'chip':chip,'register':r['name'],'fields_nonoverlap':True})
    ir['base_schema']=ir.get('schema')
    ir['schema']='d2d-ir-source-candidate-v3'
    ir['schema_note']='Prospective independent source-admission draft; no source certification from historical reference/model scores. Read together with candidate_source_policy.json.'
    ir['source_admission']={'status':'PROVISIONAL_GENERATION_INPUT_NOT_ADMITTED','audit':'../field_evidence.json','policy':'../candidate_source_policy.json','scope':'selected inventory only; disputed and dynamic assertions must use explicit aspect policy','historical_notes':'../legacy_ir_annotations.json','official_errata_verified':False}
    dump(OUT/'candidate_ir'/f'{chip}_gold_ir.json',ir)
dump(OUT/'applied_candidate_patches.json',applied);dump(OUT/'legacy_ir_annotations.json',legacy)

field_rules=[]
for row in rows:
    rr={k:copy.deepcopy(row[k]) for k in ['chip','register','field','bits','overall_status','source_path','source_sha256','manual_version','dimensions']}
    rr['inventory_field_id']='.'.join(key(row));rr['inventory_bits']=rr['bits']
    rr['field']=rename_map.get(key(row),rr['field'])
    reg=next(r for r in candidate[row['chip']]['registers'] if r['name']==row['register'])
    cf=next(f for f in reg['fields'] if f['name']==rr['field'])
    rr['bits']=cf['bits'];rr['candidate_addr']=reg['addr']
    bits=[int(x) for x in rr['bits'].split(':')];h,l=bits[0],bits[-1]
    rr['candidate_bit_mask']=hex(((1<<(h-l+1))-1)<<l)
    rr['candidate_reset']=cf.get('reset');rr['candidate_access_annotation']=cf['access']
    rr['status_scope']='review of prior inventory; candidate geometry above supersedes prior inventory bits for generation, with source repairs still awaiting new harness admission'
    field_rules.append(rr)
pol={'schema':'d2d-source-admission-policy-candidate-1','version':'independent-source-admission-20261012.1','status':'NOT_DROP_IN_FOR_V2_NOT_PROMOTED','field_count':572,'dimensions':DIMS,'source_lock':fingerprints,'default_rules':['A PASS covers only the exact fact and locator, not all hardware functionality','Reset numeric certainty is separate from access and legal input','Read-only does not imply constant snapshot while hardware events occur','An undocumented illegal-input response is EXCLUDE, not clamping/ignore/zero','Conditional dynamic rules require declared event and completion semantics','An empty/no-event assertion set is SKIP, never positive source certification','All source conflicts remain unresolved and disputed aspects excluded from the main oracle','Mandatory default writes are stimulus constraints, not evidence of writability','Do not use this schema with the old protocol_rules parser'],'field_rules':field_rules,'register_scope_gaps':gaps,'freeze_gate':'Implement and validate a new harness and exact generation context before a production generation freeze'}
dump(OUT/'candidate_source_policy.json',pol)

conflictrows=[]
for r in rows:
    for d,v in r['dimensions'].items():
        if v['evidence_class']=='SOURCE_CONFLICT': conflictrows.append({'chip':r['chip'],'register':r['register'],'field':r['field'],'dimension':d,'competing_evidence':v['fact'],'candidate_main_rule':v['candidate_rule'],'locators':v['locators'],'source_path':r['source_path'],'sha256':r['source_sha256'],'status':'UNRESOLVED','official_erratum':False})
for f in findings:
    if f.get('evidence_class')=='SOURCE_CONFLICT' or any(s in str(f.get('problem','')).lower() for s in ['冲突','歧义','conflict']): conflictrows.append({**f,'status':'UNRESOLVED','official_erratum':False})
assert all(any(x['chip']==c for x in conflictrows) for c in ['TMP117','INA3221','TPS23861'])
dump(OUT/'conflict_ledger.json',conflictrows)

before=read(OUT/'protected_files_before.json'); after={p:sha(ROOT/p) if (ROOT/p).is_file() else None for p in before}
changed=[p for p in before if before[p]!=after[p]]
manifest=read(BASE/'protocol_manifest.json'); mm=[p for p,h in manifest['files'].items() if sha(BASE/p)!=h]
dump(OUT/'protected_files_after.json',after)
pres={'protected_file_count':len(before),'changed_or_missing':changed,'v2_manifest_file_count':len(manifest['files']),'v2_manifest_mismatches':mm,'rule':'Read-only baseline includes d2d/ir, every existing test_d2d_blackbox.py, entire v2 tree and historical result inventories.'}
dump(OUT/'preservation_verification.json',pres)
assert not changed and not mm,('protected input change',pres)
quality={'status':'PASS_FOR_AUDIT_PACKAGE_COMPLETENESS_ONLY','field_count':len(rows),'dimension_count':dimension_count,'chips':len(perchip),'unique_field_ids':len(expected),'verdict_counts':dict(counts),'per_chip':perchip,'findings_entries':len(findings),'candidate_patch_operation_records':raw_patch_count,'duplicate_candidate_patch_records':len(duplicate_patches),'candidate_ir_attribute_patches':len(applied),'candidate_ir_field_count':sum(len(r.get('fields',[])) for ir in candidate.values() for r in ir['registers']),'source_files':len(fingerprints),'excerpt_checks':len(quote_checks),'excerpt_match_count':sum(x['matched'] for x in quote_checks),'excerpt_mismatch_count':sum(not x['matched'] for x in quote_checks),'source_pages_and_hashes_checked':True,'preservation':pres,'candidate_bit_field_structure':'nonoverlap and range checked; semantics still conditional','claim_limits':['Not all fields PASS; completeness is not manufacturer certification','No physical timing/events executed','No models/reference tests executed','No production input freeze admitted']}
dump(OUT/'quality_checks.json',quality)

md=['# 独立来源审校差异清单','','差异条目由本轮原PDF审查产生；同一机制可以影响多个字段，条目数不是互异硅缺陷数。完整原文、版本、SHA与逐维结论在field_evidence.json。','']
for f in findings:
    md += [f"## {f['id']} — {f['chip']}", '',str(f['problem']),'',f"对象：{', '.join(map(str,f.get('targets',[])))}",'',f"原策略/输入：`{json.dumps(f.get('old'),ensure_ascii=False)}`",'',f"候选：`{json.dumps(f.get('candidate_rule'),ensure_ascii=False)}`",'',f"来源：`{json.dumps(f.get('locators'),ensure_ascii=False)}`",'']
(OUT/'DIFFERENCES.md').write_text('\n'.join(md),encoding='utf-8')
dump(OUT/'project_state_update.json',{'project_id':'d2d-twin','paper_family':'M','stage_id':'M4','stage_status':'PARTIALLY_PASSED','scientific_readiness':'NOT_READY','task_status':'COMPLETE_SOURCE_REVIEW_AND_CANDIDATE_PACKAGING','data_sufficiency':'SUFFICIENT_FOR_LOCAL_SOURCE_REVIEW','external_acquisition':'NOT_NEEDED','production_generation_freeze':'NOT_ADMITTED','expert_tasks':{p:'VERIFIED' for p in PARTS},'blockers':['apply scoped candidate semantics in a new generation/harness pair','retain unresolved source conflicts','future generation provenance must be exact'],'next_action':'Implement source-scoped candidate contract in a new harness and pass admission gates before freezing new generation inputs.'})
print(json.dumps(quality,ensure_ascii=False))
