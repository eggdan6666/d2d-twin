"""CPU-only sensitivity re-scoring. Preserve raw scores and both IR versions."""
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'eval/model_comparison_20chip'
ARCH = ROOT / 'eval/expansion_qwen14b/scnet_snapshot'
rows = []
for revision, ir_source in [('archived', ARCH / 'ir/INA3221_gold_ir.json'),
                            ('current', ROOT / 'd2d/ir/INA3221_gold_ir.json')]:
    run_root = OUT / 'ina3221_recheck' / revision
    (run_root / 'ir').mkdir(parents=True, exist_ok=True)
    (run_root / 'rtl').mkdir(exist_ok=True)
    shutil.copyfile(ir_source, run_root / 'ir/INA3221_gold_ir.json')
    shutil.copyfile(ARCH / 'rtl/base_sensor.py', run_root / 'rtl/base_sensor.py')
    for tag in ('qwen3b', 'ds67b', 'qwen14b'):
        source = ROOT / 'eval' / ('expansion_' + tag) / ('results_gen_' + tag + '_ina3221.json')
        for record in json.loads(source.read_text(encoding='utf-8')):
            sandbox = run_root / 'eval' / f"{tag}_{record['seed']}_{record['i']}"
            sandbox.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ARCH / 'eval/test_d2d_blackbox.py', sandbox / 'test_d2d_blackbox.py')
            shutil.copyfile(ARCH / 'rtl/base_sensor.py', sandbox / 'base_sensor.py')
            assert record['code'] is not None
            (sandbox / 'ina3221_simulator.py').write_text(record['code'], encoding='utf-8')
            env = dict(os.environ, D2D_IR='INA3221_gold_ir.json', PYTEST_DISABLE_PLUGIN_AUTOLOAD='1')
            result = subprocess.run([sys.executable, '-m', 'pytest', 'test_d2d_blackbox.py', '-q',
                                    '--tb=short', '--junitxml=result.xml'], cwd=sandbox, env=env,
                                    capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
            (sandbox / 'pytest.log').write_text(result.stdout + '\n' + result.stderr, encoding='utf-8')
            tree = ET.parse(sandbox / 'result.xml')
            tests = []
            for case in tree.findall('.//testcase'):
                status = 'failed' if case.find('failure') is not None else 'error' if case.find('error') is not None else 'skipped' if case.find('skipped') is not None else 'passed'
                tests.append({'test': case.attrib['name'], 'status': status})
            rows.append({'revision': revision, 'model': tag, 'seed': record['seed'], 'i': record['i'],
                         'original_rc': record['rc'], 'recheck_rc': result.returncode,
                         'original_passed': record['passed'], 'recheck_passed': sum(t['status'] == 'passed' for t in tests),
                         'ir_sha256': hashlib.sha256(ir_source.read_bytes()).hexdigest(), 'tests': tests})
        print(revision, tag, 'complete', flush=True)
(OUT / 'ina3221_sensitivity.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
for revision in ('archived', 'current'):
    for tag in ('qwen3b', 'ds67b', 'qwen14b'):
        selected = [r for r in rows if r['revision'] == revision and r['model'] == tag]
        print(revision, tag, 'green', sum(r['recheck_rc'] == 0 for r in selected),
              'mean_passed', sum(r['recheck_passed'] for r in selected) / 12,
              'original_score_matches', sum(r['original_rc'] == r['recheck_rc'] and r['original_passed'] == r['recheck_passed'] for r in selected), flush=True)
summary = '# INA3221 IR 版本离线复判\n\n原始生成与分数保持不变。本次使用同一归档 harness，在 CPU 上对 36 份代码各运行两次，共 72 次复判。\n\n'
summary += '| IR版本 | 模型 | 全绿 | 平均通过测试数 | 与原始分数一致的样本 |\n|---|---|---:|---:|---:|\n'
for revision in ('archived', 'current'):
    for tag in ('qwen3b', 'ds67b', 'qwen14b'):
        group = [r for r in rows if r['revision'] == revision and r['model'] == tag]
        summary += f"| {revision} | {tag} | {sum(r['recheck_rc'] == 0 for r in group)}/12 | {sum(r['recheck_passed'] for r in group)/12:.2f} | {sum(r['original_rc'] == r['recheck_rc'] and r['original_passed'] == r['recheck_passed'] for r in group)}/12 |\n"
summary += '\n离线复判只检验评测真值变化的影响，不能等价于给模型输入新 IR 后重新生成代码；本次不证明修正版 gold IR 的手册来源已通过全部专家审校。\n'
(OUT / 'INA3221_SENSITIVITY.md').write_text(summary, encoding='utf-8')
