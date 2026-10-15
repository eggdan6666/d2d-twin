"""Replay source-bound scoped evidence; never promote whole fields or dimensions."""
import hashlib, json
from pathlib import Path
from scenarios import SCENARIOS
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE_REVIEW_SHA='87f5b61b18453f8b074aee3e6c773da0b5e292283e276d86040301d90cf1fc71'
PDF_SHA='c9b67f886d4a5241a5e070723f7b61867409eeb27eed768b9cdd9cb17e03ca2d'
LEDGER_SHA='0905059f5f981f89137533d8b6f34d33cde5b673a05707c6b7141d521bb54711'

CLAIM_SCENARIOS={
 'INA226_C01_CAL_POR':['reserved_boundaries','cold_defaults'],
 'INA226_C02_CFG_POR':['reserved_boundaries','cold_defaults'],
 'INA226_C03_MASK_POR':['reserved_boundaries','cold_defaults'],
 'INA226_C04_RESERVED_WRITE_GAP':['reserved_boundaries'],
 'INA226_C05_RESERVED_PROTOCOL':['reserved_boundaries'],
 'INA226_C06_RST_REQUEST':['dirty_reset'],
 'INA226_C07_RST_TIMING_GAP':['dirty_reset'],
 'INA226_C08_RST_COMPLETION_PROTOCOL':['dirty_reset'],
 'INA226_C09_AFF_FAULT_SET':['latched_aff','transparent_aff','alert_priority'],
 'INA226_C10_AFF_LATCH_READ':['latched_aff'],
 'INA226_C11_AFF_TRANSPARENT':['transparent_aff'],
 'INA226_C12_AFF_CONFIG_P13':['aff_config_conflict'],
 'INA226_C13_AFF_CONFIG_P27':['aff_config_conflict'],
 'INA226_C14_AFF_COMMON_PROFILE':['aff_config_conflict'],
 'INA226_C15_CVRF_COMPLETE':['cv_sequence'],
 'INA226_C16_CVRF_CLEAR':['cv_sequence','cv_config_boundaries'],
 'INA226_C17_MODE_ENCODING':['cv_config_boundaries','token_and_domain_guards'],
 'INA226_C18_CVRF_COMPLETION_PROTOCOL':['cv_sequence','token_and_domain_guards'],
 'INA226_C19_READ_DIAGNOSTIC':['latched_aff','transparent_aff','cv_sequence'],
 'INA226_C20_READ_ORDER_GAP':['latched_aff','transparent_aff','cv_sequence'],
 'INA226_C21_CNVR_SCOPE':['cv_sequence'],
 'INA226_C22_CONFIG_SIDE_EFFECTS':['token_and_domain_guards','cv_config_boundaries'],
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)

def accepted_source():
    if sha(HERE/'source_review.json')!=SOURCE_REVIEW_SHA:
        raise ValueError('Accepted source expert bytes changed')
    result=json.loads((HERE/'source_review.json').read_text(encoding='utf-8'))
    expected={'contract_version':'1.0','expert_skill':'sci-skills-paper-deep-reading','project_id':'d2d-twin',
              'paper_family':'M','stage_id':'M4','task_id':'ina226-v37/source_review','task_status':'COMPLETE',
              'merge_permission':'orchestrator_only'}
    for key,val in expected.items():
        if result.get(key)!=val: raise ValueError('Wrong source expert identity: '+key)
    if result['source']!={'path':'corpus/data/raw_pdf/TI/INA226.pdf','sha256':PDF_SHA,'page_count':41}:
        raise ValueError('Wrong primary source identity')
    if sha(ROOT/result['source']['path'])!=PDF_SHA: raise ValueError('Primary PDF bytes changed')
    if result['ledger']!={'path':'eval/independent_source_admission_20261012/field_evidence.json','sha256':LEDGER_SHA}:
        raise ValueError('Wrong frozen ledger identity')
    if sha(ROOT/result['ledger']['path'])!=LEDGER_SHA: raise ValueError('Frozen source authority changed')
    return result

def produce_witness(name):
    if type(name) is not str or name not in SCENARIOS: raise ValueError('Unknown scenario identity')
    check=SCENARIOS[name]()
    kind=('SOURCE_TABLE_METADATA' if name=='nominal_table' else
          'EXPLORATORY_SOURCE_CONDITIONED_PROFILES' if name=='named_conflict_candidates' else 'DIGITAL_EVENT_PROFILE')
    return {'status':'PASS','check_count':len(check.checks),'checks':check.checks,'trace':check.trace,
            'execution_kind':kind,'chip':'INA226','no_physical_hardware_validation':True}

def validate_execution(execution):
    if type(execution) is not dict or set(execution)-set(SCENARIOS): raise ValueError('Unknown execution scope')
    for name,result in execution.items():
        if (type(result) is not dict or result.get('status')!='PASS' or type(result.get('check_count')) is not int or
            type(result.get('checks')) is not list or not result['checks'] or
            len(result['checks'])!=result['check_count'] or type(result.get('trace')) is not list or not result['trace']):
            raise ValueError('Missing, empty or invalid witness')
        if canonical(result)!=canonical(produce_witness(name)):
            raise ValueError('Witness differs from deterministic trusted replay')

def build_closure(source_review,execution):
    accepted=accepted_source()
    if canonical(source_review)!=canonical(accepted): raise ValueError('Source advice differs from accepted independent return')
    validate_execution(execution)
    ledger=json.loads((ROOT/accepted['ledger']['path']).read_text(encoding='utf-8'))
    authority={r['register']+'.'+r['field']:{k for k,v in r['dimensions'].items() if v['status']=='REPAIR'}
               for r in ledger if r['chip']=='INA226' and r['overall_status']=='REPAIR'}
    advice=accepted['field_closure_advice']
    if len(advice)!=6 or len({r['field'] for r in advice})!=6 or {r['field'] for r in advice}!=set(authority):
        raise ValueError('Original six-field denominator changed')
    claims={c['id']:c for c in accepted['claims']}
    if len(claims)!=len(accepted['claims']): raise ValueError('Duplicate claim identity')
    rows=[]
    for item in advice:
        required=item['claims']
        if not required or any(c not in claims for c in required): raise ValueError('Missing/unknown source claim')
        if authority[item['field']]!={item['dimension']}: raise ValueError('Original dimension identity changed')
        missing=[c for c in required if c not in CLAIM_SCENARIOS or any(s not in execution for s in CLAIM_SCENARIOS[c])]
        rows.append({'inventory_field_id':'INA226.'+item['field'],'dimension':item['dimension'],
            'source_verdict':'REPAIR','assessment':'BOUNDED_CLAUSES_VERIFIED' if not missing else 'PARTIAL',
            'bounded_disposition':item['recommended_disposition'],'required_claim_ids':required,
            'source_claim_classes':{c:claims[c]['class'] for c in required},
            'claim_scenarios':{c:CLAIM_SCENARIOS.get(c,[]) for c in required},'missing_claim_ids':missing,
            'source_conflict_ids':item.get('conflicts',[]),'whole_dimension_closed':False,'whole_field_promoted':False,
            'scope':'Three reserved-access exclusion guards; qualified reset and flag events; common AFF CONFIG-write conflict remains unknown; read-before-clear is protocol assumption; single-channel/physical/timing excluded',
            'evidence_meaning':'Runtime confirms bounded dispositions, not the manufacturer truth or full implementation of every source statement.'})
    if len(rows)!=6: raise ValueError('Original six-dimension denominator changed')
    return rows
