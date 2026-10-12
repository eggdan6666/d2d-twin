# 来源冲突与主协议裁决

| 对象 | 两种证据 | 当前裁决 | 状态 |
|---|---|---|---|
| INA3221 SHUNT_SUM_LIMIT | p33 title/位图RW/7FFE；同页字段表R/0 | 仅比较两表一致的bits15/0，排除数据bits14:1复位与整个寄存器写入行为 | UNRESOLVED；非官方勘误 |
| TMP117 DEVICE_ID Rev | p32位图R-x；表reset0，ID低12位117一致 | 低12位mask0x0FFF；高4位不裁定 | UNRESOLVED |
| TPS23861 GENERAL_MASK R17[3:1] | p45总览整寄存器80；p63详细reset为Reserved并警告勿改变 | 排除三位复位/访问oracle；写入时保留新实例读回 | UNRESOLVED |
| AD5592R DAC_RD_EN | p36两位组表只列0/1文本；p29正文明确[4:3]=11使能 | 撤回早期只测字段值0/1的建议；当前保守测试00/11，01/10暂不判定 | RESOLVED_BY_ORCHESTRATOR for bounded domain；组合歧义仍需保留 |
| MPU6050 DEVICE_RESET审校状态 | 旧IR tier=UNVERIFIED；本地RM Rev4.2 pp40–41和先前独立审校已确认复位后自清零 | 精确override恢复原子完成后的read_as0；42项回归防止标签吞掉已知行为 | RESOLVED_BY_ORCHESTRATOR for static MVP；真实时间未验证 |

来源事实、保守域选择和尚未解决的真实器件状态分别记录。参考代码通过不能提高来源证据等级；保持 UNKNOWN 不等于写成0。
