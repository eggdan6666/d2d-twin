# 独立来源审校交付索引

主结论与签审：[INDEPENDENT_SIGNOFF.md](INDEPENDENT_SIGNOFF.md)。

- 输入冻结建议：[INPUT_FREEZE_RECOMMENDATION.md](INPUT_FREEZE_RECOMMENDATION.md)；当前正式冻结不准入。
- 572字段快速结论：field_verdicts.csv；4004维度原文证据：dimension_evidence.csv / field_evidence.json。
- 84差异记录：DIFFERENCES.md / revision_candidates.json；候选输入：candidate_ir/、candidate_source_policy.json。
- 来源身份：SOURCE_IDENTITIES.md / reviewed_source_manifest.json；未解决冲突：conflict_ledger.json。
- 审校材料冻结：audit_bundle_manifest.json；输入候选字节快照：input_freeze_candidate_manifest.json。
- 保护证明：preservation_verification.json；分区签审与契约：partitions/、expert_returns.json。

复现仅需现有Python与PyMuPDF：prepare.py是仅首次提取/建立baseline用，不要覆盖本轮before基线；consolidate.py整合与保护复核，finalize.py写签审/冻结候选。所有脚本只写新目录。

唯一下一步：在独立新目录落实契约与新harness、验证门控后再冻结正式生成。
