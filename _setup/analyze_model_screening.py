"""Validate the supplied SCNet export and report three exploratory model arms."""
import csv
import hashlib
import json
import platform
import re
import sys
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ZIP = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('E:/迅雷下载/D2D_QWEN14B_RESULTS.zip')
OUT = ROOT / 'eval' / 'model_comparison_20chip'
NEW = ROOT / 'eval' / 'expansion_qwen14b'
EXPECTED = {(s, i) for s in (1, 2, 3) for i in range(4)}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != data:
        raise RuntimeError(f'Refusing to overwrite differing file: {path}')
    path.write_bytes(data)


def remove_annotations(node):
    if isinstance(node, dict):
        return {k: remove_annotations(v) for k, v in node.items()
                if k not in ('tier', 'tier_evidence', 'desc')}
    if isinstance(node, list):
        return [remove_annotations(x) for x in node]
    return node


OUT.mkdir(parents=True, exist_ok=True)
audit = {'archive_sha256': sha(ZIP.read_bytes()), 'hash_checks': [], 'ir_differences': [],
         'notes': ['Export hashes verify archive integrity, not run-time inputs of all three arms.',
                   'Qwen3B and DeepSeek6.7B lack per-run input hashes; protocol identity is documented but not cryptographically established.']}
with zipfile.ZipFile(ZIP) as z:
    manifest = json.loads(z.read('export_manifest.json'))
    for name, expected in manifest['sha256'].items():
        data = z.read(name)
        assert sha(data) == expected, name
        audit['hash_checks'].append(name)
        if name.startswith('eval/results_gen_qwen14b_'):
            save(NEW / Path(name).name, data)
        else:
            save(NEW / 'scnet_snapshot' / name, data)
        local = ROOT / 'd2d' / name
        if name.startswith('ir/'):
            source = json.loads(data)
            current = json.loads(local.read_text(encoding='utf-8'))
            if source != current:
                audit['ir_differences'].append({'chip': source['device'],
                    'kind': 'SEMANTIC' if remove_annotations(source) != remove_annotations(current) else 'ANNOTATION_ONLY',
                    'archive_sha256': sha(data), 'current_sha256': sha(local.read_bytes())})
        elif name in ('eval/gen_code.py', 'eval/test_d2d_blackbox.py', 'rtl/base_sensor.py'):
            audit.setdefault('current_source_matches', {})[name] = local.read_bytes() == data
    save(NEW / 'export_manifest.json', z.read('export_manifest.json'))
chips = sorted(r['chip'] for r in manifest['results'])
assert len(chips) == len(set(chips)) == 20
models = [('Qwen2.5-Coder-3B', 'qwen3b'), ('DeepSeek-Coder-6.7B', 'ds67b'), ('Qwen2.5-Coder-14B', 'qwen14b')]
details, summaries, failures, matrix, inputs = [], [], [], [], []
test_names = re.findall(r'^def (test_\w+)\(', (NEW / 'scnet_snapshot/eval/test_d2d_blackbox.py').read_text(encoding='utf-8'), re.M)
for label, tag in models:
    records = []
    chip_rates = []
    for chip in chips:
        path = ROOT / 'eval' / ('expansion_' + tag) / ('results_gen_' + tag + '_' + chip.lower() + '.json')
        data = json.loads(path.read_text(encoding='utf-8'))
        assert len(data) == 12 and {(r['seed'], r['i']) for r in data} == EXPECTED, path
        assert all(all(k in r for k in ('rc', 'passed', 'tail', 'code', 'code_extracted')) for r in data), path
        inputs.append({'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())})
        green = sum(r['rc'] == 0 for r in data)
        extracted = sum(bool(r['code_extracted']) for r in data)
        elapsed = max(r['gen_s'] for r in data)
        details.append({'model': label, 'chip': chip, 'samples': 12, 'green': green,
                        'green_rate': green / 12, 'extracted': extracted,
                        'mean_passed_tests': sum(r['passed'] for r in data) / 12,
                        'generation_and_test_elapsed_s': elapsed})
        for test in test_names:
            # Tail text may be truncated. This is a lower bound, not a complete diagnosis.
            count = sum(bool(re.search(r'FAILED\s+[^\n]*::' + re.escape(test) + r'\b', r['tail'])) for r in data)
            failures.append({'model': label, 'chip': chip, 'test': test, 'observed_failed_in_tail': count})
        records.extend(data)
        chip_rates.append(green / 12)
    matrix.append(chip_rates)
    summaries.append({'model': label, 'chips': 20, 'samples': len(records),
                      'green': sum(r['rc'] == 0 for r in records),
                      'green_rate': sum(r['rc'] == 0 for r in records) / len(records),
                      'extracted': sum(bool(r['code_extracted']) for r in records),
                      'mean_passed_tests': sum(r['passed'] for r in records) / len(records)})


def csv_out(name, rows):
    with (OUT / name).open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


csv_out('model_summary.csv', summaries)
csv_out('per_chip_comparison.csv', details)
csv_out('failure_tail_counts.csv', failures)
# Resample paired chips, not individual generated samples. Exploratory roster sensitivity.
rng = np.random.default_rng(20261012)
values = np.asarray(matrix)
indices = rng.integers(0, 20, size=(10000, 20))
means = values[:, indices].mean(axis=2)
contrasts = []
for a, b in [(2, 0), (2, 1), (1, 0)]:
    diffs = means[a] - means[b]
    lo, hi = np.quantile(diffs, [.025, .975])
    contrasts.append({'contrast': models[a][0] + ' minus ' + models[b][0],
                      'difference_pp': 100 * (values[a].mean() - values[b].mean()),
                      'chip_bootstrap_lower_pp': 100 * lo, 'chip_bootstrap_upper_pp': 100 * hi})
csv_out('exploratory_chip_bootstrap.csv', contrasts)
audit['inputs'] = inputs
audit['software'] = {'python': platform.python_version(), 'numpy': np.__version__, 'matplotlib': matplotlib.__version__}
audit['counts'] = summaries
(OUT / 'validation_manifest.json').write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')

fig, (ax, heat) = plt.subplots(1, 2, figsize=(10.5, 7.8), gridspec_kw={'width_ratios': [1, 1.4]}, constrained_layout=True)
labels = ['Qwen\n3B', 'DeepSeek\n6.7B', 'Qwen\n14B']
rates = [100 * x['green_rate'] for x in summaries]
bars = ax.bar(labels, rates, color=['#77AADD', '#EE8866', '#4477AA'])
ax.set_ylim(0, 100)
ax.set_ylabel('Fully passing samples (%)')
ax.set_title('A. Overall performance')
ax.spines[['top', 'right']].set_visible(False)
for bar, rec in zip(bars, summaries):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
            f"{rec['green']}/240\n{rec['green_rate']:.1%}", ha='center', fontsize=10)
ax.text(.5, .5, '20 chips; 12 samples per chip\nDescriptive comparison\nNo significance claim', transform=ax.transAxes, ha='center', fontsize=10)
im = heat.imshow(100 * values.T, vmin=0, vmax=100, cmap='Blues', aspect='auto')
heat.set_yticks(range(20), chips)
heat.set_xticks(range(3), labels)
heat.set_title('B. Performance by chip')
for i in range(20):
    for j in range(3):
        count = round(values[j, i] * 12)
        heat.text(j, i, f'{count}/12', ha='center', va='center', fontsize=8, color='white' if count >= 7 else 'black')
fig.colorbar(im, ax=heat, label='Fully passing samples (%)', shrink=.7)
fig.savefig(OUT / 'model_comparison.png', dpi=180)
fig.savefig(OUT / 'model_comparison.pdf')
plt.close(fig)

table = '\n'.join(f"| {s['model']} | {s['samples']} | {s['green']} | {s['green_rate']:.1%} | {s['extracted']} | {s['mean_passed_tests']:.2f} |" for s in summaries)
report = f'''# 三模型 20 芯片评测：核验与描述性对比

数据状态：原始结果已核验，跨模型输入版本证据尚不完整；论文推断仍为暂定。

## 核验

- 压缩包中 43 个文件的 SHA-256 与导出清单一致。
- 三模型各 20 颗芯片，每颗 seed 1、2、3 各 4 个样本；合计 720 个样本，无重复或缺失的 seed/i。
- 导出的 harness、生成脚本、基类与当前本地字节一致；归档保持独立，不覆盖当前 IR。
- 14B 全绿为 48/240（20.0%）。此前截图汇报的 38/240 为读取错误，已更正。

## 描述性结果

| 模型 | 样本 | 全绿 | 全绿率 | 提取代码 | 平均通过测试数 |
|---|---:|---:|---:|---:|---:|
{table}

每颗贡献相同的 12 个样本，因此整体全绿率也等于 20 颗芯片全绿率的宏平均。
平均通过测试数只是测试函数计数，不是断言覆盖率；各芯片跳过项不同，不能把它除以 8 当通用准确率。
耗时字段 gen_s 是从模型加载后计时的累计生成与测试时间，不是逐样本延迟，也不包含加载时间。

## 输入版本审计

远端与本地有 8 颗 IR 不同。其中 BME280、HDC2021、LM83、TMP100、TMP102、TMP117、TMP126 仅证据分级/说明不同；这些字段仍会进入 prompt，不能视为提示词字节相同。
INA3221 存在实际访问权限变化：远端若干保留字段编码为 RO，本地修正版为 RW。其原始分数不可自动视为当前修正版 IR 的分数。
3B 与 6.7B 没有逐次运行的 IR/prompt/model-revision 哈希记录，导出时的 14B 快照也不能证明全部生成时的文件状态。
所以本表可以用于描述本次结果，但“所有输入严格一致”的正式比较结论仍待审计。

## 统计与解释

技术重复为同一芯片内的 3 seeds × 4 samples，不把 240 份生成当作 240 个独立器件。
探索性不确定性计算以芯片为组，在三个模型间配对重采样 20 颗芯片 10,000 次，seed=20261012，结果在 exploratory_chip_bootstrap.csv。
这是对便利样本清单的敏感性分析，不代表随机抽取工业芯片的总体置信区间；不做显著性或因果结论。
Qwen14B 与 Qwen3B 的全绿率差为 10.83 个百分点；DeepSeek6.7B 是跨家族对照，不能当作同家族规模曲线的中间点。
图使用真实原始 JSON 派生的计数，纵轴从 0 开始，不含手填数据或显著性标记。
failure_tail_counts.csv 只统计 tail 中可识别的 FAILED 测试名称；由于日志截断与 fixture 错误可能存在，该表是失败出现次数下界，不能当完整失败归因。

## INA3221 离线敏感性复判

对本次 36 份 INA3221 生成代码，分别用远端归档和本地修正版 IR 运行相同归档 harness，共 72 次 CPU 复判。
两种 IR 下三模型均为 0/12 全绿，各 12 个样本的返回码和通过测试数均与原记录一致。本次 IR 修正不改变总体全绿率。
完整结果见 INA3221_SENSITIVITY.md 和 ina3221_sensitivity.json。复判不等价于用新版 IR 重新生成，也不能补回缺失的生成时输入哈希。

## 下一步行动卡

确定并冻结用于投稿的 IR 版本，完成剩余金标审计与完整失败归因；补足或如实披露既有模型的运行输入证据后再更新论文主表。现阶段无需重跑 GPU。
'''
(OUT / 'REPORT_three_models.md').write_text(report, encoding='utf-8')
(OUT / 'analysis_plan.json').write_text(json.dumps({'execution_status': 'EXECUTED_LOCAL',
    'sample_unit': 'chip, with nested seeds and samples', 'exclusions': 'none',
    'outcomes': 'rc == 0 and code_extracted', 'bootstrap_seed': 20261012,
    'bootstrap_repetitions': 10000, 'tests': 'none; exploratory descriptive analysis',
    'uncertainty': 'paired chip bootstrap roster sensitivity',
    'software': audit['software'], 'sources': inputs}, indent=2), encoding='utf-8')
contract = {'contract_version': '1.0', 'expert_skill': 'sci-skills-statistical-reporting',
    'project_id': None, 'paper_family': None, 'stage_id': None, 'task_id': None,
    'task_status': 'PROVISIONAL', 'inputs_reviewed': [str(ZIP), '60 raw result JSON files'],
    'outputs': [str(p.relative_to(ROOT)) for p in OUT.iterdir() if p.is_file()],
    'evidence_status': ['VERIFIED_USER_MATERIAL', 'EXECUTED_LOCAL', 'PENDING_VERIFICATION: cross-arm runtime hashes'],
    'assumptions': ['fixed convenience roster; correlated trials within chips'],
    'author_input_needed': [], 'manual_actions': [],
    'quality_checks': ['all export hashes match', '720 unique seed/index samples validated', 'real-data plots generated'],
    'conflicts': ['Runtime input provenance incomplete; INA3221 original and revised scoring both retained'],
    'conflict_resolution_status': 'UNRESOLVED', 'merge_permission': 'orchestrator_only',
    'recommended_next_action': 'Freeze canonical IR and complete gold-standard and failure audits.',
    'stage_acceptance_recommendation': 'NOT_ASSESSED'}
(OUT / 'expert_result.json').write_text(json.dumps(contract, indent=2), encoding='utf-8')
print(json.dumps({'models': summaries, 'ir_differences': audit['ir_differences'], 'contrasts': contrasts}, ensure_ascii=False, indent=2))
print('OUTPUT', OUT)
