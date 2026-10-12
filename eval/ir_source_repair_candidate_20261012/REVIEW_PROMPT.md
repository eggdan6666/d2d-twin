# 独立复核提示词

以下内容可复制给另一个 AI。复核应读取文件本身，不把本审查者的结论当作正确答案。

> 请独立复核 D2D-Twin 的金标来源修订候选。项目根目录是 `E:\HD-Agent·分层记忆RAG的电子Dstasheet智能问答`。
>
> 读取 `eval/ir_freeze_20261012/SOURCE_AUDIT.md`、`eval/ir_freeze_20261012/freeze_manifest.json`、`eval/ir_source_repair_candidate_20261012/repair_manifest.json`。比较两个目录的 `ir/`，不得修改 `d2d/ir/`、原始模型结果或冻结测试。
>
> 用 `source_document_manifest.json` 的路径和 SHA-256 确定原文版本。优先核对：TMP100 p.18 阈值 12 位与旧参考 FF80h 掩码；12 处字段复位值修订；LIS3DH p.35 ODR 合法值及现有 harness 是否真的执行排除规则；INA3221 p.33 图表冲突；TMP117 p.32 版本号未知位；两颗芯片 RO 保护函数空断言。
>
> 请将每条结论分为 PASS / REPAIR / UNRESOLVED，写明文件、寄存器/字段、源页码/表格、采用的证据、评分影响和仍存在的假设。不要将“存储行为”与“有效功能编码”混为一谈，不要因为参考实现通过便认定原文无误。必要时查看原 PDF 渲染页，不能只依赖 OCR。
>
> 检查 `tmp100_sensitivity.json` 和 `tmp100_pytest_evidence.zip`，确认原/新参考以及 36 个原始模型样本的复判结果。不得将修订候选的离线分数描述为重新生成后的性能。
>
> 输出到 `eval/ir_source_repair_candidate_20261012/INDEPENDENT_RECHECK.md`。给出逐项裁决及第二版评分协议能否准入的条件；不要自行宣称投稿审查通过。
