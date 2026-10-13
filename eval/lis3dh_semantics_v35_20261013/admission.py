"""Replayed clause evidence without any whole-field source promotion."""
import hashlib
import json
from pathlib import Path
from scenarios import SCENARIOS,CLAIM_SCENARIOS
HERE=Path(__file__).resolve().parent


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)


def produce_witness(name):
    if name not in SCENARIOS: raise ValueError('Unknown scenario identity')
    c=SCENARIOS[name]()
    if name=='nominal_odr_table': kind='SOURCE_TABLE_METADATA'
    elif name in ('candidate_consumption','bdu_boundary','power_on_defaults'): kind='EXPLORATORY_READ_CONSUMPTION_POLICY'
    else: kind='DIGITAL_EVENT_PROFILE'
    return {'status':'PASS','check_count':len(c.checks),'checks':c.checks,'trace':c.trace,'execution_kind':kind}


def validate_execution(execution):
    if type(execution) is not dict or set(execution)-set(SCENARIOS): raise ValueError('Unknown scenario identity')
    for name,result in execution.items():
        if (type(result) is not dict or result.get('status')!='PASS' or type(result.get('check_count')) is not int
                or type(result.get('checks')) is not list or not result['checks']
                or len(result['checks'])!=result['check_count'] or type(result.get('trace')) is not list or not result['trace']):
            raise ValueError('Missing/empty execution evidence')
        if canonical(result)!=canonical(produce_witness(name)):
            raise ValueError('Execution differs from deterministic trusted replay')


def build_closure(source_review,execution):
    validate_execution(execution)
    accepted=json.loads((HERE/'source_review.json').read_text(encoding='utf-8'))
    if canonical(source_review)!=canonical(accepted): raise ValueError('Source advice differs from accepted expert return')
    for key,value in {'contract_version':'1.0','project_id':'d2d-twin','paper_family':'M','stage_id':'M4',
            'task_id':'lis3dh-v35/source_review','expert_skill':'sci-skills-paper-deep-reading','task_status':'COMPLETE'}.items():
        if source_review.get(key)!=value: raise ValueError('Wrong accepted expert identity: '+key)
    primary=source_review['source']
    root=HERE.parents[1]
    if primary['path']!='corpus/data/raw_pdf/ST/LIS3DH.pdf': raise ValueError('Wrong primary source identity')
    if hashlib.sha256((root/primary['path']).read_bytes()).hexdigest()!=primary['sha256']:
        raise ValueError('Reviewed primary source changed')
    source=HERE.parent/'independent_source_admission_20261012'
    blob=(source/'field_evidence.json').read_bytes()
    expected=json.loads((source/'audit_bundle_manifest.json').read_text(encoding='utf-8'))['files']['field_evidence.json']
    if hashlib.sha256(blob).hexdigest()!=expected: raise ValueError('Frozen source-field authority changed')
    authority={r['register']+'.'+r['field']:{k for k,v in r['dimensions'].items() if v['status']=='REPAIR'}
               for r in json.loads(blob) if r['chip']=='LIS3DH' and r['overall_status']=='REPAIR'}
    advice=source_review['field_closure_advice']
    if len(advice)!=8 or len({r['field'] for r in advice})!=8 or {r['field'] for r in advice}!=set(authority):
        raise ValueError('LIS3DH source field denominator changed')
    claims={r['id']:r for r in source_review['claims']}
    rows=[]
    for item in advice:
        required=item['claims']
        if not required or any(c not in claims for c in required): raise ValueError('Missing/unknown claim')
        missing=[c for c in required if c not in CLAIM_SCENARIOS or any(n not in execution for n in CLAIM_SCENARIOS[c])]
        for dimension in sorted(authority[item['field']]):
            rows.append({'inventory_field_id':'LIS3DH.'+item['field'],'dimension':dimension,'source_verdict':'REPAIR',
                'assessment':'BOUNDED_CLAUSES_VERIFIED' if not missing else 'PARTIAL','required_claim_ids':required,'source_claim_classes':{c:claims[c]['class'] for c in required},
                'missing_claim_ids':missing,'claim_scenarios':{c:CLAIM_SCENARIOS.get(c,[]) for c in required},
                'source_conflict_ids':[r['conflict_id'] for r in source_review['conflicts']],
                'whole_dimension_closed':False,'whole_field_promoted':False,
                'scope':'Sevenknown defaultbits andlegalSTaccess; qualifiedXYZ events; postreadstatus unknown; readconsumption/BDU-release exploratory; no physical/full-source certification'})
    if len(rows)!=8: raise ValueError('LIS3DH dimension denominator changed')
    return rows
