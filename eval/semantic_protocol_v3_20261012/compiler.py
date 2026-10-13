"""Validate immutable source candidates and construct a fail-closed repair ledger.

The source policy is evidence, not executable code. Arbitrary prose or JSON
candidate_rule keys are never converted to a passed test or an operation.
"""
import hashlib
import json
from collections import Counter
from pathlib import Path

from runtime import geometry, number

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = HERE.parent / 'independent_source_admission_20261012'
DIMENSIONS = ('reset', 'access', 'legal_encoding', 'read_clear', 'trigger_completion', 'conditional_write', 'reserved_policy')
VERDICTS = {'PASS', 'REPAIR', 'CONDITIONAL', 'EXCLUDE'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def verify_hashes(base, entries):
    base = Path(base).resolve()
    for relative, expected in entries.items():
        path = (base / relative).resolve()
        if not path.is_relative_to(base) or not path.is_file() or sha(path) != expected:
            raise ValueError('Immutable input mismatch: ' + relative)


def validate_policy(ir_map, policy, inventory):
    if policy.get('schema') != 'd2d-source-admission-policy-candidate-1':
        raise ValueError('Unknown source-policy schema')
    if policy.get('field_count') != 572 or set(policy.get('dimensions', [])) != set(DIMENSIONS):
        raise ValueError('Source denominator or dimensions changed')
    expected = {r['chip'] + '.' + r['register'] + '.' + r['field'] for r in inventory}
    rows = policy.get('field_rules', [])
    ids = [r.get('inventory_field_id') for r in rows]
    if len(expected) != 572 or len(rows) != 572 or len(set(ids)) != 572 or set(ids) != expected:
        raise ValueError('Missing, extra or duplicate inventory identity')
    if len(ir_map) != 20:
        raise ValueError('Expected 20 chips')
    actual = {}
    for chip, ir in ir_map.items():
        width = ir['reg_width']
        for r in ir['registers']:
            occupied = 0
            for f in r['fields']:
                mask, lo = geometry(f['bits'])
                if mask >= 1 << width or mask & occupied:
                    raise ValueError('Overlapping/out-of-range field')
                occupied |= mask
                key = (chip, r['name'], f['name'])
                if key in actual:
                    raise ValueError('Duplicate candidate field')
                actual[key] = (r, f, mask, lo)
                if f.get('reset') is not None and not 0 <= number(f['reset']) <= mask >> lo:
                    raise ValueError('Reset outside field width')
        # Aliased read/write addresses are permitted; mapping is field-level.
    if len(actual) != 572:
        raise ValueError('Candidate denominator changed')
    mapped = set()
    for row in rows:
        key = row['chip'], row['register'], row['field']
        if key not in actual or key in mapped:
            raise ValueError('Unmapped/duplicate repaired field geometry')
        mapped.add(key)
        reg, field, mask, _ = actual[key]
        if (field['bits'] != row['bits'] or mask != number(row['candidate_bit_mask'])
                or number(reg['addr']) != number(row['candidate_addr'])
                or field.get('reset') != row['candidate_reset']
                or field.get('access') != row['candidate_access_annotation']):
            raise ValueError('IR/policy geometry or attributes mismatch: ' + row['inventory_field_id'])
        if policy['source_lock'].get(row['source_path']) != row['source_sha256']:
            raise ValueError('Unlocked source identity')
        if row['overall_status'] not in VERDICTS or set(row['dimensions']) != set(DIMENSIONS):
            raise ValueError('Unknown verdict/dimension')
        for d in row['dimensions'].values():
            if d['status'] not in VERDICTS or not isinstance(d.get('candidate_rule'), dict):
                raise ValueError('Unknown verdict or malformed source rule')
    return rows


# Each link is a bounded clause demonstration, never whole-field certification.
CLAUSE_LINKS = [
    ('tmp117_eeprom', 'TMP117.THIGH.H', 'conditional_write', 'Volatile EUN0 vs completed EUN1 programming'),
    ('tmp117_eeprom', 'TMP117.THIGH.H', 'reset', 'POR reloads supplied NVM image, not unconditional factory value'),
    ('tmp117_eeprom', 'TMP117.EEPROM_UL.EUN', 'conditional_write', 'Programming enable and prohibited busy-write stimulus'),
    ('tmp117_eeprom', 'TMP117.CONFIG.EEPROM_BUSY', 'trigger_completion', 'Busy mirror and explicit POR/program completion'),
    ('tmp117_eeprom', 'TMP117.EEPROM_UL.EEPROM_BUSY', 'trigger_completion', 'Busy mirror and explicit POR/program completion'),
    ('tmp117_flags', 'TMP117.CONFIG.HIGH_ALERT', 'read_clear', 'Alert clears on CONFIG read; THERM retains until below-low event'),
    ('tmp117_flags', 'TMP117.CONFIG.LOW_ALERT', 'read_clear', 'Alert low preclear; THERM low remains zero'),
    ('tmp117_flags', 'TMP117.CONFIG.DATA_READY', 'read_clear', 'TEMP or CONFIG read clears DR independently of alert flags'),
    ('tmp126_read_clear', 'TMP126.TEMP_RESULT.TEMP', 'read_clear', 'TEMP read clears DR cross-register'),
    ('tmp126_read_clear', 'TMP126.CONFIG.INT_COMP', 'trigger_completion', 'Comparator to interrupt clears Alert_Status'),
    ('tmp126_average', 'TMP126.CONFIG.ONE_SHOT', 'trigger_completion', 'One-shot completion sets MODE shutdown and DR'),
    ('tmp126_average', 'TMP126.CONFIG.AVG', 'trigger_completion', 'Eight explicit conversions required when AVG1'),
    ('hdc_start_complete', 'HDC2021.MEAS_CONFIG.MEAS_TRIG', 'trigger_completion', 'Start-clear differs from completion'),
    ('hdc_start_complete', 'HDC2021.STATUS.DRDY_STATUS', 'trigger_completion', 'DRDY only at completed conversion'),
    ('hdc_start_complete', 'HDC2021.STATUS.DRDY_STATUS', 'read_clear', 'STATUS returns preclear DRDY'),
    ('hdc_cross_read', 'HDC2021.STATUS.DRDY_STATUS', 'read_clear', 'Each of four data addresses also clears DRDY'),
    ('bosch_commit', 'BME280.ctrl_hum.osrs_h', 'conditional_write', 'Separate stored humidity from ctrl_meas committed setting'),
    ('bosch_commit', 'BME280.config.filter', 'conditional_write', 'Sleep-only config stimulus; nondeterministic normal writes excluded'),
]
CLAUSE_LINKS += [('tmp126_read_clear', 'TMP126.ALERT_STATUS.' + f, 'read_clear',
                 'Nonzero flags clear only on single read without auto increment')
                for f in ('CRC_FLAG', 'SLEW_FLAG', 'THIGH_FLAG', 'TLOW_FLAG', 'DATA_READY_FLAG')]
CLAUSE_LINKS += [('bosch_forced', chip + '.ctrl_meas.mode', 'trigger_completion',
                 'Both forced codes return to sleep on explicit measurement completion')
                for chip in ('BME280', 'BMP280')]


def compile_ledger(rows, execution):
    from scenarios import SCENARIOS
    if not isinstance(execution, dict) or set(execution) - set(SCENARIOS):
        raise ValueError('Unknown execution scenario')
    for name, result in execution.items():
        checks, trace = result.get('checks'), result.get('trace')
        if (result.get('status') != 'PASS' or type(result.get('assertions')) is not int
                or not isinstance(checks, list) or not checks or len(checks) != result['assertions']
                or not isinstance(trace, list) or not trace):
            raise ValueError('Missing or vacuous execution evidence: ' + name)
        for check in checks:
            if not isinstance(check, dict) or not isinstance(check.get('clause'), str) or not check['clause']:
                raise ValueError('Invalid execution clause')
            if set(check) == {'clause', 'actual', 'expected'}:
                if (type(check['actual']) is not int or type(check['expected']) is not int
                        or check['actual'] != check['expected']):
                    raise ValueError('Failed or unsupported comparison')
            elif set(check) != {'clause', 'outside_contract'} or check['outside_contract'] is not True:
                raise ValueError('Invalid outside-contract evidence')
        for operation in trace:
            if (not isinstance(operation, dict) or operation.get('chip') not in ('TMP117','TMP126','HDC2021','BME280','BMP280')
                    or operation.get('op') not in ('write','read','event')):
                raise ValueError('Invalid execution trace')
        expected_chips = ({'BME280', 'BMP280'} if name == 'bosch_forced' else
                          {'BME280'} if name == 'bosch_commit' else
                          {'HDC2021'} if name.startswith('hdc_') else
                          {'TMP126'} if name.startswith('tmp126_') else {'TMP117'})
        if {op['chip'] for op in trace} != expected_chips:
            raise ValueError('Scenario chip/trace mismatch')
        if not any(op['op'] == 'write' and op.get('value', 0) != 0 for op in trace):
            raise ValueError('No nonzero stimulus witness')
        if name != 'bosch_commit' and not any(op['op'] == 'event' for op in trace):
            raise ValueError('No required completion/event witness')
    by_id = {r['inventory_field_id']: r for r in rows}
    links = {}
    for name, fid, dim, clause in CLAUSE_LINKS:
        if name not in SCENARIOS or fid not in by_id or dim not in DIMENSIONS:
            raise ValueError('Unknown executable scenario or field/dimension')
        if name in execution:
            result = execution[name]
            if result.get('status') != 'PASS' or result.get('assertions', 0) <= 0:
                raise ValueError('Failed or vacuous scenario: ' + name)
            if by_id[fid]['dimensions'][dim]['evidence_class'] == 'SOURCE_CONFLICT':
                raise ValueError('Source-conflicted aspect cannot be admitted')
            links.setdefault((fid, dim), []).append({'scenario': name, 'clause': clause})
    ledger = []
    for row in rows:
        for dim in DIMENSIONS:
            d = row['dimensions'][dim]
            rule = d['candidate_rule']
            excluded = d['status'] == 'EXCLUDE' or d['evidence_class'] in ('SOURCE_CONFLICT', 'UNDEFINED_BEHAVIOR')
            nonapplicable = (rule.get('applicable') is False or rule.get('assertion') in ('none_claimed', 'not_applicable'))
            demonstrations = links.get((row['inventory_field_id'], dim), [])
            status = ('SOURCE_EXCLUDED' if excluded else 'NOT_APPLICABLE' if nonapplicable
                      else 'PARTIAL_CLAUSES_EXECUTED' if demonstrations else 'EXECUTION_PENDING')
            ledger.append({'inventory_field_id': row['inventory_field_id'], 'dimension': dim,
                           'source_verdict': d['status'], 'evidence_class': d['evidence_class'],
                           'implementation_status': status, 'whole_dimension_closed': False,
                           'executed_clauses': demonstrations, 'source_locators': d['locators'],
                           'candidate_rule_sha256': hashlib.sha256(json.dumps(rule, sort_keys=True, ensure_ascii=False).encode()).hexdigest()})
    assert len(ledger) == 4004
    return ledger


def production_gate(rows, ledger, generation_context=None):
    """No vacuous success; new input freeze requires all declared gates closed."""
    if len(rows) != 572 or len(ledger) != 4004:
        raise ValueError('Incomplete gate denominator')
    pairs = [(r['inventory_field_id'], r['dimension']) for r in ledger]
    if len(set(pairs)) != 4004:
        raise ValueError('Duplicate gate identity')
    verdicts = Counter(r['overall_status'] for r in rows)
    implementation = Counter(r['implementation_status'] for r in ledger)
    # Runtime traces cannot promote source review status or certify all clauses.
    return {'production_generation_ready': False, 'status': 'NOT_ADMITTED',
            'source_field_verdicts': dict(verdicts), 'implementation_dimensions': dict(implementation),
            'reason': ['Whole source dimensions are not closed by bounded clause demonstrations',
                       'Unresolved source conflicts remain excluded',
                       'Full static/event harness and generation context not yet admitted'],
            'generation_context_supplied': generation_context is not None}


def verified_inputs():
    bundle = load(SOURCE / 'audit_bundle_manifest.json')
    verify_hashes(SOURCE, bundle['files'])
    verify_hashes(ROOT, bundle['source_files'])
    policy = load(SOURCE / 'candidate_source_policy.json')
    inventory = load(HERE.parent / 'protocol_v2_20261012/field_policy_inventory.json')
    ir_map = {p.name.removesuffix('_gold_ir.json'): load(p) for p in (SOURCE / 'candidate_ir').glob('*.json')}
    rows = validate_policy(ir_map, policy, inventory)
    return rows, bundle
