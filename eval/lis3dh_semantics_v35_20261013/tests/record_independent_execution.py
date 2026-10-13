"""Record actual independent pytest and exact replay of the accepted package."""
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


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    import admission
    env = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD='1', PYTHONIOENCODING='utf-8',
               PYTHONDONTWRITEBYTECODE='1')
    command = [sys.executable, '-m', 'pytest', str(HERE / 'tests/test_independent_lis3dh.py'),
               '-q', '-p', 'no:cacheprovider', '--junitxml=' + str(HERE / 'independent_code_results.xml')]
    run = subprocess.run(command, cwd=PROJECT, env=env, capture_output=True, text=True, encoding='utf-8')
    (HERE / 'independent_code_execution.log').write_text(run.stdout + run.stderr, encoding='utf-8')
    if run.returncode:
        raise SystemExit(run.returncode)
    suites = ET.parse(HERE / 'independent_code_results.xml').getroot().findall('testsuite')
    counts = {k: sum(int(s.attrib.get(k, 0)) for s in suites) for k in ('tests','failures','errors','skipped')}
    counts['passed'] = counts['tests'] - counts['failures'] - counts['errors'] - counts['skipped']
    assert counts['tests'] and counts['tests'] == counts['passed']
    case_names = [c.attrib['name'] for s in suites for c in s.findall('testcase')]
    fault_count = sum(n.startswith('test_source_oracle_detects_synthetic_runtime_fault') for n in case_names)
    corruption_count = sum(n.startswith(('test_corrupted_or_fabricated_execution','test_changed_source_identity',
                                        'test_primary_pdf_and_frozen_authority','test_exploratory_policy')) for n in case_names)
    partial_count = sum(n.startswith('test_missing_required_scenario') and not any('['+name+']' in n for name in ('word_formats','candidate_consumption','bdu_boundary')) for n in case_names)
    execution = json.loads((HERE / 'scenario_execution.json').read_text(encoding='utf-8'))
    source = json.loads((HERE / 'source_review.json').read_text(encoding='utf-8'))
    admission.validate_execution(execution)
    rows = admission.build_closure(source, execution)
    saved = json.loads((HERE / 'closure_ledger.json').read_text(encoding='utf-8'))
    assert admission.canonical(rows) == admission.canonical(saved)
    manifest = json.loads((HERE / 'execution_manifest.json').read_text(encoding='utf-8'))
    verified = {}
    for name, sha in manifest['input_sha256'].items():
        assert digest(PROJECT / name) == sha, name
        verified[name] = sha
    for name, sha in manifest['output_sha256'].items():
        assert digest(HERE / name) == sha, name
        verified[(HERE / name).relative_to(PROJECT).as_posix()] = sha
    for path in [HERE / 'tests/test_independent_lis3dh.py', Path(__file__), HERE / 'execution_manifest.json',
                 PROJECT / 'eval/independent_source_admission_20261012/field_evidence.json',
                 PROJECT / 'eval/semantic_protocol_v3_20261012/runtime.py']:
        verified[path.relative_to(PROJECT).as_posix()] = digest(path)
    md5 = hashlib.md5((PROJECT / 'd2d/eval/test_d2d_blackbox.py').read_bytes()).hexdigest()
    assert md5 == '8cf0854d4779467bc8e472ee4fb97023'
    result = {'status':'EXECUTED_LOCAL', 'command':command, 'returncode':run.returncode,
              'independent_test_counts':counts,
              'synthetic_runtime_faults_detected':fault_count,
              'proof_or_source_corruption_rejections':corruption_count,
              'missing_scenario_partial_checks':partial_count,
              'exact_saved_scenarios_replayed':len(execution), 'bounded_ledger_rows':len(rows),
              'whole_field_promotion':False, 'production_generation_ready':False,
              'reviewed_input_sha256':verified, 'harness_md5':md5,
              'output_sha256':{name:digest(HERE / name) for name in ('independent_code_results.xml','independent_code_execution.log')}}
    (HERE / 'independent_code_execution.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps(counts))


if __name__ == '__main__':
    main()
