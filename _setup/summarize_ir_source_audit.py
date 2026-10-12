"""Summarize complete test logs while keeping source/protocol risks visible."""
import csv
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'eval/ir_freeze_20261012'
REPAIR = ROOT / 'eval/ir_source_repair_candidate_20261012'


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def applicable(ir):
    regs = ir['registers']
    sem = ir.get('single_byte_semantics') or {}
    return {
        'test_reset_values': any(not r.get('runtime_value') and r['access'] != 'W' for r in regs),
        'test_readonly_protection': any(r['access'] == 'RO' for r in regs),
        'test_rw_field_persistence': any(r['access'] == 'RW' and any(f['access'] == 'RO' or (f['access'] == 'RW' and f.get('read_as') is None) for f in r['fields']) for r in regs),
        'test_write_trigger_fields': any(f['access'] == 'RW' and f.get('read_as') is not None for r in regs for f in r['fields']),
        'test_single_byte_semantics': bool(sem.get('test_register')) and sem.get('applies_to') not in (None, 'none'),
        'test_read_write_alias': any(r.get('write_addr') for r in regs),
        'test_clear_on_read': any(r.get('cor_addr') for r in regs),
        'test_write_only_reset_key': any(r['access'] == 'W' and r.get('write_key') for r in regs),
    }


def main():
    rows = json.loads((OUT / 'full_recheck_results.json').read_text(encoding='utf-8'))
    manifest = json.loads((OUT / 'freeze_manifest.json').read_text(encoding='utf-8'))
    apps = {entry['chip']: applicable(json.loads((OUT / entry['ir_file']).read_text(encoding='utf-8'))) for entry in manifest['entries']}
    coverage, vacuous, counts = [], [], []
    for r in rows:
        if r['model'] != 'reference':
            continue
        empty = [t['test'] for t in r['tests'] if t['status'] == 'passed' and not apps[r['chip']][t['test']]]
        vacuous.extend({'chip': r['chip'], 'test': name} for name in empty)
        coverage.append({'chip': r['chip'], 'reported_passed_tests': r['passed'],
                         'nonvacuous_applicable_tests': sum(apps[r['chip']].values()),
                         'vacuous_passes': len(empty), 'skipped_tests': sum(t['status'] == 'skipped' for t in r['tests'])})
    for tag in ('qwen3b', 'ds67b', 'qwen14b'):
        for test in sorted(next(iter(apps.values()))):
            group = [next(t for t in r['tests'] if t['test'] == test) for r in rows if r['model'] == tag and apps[r['chip']][test]]
            count = {'model': tag, 'test': test, 'applicable_chips': sum(a[test] for a in apps.values()), 'applicable_samples': len(group)}
            count.update({status: sum(t['status'] == status for t in group) for status in ('passed', 'failed', 'error', 'skipped')})
            completed = count['passed'] + count['failed']
            count['failure_rate_among_completed_tests'] = count['failed'] / completed if completed else ''
            count['error_rate_among_applicable_samples'] = count['error'] / len(group) if group else ''
            counts.append(count)
    write_csv(OUT / 'applicable_dimension_outcomes.csv', counts)
    write_csv(OUT / 'reference_coverage.csv', coverage)
    write_json(OUT / 'vacuous_reference_passes.json', vacuous)
    shutil.copyfile(ROOT / '_setup/freeze_recheck_20chip_execution.log', OUT / 'execution.log')
    shutil.copyfile(ROOT / '_setup/ir_source_repairs_execution.log', REPAIR / 'execution.log')
    with zipfile.ZipFile(OUT / 'source_page_evidence.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for p in (OUT / 'source_pages').iterdir():
            if p.is_file():
                z.write(p, p.name)
    with zipfile.ZipFile(REPAIR / 'tmp100_pytest_evidence.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for p in (REPAIR / 'work').rglob('*'):
            if p.name in ('pytest.log', 'result.xml', 'd2d_diag.json'):
                z.write(p, p.relative_to(REPAIR / 'work').as_posix())
    summaries = json.loads((OUT / 'summary.json').read_text(encoding='utf-8'))
    table = '\n'.join(f"| {s['model']} | {s['green']}/{s['samples']} | {s['passed']} | {s['failed']} | {s['error']} | {s['skipped']} |" for s in summaries)
    fourteen = [c for c in counts if c['model'] == 'qwen14b']
    dims = '\n'.join(f"| {c['test']} | {c['applicable_chips']} | {c['passed']} | {c['failed']} | {c['error']} |" for c in fourteen)
    report = f'''# 20 芯片离线复判与失败分析

状态：EXECUTED_LOCAL。当前 IR 保存为 `20261012-candidate` 快照；这不是全部来源审校通过的声明。

## 可复核结果

740 次 CPU pytest 已完成：20 份参考实现与 720 份原始生成代码。冻结 harness MD5 仍为 {manifest['harness_md5']}。

| 模型/参考 | 全绿 | passed 测试函数 | failed | error | skipped |
|---|---:|---:|---:|---:|---:|
{table}

全绿数与原记录一致。719/720 样本返回码与 passed 计数同时匹配；Qwen3B/BMP280/seed1/i2 原本提取代码失败（rc=-1），本次将空模块送入 pytest 得到 fixture error（rc=1），两次均不全绿。
该样本属于代码提取失败，不把其 8 次 fixture error 当 8 个独立硬件行为缺陷。

## 分母与空断言

参考实现共 77 个 passed、83 个 skipped。然而 `test_readonly_protection` 在 AD5592R 和 ADS1220 上没有 RO 寄存器可遍历，返回 passed 却没有执行保护断言。
因此只有 75 个非空适用测试函数（每颗 2–5 项），不能把参考 20/20 全绿写成全部硬件语义 100% 真实。
`reference_coverage.csv` 区分 reported passed 与非空适用项。`applicable_dimension_outcomes.csv` 根据 IR 与实际 harness 分支定义分母；空断言、skip 和 fixture error 分开记录。

## Qwen14B 逐维结果

| 测试 | 适用芯片 | passed | failed | error |
|---|---:|---:|---:|---:|
{dims}

这批样本的复位值检查全部通过；RW 位域、写触发、读写别名和读清除仍产生失败。
RO 保护结果仍受到源契约和保留位约定的影响。别名仅覆盖 2 颗芯片，读清除仅 1 颗，不能写成对全部工业芯片的总体结论。
Qwen3B 有 17 个样本出现 fixture error，DeepSeek 有 3 个，14B 为 0；按样本统计于 execution_error_samples.json，不把同一初始化错误重复解释为多个独立发现。

## 证据范围

full_recheck_results.json、test_outcomes.csv 和 full_pytest_evidence.zip 包含全部逐测试结果、完整 traceback、JUnit 和诊断文件，替代之前仅从 tail 提取的失败下界。
每个测试函数内部遇到首个断言失败就停止；完整日志不等于该函数所有寄存器和位都已穷尽诊断。
本次保存了执行前的 IR、参考实现、harness、基类和原始结果哈希，但不能补回模型生成时的 IR/prompt/model revision 哈希。

## 唯一下一步

按 SOURCE_AUDIT.md 修订并复核源契约，建立单独编号的第二版评分协议；在协议准入前保留当前探索性结果，不替换论文主表。下一步可在本机完成，不需要 SCNet GPU 或购买硬件。
'''
    (OUT / 'FAILURE_ANALYSIS.md').write_text(report, encoding='utf-8')
    sensitivity = json.loads((REPAIR / 'tmp100_sensitivity.json').read_text(encoding='utf-8'))
    changed = [{k: r[k] for k in ('model', 'seed', 'i', 'original_rc', 'rc', 'original_passed', 'passed')} for r in sensitivity if r['matches_original'] is False]
    write_json(REPAIR / 'changed_samples.json', changed)
    print(json.dumps({'vacuous_reference_tests': vacuous, 'nonvacuous_reference_test_count': sum(c['nonvacuous_applicable_tests'] for c in coverage), 'tmp100_score_changes': changed}))


if __name__ == '__main__':
    main()
