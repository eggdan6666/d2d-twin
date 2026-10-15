# INA226 v37 独立实现与证据准入审阅

**结论：PASS_CANDIDATE，仅针对声明的有界条款。** 未发现阻断当前六字段／六维度有界验收的实现缺陷；不建议整字段晋升、正式生成输入准入或物理硬件认证。M4 的阶段决定仍由 SCI-Skills 主协调者作出。

## 范围与输入

任务 `ina226-v37/code_review`，专家 `sci-skills-presubmission-review`，项目 `d2d-twin`，M4。独立读取原始 PDF SBOS547C（41 页，SHA256 `c9b67f886d4a5241a5e070723f7b61867409eeb27eed768b9cdd9cb17e03ca2d`）并直接重新提取 p11–13、p22–28；目视检查来源专家渲染的 p23、26、27。原文 p13 与 p27 的 AFF CONFIG-write 冲突直接确认，不以实现替代原始来源。

审阅 `ina226.py`、`scenarios.py`、`admission.py`、独立来源清单与接受合同、原字段范围及 README。测试先从原 PDF 的 POR、RST、AFF、CVRF 条款及独立来源清单制定；候选程序仅提供接口绑定，主场景不是独立 oracle。所有辅助代码、测试、突变副本、日志及本报告均仅写入 `sandbox/ina226_v37/code_review/`。

## 三个审阅视角

**Contribution。** 当前证据能支持“来源约束与独立验收的可审计有界闭环”在 INA226 六个待修维度上的一个数字事件实现。三项 reserved-access 以排除非默认访问 oracle 收口；RST、AFF、CVRF 以有条件事件规则收口。不能把排除门禁成功写成厂商访问行为已证实，不能把合成突变检出率写成 LLM 修复率。

**Methods。** 122 个独立运行时用例全部通过。覆盖严格类型／范围／事件形状、非法输入无状态及 trace 污染、当前配置代际与序列绑定、完成前暂存、三种完成条件严格布尔、两种 powerdown 例外、非零 AFF 的锁存保持与透明清除、MODE3 重触发、复位请求与完成、reserved POR knownness 与写后未知。10 个缺陷副本均被对应的原始来源 oracle 检出，原候选实现通过相同 oracle。

55 个准入与场景用例全部通过。其中包括 12 个真实主场景的独立重放、10 个必要见证缺失、3 个可选见证删除组合、10 个见证伪造、10 个来源建议伪造、3 个权威文件字节篡改、5 个非法执行载荷、无见证与原六维分母核验。缺必要见证产生 `PARTIAL`；删除 `nominal_table`／`named_conflict_candidates` 不妨碍 common-source 条款闭包。全部六行都保持 `whole_field_promoted=false`、`whole_dimension_closed=false`。

**Communication。** 已识别并修正文档解释边界：`read_masked` 是完整 16 位寄存器读取后的投影，线性化清除前快照采用不可穿插事件假设。候选模块与 README 现已说明；不能把它称为局部位／字节读取的硅片清除时序。来源冲突、未知位、MODE1/2/5/6 排除、非零校准后 CURRENT/POWER 未知均显式保留。

## 实际执行与字节绑定

最终执行：2026-10-14 03:50:24–03:50:26（Asia/Shanghai）。`execution_manifest.json` 记录精确命令、Python 版本、环境、全部输入前后 SHA256、逐场景检查数与输出哈希；所有输入前后字节一致。`review_junit.xml` 含每个测试用例及输入哈希 properties。

| 类别 | 实际通过数 |
|---|---:|
| 独立运行时 oracle | 122 |
| 合成缺陷区分测试 | 10 |
| 来源／见证准入及主场景重放 | 55 |
| 合计 | 187 |

最终 JUnit：187 tests，0 failures，0 errors，0 skipped。实际重放主场景 12 个，记录 215 条检查；不把场景检查数与 pytest 用例数相加为实验样本数。

实现字节绑定：

| 文件 | SHA256 |
|---|---|
| ina226.py | `13c0af60b11ada5459496e20ed321a7361fae7ec7589b978cfb572f06a1cef7a` |
| scenarios.py | `37d7705841ba5f962b9ec7bd4330ec099d460eb692efaafddd294d5f00a6208e` |
| admission.py | `0568a4fa9561d552574ea55a6f2fc205ce086d80d1d31f7e514b3876c9acfc05` |
| 接受的 source_review.json | `87f5b61b18453f8b074aee3e6c773da0b5e292283e276d86040301d90cf1fc71` |

10 种合成缺陷：忽略 stale epoch／sequence、忽略 averaging completion、非法输入先污染 trace、锁存无故障清零、透明读错误清零、CVRF 错误依赖 CNVR、脏复位不清 CAL、MODE4 错误清 CVRF、写后 reserved 保持假已知、common profile 静默选择 CONFIG 清 AFF。每个测试执行独立 oracle 并要求该 oracle 在缺陷副本上失败，不通过检查源代码字符串来冒充缺陷检出。

## 限制与风险

物理 I2C、ADC、模拟阈值、平均／乘法真实实现、时钟／复位／恢复时间、OVF 生命周期、并发重置位和 2260/2261 DIE variant 未验证。完成／告警事件是外部资格化数字刺激；代码不验证刺激来自硬件。文件哈希与确定性重放能阻止当前信任边界内的内容伪造，不是抵御同时改写受信任代码、哈希常量和审阅记录的加密远程证明。

AFF CONFIG 写后行为的厂商冲突仍 `UNRESOLVED`，common profile 保持未知；两个 named profiles 是来源条件候选而非解决冲突。read-before-clear 是协议假设，reserved 非默认写拒绝是范围入口策略。主协调者仍需核对旧 Harness／Gold 保全与最终包哈希，本专家未写入这些文件，也不声称替主协调者完成全项目冻结验收。

## 产物与质量检查

独立 oracle、缺陷副本生成器、准入测试、原文提取、12 场景见证、六行闭包、全用例 JUnit、执行日志及 manifest 均可本地复核。中间一次突变测试助手把副本的异常类误认作原模块异常类，已修正为绑定副本异常类型；这是测试助手问题，未据此报告候选缺陷。最终执行通过且绑定最终输入字节。

下一步：主协调者核对上述实现哈希及辅助产物 manifest 后，决定是否接受 INA226 六维有界条款，并继续保持整字段与生成输入未准入。
