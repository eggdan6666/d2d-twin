# 20 芯片离线复判与失败分析

状态：EXECUTED_LOCAL。当前 IR 保存为 `20261012-candidate` 快照；这不是全部来源审校通过的声明。

## 可复核结果

740 次 CPU pytest 已完成：20 份参考实现与 720 份原始生成代码。冻结 harness MD5 仍为 8cf0854d4779467bc8e472ee4fb97023。

| 模型/参考 | 全绿 | passed 测试函数 | failed | error | skipped |
|---|---:|---:|---:|---:|---:|
| reference | 20/20 | 77 | 0 | 0 | 83 |
| qwen3b | 22/240 | 355 | 505 | 136 | 924 |
| ds67b | 25/240 | 364 | 548 | 24 | 984 |
| qwen14b | 48/240 | 551 | 373 | 0 | 996 |

全绿数与原记录一致。719/720 样本返回码与 passed 计数同时匹配；Qwen3B/BMP280/seed1/i2 原本提取代码失败（rc=-1），本次将空模块送入 pytest 得到 fixture error（rc=1），两次均不全绿。
该样本属于代码提取失败，不把其 8 次 fixture error 当 8 个独立硬件行为缺陷。

## 分母与空断言

参考实现共 77 个 passed、83 个 skipped。然而 `test_readonly_protection` 在 AD5592R 和 ADS1220 上没有 RO 寄存器可遍历，返回 passed 却没有执行保护断言。
因此只有 75 个非空适用测试函数（每颗 2–5 项），不能把参考 20/20 全绿写成全部硬件语义 100% 真实。
`reference_coverage.csv` 区分 reported passed 与非空适用项。`applicable_dimension_outcomes.csv` 根据 IR 与实际 harness 分支定义分母；空断言、skip 和 fixture error 分开记录。

## Qwen14B 逐维结果

| 测试 | 适用芯片 | passed | failed | error |
|---|---:|---:|---:|---:|
| test_clear_on_read | 1 | 0 | 12 | 0 |
| test_read_write_alias | 2 | 0 | 24 | 0 |
| test_readonly_protection | 18 | 100 | 116 | 0 |
| test_reset_values | 20 | 240 | 0 | 0 |
| test_rw_field_persistence | 20 | 97 | 143 | 0 |
| test_single_byte_semantics | 1 | 12 | 0 | 0 |
| test_write_only_reset_key | 3 | 26 | 10 | 0 |
| test_write_trigger_fields | 10 | 52 | 68 | 0 |

这批样本的复位值检查全部通过；RW 位域、写触发、读写别名和读清除仍产生失败。
RO 保护结果仍受到源契约和保留位约定的影响。别名仅覆盖 2 颗芯片，读清除仅 1 颗，不能写成对全部工业芯片的总体结论。
Qwen3B 有 17 个样本出现 fixture error，DeepSeek 有 3 个，14B 为 0；按样本统计于 execution_error_samples.json，不把同一初始化错误重复解释为多个独立发现。

## 证据范围

full_recheck_results.json、test_outcomes.csv 和 full_pytest_evidence.zip 包含全部逐测试结果、完整 traceback、JUnit 和诊断文件，替代之前仅从 tail 提取的失败下界。
每个测试函数内部遇到首个断言失败就停止；完整日志不等于该函数所有寄存器和位都已穷尽诊断。
本次保存了执行前的 IR、参考实现、harness、基类和原始结果哈希，但不能补回模型生成时的 IR/prompt/model revision 哈希。

## 唯一下一步

按 SOURCE_AUDIT.md 修订并复核源契约，建立单独编号的第二版评分协议；在协议准入前保留当前探索性结果，不替换论文主表。下一步可在本机完成，不需要 SCNet GPU 或购买硬件。
