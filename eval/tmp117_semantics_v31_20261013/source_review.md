# TMP117 v3.1 原始来源审校

本报告是独立、限定任务的原始来源审校，不是硬件验证或阶段准入批准。已直接读取本地完整厂商PDF，并检查关键页图像。时间：2026-10-13。项目d2d-twin，方法应用路线M，M4，任务tmp117-v31/source_review。

## 1. 文献定位
Texas Instruments TMP117数据手册，SNOSD82D，June2018 / revisedSeptember2022。本地PDF共50页，印刷页码与PDF页码在所审正文段一致。路径`corpus/data/raw_pdf/TI/TMP117.pdf`；SHA-256 `afe974873c80a7a4e1d342e9044e71c6f905caf4f04c1f0ea0df5c6ba35f980e`。来源级别为完整厂商文件，非摘要或二手转述。

## 2. 审校问题
限定核验EEPROM后备CONFIG/门限/offset、POR与general-call、单次转换/平均/完成与读取副作用。目标是阻止把未知、时间典型值、任意实现约定写成唯一来源真值。

## 3. 已有路线
旧v3对EEPROM忙/加载和阈值事件做了有限实现；本次为独立新目录提供源事实和闭包约束。旧文件保持隔离，不修改原IR、冻结测试或历史结果。

## 4. 尚未解决的问题
活跃周期中AVG/CONV改写和重复MOD11、自动shutdown后MOD数值读回、非整除平均舍入、offset相对平均的精确管线顺序都没有完整来源规定。旧SoftReset与Revision图/表冲突继续保留。

## 5. 核心约束
持久配置mask必须为0x07fc；MOD1不持久。禁止把未知MOD读回固定成01、把含负数的平均套用未经来源证明的Python舍入、把offset溢出写成回绕。来源明确要求offset结果饱和。

## 6. 机制概述
EUN0写易失寄存器；EUN1写可编程后备并产生Busy，完成后通过general-call reset / POR加载生效。POR期间CONFIG/limits写忽略并允许读。Busy是状态谓词，不是固定毫秒计时。单次转换按AVG收满1/8/32/64样本后发布结果并进入shutdown；MOD01可立即中止。

## 7. 模块与证据约束

### NVM-CONFIG-MASK
原文事实（释义）：Only MOD0 and CONFIG bits9:2 are EEPROM-persistent; MOD1 is not. Exact backing mask is 0x07fc. Factory CONFIG is0x0220.

定位：印刷/PDF页27,28；Figure7-14 notes(1)-(2); Table7-6。

- Separate persistent mask0x07fc from volatile writable mask0x0ffc and from source-conflicted SOFT_RESET bit1.
- Source-prohibited default one-shot maps to shutdown at startup; never persist MOD1.
- Mask derivation is a digital bitwise consequence of explicitly tagged bits, not a silicon measurement.

### NVM-BACKED-LOCATIONS
原文事实（释义）：CONFIG tagged bits, THIGH, TLOW and TEMP_OFFSET have writable EEPROM reset images; defaults0x0220,0x6000,0x8000,0x0000 are factory profile values.

定位：印刷/PDF页18,25,27,28,29,31；Section7.5.1.1; Table7-3 note(1); Figure7-14; Tables7-8,7-9,7-13。

- Keep arbitrary seeded image separate from factory defaults.
- General-call reset loads EEPROM-backed values, including signed nonzero offset.
- Do not enlarge this IR into general-purpose EEPROM1/2/3 without a separate task.

### NVM-LOCKED-WRITES
原文事实（释义）：With EUN0, programmable-address writes change digital volatile registers without programming EEPROM.

定位：印刷/PDF页18,30；Section7.5.1.2; Table7-10 EUN。

- Test volatile changes then reset reload of old backing image.
- Assert no Busy/program event for ordinary locked write.

### NVM-PROGRAM
原文事实（释义）：EUN1 enables backing programming on writes to programmable locations. Busy is set, readiness is polled, no I2C write should occur before completion. A subsequent general-call reset loads programmed data and clears EUN.

定位：印刷/PDF页18,19,30；Section7.5.1.2; Figure7-7; Table7-10。

- Use explicit program-completed event with nonzero before/after observables.
- Reject prohibited busy writes as outside contract; do not assert their hardware response is ignore, NACK or exception.
- Do not score immediate volatile readback/activation of unlocked writes: it is not specified explicitly.
- Avoid temperature conversions while EUN1.

### NVM-POR
原文事实（释义）：Reset starts approximately1.5ms EEPROM load; CONFIG and limit writes in this initial POR are ignored, reads are allowed, and EEPROM Busy is set while load executes.

定位：印刷/PDF页18,30；Section7.5.1.1; Table7-10。

- POR started and POR completed are logical events, not wall-clock simulation.
- Verify CONFIG/THIGH/TLOW ignore using nonzero attempted writes and later backing reload.
- POR writes to OFF, EUN or scratch EEPROM are not defined by the ignore clause: reject or leave unscored.

### NVM-BUSY-MIRROR
原文事实（释义）：EEPROM_UL bit14 mirrors CONFIG bit12; flags indicate EEPROM programming or POR load. Clear only when completion/readiness established.

定位：印刷/PDF页27,30；Tables7-6,7-10。

- Both mirrors must be1 in active program and POR,0 after corresponding completion.
- Read must not clear Busy. Register table reset0 is post-load baseline, not permission to skip active POR phase.

### GENERAL-CALL-RESET
原文事实（释义）：The device responds to general-call address0000000 with eighthbit0 and secondbyte00000110 by resetting registers to power-up values.

定位：印刷/PDF页18,22,24；Section7.5.3.1.6; Figure7-12; Section7.5.1.2。

- A semantic general-call event can stand for this accepted frame; no physical ACK, arbitration or wire-timing claim.
- General-call then POR completion reloads image and locks EUN.

### MODE-ENCODINGS
原文事实（释义）：MOD00 and10 are continuous;10 reads back00. MOD01 instantly aborts active conversion into shutdown. MOD11 starts one-shot; after completion device enters shutdown.

定位：印刷/PDF页14,15,27；Sections7.4.1-3; Table7-6 MOD。

- Use runtime mode state separately from raw post-one-shot MOD bits.
- Unknown automatic-shutdown numeric readback must not be fabricated as01.
- Allow explicit MOD01 abort with previously accumulated samples discarded.
- Do not assert unsupported AVG/CONV edits, repeated MOD11 or mode changes restart a partial cycle.

### AVERAGE-COUNTS
原文事实（释义）：AVG0/1/2/3 choose1/8/32/64 conversions; accumulation is batch average, not a running average. Result and DataReady publish only at end of batch. Applies CC and OS.

定位：印刷/PDF页12,15,26,27；Section7.3.2; Section7.4.3; Table7-6 AVG; Table7-5。

- Require exactlyN completed sample events before first publication; test N-1 and N.
- OS completion enters shutdown, so N+1 event is unsupported.
- Rounding of nonintegral means and precise offset-versus-average pipeline order are not specified.
- Use identical or evenly divisible nonsaturating samples for exact mean oracle; saturation tests can use constant samples.

### OS-CONV-INDEPENDENT
原文事实（释义）：One-shot duration contains active conversion only and is affected by AVG, not CONV; after completion DataReady can be cleared by TEMP or CONFIG read.

定位：印刷/PDF页15,27；Section7.4.3; Table7-6 DataReady。

- Sweep CONV0..7 with fixedAVG and assert the same sample count, not identical physical elapsed time.
- Completion event is post-linearization sample/result abstraction.

### CC-CYCLE-TABLE
原文事实（释义）：Table7-7 reports CC conversion CYCLE times; rowsCONV0..7 and columnsAVG0..3: [15.5,125,500,1000], [125,125,500,1000], [250,250,500,1000], [500,500,500,1000], four1000, four4000, four8000, four16000 milliseconds.

定位：印刷/PDF页14,28；Figure7-3; Table7-7; paragraph after table。

- Do not describe the entire table as standalone standby time.
- No standby when required averaging active period is longer than requested cycle.
- A table lookup check validates transcription only; no physical timer/conversion accuracy proof.

### SIGNED-OFFSET-SATURATION
原文事实（释义）：TEMP_OFFSET is signed16 two's-complement with1LSB=7.8125mC, added after linearization; out-of-bound sum shows maximum/minimum result.

定位：印刷/PDF页26,31；Sections7.6.2,7.6.9; Tables7-5,7-13。

- Decode signed16 before arithmetic; clamp to[-32768,32767], then encode.
- Test nonzero positive and negative offset and positive/negative saturation; never wrap.
- Do not invent physical temperature or linearization model: injected code is already linearized.
- Use uniform sample vectors for saturation to avoid unspecified pipeline ordering.

### SIGNED-LIMITS
原文事实（释义）：THIGH/TLOW use signed16 two's complement, sameLSB asTEMP, loaded from backing EEPROM on reset.

定位：印刷/PDF页29；Sections7.6.4-5; Tables7-8-9。

- Compare signed temperature against signed limits; positive/negative cross-zero cases required.
- Ordered limits are a benchmark domain guard, not an asserted hardware prohibition for reversed limits.

### READY-READ-CLEAR
原文事实（释义）：DataReady sets on completed register update and clears on either TEMP or CONFIG read.

定位：印刷/PDF页14,15,27；Sections7.4.1,7.4.3; Table7-6 DataReady。

- Return the pre-clear CONFIG flag value then clear side effect.
- TEMP reads clearReady only; they do not acquire the CONFIG alert-clear side effect.

### ALERT-MODE
原文事实（释义）：TNA0: >THIGH setsHIGH, <TLOW setsLOW; CONFIG read clears flags. ALERT signal reflectsHIGH orLOW unlessDR_ALERT selectsReady; POL chooses active polarity.

定位：印刷/PDF页16,27；Section7.4.4.1; Figure7-5; Table7-6。

- Test positive and negative signed thresholds, snapshot-then-clear, and re-arm with a later conversion.
- The vague ALERT wording in p15 OS paragraph does not imply unconditionalHIGH/LOW on every OS completion.
- Equality does not exceed/fall below thresholds; avoid inventing an unconditional clear at equality.

### THERM-MODE
原文事实（释义）：TNA1:HIGH sets abovehigh and clears belowlow; between/equality preserves hysteresis state;LOW reads0. CONFIG reads do not clearHIGH. ALERT remains until qualifying conversion, not CONFIG/SMBus response.

定位：印刷/PDF页17,27；Section7.4.4.2; Figure7-6; Table7-6。

- Test assertedHIGH survivingCONFIG read, intermediate and threshold-equality values, then belowlow clear.
- DataReady still clears onCONFIG/TEMP inTHERM.
- Do not assert unspecified mode-change-time alert flag clearing/recomputation.

### SOURCE-TIMING
原文事实（释义）：Single active conversion has13/15.5/17.5ms min/typ/max under specified conditions; p12 example8conversions is124ms active, Table7-7 uses125ms CC cycle. Programming7ms is typical; POR1.5ms approximate. SoftReset prose duration2ms is separate and source-conflicted.

定位：印刷/PDF页6,12,18,28；Section6.5; Section7.3.2; Section7.5.1.2; Table7-6。

- No measured latency claims from logical events.
- Do not collapse124ms active into125ms cycle, or treat typ/program/POR figures as guaranteed event deadlines.

## 8. 算术与假设
输入code按signed16解码（高位1时减65536）；只有可精确整除的样本和或均匀样本支持唯一整数平均oracle。offset按signed16解码，和限定到[-32768,32767]，再编码为16位。饱和测试使用恒定样本；不将未规定的管线先后顺序变成来源事实。样本是已线性化数字事件，不是物理温度采集。寄存器±256°C表述不改变signed16的整数端点。

## 9. 材料范围
审阅正文页6、12、14-19、21-22、24-32；关键页15/18/27/28/31直接看图。核对独立审校中的15个REPAIR字段、16个REPAIR维度。未调用网络、第三方API或模型服务，也未采集硬件实测。

## 10. 验证设计要求
必须有非零旧值/新值、N-1/N样本、负数比较、锁定与解锁差异、两个Busy镜像、复位后reload和实际故障检出。仅观察reset0或把未执行功能算作通过均不构成闭包。未知bit用knownmask隔离；完整CONFIG若含未知MOD不能返回伪造零。

## 11. 字段—来源—闭包建议
字段对应的全部必需claimID见同目录JSON的closure_advice。来源事实只支持已实现/已执行的具体条款，不能按字段名批量关闭整个维度。

| 字段 | REPAIR维度 | 必须落实的主要条款 |
|---|---|---|
| TMP117.CONFIG.AVG | conditional_write | NVM-CONFIG-MASK,NVM-LOCKED-WRITES,NVM-PROGRAM,NVM-POR,AVERAGE-COUNTS |
| TMP117.CONFIG.CONV | legal_encoding,conditional_write | CC-CYCLE-TABLE,NVM-CONFIG-MASK,NVM-LOCKED-WRITES,NVM-PROGRAM,NVM-POR,OS-CONV-INDEPENDENT |
| TMP117.CONFIG.DATA_READY | read_clear | READY-READ-CLEAR,AVERAGE-COUNTS,OS-CONV-INDEPENDENT |
| TMP117.CONFIG.DR_ALERT | conditional_write | NVM-CONFIG-MASK,NVM-LOCKED-WRITES,NVM-PROGRAM,NVM-POR,ALERT-MODE,READY-READ-CLEAR |
| TMP117.CONFIG.EEPROM_BUSY | trigger_completion | NVM-BUSY-MIRROR,NVM-PROGRAM,NVM-POR |
| TMP117.CONFIG.HIGH_ALERT | read_clear | ALERT-MODE,THERM-MODE,SIGNED-LIMITS |
| TMP117.CONFIG.LOW_ALERT | read_clear | ALERT-MODE,THERM-MODE,SIGNED-LIMITS |
| TMP117.CONFIG.MOD | conditional_write | MODE-ENCODINGS,NVM-CONFIG-MASK,NVM-LOCKED-WRITES,NVM-PROGRAM,NVM-POR,AVERAGE-COUNTS |
| TMP117.CONFIG.POL | conditional_write | NVM-CONFIG-MASK,NVM-LOCKED-WRITES,NVM-PROGRAM,NVM-POR,ALERT-MODE |
| TMP117.CONFIG.TNA | conditional_write | NVM-CONFIG-MASK,NVM-LOCKED-WRITES,NVM-PROGRAM,NVM-POR,THERM-MODE,ALERT-MODE |
| TMP117.EEPROM_UL.EEPROM_BUSY | trigger_completion | NVM-BUSY-MIRROR,NVM-PROGRAM,NVM-POR |
| TMP117.EEPROM_UL.EUN | conditional_write | NVM-LOCKED-WRITES,NVM-PROGRAM,NVM-POR,GENERAL-CALL-RESET |
| TMP117.TEMP_OFFSET.OFF | conditional_write | NVM-BACKED-LOCATIONS,NVM-LOCKED-WRITES,NVM-PROGRAM,SIGNED-OFFSET-SATURATION |
| TMP117.THIGH.H | conditional_write | NVM-BACKED-LOCATIONS,NVM-LOCKED-WRITES,NVM-PROGRAM,NVM-POR,SIGNED-LIMITS,ALERT-MODE,THERM-MODE |
| TMP117.TLOW.L | conditional_write | NVM-BACKED-LOCATIONS,NVM-LOCKED-WRITES,NVM-PROGRAM,NVM-POR,SIGNED-LIMITS,ALERT-MODE,THERM-MODE |

## 12. 结论边界
本次source_review任务完成，17条来源约束已核验。不能据此声称15字段整体PASS、16维度整体关闭、20芯片572字段已获正式生成准入；新实现和独立测试必须另验。可以建立有明确guard和knownmask的限定数字场景，不需要硬件才能完成此限定验证。

## 13. 来源自身限制
典型时间依赖条件；手册没有提供上述边界的完整状态转移表、平均舍入规则、offset平均饱和管线细节。图与表在SOFT_RESET类型和revision reset上冲突，未找到或声称官方勘误。

## 14. 批判性判断
最危险的假通过来自把未知读回算成常量、把违反编程条件的写入响应自定义为oracle、以及将工厂EEPROM默认当成任意设备的reset真值。后备image、状态事件、knownmask和合法刺激域应彼此独立；拒绝越界行为是基准scopeguard，不是芯片会抛异常的硬件事实。

## 15. 可复用认识
带NVM的配置不等于普通静态RW；完成事件不等于耗时；一个字段多个来源条款不能由一次读写通过证明全闭包。动态图/表的事实应精确落到测试维度，而不是只落到chip/field标签。

## 16. 可证伪后续工作
唯一下一步：按照17条约束实现v3.1，并使用独立非零事件/故障场景核验每个已覆盖条款，再由编排者决定限定闭包；未覆盖与来源冲突继续留在队列中。重点可证伪条件是错误持久MOD1、提前N-1更新、负数回绕、Busy清读、THERM误清都被检测出来。

审校签审建议：REPAIR；阶段权威仍归SCI-Skills编排者。所有未知或冲突在source_review.json逐项保留。
