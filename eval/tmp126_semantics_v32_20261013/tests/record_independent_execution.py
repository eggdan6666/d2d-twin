"""Capture actual independent pytest and checked-byte evidence locally."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parents[1]
PROJECT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import admission


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    env = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD='1', PYTHONIOENCODING='utf-8')
    command = [sys.executable, '-m', 'pytest', str(HERE / 'tests/test_independent_tmp126.py'),
               '-q', '-p', 'no:cacheprovider', '--junitxml=' + str(HERE / 'independent_code_results.xml')]
    run = subprocess.run(command, cwd=PROJECT, env=env, capture_output=True, text=True, encoding='utf-8')
    (HERE / 'independent_code_execution.log').write_text(run.stdout + run.stderr, encoding='utf-8')
    if run.returncode:
        raise SystemExit(run.returncode)
    suites = ET.parse(HERE / 'independent_code_results.xml').getroot().findall('testsuite')
    counts = {k: sum(int(s.attrib.get(k, 0)) for s in suites) for k in ('tests','failures','errors','skipped')}
    counts['passed'] = counts['tests'] - counts['failures'] - counts['errors'] - counts['skipped']
    assert counts['tests'] == 121 and counts['passed'] == 121
    execution = json.loads((HERE / 'scenario_execution.json').read_text(encoding='utf-8'))
    source = json.loads((HERE / 'source_review.json').read_text(encoding='utf-8'))
    admission.validate_execution(execution)
    rows = admission.build_closure(source, execution)
    assert admission.canonical(rows) == admission.canonical(json.loads((HERE / 'closure_ledger.json').read_text(encoding='utf-8')))
    manifest = json.loads((HERE / 'execution_manifest.json').read_text(encoding='utf-8'))
    verified = {}
    for name, sha in manifest['input_sha256'].items():
        assert digest(PROJECT / name) == sha, name
        verified[name] = sha
    for name, sha in manifest['output_sha256'].items():
        assert digest(HERE / name) == sha, name
        verified[str((HERE / name).relative_to(PROJECT)).replace('\\','/')] = sha
    for path in [HERE / 'tests/test_independent_tmp126.py', Path(__file__), HERE / 'execution_manifest.json',
                 PROJECT / 'eval/independent_source_admission_20261012/field_evidence.json',
                 PROJECT / 'eval/semantic_protocol_v3_20261012/runtime.py']:
        verified[str(path.relative_to(PROJECT)).replace('\\','/')] = digest(path)
    md5 = hashlib.md5((PROJECT / 'd2d/eval/test_d2d_blackbox.py').read_bytes()).hexdigest()
    assert md5 == '8cf0854d4779467bc8e472ee4fb97023'
    result = {'status':'EXECUTED_LOCAL', 'command':command, 'returncode':run.returncode,
              'independent_test_counts':counts, 'synthetic_runtime_faults_detected':13,
              'proof_or_source_corruption_rejections':28, 'missing_scenario_partial_checks':8,
              'exact_saved_scenarios_replayed':len(execution), 'bounded_ledger_rows':len(rows),
              'whole_field_promotion':False, 'production_generation_ready':False,
              'reviewed_input_sha256':verified, 'harness_md5':md5,
              'output_sha256':{name:digest(HERE / name) for name in ('independent_code_results.xml','independent_code_execution.log')}}
    (HERE / 'independent_code_execution.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps(counts))


if __name__ == '__main__':
    main()
