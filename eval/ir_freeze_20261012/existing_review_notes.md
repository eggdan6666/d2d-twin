
## AD5592R
{
  "date": "2026-10-10",
  "method": "PDF text extraction plus page-level inspection of Register Map pages 35-52",
  "erratum_found": "not checked by an independent reviewer",
  "open_questions": [
    "Confirm that the frozen harness can represent selector-based SPI command words.",
    "Confirm reset timing and readback transaction sequencing.",
    "Independent reviewer must verify reserved-bit policy and defaults."
  ]
}

## ADS1115
null

## ADS1220
{
  "date": "2026-10-07",
  "method": "PDF 原生文本层逐位取 Figure 8-32~8-35 的 R/W-n 访问码与 [reset=00h]",
  "erratum_found": "未发现手册错误。但这颗提供了 Q0 讨论的关键反例：**同一份文档里 RESERVED 有两层完全不同的含义**——字段名 RESERVED 可以是『可写位』（CONFIG3 bit0，标 R/W），而 '1111b: Reserved' 指的是『保留编码值』。把它们混成一类就会错",
  "open_questions": [
    "Q1: 这颗是可断言面最小的芯片（只有复位值 + RW 位域持久两条；RO 保护/写触发/软复位键按 IR 自动跳过）。作为正对照，预期接近满分；若显著不满分，说明 prompt 里的『纯寄存器堆默认』倾向不够，得回看任务书。",
    "Q2: CONFIG3 bit0 的 RESERVED 按 R/W 编码（B 档）。若你认为 TI 本意是不可写，改 access 即可，重判免费。",
    "Q3: 非法编码值（MUX=1111b 等）写入后读回什么，手册未定义 → 不属 MVP。"
  ]
}

## BME280
{
  "date": "2026-10-07",
  "method": "从 MinerU 解析文本提炼初稿；PDF 对照校验中（用户环节）",
  "erratum_found": "§5.4.2 reset 键值被 OCR 系统性误识为 0x86（B→8 字体替换）——与 BMP280 解析（同段 0x86/0xB6 自相矛盾）跨文档复现。权威键值 0xB6（Bosch API BME280_SOFT_RESET_COMMAND）。",
  "open_questions": [
    "Q1: press/temp/hum_msb 复位 0x80（对应 raw 输出 0x8000/0x80000）请对照 PDF 寄存器地图确认",
    "Q2: ctrl_hum『写后需写 ctrl_meas 才生效』——MVP 未断言该时序语义，Phase 1.5 是否纳入请定夺",
    "Q3: config bit1 与各 UNUSED 位编成（Bosch 未给访问码，沿用 TMP102 对照惯例处理）",
    "Q4: calib 块 0x88-0xA1 + 0xE1-0xF0 共 42 字节未入断言（runtime 值）"
  ]
}

## BMP280
{
  "date": "2026-10-07",
  "method": "从 MinerU 解析文本提炼初稿；PDF 对照校验中（用户环节）",
  "erratum_found": "§4.3.2 OCR 错误：同段前句写 '0x86' 触发复位、后句写 'Writing other values than 0xB6 has no effect'——前句 0xB6 被误识为 0x86。权威键值取 0xB6（后句+行业惯例）。与 TMP1075 Table 7-11 TYPE 列笔误并列为人工校对价值案例。",
  "open_questions": [
    "Q1: press_msb/temp_msb 复位值 0x80 由解析表格给出（对应上电 raw 输出非零），请对照 PDF Table 18 确认",
    "Q2: config 在 normal 模式下『写可能被忽略』——MVP 断言均在 sleep 态执行不触发该语义；Phase 1.5 行为测试需覆盖",
    "Q3: calib 块 0x88-0xA1 未纳入断言（runtime 值），是否需要在 IR 中逐个列出（26 个）请定夺"
  ]
}

## HDC2021
{
  "date": "2026-10-07",
  "method": "PDF 原生文本层逐寄存器取 Table 7-6 复位值 + 各 Table 的 TYPE/RESET 列；MinerU 并行解析仅作 Phase 2 对照",
  "erratum_found": "①STATUS 与 INTERRUPT_ENABLE 的 Reserved 行 **TYPE 列 TI 干脆没填**（只写 RES + reset 0）——这是 Q0 保留位约定的第三个受害者（前两个是 TMP102/BME280）；②MEAS_CONFIG bit3 名为 RES 却标 R/W，与 INA3221 Mask/Enable bit15 同类：同一份手册里 reserved 有两种访问码，一刀切必错",
  "open_questions": [
    "Q1: SOFT_RES（0x0E bit7）按『写 1 自清零 + 复位全部寄存器』建模，read_as=0；是否加『软复位级联』断言（会改各芯片断言分母）——与 INA3221 Q1 同一裁决",
    "Q2: STATUS bits2:0 与 INTERRUPT_ENABLE bits2:0 的 Reserved 位 TI 未填 TYPE，现按 Q0 现约定编成 RO 硬连 0。若 Q0 裁成放宽，这两处（共 6 位）也随之改",
    "Q3: MEAS_TRIG（0x0F bit0）转换完成后硬件清 0；MVP 无转换过程，编成普通 RW。是否 Phase 1.5",
    "Q4: TACC/HACC/MEAS_CONF 的『11 = NA』非法编码未断言（写非法值后读回什么，手册未定义）",
    "Q5: 温度/湿度/偏移量纲（165·x/2^16−40、%RH=100·x/2^16、偏移补码）属数值语义，MVP 只断言权限与复位值"
  ]
}

## INA219
null

## INA226
[
  {
    "id": "N1",
    "item": "CONFIG[14:12] 定为 C 档且复位值非零（100b）",
    "risk": "基准第一个非零 C 档；若 is_convention_bit 不短路 reset==0，④b 会静默漏算这一档",
    "verify": "p.22 Table 7-2 POR 行 D14=1,D13=0,D12=0"
  },
  {
    "id": "N2",
    "item": "DIE_ID 复位值二义（2260/2261）",
    "risk": "写死 0x2260 会让 ② 变成可争议断言；已用 runtime_value 标注，但 harness 目前仍按 reset 字段判 ⇒ 需人工裁决是否把 0xFF 排除出 ②",
    "verify": "p.22 Table 7-1 脚注 (3)"
  },
  {
    "id": "N3",
    "item": "RST 自清零 + 全寄存器回默认",
    "risk": "低（原文直引）",
    "verify": "p.23『this bit self-clears』"
  },
  {
    "id": "N4",
    "item": "外部 AI 提供的 IR 草稿里把 CALIBRATION/MASK_ENABLE 的未命名位写成普通 RO 无 tier、且未处理 DIE_ID 二义",
    "risk": "会同时漏算 ④b 并制造一个假 ② 断言",
    "verify": "对照 p.22/p.26 位图"
  }
]

## INA3221
{
  "date": "2026-10-07",
  "method": "金标直接取自 PDF 原生文本层（p.24-37），逐寄存器对 [reset=] 与 Table 8-3/8-33/8-35/8-41 的逐位 R-n 编码；MinerU 并行解析仅作 Phase 2 的对照素材，不参与金标",
  "erratum_found": "未见解析层笔误（本次直接绕过了 MinerU）。但发现手册内部的两处易混点：①Mask/Enable 的 bit15『Reserved』标 **R/W**-0，而 10h/11h 的『Reserved』标 **R**-0——同为 reserved 却访问码不同，模型（和人）都容易一刀切；②CONFIG 的 RST 位写 1 后自清零并复位全部寄存器，与 BME280 的 0xE0 写键值软复位是两种不同机制（位级 vs 独立 W 寄存器）",
  "open_questions": [
    "Q1: RST（CONFIG bit15）按『写 1 自清零 + 复位全部寄存器』建模，read_as=0。是否另加一条『位级软复位级联』断言（会改变各芯片断言分母，需把已跑的 5 颗重算）——请裁决",
    "Q2: Mask/Enable 的 CF/SF/WF/PVF/TCF/CVRF 是 read-clear（读该寄存器即清除标志），且 CVRF 也会被写 CONFIG 清除。MVP 参考实现**未**建模 read-clear（否则与现有 RW 持久断言冲突），是否进 Phase 1.5",
    "Q3: Mask/Enable bit15 Reserved 按手册标 R/W 编码为可写；若你认为 TI 本意是不可写，请改 access",
    "Q4: 测量寄存器（01h-06h、0Dh）复位 0x0000 且转换值依赖外部输入，MVP 只断言 RO 写保护、不断言数值语义",
    "Q5: 0Eh/07h-0Ch 的位域按 Table 给定位宽（14/13 位）编码，未用位读 0；请对照 PDF p.31-34 确认未用位在写全 1 后确实保持 0"
  ]
}

## LIS2DW12
[
  {
    "id": "L1",
    "item": "CTRL2[5] 定 C 档（脚注 must be set to 0，无访问码列）",
    "risk": "它决定 ④b 在这颗上有没有份；若你认为脚注即等于文档明示读 0，应改 A",
    "verify": "PDF p.37 Table 32 位图第三格 + 脚注 (1)"
  },
  {
    "id": "L2",
    "item": "WAKE_UP_SRC[7:6] 定 C 档（位图只写 0）",
    "risk": "同上",
    "verify": "PDF p.50 Table 77"
  },
  {
    "id": "L3",
    "item": "SOFT_RESET(CTRL2[6]) 编成 read_as=0",
    "risk": "低：ST 原文『performs a reset of the internal blocks and then returns to 0』",
    "verify": "PDF p.37 Table 33"
  },
  {
    "id": "L4",
    "item": "解析稿 md 不可用于本颗（SOFT_RESET/COM_OR_EN/LPEN 等位名在 md 里 0 命中）",
    "risk": "若别人拿 md 复核会得出『手册没写』的错误结论",
    "verify": "对比 d2d/parsed/LIS2DW12/auto/LIS2DW12.md 与 PDF p.36-40"
  }
]

## LIS3DH
{
  "date": "2026-10-10",
  "method": "PDF text extraction plus page-level inspection of pages 31-40",
  "erratum_found": "not checked by an independent reviewer",
  "open_questions": [
    "Independent review passed after removing static reset assertions for dynamic output registers and annotating ODR legal values."
  ]
}

## LM83
{
  "date": "2026-10-07",
  "method": "PDF 原生文本层 §2.1 命令字表（p.13-14）+ §2.2-2.7 位表（p.14-15）；每寄存器逐位抄 R/W 与默认值",
  "erratum_found": "未见手册内部矛盾。这颗的价值在**同一份文档把『保留』分成两类**：①位级『always set to 0 and reserved for future use. A write of 1 will return a 0 when read』（SR1/SR2/CONFIG 的若干位）＝A 档，可断言；②地址级『Reserved for Future Use』（几十个地址）＝手册完全没说读回什么＝C 档，不可断言。这正好给 Q0 的三档分级提供同一芯片内的对照",
  "open_questions": [
    "Q1（新维度）: 6 个读写别名寄存器（03h/09h、05h/0Bh、07h/0Dh、38h/50h、3Ah/52h、42h/5Ah）由**新加的断言⑦**覆盖。要不要把它同时用于 BME280/BMP280 之类没有别名的芯片（会 skip，分母不变）？已默认如此",
    "Q2（C 档）: 读保留地址（如 04h/06h/08h）返回什么，手册未定义 ⇒ 不入断言。是否要按『返回 0』约定并计分？（我不建议：那是我们在替手册编话）",
    "Q3: 温度/设定点的补码量纲与 INT/T_CRIT_A 引脚行为属运行时语义，MVP 只断言权限、复位值与别名联动",
    "Q4: 老版式文档（本份 p.13 表头是 <P7:P0> hex / <D7:D0> binary / decimal 三列）在解析层极易错位，是 Phase 2 结构保持解析的天然难题样本，建议保留作 MinerU/VLM 对照"
  ]
}

## MPU6050
{
  "date": "2026-10-10",
  "method": "Product Specification pp.30-36 plus 46-page RM-MPU-6000A-00 Revision 4.2 local mirror and official web index",
  "erratum_found": "not checked by an independent reviewer",
  "open_questions": [
    "Independent review passed after adding reserved fields, correcting PWR_MGMT_1 page references, and recording primary-I2C framing metadata."
  ]
}

## TMP100
{
  "date": "2026-10-07",
  "method": "外部 agent（Gemini 3.8 Flash）先交一版 IR+参考实现；其声称的『本地回归 10/10 全绿』不可核——文件未落盘，且其 IR 键名(chip/address/size/bitRange)与基类(d2d.rtl.base_sensor.BaseSensor)均与本 harness 契约不符，10 项检查名也不对应我这 6 项 IR 驱动断言。故本轮只采纳其事实、重写 IR 与参考实现，并按本项目纪律先跑本地回归。",
  "adopted_facts": [
    "CONFIG 复位读回 0x80：原文两句『power-up or reset value of the Configuration Register is all bits equal to 0』+『The OS/ALERT bit reads as 1 after power-up or reset value』——推导正确，已核实",
    "R1/R0 = 可写、复位 00（9 位），与 TMP102 的 RO=11 形成对照：原文『The user can obtain 9, 10, 11, or 12 bits of resolution by addressing the Configuration Register and setting the resolution bits accordingly』，已核实",
    "4 个数据寄存器（Table 5 标题为 'Pointer Addresses of the TMP100 and TMP101 Registers'）：纠正了此前 HANDOFF 与本会话早先的『2 寄存器最简芯片』措辞",
    "TLOW/THIGH 复位 0x4B00/0x5000（75°C/80°C）：已核实，且两种分辨率口径得到同一读回值"
  ],
  "corrections_to_external": [
    "TEMP/TLOW/THIGH 位域照抄了 TMP102 的 12-bit 布局（[15:4] 有效 + [3:0] 恒 0）。TMP100 默认 R1R0=00 是 9 位，手册明确未用低位恒 0 → 本 IR 改为 [15:7] 有效 + [6:0] 恒 0。这直接改变『RW 位域持久』与『RW 内只读位保护』两条断言的宽度"
  ],
  "open_questions": [
    "Q1(T1 已按推荐编码，请对 PDF p.15-16 确认): TEMP/TLOW/THIGH 的位域按默认 9-bit 编码（[15:7] 有效、[6:0] 恒 0）。选 12-bit 会放宽可写位范围；两种写法复位读回相同，差别只在写全 1 后读回 0xFF80 还是 0xFFF0",
    "Q2(T2): CONFIG 是 8 位寄存器，被 2 字节读时返回什么？MVP 约定『无论 nbytes=1/2 都只返回该 8 位值』；真实器件在 nbytes=2 时会指针自增读到 TLOW 高字节。请裁定是否入 Phase 1.5",
    "Q3: OS/ALERT 编成 RW + read_as=1（默认态读 1）。TMP100 无 ALERT 引脚但内部比较器存在，ARA(0001_1001b) 行为与转换期间读 0 的动态语义 MVP 未断言",
    "Q4: 分辨率切换（写 R1R0）后 TEMP/阈值位域宽度应随之变化——Phase 1.5 行为断言候选，本芯片是四颗里唯一能让这条可测的（TMP102 的 R1R0 是只读）",
    "Q5: TM/SD 与 TMP101 的差异（TMP100 无中断模式行为）是否需要在 IR 里标 access 差异"
  ]
}

## TMP102
{
  "date": "2026-10-07",
  "method": "从 MinerU 解析文本提炼初稿；PDF 对照校验中（用户环节）",
  "erratum_found": "Table 6-10 复位行被 OCR 打残（'OS0/R11' 粘连、复位行只剩 4 格）——byte1 复位值按 §6.5.3.5 prose（R1R0 启动=11）+ byte2 完整表格推得 0x60A0",
  "open_questions": [
    "Q1: CONFIG 复位值 0x60A0 的 byte1 复位行 OCR 残缺——请对照 PDF Table 6-10 逐位确认（重点 R0 复位是 1 还是 0）",
    "Q2: OS 位转换完成后读 0 还是回读 1？§6.5.3.6 只说『转换期间读 0』——IR 暂不设 read_as 断言，仅测可写持久性",
    "Q3: R1/R0/AL 三个 RO 位位于 RW 寄存器内——新增的『RW 内 RO 位保护』断言会检查写全 1 后它们保持复位值，AL 依赖环境温度的运行时语义未断言（仿真在默认态 AL=1）",
    "Q4: 13 位扩展模式（EM=1）未纳入 MVP 断言"
  ]
}

## TMP1075
{
  "date": "2026-10-07",
  "method": "人工对照原 PDF（corpus/data/raw_pdf/TI/TMP1075.pdf）截图逐表核验",
  "decisions": [
    {
      "q": "Q1 CFGR bits 7:0 与 LLIM/HLIM bits 3:0 可写性",
      "decision": "保持 RW（可写存储）",
      "evidence": "Figure 7-12 低字节逐位 R/W-1；Table 7-9 bits 3:0 行 TYPE=R/W"
    },
    {
      "q": "Q2 OS 位 read_as=0",
      "decision": "确认",
      "evidence": "解析文本 Table 7-8 明文 'Read returns 0'，与 Figure 7-12 OS=R/W-0 复位值一致"
    },
    {
      "q": "Q3 单字节语义范围",
      "decision": "保持 all_registers",
      "evidence": "§7.5.1.2 Note 明文（CFGR）；其余寄存器按 I2C 高字节惯例推广"
    },
    {
      "q": "Q4 TMP1075N 变体",
      "decision": "排除出 MVP",
      "evidence": "Figure 7-13：R1/R0 只读 R-1、bits 7:0 Reserved，与标准版行为差异实质存在"
    }
  ],
  "erratum_found": "Table 7-11（DIEID）TYPE 列印作 R/W，与同表描述 '16-bit, read-only register' 及 Figure 7-16 逐位 R 码矛盾——判定为手册笔误，IR 取 RO。人工校对环节价值之实证。"
}

## TMP117
{
  "date": "2026-10-07",
  "method": "PDF 原生文本层逐寄存器取 Table 7-3 的 TYPE/RESET 列 + Figure 7-13~7-17 的逐位 R-n/R/W-n；MinerU 解析仅作 Phase 2 对照素材",
  "erratum_found": "**手册内部自相矛盾**：bit1 SOFT_RESET 在 Figure 7-14（p.27）标 `R-0`（只读），而 Table 7-6 续表（p.28）同一位标 `R/W` 并写明『When set to 1 it triggers software reset with a duration of 2 ms / This bit will always read back 0』。金标采信表格描述（R/W + read_as=0）。这是继 TMP1075 Table 7-11 TYPE 列、Bosch 0xB6→0x86 之后的第 4 处手册级 erratum，且第一处是同一份文档图/表不一致——纯文本 QA 永远发现不了，只有必须逐位编码访问码时才会撞上",
  "open_questions": [
    "Q1: EEPROM 写 gating（EUN=0 时写 EEPROM1-3 应无效）与 SOFT_RESET 级联复位都未断言。加『位级软复位级联』断言会改变各芯片断言分母（需把已跑的 7 颗重算），是否与 INA3221 Q1/HDC2021 Q1 一起裁决",
    "Q2: HIGH_ALERT/LOW_ALERT/DATA_READY 是 **read-to-clear**（读 CONFIG/TEMP 即清除）。注意：一旦金标实现 read-clear，本基准的断言③『RO 寄存器写脏后快照不变』会与之冲突——快照本身要先读一次才拿到 before，实现 read-clear 的器件 before/after 必不同。要么断言③对这类寄存器加豁免标记，要么 Phase 1.5 新增 read-clear 专项断言。请裁决（这条影响 TMP117/INA3221 Mask-Enable 两颗）",
    "Q3: EEPROM1-3（0x05/0x06/0x08）复位值为 xxxxh（出厂编程），已标 runtime_value 且字段留空＝完全不参与断言。是否改成『断言 EUN gating 行为』才有信息量",
    "Q4: MOD=10 手册明说『读回 00』——这是天然的 read_as 型非法编码约束，MVP 未断言（TEMP 的 8000h 复位已断言）",
    "Q5: 温度量纲（1 LSB=7.8125 m°C、补码、−256°C 占位）属数值语义，MVP 只断言权限与复位值"
  ]
}

## TMP126
[
  {
    "id": "P1",
    "item": "SLEW_RESULT(01h) 的位划分按 00h 同格式推断（MinerU 把 Figure 8-2 的位标丢了）",
    "risk": "低：只影响 01h 的 ④/⑤ 断言粒度，寄存器级 RO 与复位 0000h 是原文直读",
    "verify": "PDF p.26 图 8-2 人眼核一次"
  },
  {
    "id": "P2",
    "item": "TLOW/THIGH/SLEW_LIMIT 三个字段的 Table 复位值是**原生位宽**（3CE0h/AA0h/0140h），寄存器复位值是左移后的 F380h/2A80h/0500h",
    "risk": "这是本颗对 ④a 最有价值的地方，但若我把两者写反会让金标自己错",
    "verify": "已交叉核对 0x3CE0<<2==0xF380、0xAA0<<2==0x2A80、0x140<<2==0x0500（三条全中）"
  },
  {
    "id": "P3",
    "item": "ALERT_STATUS 的 9 个位里 5 个是 RC（读清零），寄存器本身是 RO",
    "risk": "命中③的 read-clear 豁免条件（寄存器级 RO ＋ 读清零 ＋ 复位值非零时才会触发）；本颗复位为 0000h，豁免不会被动触发",
    "verify": "金标回归必须绿；已跑"
  },
  {
    "id": "P4",
    "item": "CONFIG bit8 名称手册写作 \"Resets\"，Type 列标 R/W 但描述说读回 0",
    "risk": "若照 Type 列编成普通可写位，⑤ 会漏测；这里编成 read_as=0 ＋ 写触发全寄存器复位",
    "verify": "PDF p.29 Table 8-8 第一列 Type/Reset 已直读"
  }
]

## TMP461
null

## TPS23861
{
  "date": "2026-10-07",
  "method": "PDF 原生文本层：§7.5 汇总表（p.45-46）逐行取 CMD CODE / R/W / DATA BYTE / RST STATE + 表注 1-3 + 各寄存器详情表的 POR VALUE 逐位行",
  "erratum_found": "**同一份手册里 'reserved' 式记号有三种不同含义**：`-` 在字段名列＝『无功能位』（17h，但 RST 给了确定值 0 → A 档）；`-` 在 RST STATE 列＝『复位值未定义』（40h 低 4 位 → C 档）；`A` ＝『取出厂编程值』（表注 2 → 第四档，前 10 颗都没见过）；`R` ＝ROM 编程位。自动抽取如果把四种都当成『保留位=0』，就会在 40h 与 01h/12h 上同时错。",
  "open_questions": [
    "Q1（新维度，需你确认）: 02h/03h 等五对 Clear-on-Read 由新加的**断言⑧**覆盖（普通读稳定 → cor 读返回同值 → 之后再普通读必须为 0）。注意 0Ah 的 POR 是 30h，清零后读回 00h≠复位值——这条判据依赖详情表里『clears all bits』的说法，请对 PDF 确认 VDUV/VPUV 也会被清",
    "Q2: 18h/19h/1Ah 三个纯写命令寄存器现有断言完全不断言（无 write_key ⇒ ⑥ 自动跳过；无可读回 ⇒ 无副作用可观测）。要不要 Phase 1.5 加『写副作用可观测』断言（例如写 1Ah 后 00h 告警位应被清）？",
    "Q3: 16h/20h/21h/29h/2Ah/2Bh 我按『宁可不断言』排除了，若你核对详情表后位域清楚，可以补进来（补一颗的断言面会变大，分数会变，重判免费）",
    "Q4: 17h 位1 的 `R` 与 27h 高 4 位 `R` 我编成 RO 硬连 0；若手册本意是可读到真实版本号（运行时值），应改 runtime_value",
    "Q5: 11h 的解锁门控写（与 INA3221 EEPROM_UL 的 EUN 同类）是否统一列为 Phase 1.5 的『寄存器写权限门控』专项？"
  ]
}