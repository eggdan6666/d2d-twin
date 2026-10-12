# 使用与复现

在项目根目录，用现有 Python（有 pytest）运行：

```powershell
python -m pytest eval/protocol_v2_20261012/tests -q
python _setup/run_protocol_v2.py --references
python _setup/run_protocol_v2.py --models
python _setup/summarize_protocol_v2.py
python skills/sci-skills-statistical-reporting/scripts/validate_execution_record.py eval/protocol_v2_20261012/execution_record.yaml
```

这会在本目录的 work/ 内重新执行隔离 CPU 测试，更新本目录的执行证据。原始模型JSON、第一版测试与 d2d/IR 保留。日志分别保存在 reference_pytest_evidence.zip 和 model_pytest_evidence.zip；每个样本含 pytest.log、result.xml、d2d_diag.json。

协议输入以 protocol_manifest.json 校验。模型重判要求20个参考都通过，且其准入记录与当前协议哈希一致；修改过输入必须先重新准入。历史输入文件另以 model_execution_manifest.json 保留并复核哈希。

`--prepare` 是作者构建候选输入的步骤。本版本已有模型证据后该命令会拒绝覆盖；若要改评分或IR，需要复制代码/输出路径并设立新版本，保留此版本输入、分数与证据。

阅读 REPORT.md 查看结论；source_policy.json 查看具体来源规则；coverage_plan.json 查看适用维度和掩码；exclusion_inventory.json 查看未评分输入；per_chip_protocol_comparison.csv 查看逐芯片对照。候选运行通过不等于全来源认证或实物验证。
