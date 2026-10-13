# 唯一下一步行动卡

当前M4；TMP117本轮限定条款实现与验证已完成，正式20芯片生成输入仍未准入。

唯一任务：在新版本中补齐TMP126的8个REPAIR字段，把事务限定读清、跨地址清除、模式切换与平均完成接入同样的条款重放和独立故障验收；保留未知/物理时序排除，不重评旧720样本。

复制提示词：

> 请继续M4来源契约修复。读取eval/tmp117_semantics_v31_20261013/REPORT.md、admission.py、closure_ledger.json，以及eval/independent_source_admission_20261012中TMP126的逐项证据与修订建议。参照TMP117的不可变输入、确定性条款重放和独立故障测试机制，在一个新目录实现TMP126剩余8个REPAIR字段。重点验证single-register read/no auto-increment的非零flag preclear/postclear、TEMP_RESULT跨清DATA_READY、Comparator→Interrupt清状态、one-shot/AVG完成及MODE变化，按原PDF确认哪些live status保留、哪些flag清除。不要把CRC/阈值事件的抽象输入称实物刺激或已验证算法；未知副作用、非法输入响应和物理完成时长保留不评分。输入改变、事件状态和来源字段身份都需有精确哈希/映射，伪造PASS或空断言不能通过。保留所有旧IR、测试、来源审校、历史模型结果。本步用本地PDF、CPU和pytest即可，不使用SCNet或新增模型生成。输出逐条来源—代码—反例—执行闭环，以及下一阶段全项目准入所需缺口。

验收材料：新版本代码、明确事件/事务接口、非零正例和独立错误夹具、严格证据重放、原文件保护检查和唯一准入行动。需要用户提供：当前没有新增资料、账号或硬件需求。
