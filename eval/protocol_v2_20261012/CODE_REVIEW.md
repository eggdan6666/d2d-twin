# 第二版评分协议：独立代码与失效敏感性审查

日期：2026-10-12。审查任务：`/root/protocol_review`。这是独立 AI 子任务的有界代码审查，不能替代原始来源逐字段认证、实物测试或论文阶段验收。本任务只编写本报告及 `tests/test_policy_regressions.py`；主任务修复了 helper、harness 和 runner，第一版冻结测试及原始分数未由本任务修改。

## 结论

实际运行 `python -m pytest eval/protocol_v2_20261012/tests/test_policy_regressions.py -q --tb=short`：**41 passed**；最终来源补充落实后的复查为 0.23s。这组测试包括来源域约束、逐写入前置条件、未知位掩码、适用性及故意错误的传感器实现，不是将当前参考代码输出复制为期望值。

代码审查发现的失效敏感性和执行证据问题均已修复并有回归覆盖。最晚返回的 `LEGAL_DOMAIN_SUPPLEMENT.md` 新增的 TMP117 one-shot 与强制默认输入规则已与最终 policy 对齐，详情见下节。**有界第二版代码协议可用于已保存样本的独立重评；这不是 572 字段的完整来源认证。**

`reference_summary.json` 在最终检查点显示 20/20 参考实现返回成功，74 个聚合测试通过、86 个跳过、0 个失败/错误/超时；这是主任务执行输出的读取，**不是本审查重新跑了 20 个参考实现**。本审查另外实际验证 reference execution manifest 的协议 SHA-256 等于当前 manifest 的 SHA-256，且所列输入文件哈希全部一致。来源范围仍保留 `SOURCE_POLICY_REVIEW.md`、`LEGAL_DOMAIN_SUPPLEMENT.md`、`INDEPENDENT_REPAIR_REVIEW.md` 所列条件和冲突。

## 已修复的问题及其实际影响

| 问题 | 严重性 / 后果 | 最低修复与当前验证 |
|---|---|---|
| COR 只检查清零后的状态，不检查清零前返回值 | MAJOR：TPS23861 的 SUPPLY_EVENT 初始为 0x30，读 COR 时错误返回 0 仍可能通过 | 现在对全部已知位比较 COR 返回值与清零前普通读取值。故意“正确清零但错误返回 0”的传感器被回归测试拒绝。 |
| 非复位键写入仅在默认状态下检查 | MAJOR：任何写入都复位的实现无法与真正的键值保护区分 | 先用合法且可观察的写入产生非默认状态，错误键应保持该状态，正确键应复位。AD5592R 的“永不复位”和“每次写都复位”两个故障实现都被拒绝。 |
| reset 已知不等于访问已知，零掩码仍可能产生 passed | MAJOR：只有 reset 证据的字段会被错误算成写保护证据 | RO 保护使用访问掩码及非 read-clear 位；空 RO 集合跳过。普通 RW、触发、别名、COR 的实际循环与适用性都避开零掩码对象；混合已知/未知对象不误判未知对象。 |
| 有键值但没有合法可观察的状态扰动 | MODERATE：不能建立复位动作对照，可能产生空通过或错误失败 | reset-key 适用性依赖可观察的合法扰动。考虑 readback normalization 后仍与初始值相同的写入不会误称为扰动。 |
| 复用执行目录导致旧 XML / trace 留存 | MAJOR：超时或早期失败可能继承上一轮 passing case / assertion 计数 | runner 开始前删除指定的旧输出文件。含旧成功 XML 和 trace 的超时夹具证明本次结果不继承旧证据。 |
| 模型重评可以复用旧协议的参考准入 | MAJOR：修改 protocol 后未重新准入也可能继续评分 | 模型重评前必须验证 reference execution manifest 绑定当前 protocol manifest SHA-256。修改协议而保留旧准入记录的夹具被拒绝。 |
| 合法域不完整，未执行显式排除 | MAJOR：例如 TMP461 的 CR 写 15、LIS3DH 的 ODR 写 15，没有来源定义的 oracle | 来源审查建议进入独立 policy；回归检查 LIS3DH / ADS1220 / HDC2021 等合法域以及补充编码域，保留真正合法的 ADS1220 GAIN=7、IDAC=7、VREF=3。 |
| TMP117 MOD=2 不能按写值恒等读回 | MAJOR：明确的读回规范化会被判成模型错误 | policy 支持 2→0 的独立期望；正确规范化夹具通过，恒等存储 2 的夹具被拒绝。 |

以上修复只说明**明确错误行为能被当前测试识别**，不表示所有错误模型都能被检出。一次聚合测试仍可能在第一个失败处停止；执行日志不是每个字段、每条事件序列的完整穷举归因。

## 41 个回归用例的范围

- LIS3DH 每个计划写入的中间状态：ODR 只取 0–9，ODR=8 配 LPen=1 / HR=0，LPen 与 HR 不同时为 1，CTRL_REG0 低七位保持 0x10；非法 ODR=15 被拒绝。
- ADS1220 的 MUX / MODE / DR / IDAC 路由保留编码排除，single-ended PGA 前置条件，50/60 Hz 组合限制，CONFIG3 bit0 保持 0；定义明确的高编码不被误当保留。
- HDC2021 的精度合法域、已知 reset 与未知访问分离；TMP117 revision 高四位屏蔽不会掩盖 DID 低位错误；INA3221 冲突寄存器写入不评分。
- TMP461、MPU6050、AD5592R、LIS2DW12 的九个新增编码域；AD5592R DAC_RD_EN 的 [0,3] 根据 p.29 明确 Bits[4:3]=11 的正文，并保留 p.36 表格表达歧义的范围声明。
- 无 RO 的真实芯片、只有 reset 证据的合成 RO、全部 read-clear 的 RO、只有排除字段的别名、没有已知输出的 RW / byte 以及不能产生扰动的 reset-key 均正确判为无适用断言。
- 三种混合已知 / 零掩码对象，以及错误 COR 返回值、无效复位动作、错误键触发复位、TMP117 读回规范化、旧执行产物和旧准入记录的故障敏感性。

合成 IR 和错误传感器都是明确标注的单元测试夹具，**不属于 720 个模型样本、20 芯片实验结果或硬件观测**。LIS3DH / ADS1220 的逐写入检查独立表达来源条件，没有直接调用 helper 的 `validate_state()` 充当期望真值。

## 最晚来源补充的最终落实

下列来源要求在本报告最初检查点尚待落实；随后主任务修复 policy、重新冻结并重跑参考准入。本审查实际读取更新后的 policy 并重跑原有 41 个回归，均通过。来源事实依据补充报告，主任务的精确规则是明确的有限范围协议选择。

1. **TMP117 CONFIG.MOD=3**：`LEGAL_DOMAIN_SUPPLEMENT.md` 引 p.27 Table 7-6：one-shot 完成后进入 shutdown。最终 policy 保留合法域 [0,1,2,3]，普通静态测试域限制为 [0,1,2]，明确排除 3 的完成/时序行为，保留 2→0 规范化。不能把 3 称为非法值，也不要求它无限保留 3。
2. **TMP461 CONFIG 保留 [4:3] / [1:0]**：补充报告引 p.20 §8.6.1.4 要求一直保持 0。最终 `CONFIG.RSV_4_3` / `CONFIG.RSV_1_0` 保留已知初始值、输入固定为 0、排除翻转后的访问行为检查；`CONSECUTIVE_ALERT.FIXED_1` 的输入保持 1。
3. **TPS23861 INTERRUPT_TIMER / GENERAL_MASK 保留字段**：独立来源审查续核 pp.68 / 63 后，最终 `INTERRUPT_TIMER.ROM` 已知初始 0，输入固定 0 且不翻转评分；`GENERAL_MASK.RSV3` / `RSV2` / `ROM1` 的 reset 为 Reserved，访问/初值不裁定，不改写成零保证，而是通过新实例读取保留位，在合法写入时保持已观察位值。这与 INTERRUPT_TIMER 的确定初值规则分开处理。

这些规则均进入 `source_policy.json`；参考准入已绑定更新后的 manifest。保守排除缩小了断言范围，不能由此宣称被排除的真实功能已验证。

## 审查边界与证据状态

贡献视角：第二版可以提高有界来源契约的可信度，分数变化来自协议、掩码、合法域和参考修订，不能写成新模型能力提高。

方法视角：保留第一版及原始生成记录；这里的重评没有恢复早期 prompt / IR / model revision 的生成指纹。静态直接寄存器通过不证明模拟转换、总线时序、跨字段全部语义或实物一致性。未核实的 572 字段与 INA3221 / TMP117 原文冲突不能因参考通过或 41 个测试通过而关闭。

表达视角：74 个聚合函数、41 个回归用例、572 个字段以及每模型 240 个样本是不同计数，不能互相替换；无适用的 skip 应独立报告，不能计作芯片功能通过。

- `EXECUTED_LOCAL`：本审查实际运行了 41 个回归，0 失败，命令与用例源文件在仓库内；故障夹具与超时夹具均为本地受控测试。
- `VERIFIED_USER_MATERIAL`：实际读取独立 source / repair review、20 IR、policy、coverage plan、helper、harness、runner 及 reference summary。
- `VERIFIED_SOURCE` 的直接范围：实际提取 AD5592R p.29 正文核对 Bits[4:3]=11；其他来源域依据已读取的独立来源审查报告，不冒称本审查逐页复核所有原始 PDF。
- `NOT_EXECUTED`：本审查未新增模型生成、未重跑 720 样本、未进行硬件测量、未认证当前厂商官网版本。
- `PENDING_VERIFICATION`：未全面审校字段、动态事件/完成行为以及厂家内部冲突；最终补充规则的本轮有限范围落实已经核对。

## 专家返回契约

```yaml
contract_version: "1.0"
expert_skill: sci-skills-presubmission-review
project_id: d2d-twin
paper_family: M
stage_id: M4
task_id: /root/protocol_review
task_status: COMPLETE
inputs_reviewed: ["source_policy.json", "SOURCE_POLICY_REVIEW.md", "LEGAL_DOMAIN_SUPPLEMENT.md", "INDEPENDENT_REPAIR_REVIEW.md", "20 v2 IR files", "coverage_plan.json", "protocol_rules.py", "test_d2d_protocol_v2.py", "run_protocol_v2.py", "reference_summary.json", "AD5592R p.29 text"]
outputs: ["eval/protocol_v2_20261012/CODE_REVIEW.md", "eval/protocol_v2_20261012/tests/test_policy_regressions.py"]
evidence_status: ["EXECUTED_LOCAL: 41 focused tests passed and reference admission hash binding verified", "VERIFIED_USER_MATERIAL for reviewed artifacts and final supplementary policy integration", "VERIFIED_SOURCE only for bounded AD5592R prose", "PENDING_VERIFICATION for broader source boundaries", "NOT_EXECUTED for model generation and hardware"]
assumptions: ["Static source-contract MVP", "Independent AI code reviewer", "Synthetic fixtures are not experimental results", "Factory EEPROM scope follows independent review"]
author_input_needed: []
manual_actions: []
quality_checks: ["41 tests passed", "Faulty COR return rejected", "No-op and any-key reset mutants rejected", "Unknown masks never create scored comparisons", "Stale execution evidence rejected", "Stale reference admission rejected", "Final supplementary policies read and aligned", "Current reference admission manifest binding and all listed input hashes verified"]
conflicts: ["Existing INA3221 source conflict", "Existing TMP117 revision ambiguity"]
conflict_resolution_status: UNRESOLVED
merge_permission: orchestrator_only
recommended_next_action: Rescore preserved samples under the admitted separately versioned finite-scope protocol, retain original scores, and report applicability/exclusions.
stage_acceptance_recommendation: NOT_ASSESSED
```

唯一下一步：主任务按已准入的独立第二版有限范围协议重评保存样本，保留第一版分数并输出适用/排除与差异清单。M4 的全面来源准入仍由主编排任务判断，本代码审查不推进论文阶段。
