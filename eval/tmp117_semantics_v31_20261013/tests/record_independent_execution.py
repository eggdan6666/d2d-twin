"""Run the independent TMP117 acceptance suite and retain local evidence."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
INPUTS = [
    HERE / 'tmp117.py', HERE / 'tests/test_independent_tmp117.py',
    HERE / 'admission.py', HERE / 'scenarios.py', HERE / 'source_review.json',
    HERE / 'tests/record_independent_execution.py',
    REPO / 'corpus/data/raw_pdf/TI/TMP117.pdf',
    HERE.parent / 'semantic_protocol_v3_20261012/runtime.py',
    HERE.parent / 'semantic_protocol_v3_20261012/artifact_manifest.json',
    HERE.parent / 'independent_source_admission_20261012/candidate_ir/TMP117_gold_ir.json',
    HERE.parent / 'independent_source_admission_20261012/candidate_source_policy.json',
]


def hashes():
    return {p.relative_to(REPO).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in INPUTS}


def main():
    before = hashes()
    command = [sys.executable, '-B', '-m', 'pytest',
               str(HERE / 'tests/test_independent_tmp117.py'), '-q', '--tb=short',
               '-p', 'no:cacheprovider', '--junitxml=' + str(HERE / 'independent_code_results.xml')]
    env = os.environ.copy()
    env.update(PYTEST_DISABLE_PLUGIN_AUTOLOAD='1', PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')
    started = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
    begin = time.perf_counter()
    run = subprocess.run(command, cwd=REPO, env=env, capture_output=True, timeout=90)
    elapsed = time.perf_counter() - begin
    output = run.stdout.decode('utf-8', errors='replace') + run.stderr.decode('utf-8', errors='replace')
    (HERE / 'independent_code_execution.log').write_text(output, encoding='utf-8')
    after = hashes()
    cases = list(ET.parse(HERE / 'independent_code_results.xml').getroot().iter('testcase'))
    counts = {'tests': len(cases), 'failures': sum(c.find('failure') is not None for c in cases),
              'errors': sum(c.find('error') is not None for c in cases),
              'skipped': sum(c.find('skipped') is not None for c in cases)}
    passed = counts['tests'] - counts['failures'] - counts['errors'] - counts['skipped']
    result = {'schema': 'd2d-independent-tmp117-local-execution-1', 'task_id': 'tmp117-v31/code_review',
              'started_at': started, 'timezone': 'Asia/Shanghai', 'command': command,
              'cwd': str(REPO), 'environment_overrides': {k: env[k] for k in
                  ('PYTEST_DISABLE_PLUGIN_AUTOLOAD', 'PYTHONDONTWRITEBYTECODE', 'PYTHONIOENCODING')},
              'return_code': run.returncode, 'elapsed_seconds': elapsed, 'counts': dict(counts, passed=passed),
              'synthetic_fault_cases': sum(c.get('name', '').startswith('test_source_oracles_reject_meaningful_synthetic_faults') for c in cases),
              'input_hashes_before': before, 'input_hashes_after': after,
              'inputs_unchanged': before == after, 'evidence_status': 'EXECUTED_LOCAL',
              'scope': 'Independent source-scoped CPU tests; not hardware or empirical model accuracy',
              'output_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                  (HERE / 'independent_code_execution.log', HERE / 'independent_code_results.xml')}}
    (HERE / 'independent_code_execution.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'return_code': run.returncode, 'counts': result['counts'],
                      'inputs_unchanged': result['inputs_unchanged']}, ensure_ascii=False))
    if run.returncode or before != after:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
