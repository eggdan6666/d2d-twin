"""Run final independent checks, validate returns and package M4 candidate state."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'eval/semantic_protocol_v3_20261012'
SOURCE = OUT.parent / 'independent_source_admission_20261012'
FIELDS = ('contract_version', 'expert_skill', 'project_id', 'paper_family', 'stage_id', 'task_id',
          'task_status', 'inputs_reviewed', 'outputs', 'evidence_status', 'assumptions',
          'author_input_needed', 'manual_actions', 'quality_checks', 'conflicts',
          'conflict_resolution_status', 'merge_permission', 'recommended_next_action',
          'stage_acceptance_recommendation')


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    returns = [load(OUT/'source_acceptance.json'), load(OUT/'semantic_acceptance.json')]
    for item, name, task in zip(returns, ('source_acceptance','semantic_acceptance'),
                                ('semantic-v3/source_acceptance','semantic-v3/semantic_acceptance')):
        assert item['task_id'] == task
        if item.get('report_sha256'):
            assert item['report_sha256'] == sha(OUT/(name+'.md')), 'Stale expert report hash'
    returns += load(SOURCE/'expert_returns.json')
    contracts = OUT/'expert_returns'
    contracts.mkdir(exist_ok=True)
    for i, item in enumerate(returns):
        assert item['project_id'] == 'd2d-twin' and item['paper_family'] == 'M' and item['stage_id'] == 'M4'
        text = '\n'.join(k+': '+json.dumps(item[k], ensure_ascii=False) for k in FIELDS)+'\n'
        path = contracts / (str(i)+'_expert_return.yaml')
        path.write_text(text, encoding='utf-8')
        subprocess.run([sys.executable, str(ROOT/'skills/sci-skills/scripts/validate_expert_contract.py'), str(path)], check=True)
    env = os.environ.copy()
    env.update(PYTEST_DISABLE_PLUGIN_AUTOLOAD='1', PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')
    test_inputs = {p.relative_to(ROOT).as_posix(): sha(p) for p in [*sorted((OUT/'tests').glob('*.py')), OUT/'runtime.py', OUT/'compiler.py', OUT/'scenarios.py']}
    command = [sys.executable, '-m', 'pytest', str(OUT/'tests'), '-q', '-p', 'no:cacheprovider',
               '--junitxml='+str(OUT/'regression_results.xml')]
    r = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8')
    (OUT/'regression_execution.log').write_text(r.stdout+r.stderr, encoding='utf-8')
    print(r.stdout)
    assert r.returncode == 0, r.stderr
    suites = ET.parse(OUT/'regression_results.xml').getroot()
    cases = list(suites.iter('testcase'))
    assert cases and not list(suites.iter('failure')) and not list(suites.iter('error')) and not list(suites.iter('skipped'))
    subprocess.run([sys.executable, str(ROOT/'_setup/build_semantic_v3.py')], check=True)
    for relative, expected in test_inputs.items():
        assert sha(ROOT/relative) == expected
    evidence = {'status':'EXECUTED_LOCAL', 'client_date':'2026-10-13', 'command':command,
                'pytest_version':importlib.metadata.version('pytest'),
                'return_code':r.returncode, 'tests':len(cases), 'passed':len(cases), 'failed':0, 'skipped':0,
                'input_sha256':test_inputs, 'output_sha256':{n:sha(OUT/n) for n in ['regression_results.xml','regression_execution.log']}}
    (OUT/'regression_manifest.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    state = {'project_id':'d2d-twin','paper_family':'M','stage_id':'M4','status':'PARTIALLY_PASSED',
             'scientific_readiness':'NOT_READY','source_admission_review':'ACCEPTED_BOUNDED_INTEGRITY_WITH_REPAIR',
             'source_fields':572,'source_verdicts':load(OUT/'admission_gate.json')['source_field_verdicts'],
             'event_prototype_chips':5,'event_scenarios':8,'checks':load(OUT/'execution_manifest.json')['checks'],
             'regressions_passed':len(cases),'production_generation_ready':False,
             'next_action_file':'eval/semantic_protocol_v3_20261012/NEXT_ACTION.md','last_updated':'2026-10-13'}
    (OUT/'project_state_update.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    statepath = ROOT/'.sci-skills/project-state.yaml'
    text = statepath.read_text(encoding='utf-8')
    marker = '\nsemantic_v3_validation:\n'
    cut = text.index(marker) if marker in text else text.index('\nnext_action:\n',text.index('protocol_v2_validation:'))
    text = text[:cut]+f'''
semantic_v3_validation:
  status: BOUNDED_EVENT_PROTOTYPE_SOURCE_REPAIR_OPEN
  source_admission_review: ACCEPTED_BOUNDED_INTEGRITY_WITH_REPAIR
  scientific_readiness: NOT_READY
  source_fields: 572
  event_prototype_chips: 5
  event_scenarios: 8
  event_checks: 61
  independent_regressions: {len(cases)}
  evidence: eval/semantic_protocol_v3_20261012/REPORT.md
  production_generation_ready: false
next_action:
  type: PROMPT
  stage: M4
  prompt_file: eval/semantic_protocol_v3_20261012/NEXT_ACTION.md
  prompt_generated: true
  operation_guide_generated: false
last_updated: 2026-10-13
'''
    statepath.write_text(text,encoding='utf-8')


if __name__ == '__main__':
    main()
