"""Clause-level implementation admission, never a whole-chip/source promotion."""
import hashlib
import json
from pathlib import Path
from scenarios import CLAIM_SCENARIOS, SCENARIOS

HERE=Path(__file__).resolve().parent


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)


def produce_witness(name):
    if name not in SCENARIOS:
        raise ValueError('Unknown scenario identity')
    c=SCENARIOS[name]()
    return {'status':'PASS','check_count':len(c.checks),'checks':c.checks,'trace':c.trace,
            'execution_kind':'SOURCE_TABLE_METADATA' if name=='nominal_cycle_table' else 'DIGITAL_EVENT_PROFILE'}


def validate_execution(execution):
    if not isinstance(execution, dict) or set(execution) - set(SCENARIOS):
        raise ValueError('Unknown scenario identity')
    for name, result in execution.items():
        checks, trace = result.get('checks'), result.get('trace')
        if (result.get('status') != 'PASS' or type(result.get('check_count')) is not int
                or not isinstance(checks, list) or not checks or len(checks) != result['check_count']
                or not isinstance(trace, list) or not trace):
            raise ValueError('Missing/empty execution evidence')
        for check in checks:
            if not isinstance(check, dict) or not isinstance(check.get('clause'), str) or not check['clause']:
                raise ValueError('Missing clause identity')
            if set(check) == {'clause', 'actual', 'expected'}:
                if check['actual'] != check['expected']:
                    raise ValueError('Failed comparison')
            elif set(check) != {'clause', 'outside_contract'} or check['outside_contract'] is not True:
                raise ValueError('Malformed scope evidence')
        if any(not isinstance(op, dict) or op.get('chip') != 'TMP117'
               or op.get('op') not in ('read','write','event') for op in trace):
            raise ValueError('Wrong chip/operation witness')
        if not any(op['op']=='write' and op.get('value',0)!=0 for op in trace):
            raise ValueError('No nonzero stimulus witness')
        if name != 'nominal_cycle_table' and not any(op['op']=='event' for op in trace):
            raise ValueError('No event witness')
        # Exact replay verifies identity/count/value/typed checks and event order.
        # It is local reproducibility, not remote attestation or hardware proof.
        if canonical(result)!=canonical(produce_witness(name)):
            raise ValueError('Execution does not match trusted deterministic replay')


def build_closure(source_review, execution):
    validate_execution(execution)
    accepted=json.loads((HERE/'source_review.json').read_text(encoding='utf-8'))
    if canonical(source_review)!=canonical(accepted):
        raise ValueError('Source advice differs from accepted expert return')
    source=HERE.parent/'independent_source_admission_20261012'
    blob=(source/'field_evidence.json').read_bytes()
    expected=json.loads((source/'audit_bundle_manifest.json').read_text(encoding='utf-8'))['files']['field_evidence.json']
    if hashlib.sha256(blob).hexdigest()!=expected:
        raise ValueError('Frozen source-field authority changed')
    fields=json.loads(blob)
    authority={r['chip']+'.'+r['register']+'.'+r['field']:
               {k for k,v in r['dimensions'].items() if v['status']=='REPAIR'}
               for r in fields if r['chip']=='TMP117' and r['overall_status']=='REPAIR'}
    claims = {r['claim_id']:r for r in source_review['claims']}
    if set(CLAIM_SCENARIOS) - set(claims):
        raise ValueError('Scenario refers to unknown source claim')
    advice = source_review['closure_advice']
    if (len(advice)!=15 or len({r['inventory_field_id'] for r in advice})!=15
            or {r['inventory_field_id'] for r in advice}!=set(authority)):
        raise ValueError('TMP117 source-field denominator changed')
    rows=[]
    for item in advice:
        fid=item['inventory_field_id']
        if not fid.startswith('TMP117.') or item['source_overall_status']!='REPAIR':
            raise ValueError('Foreign/mismatched source field')
        required=item['required_claim_ids']
        if not required or any(c not in claims for c in required):
            raise ValueError('Empty/unknown required source claims')
        dimensions=item['source_repair_dimensions']
        if len(dimensions)!=len(set(dimensions)) or set(dimensions)!=authority[fid]:
            raise ValueError('Source repair-dimension identity differs')
        missing=[c for c in required if c not in CLAIM_SCENARIOS
                 or any(n not in execution for n in CLAIM_SCENARIOS[c])]
        for dimension in item['source_repair_dimensions']:
            rows.append({'inventory_field_id':fid,'dimension':dimension,'source_verdict':'REPAIR',
                         'assessment':'BOUNDED_CLAUSES_VERIFIED' if not missing else 'PARTIAL',
                         'required_claim_ids':required,'missing_claim_ids':missing,
                         'claim_scenarios':{c:CLAIM_SCENARIOS.get(c,[]) for c in required},
                         'whole_dimension_closed':False,'whole_field_promoted':False,
                         'scope':'Declared digital event profile and explicit exclusions only'})
    if len(rows)!=16:
        raise ValueError('TMP117 repair-dimension denominator changed')
    return rows
