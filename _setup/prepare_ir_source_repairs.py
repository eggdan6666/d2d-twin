"""Prepare auditable IR repair candidates without promoting them into d2d/."""
import copy
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import freeze_and_recheck_20chip as recheck

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'eval/ir_freeze_20261012'
OUT = ROOT / 'eval/ir_source_repair_candidate_20261012'
LOCATORS = {
    'INA3221': 'INA3221.pdf p.33 Table 8-31: diagram/reset agree; Table 8-32 conflicts',
    'TMP100': 'TMP100.pdf p.18 Tables 11-14 and final paragraph',
    'TMP102': 'TMP102.pdf p.19 Tables 6-13 to 6-16 and reset prose',
    'TMP1075': 'TMP1075.pdf p.23 Figures 7-14/7-15 and Tables 7-9/7-10',
    'TMP117': 'TMP117.pdf pp.25-26,29,32 register map and field tables',
    'TPS23861': 'TPS23861.pdf p.47 Interrupt Register POR row',
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    edits = []
    issues = json.loads((BASE / 'schema_issues.json').read_text(encoding='utf-8'))
    irs = {p.stem.replace('_gold_ir', ''): json.loads(p.read_text(encoding='utf-8'))
           for p in (BASE / 'ir').glob('*.json')}
    for issue in issues:
        chip = issue['chip']
        register = next(r for r in irs[chip]['registers'] if r['name'] == issue['register'])
        field = next(f for f in register['fields'] if f['name'] == issue['field'])
        bounds = [int(x) for x in field['bits'].split(':')]
        hi, lo = bounds[0], bounds[-1]
        value = (int(register['reset'], 16) >> lo) & ((1 << (hi - lo + 1)) - 1)
        edits.append({'chip': chip, 'register': register['name'], 'field': field['name'],
                      'path': 'fields.reset', 'before': field['reset'], 'after': value,
                      'source': LOCATORS[chip],
                      'status': 'AI_SOURCE_REVIEWED_PENDING_INDEPENDENT_RECHECK'})
        field['reset'] = value
    ir = irs['TMP100']
    for register in ir['registers']:
        if register['name'] not in ('TLOW', 'THIGH'):
            continue
        register['desc'] = '12-bit threshold storage at all converter resolutions; TMP100.pdf p.18 Tables 11-14 and final paragraph.'
        for field in register['fields']:
            if field['name'] in ('L', 'H'):
                edits.append({'chip': 'TMP100', 'register': register['name'], 'field': field['name'],
                              'path': 'fields.bits', 'before': '15:7', 'after': '15:4',
                              'source': LOCATORS['TMP100'], 'status': 'AI_SOURCE_REVIEWED_PENDING_INDEPENDENT_RECHECK'})
                edits.append({'chip': 'TMP100', 'register': register['name'], 'field': field['name'],
                              'path': 'fields.reset_after_width_change', 'before': field['reset'],
                              'after': int(register['reset'], 16) >> 4, 'source': LOCATORS['TMP100'],
                              'status': 'AI_SOURCE_REVIEWED_PENDING_INDEPENDENT_RECHECK'})
                field.update(bits='15:4', reset=int(register['reset'], 16) >> 4,
                             desc='12-bit threshold; independent of ADC conversion resolution')
            elif field['name'] == 'UNUSED':
                edits.append({'chip': 'TMP100', 'register': register['name'], 'field': field['name'],
                              'path': 'fields.bits', 'before': '6:0', 'after': '3:0',
                              'source': LOCATORS['TMP100'], 'status': 'AI_SOURCE_REVIEWED_PENDING_INDEPENDENT_RECHECK'})
                field.update(bits='3:0', reset=0, tier='SOURCE_EXPLICIT_ZERO',
                             tier_evidence='TMP100.pdf p.18 Tables 12 and 14 show lower nibble zero',
                             desc='Unused low four bits, fixed zero in threshold format')
    ir['source_repair_note'] = 'Prospective source repair: thresholds retain 12 bits at all ADC resolutions. Historical proofread_record describes the superseded 9-bit threshold interpretation.'
    for chip, ir in irs.items():
        path = OUT / 'ir' / f'{chip}_gold_ir.json'
        recheck.freeze(path, json.dumps(ir, ensure_ascii=False, indent=2).encode('utf-8'))
    recheck.freeze(OUT / 'rtl/base_sensor.py', (BASE / 'rtl/base_sensor.py').read_bytes())
    recheck.freeze(OUT / 'harness/test_d2d_blackbox.py', (BASE / 'harness/test_d2d_blackbox.py').read_bytes())
    reference = (BASE / 'references/tmp100_reference.py').read_text(encoding='utf-8')
    reference = reference.replace('0x02: 0xFF80, 0x03: 0xFF80', '0x02: 0xFFF0, 0x03: 0xFFF0')
    reference = '"""Prospective TMP100 reference: 12-bit threshold storage, source p.18.\nHistorical commentary below is superseded for threshold widths.\n"""\n' + reference
    recheck.freeze(OUT / 'references/tmp100_reference.py', reference.encode('utf-8'))
    manifest = {'status': 'REPAIR_CANDIDATE_NOT_PROMOTED', 'edits': edits,
                'boundaries': ['No original generated code or score changed', 'No d2d/IR or frozen harness edited',
                               'Independent review pending; known protocol constraints remain open'],
                'files': {p.relative_to(OUT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                          for folder in ('ir', 'rtl', 'harness', 'references')
                          for p in (OUT / folder).rglob('*') if p.is_file()}}
    (OUT / 'repair_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    # Keep the scoring code identical; only the candidate input path differs.
    recheck.OUT = OUT
    jobs = [('reference_repaired', 'TMP100', 0, 0, reference, {})]
    jobs.append(('reference_original', 'TMP100', 0, 0,
                 (BASE / 'references/tmp100_reference.py').read_text(encoding='utf-8'), {}))
    for tag in recheck.TAGS:
        records = json.loads((ROOT / f'eval/expansion_{tag}/results_gen_{tag}_tmp100.json').read_text(encoding='utf-8'))
        jobs.extend((tag, 'TMP100', r['seed'], r['i'], r['code'], r) for r in records)
    with recheck.concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(recheck.run_one, jobs))
    recheck.write_json('tmp100_sensitivity.json', rows)
    print(json.dumps([{'model': tag, 'green': sum(r['rc'] == 0 for r in rows if r['model'] == tag),
                      'passed': sum(r['passed'] for r in rows if r['model'] == tag),
                      'changed': sum(r['matches_original'] is False for r in rows if r['model'] == tag)}
                     for tag in ('reference_original', 'reference_repaired') + recheck.TAGS]), flush=True)


if __name__ == '__main__':
    main()
