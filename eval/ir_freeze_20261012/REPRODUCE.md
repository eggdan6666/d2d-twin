# 本轮离线复现

从项目根目录运行，使用已安装的 Python、pytest：

```powershell
python _setup/freeze_and_recheck_20chip.py --frozen
python _setup/prepare_ir_source_repairs.py
```

第一条验证已归档的 IR、参考实现、harness 和基类哈希，并复判 740 次；第二条从这些快照构造候选并复判 TMP100 的 38 个对象。不调用模型，不需要 GPU。

未加 `--frozen` 时，脚本会尝试对当前 `d2d/` 文件建立候选快照；如与此版本已存的快照不同，会拒绝覆盖。此保护是版本边界，不是解析错误。

`_setup/summarize_ir_source_audit.py` 用于整理执行结果、适用项和报告；当前要求 `_setup/` 下两份对应执行日志已保存。完整日志也已归档于本目录及候选目录的 evidence.zip。

原始 JSON 保存在三个 `eval/expansion_*` 目录，两个评分版本的结果应始终分开。此复现不能重建历史生成时未保存的输入和模型版本证据。
