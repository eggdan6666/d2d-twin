"""Describe the paired protocol sensitivity run, with no independence/power claims."""
import csv
import hashlib
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'eval/protocol_v2_20261012'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def table(name, rows):
    with (OUT / name).open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    rows = read(OUT / 'model_results.json')
    refs = read(OUT / 'reference_results.json')
    plan = {r['chip']: r for r in read(OUT / 'coverage_plan.json')}
    policies = read(OUT / 'source_policy.json')
    assert len(rows) == 720 and len(refs) == 20
    assert all(len(r['tests']) == 8 for r in rows + refs)
    assert all(r['rc'] == 0 for r in refs)
    assert read(OUT / 'model_execution_manifest.json')['protocol_manifest_sha256'] == digest(OUT / 'protocol_manifest.json')
    assert read(OUT / 'reference_execution_manifest.json')['protocol_manifest_sha256'] == digest(OUT / 'protocol_manifest.json')
    flat, dimensions, changes, cohorts, transitions = [], [], [], [], []
    for r in rows + refs:
        for t in r['tests']:
            applicable = plan[r['chip']]['applicability'][t['test']]
            flat.append({**{k: r[k] for k in ('model', 'chip', 'seed', 'i')},
                         'applicable': applicable, **t})
            if r['rc'] == 0:
                assert (applicable and t['status'] == 'passed') or (not applicable and t['status'] == 'skipped'), (r['chip'], t)
    for tag in ('qwen3b', 'ds67b', 'qwen14b'):
        group = [r for r in rows if r['model'] == tag]
        transition = {'model': tag, 'both_green': 0, 'v1_only_green': 0,
                      'v2_only_green': 0, 'both_not_green': 0}
        for r in group:
            old, new = r['original_rc'] == 0, r['rc'] == 0
            key = 'both_green' if old and new else 'v1_only_green' if old else 'v2_only_green' if new else 'both_not_green'
            transition[key] += 1
            if old != new:
                changes.append({**{k: r[k] for k in ('model', 'chip', 'seed', 'i', 'original_rc', 'rc')},
                                'transition': key,
                                'failed_dimensions': [t['test'] for t in r['tests'] if t['status'] == 'failed'],
                                'code_sha256': r['code_sha256']})
        transitions.append(transition)
        for chip in sorted(plan):
            g = [r for r in group if r['chip'] == chip]
            assert len(g) == 12
            cohorts.append({'model': tag, 'chip': chip, 'samples': len(g),
                            'v1_green': sum(r['original_rc'] == 0 for r in g),
                            'v2_green': sum(r['rc'] == 0 for r in g),
                            'v2_applicable_dimensions': sum(plan[chip]['applicability'].values()),
                            'error_samples': sum(any(t['status'] == 'error' for t in r['tests']) for r in g)})
        for test in sorted(plan[next(iter(plan))]['applicability']):
            g = [t for t in flat if t['model'] == tag and t['test'] == test and t['applicable']]
            excluded = [t for t in flat if t['model'] == tag and t['test'] == test and not t['applicable']]
            dimensions.append({'model': tag, 'test': test, 'applicable_chips': len({t['chip'] for t in g}),
                               'applicable_trials': len(g),
                               **{s: sum(t['status'] == s for t in g) for s in ('passed', 'failed', 'error', 'skipped')},
                               'excluded_trials': len(excluded),
                               'excluded_fixture_errors': sum(t['status'] == 'error' for t in excluded)})
    table('test_outcomes.csv', flat)
    table('applicable_dimension_outcomes.csv', dimensions)
    table('per_chip_protocol_comparison.csv', cohorts)
    write('green_classification_changes.json', changes)
    write('protocol_transitions.json', transitions)
    sys.path.insert(0, str(OUT / 'harness'))
    from protocol_rules import Contract, bounds
    inventory, exclusions = [], []
    for p in sorted((OUT / 'ir').glob('*.json')):
        ir = read(p)
        contract = Contract(ir, policies)
        cp = policies['chips'].get(ir['device'], {})
        for rn, r in contract.regs.items():
            for f in r.get('fields', []):
                q = rn + '.' + f['name']
                fp = contract.field_policy(q)
                record = {'chip': ir['device'], 'register': rn, 'field': f['name'], 'bits': f['bits'],
                          'ir_access': f['access'], 'field_policy': fp,
                          'excluded_access_assertions': contract.excluded_field(q) or bool(contract.register_policy(rn).get('exclude_writes')),
                          'known_reset_bit_mask': hex(bounds(f)[2] & contract.known_mask(rn)),
                          'known_protection_bit_mask': hex(bounds(f)[2] & contract.known_mask(rn, 'protection')),
                          'source_review_status': 'BOUNDED_POLICY_REVIEW' if fp else 'NOT_CERTIFIED_BY_THIS_V2_TASK',
                          'source_locator': fp.get('source', cp.get('source', 'Inherited IR annotation; full review pending'))}
                if f['access'] == 'RW' and ('legal_values' in fp or 'legal_values' in f):
                    record['legal_values'] = contract.legal_values(q)
                    record['tested_values'] = contract.stimulus_values(q)
                inventory.append(record)
                if record['excluded_access_assertions'] or record['known_reset_bit_mask'] == '0x0' or fp.get('test_values'):
                    exclusions.append(record)
    assert len(inventory) == 572
    write('field_policy_inventory.json', inventory)
    write('exclusion_inventory.json', exclusions)
    summaries = read(OUT / 'model_summary.json')
    summary_lines = []
    for s, t in zip(summaries, transitions):
        old = t['both_green'] + t['v1_only_green']
        new = t['both_green'] + t['v2_only_green']
        summary_lines.append(f"| {s['model']} | {old}/240 ({old/2.4:.2f}%) | {new}/240 ({new/2.4:.2f}%) | {t['v2_only_green']} | {t['v1_only_green']} |")
    ref_assertions = sum(r['assertions_executed'] for r in refs)
    ref_summary = read(OUT / 'reference_summary.json')[0]
    report = f'''# 第二版协议实施与重判报告

状态：**可执行候选协议完成，论文全面来源准入仍为 M4 部分通过 / NOT_READY**。日期：2026-10-12。

## 已核实的交付

- 独立编号 `{policies['protocol_version']}` 的 source_policy、20 个 IR 候选、20 个参考实现、8 维评分 harness；原 `d2d/` IR 和原始第一版 harness 未修改。
- 独立来源审查覆盖本次修订和有限编码/保留位规则；12 项最终 reset 修订为 8 PASS、4 CONDITIONAL，TMP100 四项位宽修订 PASS。候选内部 558 个数值 reset pair 对齐；14 个 LIS3DH 动态字段没有静态 reset，不编造零。
- 42 个针对合法输入、掩码、无适用对象、读回规范化、故障注入、过期证据等的回归测试通过。其中41个来自独立代码审查，另1个针对主任务最终核对发现的MPU6050旧注解覆盖问题。
- 20/20 参考准入：{ref_summary['passed']} 个适用测试函数通过、{ref_summary['skipped']} 个无适用维度跳过，实际执行 {ref_assertions} 条比较。**这些比较不等同认证 {ref_assertions} 条独立来源事实**。
- 720 个既有模型样本完成第二版 CPU 重判；每个样本8个 JUnit 记录，未重新生成代码，未使用 SCNet/GPU；原60个模型结果文件和原 harness 的哈希复核不变。

## 同一批代码的评分协议敏感性

| 模型 | 原第一版全通过 | 第二版候选全通过 | 由未通过转为通过 | 由通过转为未通过 |
|---|---:|---:|---:|---:|
{chr(10).join(summary_lines)}

全通过指当前协议全部适用维度通过。两版目标、输入范围和测试实例隔离有差异，表中增减是**评分协议改变**，不能写为模型学习或性能改善。原始 17 芯片/612 次主表、3 芯片/108 次扩展和本轮20芯片/720次筛查为不同队列，不合并。

具体芯片对照见 per_chip_protocol_comparison.csv；每个改变分类的样本及其代码哈希见 green_classification_changes.json。适用分母由静态 IR/policy 预先确定，见 coverage_plan.json 与 applicable_dimension_outcomes.csv，不用参考通过数反推分母。AD5592R/ADS1220 没有 RO 寄存器，相关维度正确跳过。

## 第二版为何不同

1. TMP100 门限改为所有 ADC 分辨率下均保留12位；12项 register/field reset 对齐修订在候选中执行。TMP117 门限限定 factory EEPROM 默认范围，ID高4位、INA3221冲突数据位保留不确定性。
2. 按有限来源核对补入合法域，跨字段前置条件、强制默认输入、未知访问掩码分别处理。TMP117 MOD=2读回0有明确 oracle；MOD=3、LIS2DW12 BOOT非零和Bosch forced完成时间暂不判静态持久性。AD5592R两位使能采用正文明确的00/11，01/10暂排除。
3. 每个刺激用新实例，避免先前字段或测试的副作用；无适用对象/零掩码跳过。RO字段测试在合法RW基线上仅翻转被保护字段，避免用非法整寄存器全1刺激误触发复位。
4. CoR 比较返回的完整已知数据再检查清零。复位键在可观测的非默认合法状态下分别检查错误键、正确键，故障夹具证明“读回错误数据”“总是复位”“从不复位”会被抓住。
5. 两版测试函数都在首个失败处停止；完整日志不代表逐字段全部原因已穷尽。fixture/import错误是代码载入或构造问题，8个错误测试并非8项独立硬件语义发现。

## 最终审计修正

初轮第二版错误继承了MPU6050 DEVICE_RESET的旧UNVERIFIED注解，跳过了已有来源依据的复位位，造成1个虚假的新增全通过。主任务直接复核本地RM-MPU-6000A-00 Rev4.2 pp.40–41及已有独立签审后，在 `.1` 版明确恢复该位，并以“不执行复位的存储模型必须失败”的第42项回归检查防止再漏测。静态模型将完成后的复位动作作为原子事件，不声称实际100ms时序已经验证。初轮全部输入、输出和日志保留在 audit_round_1/，其评分不用于最终结论。CODE_REVIEW.md记录的是独立审查当时41项/74维通过检查点；本报告给出主任务修正后的最终42项/75维记录。

最终27个从通过转为未通过的样本均在合法非默认状态下，正确复位键没有恢复已修改寄存器：24个AD5592R、3个BMP280。它们通过了第一版仅在默认状态下执行的复位键检查。该结果体现测试失效敏感性改进，不能当作模型在本轮变差，也不能无条件推广到全部硬件缺陷。

## 仍需准入的边界

- **尚未认证全部572字段**。field_policy_inventory.json仅是逐字段规则清单，有 policy 不等于该字段所有事实通过；未覆盖动态标志、条件写入、EEPROM门控和所有完成时序。
- TMP117 Rev、INA3221图/表、TPS23861 R17[3:1]粒度冲突保持 UNRESOLVED。TPS R17歧义位写入时保留新实例读回，已知reset与未知access分别处理，不推断所有保留位恒零。
- 部分IR原描述确有错误，第二版候选更正并保留 additional_ir_annotation_repairs.json。历史生成仍使用旧输入：后补冻结不能重建当时完整提示词、IR哈希、模型revision；本轮不能证明对修正输入生成的能力。
- 20芯片内重复生成有分组关系，不把720次调用或5760测试函数当独立样本；本轮无显著性检验、无新因果或规模结论。无实物总线、模拟刺激、时序或真实驱动验证。

## 唯一下一步行动卡

M4：完成20芯片逐字段来源准入，优先动态标志、条件写入和保留位；为每项保留来源页码/访问/复位/合法输入/排除理由，形成独立复核记录，再冻结可用于正式新一轮生成的 Gold IR v2。使用现有PDF和CPU即可，本步无需购买硬件或启动SCNet。可复制提示词见 NEXT_ACTION.md。
'''
    (OUT / 'REPORT.md').write_text(report, encoding='utf-8')
    write('summary.json', {'status': 'BOUNDED_PROTOCOL_COMPLETE_SOURCE_ADMISSION_PARTIAL',
                           'reference': read(OUT / 'reference_summary.json')[0],
                           'models': summaries, 'transitions': transitions,
                           'reference_comparisons': ref_assertions, 'inventory_fields': len(inventory),
                           'no_source_certification_of_all_fields': True, 'original_scores_preserved': True})
    inputs = read(OUT / 'model_execution_manifest.json')['inputs']
    record = {'contract_version': '1.0', 'execution_status': 'EXECUTED_LOCAL',
              'sample_unit': '20 chips; 3 models with3seeds times4 technical repeats per chip; paired protocol sensitivity',
              'input_files': ['../../' + p['path'] for p in inputs] + ['protocol_manifest.json', 'source_policy.json', 'coverage_plan.json'],
              'analysis_source': ['../../_setup/run_protocol_v2.py', '../../_setup/summarize_protocol_v2.py',
                                  'harness/protocol_rules.py', 'harness/test_d2d_protocol_v2.py'],
              'software_version': 'Python ' + platform.python_version() + '; pytest local recorded in regression log',
              'environment_notes': ['CPU-only Windows; four workers; no new model generation or remote computation'],
              'random_seed': None, 'execution_log': ['reference_execution.log', 'model_execution.log', 'regression_execution.log'],
              'output_files': ['REPORT.md', 'summary.json', 'model_results.json', 'reference_results.json',
                               'reference_pytest_evidence.zip', 'model_pytest_evidence.zip', 'test_outcomes.csv',
                               'applicable_dimension_outcomes.csv', 'per_chip_protocol_comparison.csv'],
              'assumptions_checked': ['Reference admission binds current protocol hash', '740 executions with8 JUnit records each',
                                      'Static applicability matches every fully passing sample', 'No original file mutated'],
              'deviations_from_plan': ['Full source certification postponed; candidate scoring only',
                                       'Broader source-description errors found and retained in candidate change ledger'],
              'executed_on': '2026-10-12'}
    # JSON is valid YAML, but the bundled validator expects block scalar/list syntax.
    lines = []
    for key, value in record.items():
        if isinstance(value, list):
            lines.append(key + ':')
            lines.extend('  - ' + json.dumps(v, ensure_ascii=False) for v in value)
        else:
            lines.append(key + ': ' + ('null' if value is None else json.dumps(value, ensure_ascii=False)))
    (OUT / 'execution_record.yaml').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps({'models': summaries, 'transitions': transitions, 'reference_comparisons': ref_assertions}), flush=True)


if __name__ == '__main__':
    main()
