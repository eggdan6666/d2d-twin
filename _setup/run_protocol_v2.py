"""Prepare/admit/rescore protocol v2 without changing historical inputs.

Commands: python _setup/run_protocol_v2.py --prepare
          python _setup/run_protocol_v2.py --references
          python _setup/run_protocol_v2.py --models
"""
import argparse
import concurrent.futures
import csv
import hashlib
import json
import os
import platform
from pathlib import Path
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'eval/ir_freeze_20261012'
REPAIR = ROOT / 'eval/ir_source_repair_candidate_20261012'
OUT = ROOT / 'eval/protocol_v2_20261012'
TAGS = ('qwen3b', 'ds67b', 'qwen14b')
VERSION = '2.0-candidate-20261012.1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def policy():
    lis = {'fields': {'CTRL_REG1.ODR': {'legal_values': list(range(10))},
                      **{name: {'known_reset': True, 'fixed_write': val}
                         for name, val in {'CTRL_REG0.FIXED_6': 0, 'CTRL_REG0.FIXED_5': 0,
                                           'CTRL_REG0.FIXED_4': 1, 'CTRL_REG0.FIXED_3_0': 0,
                                           'TEMP_CFG_REG.FIXED_5_0': 0}.items()}},
           'constraints': [
               {'when': {'CTRL_REG1.ODR': [8]}, 'set': {'CTRL_REG1.LPen': 1, 'CTRL_REG4.HR': 0}},
               {'when': {'CTRL_REG4.HR': [1]}, 'set': {'CTRL_REG1.LPen': 0}},
           ], 'source': 'ST/LIS3DH.pdf pp.16,35,37 Tables10,31'}
    ads = {'fields': {key: {'legal_values': values} for key, values in {
               'CONFIG0.MUX': list(range(15)), 'CONFIG1.MODE': list(range(3)),
               'CONFIG1.DR': list(range(7)), 'CONFIG3.I1MUX': list(range(7)),
               'CONFIG3.I2MUX': list(range(7)), 'CONFIG3.RESERVED': [0]}.items()},
           'constraints': [
               {'when': {'CONFIG0.MUX': [8, 9, 10, 11]},
                'set': {'CONFIG0.GAIN': 0, 'CONFIG0.PGA_BYPASS': 1}},
               {'when': {'CONFIG0.MUX': [12, 13]}, 'set': {'CONFIG0.PGA_BYPASS': 1}},
               {'when': {'CONFIG2.FIFTY_SIXTY': [1, 2, 3]},
                'set': {'CONFIG1.MODE': 0, 'CONFIG1.DR': 0}},
           ], 'source': 'TI/ADS1220.pdf SBAS501D pp.43-46 Tables8-10..8-14'}
    ads['fields']['CONFIG3.RESERVED']['fixed_write'] = 0
    bosch = {}
    for chip in ('BME280', 'BMP280'):
        fields = {'config.UNUSED': {'exclude': 'Grey do-not-change/write bit; no storage oracle',
                                    'fixed_write': 0, 'known_reset': True},
                  'status.UNUSED': {'exclude': 'Grey source bit, no known readback oracle'},
                  'status.UNUSED2': {'exclude': 'Grey source bit, no known readback oracle'}}
        if chip == 'BME280':
            fields['ctrl_hum.UNUSED'] = {'exclude': 'Grey do-not-change/write bits', 'fixed_write': 0}
            for name in ('press_xlsb', 'temp_xlsb'):
                fields[name + '.UNUSED'] = {'verified_access': True, 'known_reset': True,
                                            'source': 'p.27 Table18 explicit RO zero bits'}
        bosch[chip] = {'fields': fields,
                      'source': 'Bosch/' + chip + '.pdf Table18 p.' + ('27' if chip == 'BME280' else '24')}
        bosch[chip]['fields']['ctrl_meas.mode'] = {
            'legal_values': [0, 1, 2, 3], 'test_values': [0, 3],
            'excluded_behavior': 'Forced modes1/2 complete then return tosleep; no completion model'}
    hdc = {'fields': {
        'STATUS.UNUSED': {'exclude': 'Reset0 known; access unspecified', 'known_reset': True, 'fixed_write': 0},
        'INTERRUPT_ENABLE.UNUSED': {'exclude': 'Reset0 known; access unspecified', 'known_reset': True, 'fixed_write': 0},
        'MEAS_CONFIG.TACC': {'legal_values': [0, 1, 2]},
        'MEAS_CONFIG.HACC': {'legal_values': [0, 1, 2]},
        'MEAS_CONFIG.MEAS_CONF': {'legal_values': [0, 1]},
        'MEAS_CONFIG.RSVD3': {'exclude': 'RW label known, no defined function; conservative scope',
                             'fixed_write': 0, 'known_reset': True},
    }, 'source': 'TI/HDC2021.pdf pp.23,25,31 Tables7-16,7-22,7-38'}
    return {'protocol_version': VERSION,
            'scope': 'Prospective static register MVP, factory defaults, no analog or physical bus validation',
            'default_rules': ['UNSPEC and unverified access omitted from field scoring',
                              'Known reset and known access handled separately',
                              'Declared domains exhaustive except explicit temporal test_values exclusions; unconstrained fields boundary0/max only',
                              'Fresh instance for each stimulus; no cross-test shared state',
                              'Mandatory constant inputs are not writability evidence',
                              'Original8 aggregate dimensions, empty applicable sets skipped',
                              'Reset-key checks include one legal state perturbation'],
            'source_certification': 'Bounded reviewed repairs/policies, not certification of all572 fields',
            'chips': {'LIS3DH': lis, 'ADS1220': ads,
                      'TMP117': {'registers': {'DEVICE_ID': {'known_mask': '0x0FFF'}},
                                 'fields': {'CONFIG.MOD': {'legal_values': [0, 1, 2, 3],
                                                           'test_values': [0, 1, 2],
                                                           'excluded_behavior': 'MOD3 one-shot completion/timing outside persistence oracle',
                                                           'readback_values': {'2': 0}}},
                                 'source': 'TI/TMP117.pdf p.32 Figure7-22 versus Table7-15; factory EEPROM defaults assumed'},
                      'INA3221': {'registers': {'SHUNT_SUM_LIMIT': {
                          'known_mask': '0x8001', 'exclude_writes': 'Unresolved source access/reset conflict'}},
                          'fields': {'MASK_ENABLE.RSVD15': {'exclude': 'Reserved function unverified; keep default',
                                                         'fixed_write': 0, 'known_reset': True}},
                          'source': 'TI/INA3221.pdf p.33 Tables8-31/8-32; bits14:1 quarantined'},
                      'LIS2DW12': {'fields': {
                          'CTRL1.ODR': {'legal_values': list(range(10))},
                          'CTRL1.MODE': {'legal_values': [0, 1, 2]},
                          'FIFO_CTRL.FMODE': {'legal_values': [0, 1, 3, 4, 6]},
                          'CTRL2.MUST_BE_ZERO': {'exclude': 'Must write0; no oracle for illegal1',
                                                 'fixed_write': 0, 'known_reset': True},
                          'CTRL2.BOOT': {'exclude': 'Self-clears after NVM operation; completion/timing not modeled',
                                        'fixed_write': 0, 'known_reset': True}},
                          'source': 'ST/lis2dw12.pdf DS11811 Rev9 p.37 Table32 and BOOT description'},
                      'TMP461': {'fields': {
                          'CONV_RATE.CR': {'legal_values': list(range(10))},
                          'CONSECUTIVE_ALERT.CONAL': {'legal_values': [0, 1, 3, 7]},
                          'DIGITAL_FILTER.DF': {'legal_values': [0, 1, 2]},
                          **{q: {'exclude': 'Source requires default write0; no nonzero input oracle',
                                 'fixed_write': 0, 'known_reset': True}
                             for q in ('CONFIG.RSV_4_3', 'CONFIG.RSV_1_0')},
                          'CONSECUTIVE_ALERT.FIXED_1': {'exclude': 'Keep bit0=1 for listed register inputs',
                                                       'fixed_write': 1, 'known_reset': True}},
                          'source': 'TI/TMP461.pdf p.21 Tables7/8 and p.12 section8.3.4'},
                      'MPU6050': {'fields': {'CONFIG.DLPF_CFG': {'legal_values': list(range(7))},
                                            'PWR_MGMT_1.CLKSEL': {'legal_values': [0, 1, 2, 3, 4, 5, 7]},
                                            'PWR_MGMT_1.DEVICE_RESET': {'verified_access': True, 'known_reset': True,
                                                'source': 'RM-MPU-6000A-00 Rev4.2 pp.8,40-41; prior independent review signoff',
                                                'abstraction': 'Atomic completed reset in register MVP; elapsed time not verified'}},
                                  'source': 'MPU-6000 register map Rev4.2 pp.13,40'},
                      'AD5592R': {'fields': {'DAC_RD.DAC_RD_EN': {'legal_values': [0, 3]}},
                                  'source': 'ADI/ad5592r.pdf p.29 DAC READBACK requires bits4:3=11; Table15 grouping ambiguous'},
                      'TPS23861': {'fields': {
                          **{q: {'exclude': 'Reserved reset unspecified; preserve fresh observed bits',
                                 'preserve_write': True}
                             for q in ('GENERAL_MASK.RSV3', 'GENERAL_MASK.RSV2', 'GENERAL_MASK.ROM1')},
                          'INTERRUPT_TIMER.ROM': {'exclude': 'Must retain reset0; no nonzero input oracle',
                                                  'fixed_write': 0, 'known_reset': True}},
                          'source': 'TI/TPS23861.pdf p.63 R17[3:1] reset Reserved; p.68 R27[7:4] reset0'},
                      'HDC2021': hdc, **bosch}}


def prepare():
    if (OUT / 'model_results.json').exists():
        raise RuntimeError('This version has model evidence; prepare a new version instead of overwriting its inputs')
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(OUT / 'source_policy.json', policy())
    (OUT / '.gitattributes').write_text('* -text\n', encoding='utf-8')
    (OUT / '.gitignore').write_text('work/\n__pycache__/\n.pytest_cache/\n', encoding='utf-8')
    edits = []
    for path in sorted((REPAIR / 'ir').glob('*.json')):
        ir = json.loads(path.read_text(encoding='utf-8'))
        if ir['device'] == 'ADS1220':
            descriptions = {
                'CONFIG0.GAIN': 'PGA gain: codes0..7 correspond to gain1..128; p.43 Table8-10',
                'CONFIG1.MODE': 'Operating mode: normal/duty-cycle/turbo codes0..2; code3 reserved; p.44',
                'CONFIG1.CM': '0 single-shot, 1 continuous conversion; p.44 Table8-11',
                'CONFIG2.VREF': 'Reference codes0..3 all defined; code3 analog supply; p.45 Table8-13',
                'CONFIG2.IDAC': 'Codes0..7 all defined; code7=1500 microampere; p.45 Table8-13',
                'CONFIG3.RESERVED': 'R/W-0 label plus explicit Always write0b; only0 input allowed, no writability scoring; p.46 Table8-14',
            }
            for r in ir['registers']:
                for f in r['fields']:
                    key = r['name'] + '.' + f['name']
                    if key in descriptions:
                        edits.append({'chip': ir['device'], 'field': key, 'before': f.get('desc'),
                                      'after': descriptions[key]})
                        f['desc'] = descriptions[key]
            ir['source_repair_note_v2'] = 'This note and policy supersede conflicting historical descriptions/proofread_record; legal input is explicit in source_policy.json.'
        if ir['device'] == 'TMP117':
            config = next(r for r in ir['registers'] if r['name'] == 'CONFIG')
            for f in config['fields']:
                if f['name'] in ('MOD', 'AVG'):
                    desc = ('MOD codes00 continuous,01 shutdown,10 continuous with readback00,11 one-shot; p.27 Table7-6'
                            if f['name'] == 'MOD' else 'AVG codes0/1/2/3 = no averaging/8/32/64 conversions; p.27 Table7-6')
                    edits.append({'chip': ir['device'], 'field': 'CONFIG.' + f['name'],
                                  'before': f.get('desc'), 'after': desc})
                    f['desc'] = desc
        annotation_fixes = {
            'TMP102': {'CONFIG.CR1': 'CR[1:0] codes00/01/10/11 = 0.25/1/4/8Hz; default10=4Hz; p.15 Table6-5',
                       'CONFIG.CR0': 'Low bit of conversion rate; see CR1 corrected code table'},
            'BME280': {'ctrl_meas.mode': '00 sleep,01/10 forced,11 normal; forced completion outside static storage scoring; p.29 section5.4.5',
                       'config.t_sb': 'codes0..7 = 0.5/62.5/125/250/500/1000/10/20ms; p.30 Table27'},
            'TMP1075': {'CFGR.F': 'Fault queue codes00/01/10/11 = 1/2/3/4 for non-N TMP1075; N variant differs; p.22 Table7-8'},
            'TMP126': {'CONFIG.CONV_PERIOD': 'codes0..7 = 6/31.25/62.5/125/250/500ms/1/2s; code7=2s(0.5Hz); p.29 Table8-8'},
        }.get(ir['device'], {})
        for r in ir['registers']:
            for f in r.get('fields', []):
                key = r['name'] + '.' + f['name']
                if key in annotation_fixes:
                    edits.append({'chip': ir['device'], 'field': key, 'before': f.get('desc'),
                                  'after': annotation_fixes[key]})
                    f['desc'] = annotation_fixes[key]
        (OUT / 'ir').mkdir(exist_ok=True)
        write_json(OUT / 'ir' / path.name, ir)
    for p in (BASE / 'references').glob('*.py'):
        source = REPAIR / 'references' / p.name
        if not source.exists():
            source = p
        (OUT / 'references').mkdir(exist_ok=True)
        raw = source.read_bytes()
        if p.name == 'tmp117_reference.py':
            text = raw.decode('utf-8')
            text = text.replace('        return v\n',
                '        # p.27 Table7-6: MOD=10 reads back00; mode functionality outside this MVP.\n'
                '        if addr == 0x01 and (v & 0x0C00) == 0x0800:\n'
                '            v &= ~0x0C00\n'
                '        return v\n')
            assert text != raw.decode('utf-8'), 'TMP117 normalization patch did not match'
            raw = text.encode('utf-8')
        (OUT / 'references' / p.name).write_bytes(raw)
    (OUT / 'rtl').mkdir(exist_ok=True)
    (OUT / 'rtl/base_sensor.py').write_bytes((BASE / 'rtl/base_sensor.py').read_bytes())
    write_json(OUT / 'additional_ir_annotation_repairs.json', edits)
    sys.path.insert(0, str(OUT / 'harness'))
    from protocol_rules import Contract
    coverage = []
    for p in sorted((OUT / 'ir').glob('*.json')):
        ir = json.loads(p.read_text(encoding='utf-8'))
        contract = Contract(ir, policy())
        # Validate every planned ordinary RW input before execution.
        for q, v in contract.rw_cases():
            contract.writes(q, v)
        coverage.append({'chip': ir['device'], 'applicability': contract.applicable(),
                         'rw_stimuli': len(contract.rw_cases()), 'ro_field_cases': len(contract.ro_field_cases()),
                         'reset_known_masks': {rn: hex(contract.known_mask(rn)) for rn in contract.regs},
                         'protection_known_masks': {rn: hex(contract.known_mask(rn, 'protection')) for rn in contract.regs}})
    write_json(OUT / 'coverage_plan.json', coverage)
    files = {p.relative_to(OUT).as_posix(): sha(p) for folder in ('ir', 'references', 'rtl', 'harness')
             for p in (OUT / folder).glob('*') if p.is_file() and p.suffix in ('.py', '.json')
             and p.name != 'd2d_diag.json'}
    files['source_policy.json'] = sha(OUT / 'source_policy.json')
    write_json(OUT / 'protocol_manifest.json', {
        'version': VERSION, 'status': 'CANDIDATE_NOT_PROMOTED', 'files': files,
        'frozen_v1_harness_md5': hashlib.md5((ROOT / 'd2d/eval/test_d2d_blackbox.py').read_bytes()).hexdigest(),
        'base_freeze_manifest_sha256': sha(BASE / 'freeze_manifest.json'),
        'repair_manifest_sha256': sha(REPAIR / 'repair_manifest.json')})
    print('PREPARED: 20 chips, all ordinary RW stimuli validated', flush=True)


def verify():
    manifest = json.loads((OUT / 'protocol_manifest.json').read_text(encoding='utf-8'))
    for path, digest in manifest['files'].items():
        assert sha(OUT / path) == digest, path
    assert hashlib.md5((ROOT / 'd2d/eval/test_d2d_blackbox.py').read_bytes()).hexdigest() == '8cf0854d4779467bc8e472ee4fb97023'


def run_one(job):
    model, chip, seed, index, code, original = job
    folder = OUT / 'work' / model / chip / f'{seed}_{index}'
    folder.mkdir(parents=True, exist_ok=True)
    # Exact generated files only: prevent stale evidence on failed reruns.
    for name in ('result.xml', 'd2d_diag.json', 'pytest.log'):
        (folder / name).unlink(missing_ok=True)
    for name in ('protocol_rules.py', 'test_d2d_protocol_v2.py'):
        (folder / name).write_bytes((OUT / 'harness' / name).read_bytes())
    (folder / (chip.lower() + '_simulator.py')).write_text(code or '', encoding='utf-8')
    env = dict(os.environ, D2D_V2_ROOT=str(OUT), D2D_IR=chip + '_gold_ir.json', D2D_DIAG='1',
               PYTEST_DISABLE_PLUGIN_AUTOLOAD='1', PYTHONIOENCODING='utf-8')
    start = time.monotonic()
    try:
        proc = subprocess.run([sys.executable, '-m', 'pytest', 'test_d2d_protocol_v2.py', '-q',
                               '--tb=short', '--junitxml=result.xml'], cwd=folder, env=env,
                              capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=90)
        rc, log = proc.returncode, proc.stdout + '\n' + proc.stderr
    except subprocess.TimeoutExpired:
        rc, log = 124, 'Timed out; no semantic score assigned.'
    (folder / 'pytest.log').write_text(log, encoding='utf-8')
    tests = []
    if (folder / 'result.xml').exists():
        for case in ET.parse(folder / 'result.xml').findall('.//testcase'):
            node = next((case.find(k) for k in ('failure', 'error', 'skipped') if case.find(k) is not None), None)
            status = {'failure': 'failed', 'error': 'error', 'skipped': 'skipped'}.get(node.tag if node is not None else '', 'passed')
            tests.append({'test': case.attrib['name'], 'status': status,
                          'message': node.attrib.get('message', '') if node is not None else '',
                          'detail': node.text or '' if node is not None else ''})
    trace_path = folder / 'd2d_diag.json'
    trace = json.loads(trace_path.read_text(encoding='utf-8')) if trace_path.exists() else {}
    return {'model': model, 'chip': chip, 'seed': seed, 'i': index, 'rc': rc, 'tests': tests,
            'passed': sum(t['status'] == 'passed' for t in tests),
            'original_rc': original.get('rc'), 'original_passed': original.get('passed'),
            'code_sha256': hashlib.sha256((code or '').encode('utf-8')).hexdigest(),
            'seconds': time.monotonic() - start,
            'assertions_executed': len(trace.get('assertions', [])),
            'stimuli_executed': len(trace.get('stimuli', [])),
            'log_file': (folder / 'pytest.log').relative_to(OUT).as_posix()}


def run(models=False):
    verify()
    if models:
        admission = json.loads((OUT / 'reference_results.json').read_text(encoding='utf-8'))
        assert len(admission) == 20 and all(r['rc'] == 0 for r in admission), 'Reference admission must pass first'
        execution = json.loads((OUT / 'reference_execution_manifest.json').read_text(encoding='utf-8'))
        assert execution['protocol_manifest_sha256'] == sha(OUT / 'protocol_manifest.json'), 'Reference admission is stale for this protocol'
    jobs, inputs = [], []
    for p in sorted((OUT / 'ir').glob('*.json')):
        chip = json.loads(p.read_text(encoding='utf-8'))['device']
        if not models:
            jobs.append(('reference', chip, 0, 0,
                         (OUT / 'references' / (chip.lower() + '_reference.py')).read_text(encoding='utf-8'), {}))
        else:
            for tag in TAGS:
                path = ROOT / f'eval/expansion_{tag}/results_gen_{tag}_{chip.lower()}.json'
                records = json.loads(path.read_text(encoding='utf-8'))
                assert len(records) == 12 and {(r['seed'], r['i']) for r in records} == {(s, i) for s in (1, 2, 3) for i in range(4)}
                inputs.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path)})
                jobs.extend((tag, chip, r['seed'], r['i'], r.get('code'), r) for r in records)
    start, rows = time.monotonic(), []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(run_one, job) for job in jobs]
        for completed, f in enumerate(concurrent.futures.as_completed(futures), 1):
            rows.append(f.result())
            if completed % 40 == 0 or completed == len(jobs):
                print(f'PROTOCOL V2 {completed}/{len(jobs)} elapsed={time.monotonic()-start:.1f}s', flush=True)
    rows.sort(key=lambda r: (r['model'], r['chip'], r['seed'], r['i']))
    name = 'model' if models else 'reference'
    write_json(OUT / (name + '_results.json'), rows)
    with zipfile.ZipFile(OUT / (name + '_pytest_evidence.zip'), 'w', zipfile.ZIP_DEFLATED) as archive:
        for r in rows:
            folder = OUT / Path(r['log_file']).parent
            for f in folder.iterdir():
                if f.name in ('pytest.log', 'result.xml', 'd2d_diag.json'):
                    archive.write(f, f.relative_to(OUT / 'work').as_posix())
    summary = [{'model': tag, 'samples': sum(r['model'] == tag for r in rows),
                'green': sum(r['model'] == tag and r['rc'] == 0 for r in rows),
                **{status: sum(t['status'] == status for r in rows if r['model'] == tag for t in r['tests'])
                   for status in ('passed', 'failed', 'error', 'skipped')},
                'timeout': sum(r['model'] == tag and r['rc'] == 124 for r in rows)}
               for tag in (TAGS if models else ('reference',))]
    write_json(OUT / (name + '_summary.json'), summary)
    write_json(OUT / (name + '_execution_manifest.json'), {
        'status': 'EXECUTED_LOCAL', 'command': 'python _setup/run_protocol_v2.py --' + ('models' if models else 'references'),
        'python': platform.python_version(), 'elapsed_seconds': time.monotonic() - start,
        'workers': 4, 'inputs': inputs, 'protocol_manifest_sha256': sha(OUT / 'protocol_manifest.json'),
        'evidence_archive_sha256': sha(OUT / (name + '_pytest_evidence.zip')),
        'generation': 'none', 'summary': summary})
    for f in inputs:
        assert sha(ROOT / f['path']) == f['sha256'], 'Historical result changed: ' + f['path']
    verify()
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    flags = parser.add_mutually_exclusive_group(required=True)
    flags.add_argument('--prepare', action='store_true')
    flags.add_argument('--references', action='store_true')
    flags.add_argument('--models', action='store_true')
    args = parser.parse_args()
    if args.prepare:
        prepare()
    else:
        run(models=args.models)
