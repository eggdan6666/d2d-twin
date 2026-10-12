# 唯一下一步行动卡

阶段 M4，方式 PROMPT。目标：完成全部来源契约准入，再冻结正式实验输入。

复制提示词：

> 请以独立来源审校者身份，阅读 eval/protocol_v2_20261012/REPORT.md、SOURCE_POLICY_REVIEW.md、LEGAL_DOMAIN_SUPPLEMENT.md、INDEPENDENT_REPAIR_REVIEW.md、source_policy.json、field_policy_inventory.json 与 protocol_manifest.json。使用 corpus/data/raw_pdf/ 内原始厂商 PDF，逐项审查20芯片/572字段的 reset、access、合法编码、读后清零、触发完成条件、条件写入和保留位策略，保留器件/手册版本/文件SHA-256/印刷页码/表号/结论。重点核对未覆盖的动态标志、EEPROM门控和模式副作用。区分厂商事实、寄存器抽象假设、未定义行为和来源冲突，不以参考通过或模型高分代替来源证据。不要修改 d2d/ir、冻结 test_d2d_blackbox.py 或任何历史模型结果；先把修订候选、逐项PASS/REPAIR/CONDITIONAL/EXCLUDE证据和差异清单保存到一个新目录。保留TMP117/INA3221/TPS23861冲突，不将推测称为官方勘误。输出独立签审和可被新一轮生成使用的输入冻结建议；本步不需要SCNet或购买实物。

验收材料：逐字段来源台账；所有关键冲突与排除理由；候选IR/policy差异；参考准入与回归日志；IR、policy、提示词模板、harness和软件版本哈希。通过后再决定正式新生成实验及是否加入驱动/硬件验证。
