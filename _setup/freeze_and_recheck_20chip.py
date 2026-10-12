"""Freeze the current candidate IRs and rescore existing code with full evidence.

No model generation, harness edits, or raw-score overwrites. Run from any cwd.
"""
import concurrent.futures
import argparse
import csv
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'eval/ir_freeze_20261012'
HARNESS = ROOT / 'd2d/eval/test_d2d_blackbox.py'
TAGS = ('qwen3b', 'ds67b', 'qwen14b')
EXPECTED_MD5 = '8cf0854d4779467bc8e472ee4fb97023'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def freeze(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != data:
        raise RuntimeError('Frozen input differs; use a new version: ' + str(path))
    path.write_bytes(data)


def write_json(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def write_csv(name, rows):
    with (OUT / name).open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def preflight():
    assert hashlib.md5(HARNESS.read_bytes()).hexdigest() == EXPECTED_MD5
    files = sorted((ROOT / 'd2d/ir').glob('*_gold_ir.json'))
    assert len(files) == 20
    entries, issues, fields = [], [], []
    for path in files:
        raw = path.read_bytes()
        ir = json.loads(raw)
        chip = ir['device']
        width = ir.get('reg_width', 16)
        names, addresses = set(), set()
        for register in ir['registers']:
            name = register['name']
            addr = int(register['addr'], 16)
            assert name not in names and addr not in addresses, (chip, name)
            names.add(name)
            addresses.add(addr)
            assert register['access'] in ('RO', 'RW', 'W'), (chip, name)
            reset = int(register['reset'], 16) if 'reset' in register else None
            if reset is not None:
                assert 0 <= reset < 1 << width, (chip, name, reset)
            elif not register.get('runtime_value') and register['access'] != 'W':
                issues.append({'chip': chip, 'register': name, 'issue': 'Static register lacks reset'})
            occupied = 0
            for field in register.get('fields', []):
                bits = [int(v) for v in field['bits'].split(':')]
                hi, lo = bits[0], bits[-1]
                assert 0 <= lo <= hi < width, (chip, name, field)
                mask = ((1 << (hi - lo + 1)) - 1) << lo
                assert not occupied & mask, (chip, name, field)
                occupied |= mask
                assert field['access'] in ('RO', 'RW', 'UNSPEC', 'W'), (chip, name, field)
                if 'reset' in field:
                    assert 0 <= field['reset'] < 1 << (hi - lo + 1), (chip, name, field)
                    if reset is not None and (reset & mask) >> lo != field['reset']:
                        issues.append({'chip': chip, 'register': name, 'field': field['name'],
                                       'issue': 'Register and field reset mismatch'})
                fields.append({'chip': chip, 'register': name, 'addr': register['addr'],
                               'register_access': register['access'], 'bits': field['bits'],
                               'field': field['name'], 'access': field['access'],
                               'reset': field.get('reset', ''), 'runtime': bool(register.get('runtime_value')),
                               'read_as': field.get('read_as', ''),
                               'evidence_annotation': field.get('tier_evidence', field.get('desc', '')),
                               'source_review_status': 'NOT_AUTOMATICALLY_CERTIFIED'})
        reference = ROOT / 'd2d/rtl' / (chip.lower() + '_reference.py')
        assert reference.exists(), chip
        freeze(OUT / 'ir' / path.name, raw)
        freeze(OUT / 'references' / reference.name, reference.read_bytes())
        entries.append({'chip': chip, 'ir_file': 'ir/' + path.name, 'ir_sha256': sha(raw),
                        'reference_file': 'references/' + reference.name,
                        'reference_sha256': sha(reference.read_bytes()), 'registers': len(ir['registers']),
                        'proofread_record': ir.get('proofread_record'),
                        'excluded_blocks': ir.get('excluded_blocks', []),
                        'admission_evidence': ir.get('admission_evidence')})
    freeze(OUT / 'harness/test_d2d_blackbox.py', HARNESS.read_bytes())
    freeze(OUT / 'rtl/base_sensor.py', (ROOT / 'd2d/rtl/base_sensor.py').read_bytes())
    write_csv('field_inventory.csv', fields)
    write_json('schema_issues.json', issues)
    manifest = {'version': '20261012-candidate', 'status': 'FROZEN_CANDIDATE_NOT_FULL_SOURCE_CERTIFICATION',
                'harness_md5': EXPECTED_MD5, 'harness_sha256': sha(HARNESS.read_bytes()),
                'base_sha256': sha((OUT / 'rtl/base_sensor.py').read_bytes()),
                'entries': entries, 'field_count': len(fields), 'schema_issues': issues,
                'original_scores_preserved': True,
                'runtime_generation_provenance': 'Incomplete; freeze does not reconstruct historical prompts'}
    write_json('freeze_manifest.json', manifest)
    return manifest


def run_one(job):
    label, chip, seed, index, code, original = job
    sandbox = OUT / 'work' / label / chip / f'{seed}_{index}'
    sandbox.mkdir(parents=True, exist_ok=True)
    (sandbox / 'test_d2d_blackbox.py').write_bytes((OUT / 'harness/test_d2d_blackbox.py').read_bytes())
    (sandbox / 'base_sensor.py').write_bytes((OUT / 'rtl/base_sensor.py').read_bytes())
    (sandbox / (chip.lower() + '_simulator.py')).write_text(code or '', encoding='utf-8')
    env = dict(os.environ, D2D_IR=chip + '_gold_ir.json', D2D_DIAG='1',
               PYTEST_DISABLE_PLUGIN_AUTOLOAD='1', PYTHONIOENCODING='utf-8')
    start = time.monotonic()
    try:
        process = subprocess.run([sys.executable, '-m', 'pytest', 'test_d2d_blackbox.py', '-q',
                                  '--tb=short', '--junitxml=result.xml'], cwd=sandbox, env=env,
                                 capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=90)
        rc, log = process.returncode, process.stdout + '\n' + process.stderr
    except subprocess.TimeoutExpired:
        rc, log = 124, 'Local recheck exceeded 90-second limit; not scored as a semantic test failure.'
    (sandbox / 'pytest.log').write_text(log, encoding='utf-8')
    tests = []
    xml_path = sandbox / 'result.xml'
    if xml_path.exists():
        for case in ET.parse(xml_path).findall('.//testcase'):
            node = next((case.find(k) for k in ('failure', 'error', 'skipped') if case.find(k) is not None), None)
            status = {'failure': 'failed', 'error': 'error', 'skipped': 'skipped'}.get(node.tag if node is not None else '', 'passed')
            tests.append({'test': case.attrib['name'], 'status': status,
                          'message': node.attrib.get('message', '') if node is not None else '',
                          'detail': node.text or '' if node is not None else ''})
    return {'model': label, 'chip': chip, 'seed': seed, 'i': index, 'rc': rc,
            'code_sha256': sha((code or '').encode('utf-8')), 'seconds': time.monotonic() - start,
            'passed': sum(t['status'] == 'passed' for t in tests), 'tests': tests,
            'original_rc': original.get('rc'), 'original_passed': original.get('passed'),
            'matches_original': (rc == original['rc'] and sum(t['status'] == 'passed' for t in tests) == original['passed']) if original else None,
            'log_file': str((sandbox / 'pytest.log').relative_to(OUT)),
            'input_extraction_failed': bool(original) and not original.get('code_extracted', False)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frozen', action='store_true', help='Reuse and verify the archived inputs instead of reading current d2d/ files')
    args = parser.parse_args()
    started = time.monotonic()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.frozen:
        manifest = json.loads((OUT / 'freeze_manifest.json').read_text(encoding='utf-8'))
        assert sha((OUT / 'harness/test_d2d_blackbox.py').read_bytes()) == manifest['harness_sha256']
        assert sha((OUT / 'rtl/base_sensor.py').read_bytes()) == manifest['base_sha256']
        for entry in manifest['entries']:
            assert sha((OUT / entry['ir_file']).read_bytes()) == entry['ir_sha256']
            assert sha((OUT / entry['reference_file']).read_bytes()) == entry['reference_sha256']
    else:
        manifest = preflight()
    jobs, input_files = [], []
    for entry in manifest['entries']:
        chip = entry['chip']
        code = (OUT / entry['reference_file']).read_text(encoding='utf-8')
        jobs.append(('reference', chip, 0, 0, code, {}))
        for tag in TAGS:
            path = ROOT / f'eval/expansion_{tag}/results_gen_{tag}_{chip.lower()}.json'
            records = json.loads(path.read_text(encoding='utf-8'))
            assert len(records) == 12 and {(r['seed'], r['i']) for r in records} == {(s, i) for s in (1, 2, 3) for i in range(4)}
            input_files.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())})
            jobs.extend((tag, chip, r['seed'], r['i'], r.get('code'), r) for r in records)
    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(run_one, job) for job in jobs]
        for done, future in enumerate(concurrent.futures.as_completed(futures), 1):
            rows.append(future.result())
            if done % 25 == 0 or done == len(jobs):
                print(f'RECHECK {done}/{len(jobs)} elapsed={time.monotonic()-started:.1f}s', flush=True)
    rows.sort(key=lambda r: (r['model'], r['chip'], r['seed'], r['i']))
    write_json('full_recheck_results.json', rows)
    test_rows = [{k: r[k] for k in ('model', 'chip', 'seed', 'i')} | t for r in rows for t in r['tests']]
    write_csv('test_outcomes.csv', test_rows)
    summaries = []
    for tag in ('reference',) + TAGS:
        group = [r for r in rows if r['model'] == tag]
        summaries.append({'model': tag, 'samples': len(group), 'green': sum(r['rc'] == 0 for r in group),
                          'passed': sum(r['passed'] for r in group),
                          'failed': sum(t['status'] == 'failed' for r in group for t in r['tests']),
                          'error': sum(t['status'] == 'error' for r in group for t in r['tests']),
                          'skipped': sum(t['status'] == 'skipped' for r in group for t in r['tests']),
                          'matched_original': sum(r['matches_original'] is True for r in group),
                          'timeout': sum(r['rc'] == 124 for r in group)})
    write_json('summary.json', summaries)
    write_json('score_changes.json', [r for r in rows if r['model'] != 'reference' and not r['matches_original']])
    dimension_rows = []
    for tag in TAGS:
        for test in sorted({t['test'] for t in test_rows}):
            group = [t for t in test_rows if t['model'] == tag and t['test'] == test]
            dimension_rows.append({'model': tag, 'test': test,
                                   **{status: sum(t['status'] == status for t in group) for status in ('passed', 'failed', 'error', 'skipped')}})
    write_csv('dimension_outcomes.csv', dimension_rows)
    with zipfile.ZipFile(OUT / 'full_pytest_evidence.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for p in sorted((OUT / 'work').rglob('*')):
            if p.name in ('pytest.log', 'result.xml', 'd2d_diag.json'):
                archive.write(p, p.relative_to(OUT / 'work').as_posix())
    write_json('execution_manifest.json', {'status': 'EXECUTED_LOCAL', 'date': '2026-10-12',
               'python': platform.python_version(), 'pytest': pytest.__version__, 'workers': 4,
               'command': 'python _setup/freeze_and_recheck_20chip.py', 'generation': 'none',
               'inputs': input_files, 'frozen_manifest_sha256': sha((OUT / 'freeze_manifest.json').read_bytes()),
               'log_archive_sha256': sha((OUT / 'full_pytest_evidence.zip').read_bytes()),
               'elapsed_seconds': time.monotonic() - started, 'summary': summaries})
    print(json.dumps(summaries), flush=True)


if __name__ == '__main__':
    main()
