"""Package bounded expert returns and update only the current M4 action locally."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'eval/protocol_v2_20261012'
FIELDS = ('contract_version', 'expert_skill', 'project_id', 'paper_family', 'stage_id', 'task_id',
          'task_status', 'inputs_reviewed', 'outputs', 'evidence_status', 'assumptions',
          'author_input_needed', 'manual_actions', 'quality_checks', 'conflicts',
          'conflict_resolution_status', 'merge_permission', 'recommended_next_action',
          'stage_acceptance_recommendation')


def yaml_lines(data):
    lines = []
    for key, value in data.items():
        if isinstance(value, list):
            # Inline arrays also work with the suite's line-oriented validator.
            items = [json.dumps(item, ensure_ascii=False) if not isinstance(item, str) else item
                     for item in value]
            lines.append(key + ': ' + json.dumps(items, ensure_ascii=False))
        else:
            lines.append(key + ': ' + json.dumps(value, ensure_ascii=False))
    return '\n'.join(lines) + '\n'


def main():
    contracts = OUT / 'expert_returns'
    contracts.mkdir(exist_ok=True)
    for name in ('source_policy_review', 'legal_domain_supplement', 'independent_repair_review'):
        data = json.loads((OUT / (name + '.json')).read_text(encoding='utf-8'))
        assert data['project_id'] == 'd2d-twin' and data['stage_id'] == 'M4' and data['paper_family'] == 'M'
        assert data['merge_permission'] == 'orchestrator_only'
        (contracts / (name + '.yaml')).write_text(yaml_lines({k: data[k] for k in FIELDS}), encoding='utf-8')
    code = (OUT / 'CODE_REVIEW.md').read_text(encoding='utf-8')
    match = re.search(r'```yaml\n(contract_version:.*?)```', code, re.S)
    assert match
    (contracts / 'protocol_review.yaml').write_text(match.group(1), encoding='utf-8')
    summary = json.loads((OUT / 'summary.json').read_text(encoding='utf-8'))
    state_update = {
        'project_id': 'd2d-twin', 'diagnosed_stage': 'M4', 'stage_status': 'PARTIALLY_PASSED',
        'scientific_readiness': 'NOT_READY', 'protocol_task_status': 'BOUNDED_COMPLETE',
        'protocol_version': '2.0-candidate-20261012.1',
        'regression_tests': '42 passed; 41 independent code-review tests plus1 final metadata override regression',
        'reference_admission': '20/20,75 passed/85 skipped,1043 comparisons; not source certification',
        'models': [f"{r['model']}: {r['green']}/{r['samples']} full passes" for r in summary['models']],
        'blockers': ['All572 fields not independently source-certified',
                     'Source conflicts and dynamic/conditional behavior outside current protocol',
                     'Historical generation provenance incomplete'],
        'next_action': 'Complete20-chip source admission and freeze IR/policy/prompt/harness before new generation',
        'evidence': ['REPORT.md', 'STAGE_REVIEW.md', 'CONFLICT_LEDGER.md', 'NEXT_ACTION.md', 'execution_record.yaml'],
        'last_updated': '2026-10-12'}
    (OUT / 'project_state_update.yaml').write_text(yaml_lines(state_update), encoding='utf-8')
    state = ROOT / '.sci-skills/project-state.yaml'
    text = state.read_text(encoding='utf-8')
    section_start = text.index('expansion_source_contract_audit:')
    marker = '\nprotocol_v2_validation:\n'
    start = (text.index(marker, section_start) if marker in text[section_start:]
             else text.index('\nnext_action:\n', section_start))
    text = text[:start] + '''
protocol_v2_validation:
  status: BOUNDED_COMPLETE_SOURCE_ADMISSION_PARTIAL
  scientific_readiness: NOT_READY
  version: "2.0-candidate-20261012.1"
  evidence: "eval/protocol_v2_20261012/REPORT.md"
  regression: "42 passed; 41 independent review cases plus1 metadata override regression"
  reference: "20/20;75 applicable tests passed/85 skipped;1043 comparisons"
  original_scores_preserved: true
  current_blockers:
    - "All572 source fields not independently certified"
    - "Source conflicts and missing dynamic/conditional oracles remain"
    - "Historical generation provenance incomplete"
next_action:
  type: PROMPT
  stage: M4
  prompt_generated: true
  operation_guide_generated: false
  prompt_file: "eval/protocol_v2_20261012/NEXT_ACTION.md"
  expected_return_materials:
    - "20-chip source-contract admission ledger and independent signoff"
    - "Candidate changes, conflicts and exclusions with source locators"
    - "Pre-generation freeze of IR/policy/prompt/harness/software inputs"
last_updated: 2026-10-12
'''
    state.write_text(text, encoding='utf-8')
    print('Expert contracts packaged; local project remains M4 PARTIAL', flush=True)


if __name__ == '__main__':
    main()
