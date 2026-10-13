"""Final independent regression, contracts and M4 state for scoped TMP126 work."""
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'eval/tmp126_semantics_v32_20261013'
FIELDS=('contract_version','expert_skill','project_id','paper_family','stage_id','task_id','task_status',
        'inputs_reviewed','outputs','evidence_status','assumptions','author_input_needed','manual_actions',
        'quality_checks','conflicts','conflict_resolution_status','merge_permission','recommended_next_action',
        'stage_acceptance_recommendation')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p):
    return json.loads(p.read_text(encoding='utf-8'))


def write(name,value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    contractdir=OUT/'expert_returns'
    contractdir.mkdir(exist_ok=True)
    for name,expert in [('source_review','sci-skills-paper-deep-reading'),('code_review','sci-skills-presubmission-review')]:
        item=load(OUT/(name+'.json'))
        for key,expected in [('project_id','d2d-twin'),('paper_family','M'),('stage_id','M4'),
                             ('task_id','tmp126-v32/'+name),('expert_skill',expert)]:
            assert item[key]==expected
        if item.get('report_sha256'):
            assert sha(OUT/(name+'.md'))==item['report_sha256']
        p=contractdir/(name+'.yaml')
        p.write_text('\n'.join(k+': '+json.dumps(item[k],ensure_ascii=False) for k in FIELDS)+'\n',encoding='utf-8')
        subprocess.run([sys.executable,str(ROOT/'skills/sci-skills/scripts/validate_expert_contract.py'),str(p)],check=True)
    inputpaths=[OUT/'tmp126.py',OUT/'scenarios.py',OUT/'admission.py',OUT/'source_review.json',
                *sorted((OUT/'tests').glob('*.py'))]
    inputs={p.relative_to(ROOT).as_posix():sha(p) for p in inputpaths}
    env=os.environ.copy()
    env.update(PYTEST_DISABLE_PLUGIN_AUTOLOAD='1',PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8')
    cmd=[sys.executable,'-m','pytest',str(OUT/'tests'),'-q','-p','no:cacheprovider',
         '--junitxml='+str(OUT/'regression_results.xml')]
    result=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,encoding='utf-8')
    (OUT/'regression_execution.log').write_text(result.stdout+result.stderr,encoding='utf-8')
    print(result.stdout)
    assert result.returncode==0,result.stderr
    tree=ET.parse(OUT/'regression_results.xml').getroot()
    cases=list(tree.iter('testcase'))
    assert cases and not any(list(tree.iter(tag)) for tag in ('failure','error','skipped'))
    # Preserve the exact producer record already inspected by the independent
    # reviewer; validate it rather than replacing elapsed time after signoff.
    producer=load(OUT/'execution_manifest.json')
    for rel,expected in producer['input_sha256'].items():
        assert sha(ROOT/rel)==expected,'Producer input changed'
    for name,expected in producer['output_sha256'].items():
        assert sha(OUT/name)==expected,'Producer output changed'
    for rel,expected in inputs.items():
        assert sha(ROOT/rel)==expected,'Test input changed'
    write('regression_manifest.json',{'client_date':'2026-10-13','status':'EXECUTED_LOCAL',
        'command':cmd,'pytest_version':importlib.metadata.version('pytest'),'return_code':result.returncode,
        'passed':len(cases),'failed':0,'skipped':0,'input_sha256':inputs,
        'output_sha256':{n:sha(OUT/n) for n in ['regression_execution.log','regression_results.xml']}})
    scope=load(OUT/'admission_gate.json')
    assert scope['bounded_dimensions_verified']==8 and not scope['production_generation_ready']
    write('project_state_update.json',{'project_id':'d2d-twin','stage':'M4','status':'PARTIALLY_PASSED',
        'tmp126_bounded_task':'ACCEPTED','fields_targeted':8,'dimensions_with_scoped_witnesses':8,
        'source_field_promotions':0,'independent_regressions_passed':len(cases),
        'production_generation_ready':False,'last_updated':'2026-10-13',
        'next_action_file':'eval/tmp126_semantics_v32_20261013/NEXT_ACTION.md'})
    state=ROOT/'.sci-skills/project-state.yaml'
    text=state.read_text(encoding='utf-8')
    marker='\ntmp126_v32_validation:\n'
    cut=text.index(marker) if marker in text else text.index('\nnext_action:\n',text.index('tmp117_v31_validation:'))
    text=text[:cut]+f'''
tmp126_v32_validation:
  status: BOUNDED_TMP126_TASK_ACCEPTED
  fields_targeted: 8
  bounded_repair_dimensions: 8
  independent_regressions: {len(cases)}
  whole_field_promotions: 0
  evidence: eval/tmp126_semantics_v32_20261013/REPORT.md
  production_generation_ready: false
next_action:
  type: PROMPT
  stage: M4
  prompt_generated: true
  prompt_file: eval/tmp126_semantics_v32_20261013/NEXT_ACTION.md
  operation_guide_generated: false
last_updated: 2026-10-13
'''
    state.write_text(text,encoding='utf-8')


if __name__=='__main__':
    main()
