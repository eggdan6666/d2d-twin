"""Source-byte-bound deterministic local evidence; not whole-field certification."""
from pathlib import Path
import hashlib,json
from scenarios import SCENARIOS
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
SOURCE_REVIEW_SHA='fdc5c242da057c71e404b1e50bf7d45cdf2b5f2e54ffdc5532ff006468c12311'
PDF_SHA='6ef5bf2263e34332fce7ea2547d9824ff5d3900418d51d59e5e3b711dcdc98d0'
LEDGER_SHA='0905059f5f981f89137533d8b6f34d33cde5b673a05707c6b7141d521bb54711'
CLAIM_SCENARIOS={
 'INA3221-RST-01':['reset_and_pv_exception'],
 'INA3221-RST-02':['reset_and_pv_exception'],
 'INA3221-RST-03':['reset_and_pv_exception','trigger_rewrite_and_tokens'],
 'INA3221-RST-04':['cold_scope','domain_guards'],
 'INA3221-CVRF-01':['cold_scope','partial_and_read_clear'],
 'INA3221-CVRF-02':['enabled_mode_sequences'],
 'INA3221-CVRF-03':['enabled_mode_sequences','trigger_rewrite_and_tokens'],
 'INA3221-CVRF-04':['config_clear_and_disable','partial_and_read_clear'],
 'INA3221-CVRF-05':['config_clear_and_disable'],
 'INA3221-CVRF-06':['recursive_filter_scope'],
 'INA3221-CVRF-07':['domain_guards','trigger_rewrite_and_tokens','partial_and_read_clear'],
 'INA3221-CVRF-08':['partial_and_read_clear','domain_guards'],
 'INA3221-TCF-01':['cold_scope'],
 'INA3221-TCF-02':['tc_common_unknown','tc_cancel_and_rearm'],
 'INA3221-TCF-03':['tc_cancel_and_rearm'],
 'INA3221-TCF-04':['tc_common_unknown','tc_cancel_and_rearm'],
 'INA3221-TCF-05':['tc_common_unknown'],
 'INA3221-TCF-06':['domain_guards'],
 'INA3221-TCF-07':['tc_common_unknown','tc_cancel_and_rearm'],
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def accepted_source():
    if sha(HERE/'source_review.json')!=SOURCE_REVIEW_SHA:raise ValueError('Accepted independent source bytes changed or not admitted')
    r=json.loads((HERE/'source_review.json').read_text(encoding='utf-8'))
    expected={'contract_version':'1.0','expert_skill':'sci-skills-paper-deep-reading','project_id':'d2d-twin',
        'paper_family':'M','stage_id':'M4','task_id':'ina3221-v38/source_review','task_status':'COMPLETE',
        'merge_permission':'orchestrator_only'}
    for key,v in expected.items():
        if r.get(key)!=v:raise ValueError('Wrong independent source identity: '+key)
    for key,path,digest in [('source','corpus/data/raw_pdf/TI/INA3221.pdf',PDF_SHA),
                          ('ledger','eval/independent_source_admission_20261012/field_evidence.json',LEDGER_SHA)]:
        if r[key].get('path')!=path or r[key].get('sha256')!=digest or sha(ROOT/path)!=digest:
            raise ValueError('Source authority changed: '+key)
    if r['source']['page_count']!=50:raise ValueError('Wrong source page count')
    return r
def produce_witness(name):
    if type(name) is not str or name not in SCENARIOS:raise ValueError('Unknown scenario identity')
    c=SCENARIOS[name]()
    kind=('SOURCE_TABLE_METADATA' if name=='nominal_filter_metadata' else
          'EXPLORATORY_SOURCE_CONDITIONED_PROFILES' if name=='tcf_named_candidates' else 'DIGITAL_EVENT_PROFILE')
    return {'status':'PASS','check_count':len(c.checks),'checks':c.checks,'trace':c.trace,
        'execution_kind':kind,'chip':'INA3221','no_physical_hardware_validation':True}
def validate_execution(execution):
    if type(execution) is not dict or set(execution)-set(SCENARIOS):raise ValueError('Unknown execution scope')
    for name,r in execution.items():
        if (type(r) is not dict or r.get('status')!='PASS' or type(r.get('check_count')) is not int or
            type(r.get('checks')) is not list or not r['checks'] or len(r['checks'])!=r['check_count'] or
            type(r.get('trace')) is not list or not r['trace']):raise ValueError('Empty/invalid witness')
        if canonical(r)!=canonical(produce_witness(name)):raise ValueError('Witness differs from trusted replay')
def build_closure(source_review,execution):
    accepted=accepted_source()
    if canonical(source_review)!=canonical(accepted):raise ValueError('Source advice differs from independent accepted return')
    validate_execution(execution)
    ledger=json.loads((ROOT/accepted['ledger']['path']).read_text(encoding='utf-8'))
    authority={r['register']+'.'+r['field']:{k for k,v in r['dimensions'].items() if v['status']=='REPAIR'}
        for r in ledger if r['chip']=='INA3221' and r['overall_status']=='REPAIR'}
    advice=accepted['field_closure_advice']
    if len(advice)!=3 or len({r['field'] for r in advice})!=3 or {r['field'] for r in advice}!=set(authority):
        raise ValueError('Original three-field denominator changed')
    claims={c['claim_id']:c for c in accepted['claims']}
    if len(claims)!=len(accepted['claims']):raise ValueError('Duplicate source claim identity')
    rows=[]
    for item in advice:
        dimension=item['original_repair_dimension'];required=item['claim_ids']
        if authority[item['field']]!={dimension} or not required or any(c not in claims for c in required):
            raise ValueError('Original dimensions or source claim identity changed')
        missing=[c for c in required if c not in CLAIM_SCENARIOS or any(s not in execution for s in CLAIM_SCENARIOS[c])]
        conflict_ids=[c['conflict_id'] for c in accepted['conflicts'] if set(c['claim_ids'])&set(required)]
        rows.append({'inventory_field_id':'INA3221.'+item['field'],'dimension':dimension,'source_verdict':'REPAIR',
            'assessment':'BOUNDED_CLAUSES_VERIFIED' if not missing else 'PARTIAL',
            'bounded_disposition':item['recommendation'],'required_claim_ids':required,
            'source_claim_classes':{c:claims[c]['evidence_class'] for c in required},
            'claim_scenarios':{c:CLAIM_SCENARIOS.get(c,[]) for c in required},'missing_claim_ids':missing,
            'source_conflict_ids':conflict_ids,'required_exclusions':item['required_exclusions'],
            'whole_dimension_closed':False,'whole_field_promoted':False,
            'scope':'Three conditional event/unknown guards; subset-CONFIG/CVRF, TCF numeric default/polarity and 0Eh excluded; recursive filter results externally qualified; PV pin hold explicit; no hardware/timing proof',
            'evidence_meaning':'Execution verifies bounded dispositions, not all manufacturer clauses, exact filter arithmetic or physical measurements.'})
    if len(rows)!=3:raise ValueError('Original three-dimension denominator changed')
    return rows
