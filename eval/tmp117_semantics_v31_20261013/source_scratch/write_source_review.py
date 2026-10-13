"""Package a direct original-PDF review; does not alter implementation or stage state."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent.parent
PDF = ROOT / 'corpus/data/raw_pdf/TI/TMP117.pdf'
SRC = 'corpus/data/raw_pdf/TI/TMP117.pdf'
SHA = hashlib.sha256(PDF.read_bytes()).hexdigest()

def claim(cid, fact, pages, locator, constraints, status='VERIFIED_SOURCE'):
    return dict(claim_id=cid, evidence_status=status, source_path=SRC,
                source_sha256=SHA, pdf_pages=pages, printed_pages=[str(p) for p in pages],
                locator=locator, paraphrased_fact=fact, implementation_constraints=constraints)

claims = [
    claim('NVM-CONFIG-MASK', 'Only MOD0 and CONFIG bits9:2 are EEPROM-persistent; MOD1 is not. Exact backing mask is 0x07fc. Factory CONFIG is0x0220.', [27,28], 'Figure7-14 notes(1)-(2); Table7-6',
          ['Separate persistent mask0x07fc from volatile writable mask0x0ffc and from source-conflicted SOFT_RESET bit1.', 'Source-prohibited default one-shot maps to shutdown at startup; never persist MOD1.', 'Mask derivation is a digital bitwise consequence of explicitly tagged bits, not a silicon measurement.']),
    claim('NVM-BACKED-LOCATIONS', 'CONFIG tagged bits, THIGH, TLOW and TEMP_OFFSET have writable EEPROM reset images; defaults0x0220,0x6000,0x8000,0x0000 are factory profile values.', [18,25,27,28,29,31], 'Section7.5.1.1; Table7-3 note(1); Figure7-14; Tables7-8,7-9,7-13',
          ['Keep arbitrary seeded image separate from factory defaults.', 'General-call reset loads EEPROM-backed values, including signed nonzero offset.', 'Do not enlarge this IR into general-purpose EEPROM1/2/3 without a separate task.']),
    claim('NVM-LOCKED-WRITES', 'With EUN0, programmable-address writes change digital volatile registers without programming EEPROM.', [18,30], 'Section7.5.1.2; Table7-10 EUN',
          ['Test volatile changes then reset reload of old backing image.', 'Assert no Busy/program event for ordinary locked write.']),
    claim('NVM-PROGRAM', 'EUN1 enables backing programming on writes to programmable locations. Busy is set, readiness is polled, no I2C write should occur before completion. A subsequent general-call reset loads programmed data and clears EUN.', [18,19,30], 'Section7.5.1.2; Figure7-7; Table7-10',
          ['Use explicit program-completed event with nonzero before/after observables.', 'Reject prohibited busy writes as outside contract; do not assert their hardware response is ignore, NACK or exception.', 'Do not score immediate volatile readback/activation of unlocked writes: it is not specified explicitly.', 'Avoid temperature conversions while EUN1.']),
    claim('NVM-POR', 'Reset starts approximately1.5ms EEPROM load; CONFIG and limit writes in this initial POR are ignored, reads are allowed, and EEPROM Busy is set while load executes.', [18,30], 'Section7.5.1.1; Table7-10',
          ['POR started and POR completed are logical events, not wall-clock simulation.', 'Verify CONFIG/THIGH/TLOW ignore using nonzero attempted writes and later backing reload.', 'POR writes to OFF, EUN or scratch EEPROM are not defined by the ignore clause: reject or leave unscored.']),
    claim('NVM-BUSY-MIRROR', 'EEPROM_UL bit14 mirrors CONFIG bit12; flags indicate EEPROM programming or POR load. Clear only when completion/readiness established.', [27,30], 'Tables7-6,7-10',
          ['Both mirrors must be1 in active program and POR,0 after corresponding completion.', 'Read must not clear Busy. Register table reset0 is post-load baseline, not permission to skip active POR phase.']),
    claim('GENERAL-CALL-RESET', 'The device responds to general-call address0000000 with eighthbit0 and secondbyte00000110 by resetting registers to power-up values.', [18,22,24], 'Section7.5.3.1.6; Figure7-12; Section7.5.1.2',
          ['A semantic general-call event can stand for this accepted frame; no physical ACK, arbitration or wire-timing claim.', 'General-call then POR completion reloads image and locks EUN.']),
    claim('MODE-ENCODINGS', 'MOD00 and10 are continuous;10 reads back00. MOD01 instantly aborts active conversion into shutdown. MOD11 starts one-shot; after completion device enters shutdown.', [14,15,27], 'Sections7.4.1-3; Table7-6 MOD',
          ['Use runtime mode state separately from raw post-one-shot MOD bits.', 'Unknown automatic-shutdown numeric readback must not be fabricated as01.', 'Allow explicit MOD01 abort with previously accumulated samples discarded.', 'Do not assert unsupported AVG/CONV edits, repeated MOD11 or mode changes restart a partial cycle.']),
    claim('AVERAGE-COUNTS', 'AVG0/1/2/3 choose1/8/32/64 conversions; accumulation is batch average, not a running average. Result and DataReady publish only at end of batch. Applies CC and OS.', [12,15,26,27], 'Section7.3.2; Section7.4.3; Table7-6 AVG; Table7-5',
          ['Require exactlyN completed sample events before first publication; test N-1 and N.', 'OS completion enters shutdown, so N+1 event is unsupported.', 'Rounding of nonintegral means and precise offset-versus-average pipeline order are not specified.', 'Use identical or evenly divisible nonsaturating samples for exact mean oracle; saturation tests can use constant samples.']),
    claim('OS-CONV-INDEPENDENT', 'One-shot duration contains active conversion only and is affected by AVG, not CONV; after completion DataReady can be cleared by TEMP or CONFIG read.', [15,27], 'Section7.4.3; Table7-6 DataReady',
          ['Sweep CONV0..7 with fixedAVG and assert the same sample count, not identical physical elapsed time.', 'Completion event is post-linearization sample/result abstraction.']),
    claim('CC-CYCLE-TABLE', 'Table7-7 reports CC conversion CYCLE times; rowsCONV0..7 and columnsAVG0..3: [15.5,125,500,1000], [125,125,500,1000], [250,250,500,1000], [500,500,500,1000], four1000, four4000, four8000, four16000 milliseconds.', [14,28], 'Figure7-3; Table7-7; paragraph after table',
          ['Do not describe the entire table as standalone standby time.', 'No standby when required averaging active period is longer than requested cycle.', 'A table lookup check validates transcription only; no physical timer/conversion accuracy proof.']),
    claim('SIGNED-OFFSET-SATURATION', 'TEMP_OFFSET is signed16 two\'s-complement with1LSB=7.8125mC, added after linearization; out-of-bound sum shows maximum/minimum result.', [26,31], 'Sections7.6.2,7.6.9; Tables7-5,7-13',
          ['Decode signed16 before arithmetic; clamp to[-32768,32767], then encode.', 'Test nonzero positive and negative offset and positive/negative saturation; never wrap.', 'Do not invent physical temperature or linearization model: injected code is already linearized.', 'Use uniform sample vectors for saturation to avoid unspecified pipeline ordering.']),
    claim('SIGNED-LIMITS', 'THIGH/TLOW use signed16 two\'s complement, sameLSB asTEMP, loaded from backing EEPROM on reset.', [29], 'Sections7.6.4-5; Tables7-8-9',
          ['Compare signed temperature against signed limits; positive/negative cross-zero cases required.', 'Ordered limits are a benchmark domain guard, not an asserted hardware prohibition for reversed limits.']),
    claim('READY-READ-CLEAR', 'DataReady sets on completed register update and clears on either TEMP or CONFIG read.', [14,15,27], 'Sections7.4.1,7.4.3; Table7-6 DataReady',
          ['Return the pre-clear CONFIG flag value then clear side effect.', 'TEMP reads clearReady only; they do not acquire the CONFIG alert-clear side effect.']),
    claim('ALERT-MODE', 'TNA0: >THIGH setsHIGH, <TLOW setsLOW; CONFIG read clears flags. ALERT signal reflectsHIGH orLOW unlessDR_ALERT selectsReady; POL chooses active polarity.', [16,27], 'Section7.4.4.1; Figure7-5; Table7-6',
          ['Test positive and negative signed thresholds, snapshot-then-clear, and re-arm with a later conversion.', 'The vague ALERT wording in p15 OS paragraph does not imply unconditionalHIGH/LOW on every OS completion.', 'Equality does not exceed/fall below thresholds; avoid inventing an unconditional clear at equality.']),
    claim('THERM-MODE', 'TNA1:HIGH sets abovehigh and clears belowlow; between/equality preserves hysteresis state;LOW reads0. CONFIG reads do not clearHIGH. ALERT remains until qualifying conversion, not CONFIG/SMBus response.', [17,27], 'Section7.4.4.2; Figure7-6; Table7-6',
          ['Test assertedHIGH survivingCONFIG read, intermediate and threshold-equality values, then belowlow clear.', 'DataReady still clears onCONFIG/TEMP inTHERM.', 'Do not assert unspecified mode-change-time alert flag clearing/recomputation.']),
    claim('SOURCE-TIMING', 'Single active conversion has13/15.5/17.5ms min/typ/max under specified conditions; p12 example8conversions is124ms active, Table7-7 uses125ms CC cycle. Programming7ms is typical; POR1.5ms approximate. SoftReset prose duration2ms is separate and source-conflicted.', [6,12,18,28], 'Section6.5; Section7.3.2; Section7.5.1.2; Table7-6',
          ['No measured latency claims from logical events.', 'Do not collapse124ms active into125ms cycle, or treat typ/program/POR figures as guaranteed event deadlines.']),
]

unknowns = [
    dict(id='ACTIVE-RECONFIGURATION', source_pages=[14,15,27], fact='Only MOD01 immediate abort is explicit; AVG/CONV edits, repeatedMOD11 and transitions while active lack a full restart/abort oracle.', policy='Reject unsupported active reconfiguration, preserve no-hardware-claim boundary.'),
    dict(id='AUTO-SHUTDOWN-MOD-READBACK', source_pages=[15,27], fact='Runtime shutdown after OS is explicit; exact numeric MOD readback is not.', policy='MarkMOD bits unknown after automatic completion; known-mask-aware reads/assertions required.'),
    dict(id='NONINTEGRAL-AVERAGE-ROUNDING', source_pages=[12,27,31], fact='Average rounding/tie behavior and offset-relative averaging saturation pipeline are not given.', policy='Reject nondivisible means; score constant or exactly divisible safe sequences. Do not certify a chosen Python division rule.'),
    dict(id='UNLOCKED-VOLATILE-READBACK', source_pages=[18,30], fact='Backing programming established, immediate volatile exposure/activation not explicit.', policy='Assert post-general-call/POR reload rather than intermediate unlocked readback.'),
    dict(id='POR-NONLIMIT-WRITES', source_pages=[18], fact='POR ignore statement coversCONFIG andlimits, notOFF/EUN/scratch.', policy='Reject unmodeled POR writes; do not generalize ignore.'),
    dict(id='CONFIG-SOFT-RESET', source_pages=[27,28], fact='Figure7-14 marks bit1R-0; continuedTable7-6 saysR/W reset trigger alwaysread0.', policy='Keep prior unresolvedsourceconflict, leaveSOFT_RESET unscored; no officialerratum claim.'),
    dict(id='DEVICE-REVISION', source_pages=[32], fact='Figure7-22 labelsRevR-x whileTable7-15 saysreset0.', policy='OnlyDID11:0 known0x117; do not certify revisionnibble.'),
    dict(id='ALERT-MODE-SWITCH', source_pages=[16,17,27], fact='Mode-specific completed-conversion/read behavior is defined; transition-time alert-bit effects are not.', policy='ConfigureTNA before qualifyingevents; reject/leaveunscored direct sideeffects ofTNA switch.'),
]

rows = json.loads((ROOT / 'eval/independent_source_admission_20261012/field_evidence.json').read_text(encoding='utf8'))
repair = [x for x in rows if x['chip']=='TMP117' and x['overall_status']=='REPAIR']
requirements = {
 'CONFIG.AVG': ('NVM-CONFIG-MASK','NVM-LOCKED-WRITES','NVM-PROGRAM','NVM-POR','AVERAGE-COUNTS'),
 'CONFIG.CONV': ('CC-CYCLE-TABLE','NVM-CONFIG-MASK','NVM-LOCKED-WRITES','NVM-PROGRAM','NVM-POR','OS-CONV-INDEPENDENT'),
 'CONFIG.DATA_READY': ('READY-READ-CLEAR','AVERAGE-COUNTS','OS-CONV-INDEPENDENT'),
 'CONFIG.DR_ALERT': ('NVM-CONFIG-MASK','NVM-LOCKED-WRITES','NVM-PROGRAM','NVM-POR','ALERT-MODE','READY-READ-CLEAR'),
 'CONFIG.EEPROM_BUSY': ('NVM-BUSY-MIRROR','NVM-PROGRAM','NVM-POR'),
 'CONFIG.HIGH_ALERT': ('ALERT-MODE','THERM-MODE','SIGNED-LIMITS'),
 'CONFIG.LOW_ALERT': ('ALERT-MODE','THERM-MODE','SIGNED-LIMITS'),
 'CONFIG.MOD': ('MODE-ENCODINGS','NVM-CONFIG-MASK','NVM-LOCKED-WRITES','NVM-PROGRAM','NVM-POR','AVERAGE-COUNTS'),
 'CONFIG.POL': ('NVM-CONFIG-MASK','NVM-LOCKED-WRITES','NVM-PROGRAM','NVM-POR','ALERT-MODE'),
 'CONFIG.TNA': ('NVM-CONFIG-MASK','NVM-LOCKED-WRITES','NVM-PROGRAM','NVM-POR','THERM-MODE','ALERT-MODE'),
 'EEPROM_UL.EEPROM_BUSY': ('NVM-BUSY-MIRROR','NVM-PROGRAM','NVM-POR'),
 'EEPROM_UL.EUN': ('NVM-LOCKED-WRITES','NVM-PROGRAM','NVM-POR','GENERAL-CALL-RESET'),
 'TEMP_OFFSET.OFF': ('NVM-BACKED-LOCATIONS','NVM-LOCKED-WRITES','NVM-PROGRAM','SIGNED-OFFSET-SATURATION'),
 'THIGH.H': ('NVM-BACKED-LOCATIONS','NVM-LOCKED-WRITES','NVM-PROGRAM','NVM-POR','SIGNED-LIMITS','ALERT-MODE','THERM-MODE'),
 'TLOW.L': ('NVM-BACKED-LOCATIONS','NVM-LOCKED-WRITES','NVM-PROGRAM','NVM-POR','SIGNED-LIMITS','ALERT-MODE','THERM-MODE'),
}
closure=[]
for row in repair:
    key = row['register']+'.'+row['field']
    closure.append(dict(inventory_field_id='TMP117.'+key, source_overall_status='REPAIR',
        source_repair_dimensions=[k for k,v in row['dimensions'].items() if v['status']=='REPAIR'],
        required_claim_ids=list(requirements[key]), closure_recommendation='SCOPED_CLAUSES_ONLY_AFTER_EXECUTION',
        whole_field_pass_recommended=False, rationale='A source review supplies constraints; matching nonvacuous tests and exact operating-scope exclusions must be accepted separately. No automatic whole-dimension closure from field matching.'))

result = dict(
 contract_version='1.0', expert_skill='sci-skills-paper-deep-reading', project_id='d2d-twin', paper_family='M', stage_id='M4',
 task_id='tmp117-v31/source_review', task_status='COMPLETE',
 inputs_reviewed=[dict(path=SRC, sha256=SHA, access='FULL_LOCAL_MANUFACTURER_PDF', revision='SNOSD82D June2018 revisedSeptember2022', pdf_pages=50, reviewed_printed_pages=[6,12,14,15,16,17,18,19,21,22,24,25,26,27,28,29,30,31,32]),
                  'eval/independent_source_admission_20261012/field_evidence.json',
                  'eval/semantic_protocol_v3_20261012/runtime.py',
                  'eval/semantic_protocol_v3_20261012/repair_closure_ledger.json'],
 outputs=['eval/tmp117_semantics_v31_20261013/source_review.md','eval/tmp117_semantics_v31_20261013/source_review.json'],
 evidence_status=['VERIFIED_SOURCE: originalPDFdirectreview withmanualrevision/SHA/pages;17 boundedclaims','EXECUTED_LOCAL: PDFtext extraction andvisualinspectionofpp15/18/27/28/31','PENDING_VERIFICATION: newv3.1implementationandtestsnotexaminedbythisexpert'],
 assumptions=['Completed sample eventsinjectpost-linearizationdigitalcodes; noanalogtemperature or physicaltiming proof.', 'Nonintegralmeans, unknownMODreadback andunsupportedtransitionresponses remainunscored.', 'Orderedlow/highlimit is a benchmarkguard, not a datasheet-forbiddenhardwarevalue.'],
 author_input_needed=[], manual_actions=[],
 quality_checks=['Verified sourceSHA256 againstactualPDF.', 'Visually checkedCONFIGfootnotemask0x07fc andTable7-7.', 'Visually checkedoffsetsaturationstatement onp31.', 'Directlyreviewedall15TMP117REPAIRfieldrows;16REPAIRdimensionsincludingCONVlegal_encoding+conditional_write.', 'NooldIR/harness/resultartifactwritesperformedbythisreview.'],
 conflicts=[dict(conflict_id=x['id'], conflict_type='SOURCE_CONFLICT' if x['id'] in ['CONFIG-SOFT-RESET','DEVICE-REVISION'] else 'UNSPECIFIED_OR_ABSTRACTION_BOUNDARY', claim=x['fact'], source_or_locator=f"{SRC} printedpages{x['source_pages']}", competing_interpretations='Retainunknown;do notcertifyguessedbehavior', recommended_resolution=x['policy']) for x in unknowns],
 conflict_resolution_status='UNRESOLVED', merge_permission='orchestrator_only',
 recommended_next_action='Implement and independently test only the sourcedv3.1clauses with explicitknownmasksandunscoredguards, thenletorchestratorreviewclauseclosure; do notfreezeformalinputs yet.',
 stage_acceptance_recommendation='REPAIR', claims=claims, unspecified_boundaries=unknowns, closure_advice=closure,
 closure_summary=dict(repair_fields=15, repair_dimensions=16, whole_field_pass_count_recommended=0, note='Sourcefactreviewiscomplete; implementationacceptanceandwholeprojectM4remainorchestratorowned.'))
(OUT/'source_review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

md = f'''# TMP117 v3.1 原始来源审校

本报告是独立、限定任务的原始来源审校，不是硬件验证或阶段准入批准。已直接读取本地完整厂商PDF，并检查关键页图像。时间：2026-10-13。项目d2d-twin，方法应用路线M，M4，任务tmp117-v31/source_review。

## 1. 文献定位
Texas Instruments TMP117数据手册，SNOSD82D，June2018 / revisedSeptember2022。本地PDF共50页，印刷页码与PDF页码在所审正文段一致。路径`{SRC}`；SHA-256 `{SHA}`。来源级别为完整厂商文件，非摘要或二手转述。

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
'''
for c in claims:
    md += f"\n### {c['claim_id']}\n原文事实（释义）：{c['paraphrased_fact']}\n\n定位：印刷/PDF页{','.join(map(str,c['pdf_pages']))}；{c['locator']}。\n\n"
    md += '\n'.join('- '+s for s in c['implementation_constraints'])+'\n'
md += '''
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
'''
for row in closure:
    md += '| '+row['inventory_field_id']+' | '+','.join(row['source_repair_dimensions'])+' | '+','.join(row['required_claim_ids'])+' |\n'
md += '''
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
'''
(OUT/'source_review.md').write_text(md,encoding='utf8')
print(json.dumps({'source_sha256':SHA,'claims':len(claims),'repair_fields':len(closure),'outputs':['source_review.md','source_review.json']}))
