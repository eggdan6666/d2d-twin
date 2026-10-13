# 独立来源审校差异清单

差异条目由本轮原PDF审查产生；同一机制可以影响多个字段，条目数不是互异硅缺陷数。完整原文、版本、SHA与逐维结论在field_evidence.json。

## ROOT-TMP100-OS — TMP100

read_as=1覆盖动态比较器/POL副作用

对象：CONFIG.OS, CONFIG.POL

原策略/输入：`"global read_as=1"`

候选：`{"exclude_unconditional_readback": true, "read_source": "comparator state and POL", "trigger_requires_SD": 1}`

来源：`[{"pdf_page": 18, "printed_page": "18", "table": "§7.5.3.6", "excerpt": ""}]`

## ROOT-TMP100-FORMAT — TMP100

9位TEMP分区外推至全部可写resolution

对象：TEMP.T, TEMP.UNUSED

原策略/输入：`"TEMP[15:7], UNUSED[6:0]"`

候选：`{"format_by_R": "9–12bits", "always_zero": "3:0", "baseline_resolution": "00"}`

来源：`[{"pdf_page": 9, "printed_page": "9", "table": "§7.3.1", "excerpt": ""}, {"pdf_page": 16, "printed_page": "16", "table": "Tables6–7", "excerpt": ""}]`

## ROOT-TMP102-OS-AL — TMP102

动态状态被普通存储/恒值保护覆盖

对象：CONFIG.OS, CONFIG.AL, CONFIG.POL

原策略/输入：`"OS ordinary RW; AL protected fixed1"`

候选：`{"exclude_OS_persistence": true, "exclude_AL_snapshot_equality": true, "event_model": "conversion and hysteresis and POL"}`

来源：`[{"pdf_page": 15, "printed_page": "15", "table": "§6.4.4", "excerpt": ""}, {"pdf_page": 19, "printed_page": "19", "table": "§6.5.3.8", "excerpt": ""}]`

## ROOT-TMP102-EM — TMP102

EM1改变位格式，旧mask不覆盖；门限bit0不是EM标志

对象：CONFIG.EM, TEMP, TLOW, THIGH

原策略/输入：`"fixed12bits; threshold desc bit0 meaningful"`

候选：`{"static_EM_test_values": [0], "extended_format": "15:3", "TEMP_bit0": 1, "threshold_bits2_0": 0}`

来源：`[{"pdf_page": 17, "printed_page": "17", "table": "Table6-9", "excerpt": ""}, {"pdf_page": 19, "printed_page": "19", "table": "Table6-14", "excerpt": ""}, {"pdf_page": 20, "printed_page": "20", "table": "Table6-16", "excerpt": ""}]`

## ROOT-TMP1075-UNUSED — TMP1075

TYPE RW与not-used功能未定义并存

对象：CFGR.UNUSED_LOW, LLIM.UNUSED, HLIM.UNUSED

原策略/输入：`"unrestricted boundary RW testing"`

候选：`{"preserve_defaults": true, "exclude_nondefault_function_oracle": true, "pure_storage_if_explicit_assumption_only": true}`

来源：`[{"pdf_page": 22, "printed_page": "22", "table": "Table7-8", "excerpt": ""}, {"pdf_page": 23, "printed_page": "23", "table": "Tables7-9–7-10", "excerpt": ""}]`

## ROOT-TMP1075-OS — TMP1075

写触发需shutdown；always read0不证明完成

对象：CFGR.OS

原策略/输入：`"read_as under SD0 reset baseline"`

候选：`{"preconditions": {"CFGR.SD": 1}, "completion": "conversion complete", "variant": "non-N"}`

来源：`[{"pdf_page": 19, "printed_page": "19", "table": "§7.4.2", "excerpt": ""}]`

## ROOT-TMP1075-TM — TMP1075

遗漏模式写清fault counter/alert history副作用

对象：CFGR.TM, CFGR.SD

原策略/输入：`"storage-only"`

候选：`{"TM_write": "clear fault count and alert history", "SD_command": "clear interrupt history"}`

来源：`[{"pdf_page": 20, "printed_page": "20", "table": "§7.4.4 / §7.4.4.2", "excerpt": ""}]`

## ROOT-TMP1075-ID-CONFLICT — TMP1075

Table7-11 TYPE RW vs prose/map/diagram RO，旧注释称笔误/erratum缺官方证据

对象：DIEID.DID

原策略/输入：`"official-looking erratum claim"`

候选：`{"conflict_status": "UNRESOLVED", "mask_access_dispute": true, "optional_RO_assumption": "prose+diagram priority"}`

来源：`[{"pdf_page": 21, "printed_page": "21", "table": "Table7-5", "excerpt": ""}, {"pdf_page": 24, "printed_page": "24", "table": "Figure7-16 / Table7-11", "excerpt": ""}]`

## ROOT-TMP126-COR — TMP126

缺single read无auto increment约束与跨TEMP清DR

对象：ALERT_STATUS.CRC_FLAG, ALERT_STATUS.SLEW_FLAG, ALERT_STATUS.THIGH_FLAG, ALERT_STATUS.TLOW_FLAG, ALERT_STATUS.DATA_READY_FLAG, TEMP_RESULT.TEMP

原策略/输入：`"unconditional per-register clear"`

候选：`{"single_register_read_only": true, "auto_increment": false, "cross_clear": {"TEMP_RESULT": "ALERT_STATUS.DATA_READY_FLAG"}, "require_nonzero_event": true}`

来源：`[{"pdf_page": 27, "printed_page": "27", "table": "§8.6.3", "excerpt": ""}, {"pdf_page": 28, "printed_page": "28", "table": "Table8-7", "excerpt": ""}]`

## ROOT-TMP126-MODE — TMP126

遗漏one-shot完成置MODE1，模式切换clear/abort副作用，负slew数值未保证

对象：CONFIG.ONE_SHOT, CONFIG.INT_COMP, CONFIG.MODE, SLEW_RESULT.SLEW

原策略/输入：`"read_as0 only"`

候选：`{"one_shot_complete": "MODE1 DR1", "comparator_to_interrupt": "clear ALERT_STATUS", "shutdown": "abort partial conversion; slew result0; keep alerts", "negative_slew": "exclude numeric oracle"}`

来源：`[{"pdf_page": 14, "printed_page": "14", "table": "§8.4.2", "excerpt": ""}, {"pdf_page": 15, "printed_page": "15", "table": "§8.4.3", "excerpt": ""}, {"pdf_page": 16, "printed_page": "16", "table": "§8.4.4.1", "excerpt": ""}, {"pdf_page": 26, "printed_page": "26", "table": "§8.6.2", "excerpt": ""}]`

## ROOT-BOSCH-DYNAMIC — BME280

状态/输出动态与切换/写入commit条件未在静态策略明确执行

对象：status, data registers, ctrl_hum, ctrl_meas

原策略/输入：`"fresh instance only"`

候选：`{"freeze_events_for_protection": true, "wait_pending_transition": true, "ctrl_hum_commit": "write ctrl_meas", "separate_burst_read_consistency": true}`

来源：`[{"pdf_page": 15, "printed_page": "15", "table": "§3.3.1", "excerpt": ""}, {"pdf_page": 27, "printed_page": "27", "table": "§5.4.3", "excerpt": ""}, {"pdf_page": 28, "printed_page": "28", "table": "Table21", "excerpt": ""}]`

## ROOT-BMP-MODE — BMP280

候选描述仍把10写normal，寄存器描述把XLSB有效位置写低四位

对象：ctrl_meas.mode, press_xlsb, temp_xlsb

原策略/输入：`"10/11 normal; XLSB low nibble valid"`

候选：`{"mode": {"0": "sleep", "1": "forced", "2": "forced", "3": "normal"}, "XLSB_position": "7:4", "unused": "3:0"}`

来源：`[{"pdf_page": 15, "printed_page": "15", "table": "Table10", "excerpt": ""}, {"pdf_page": 24, "printed_page": "24", "table": "Table18", "excerpt": ""}, {"pdf_page": 26, "printed_page": "26", "table": "Table24", "excerpt": ""}, {"pdf_page": 27, "printed_page": "27", "table": "Table25", "excerpt": ""}]`

## ROOT-BMP-FILTER — BMP280

该版BMP没有BME式others编码逐行表；泛边界7不能算功能编码认证

对象：config.filter

原策略/输入：`"generic max7"`

候选：`{"alias_function_not_certified": [5, 6, 7], "coefficient_set": ["off", 2, 4, 8, 16]}`

来源：`[{"pdf_page": 14, "printed_page": "14", "table": "Table6", "excerpt": ""}, {"pdf_page": 26, "printed_page": "26", "table": "Table23", "excerpt": ""}]`

## ROOT-BOSCH-UNMAPPED — BMP280

原手册reserved registers读值不保证，旧未定义地址read0属于基准约定

对象：unmapped address behavior

原策略/输入：`"unmapped reads zero"`

候选：`{"source_guarantee": "none", "mark_as": "ABSTRACTION_ASSUMPTION", "exclude_from_silicon_fact": true}`

来源：`[{"pdf_page": 24, "printed_page": "24", "table": "§4.1", "excerpt": ""}]`

## ROOT-BME-VERSION — BME280

封面1.24与正文1.23标识并存

对象：source version

原策略/输入：`"single revision label"`

候选：`{"source_lock": "full file SHA256", "retain_cover_and_footer": true}`

来源：`[{"pdf_page": 1, "printed_page": "1", "table": "cover", "excerpt": ""}, {"pdf_page": 27, "printed_page": "27", "table": "footer", "excerpt": ""}]`

## TMP117_ALERT_MODE_QUALIFIED_READ_CLEAR — TMP117

无条件清HIGH/LOW与Therm模式不符

对象：CONFIG.HIGH_ALERT

原策略/输入：`"HIGH_ALERT/LOW_ALERT read_action=clear unconditional"`

候选：`{"on_read": "CONFIG", "only_if": {"CONFIG.TNA": 0}, "THERM_HIGH": "set/clear at conversion completion by high/low limits", "THERM_LOW": "always zero", "require_controlled_asserted_event": true}`

来源：`[{"pdf_page": 27, "printed_page": "27", "table": "Table 7-6", "section": null, "excerpt": "HIGH_Alert R 0 High Alert flag: 1: Set when the conversion result is higher than the high limit 0: Cleared on read of configuration register Therm mode: 1: Set when the conversion result is higher than the therm limit 0:"}, {"pdf_page": 17, "printed_page": "17", "table": null, "section": "§7.4.4.2", "excerpt": "I2C reads of the configuration register do not affect the status bits. The HIGH_Alert status flag is only set or cleared at the end of conversions based on the value of the temperature result compared to the high and low"}]`

## TMP117_DATA_READY_CROSS_REGISTER_CLEAR — TMP117

TEMP读也清DATA_READY必须纳入事件策略

对象：CONFIG.DATA_READY

原策略/输入：`"field-only CONFIG CoR metadata"`

候选：`{"on_read": ["TEMP", "CONFIG"], "return_preclear_data": true, "require_controlled_asserted_event": true, "exclude_zero_then_zero_as_coverage": true}`

来源：`[{"pdf_page": 27, "printed_page": "27", "table": "Table 7-6", "section": null, "excerpt": "Data ready flag. This flag indicates that the conversion is complete and the temperature register can be read. Every time the temperature register or configuration register is read, this bit is cleared. This bit is set a"}]`

## TMP117_EEPROM_VOLATILE_AND_NVM_GATE — TMP117

锁定不等同全部写被忽略；EEPROM空字段隐藏有效scratch行为

对象：EEPROM_UL.EUN

原策略/输入：`"旧Q1称EEPROM1-3写仅EUN1有效"`

候选：`{"EUN0": "volatile writes allowed", "EUN1": "nonvolatile programming allowed only when not busy", "lock_after_general_call_reset": true, "busy_write_behavior": "EXCLUDE prohibited write oracle"}`

来源：`[{"pdf_page": 18, "printed_page": "18", "table": null, "section": "§7.5.1.1-2", "excerpt": "Any I2C writes performed during this initial POR period to the limit registers or the configuration register are ignored. I2C read transactions can still be performed with the device during the power-up period. While the"}, {"pdf_page": 30, "printed_page": "30", "table": "Table 7-10", "section": null, "excerpt": "EEPROM is locked for programming: writes to all EEPROM addresses (such as configuration, limits, and EEPROM locations 1-4) are written to registers in digital logic and are not programmed in the EEPROM 1: EEPROM unlocked"}, {"pdf_page": 18, "printed_page": "18", "table": null, "section": "§7.5.1.2", "excerpt": "This command also clears the EUN bit and automatically locks the EEPROM to prevent any further accidental programming. Avoid using the device to perform temperature conversions when the EEPROM is unlocked. 18 Submit Docu"}]`

## TMP117_ALL_EEPROM_BACKED_RESETS — TMP117

不止门限，offset和多个CONFIG位也EEPROM后备

对象：TEMP_OFFSET.OFF

原策略/输入：`"factory condition only described in report for THIGH/TLOW"`

候选：`{"factory_eeprom_profile_expected": 0, "general_reset_rule": "reload EEPROM image", "wait_for_por_load_complete": true, "por_busy_reset_is_temporal": true, "eeprom_configuration_mask": "0x07fc", "MOD1_nonpersistent": true}`

来源：`[{"pdf_page": 31, "printed_page": "31", "table": "Table 7-13", "section": null, "excerpt": "Temperature offset data from system calibration. Copyright © 2022 Texas Instruments Incorporated Submit Document Feedback 31 Product Folder Links: TMP117"}, {"pdf_page": 25, "printed_page": "25", "table": "Table 7-3 note (1)", "section": null, "excerpt": "This value is stored in Electrically-Erasable, Programmable Read-Only Memory (EEPROM) during device manufacturing. The device reset value can be changed by writing the relevant code in the EEPROM cells (see the EEPROM Ov"}, {"pdf_page": 28, "printed_page": "28", "table": "Figure 7-14 notes (1)-(2)", "section": null, "excerpt": "These bits can be stored in EEPROM. The factory setting for this register is 0220. (2) The MOD1 bit cannot be stored in EEPROM. The device can only be programmed to start up in shutdown mode or continuous conversion mode"}]`

## TMP117_BUSY_MIRROR_AND_COMPLETION — TMP117

Busy镜像、POR1.5ms及编程7ms尚未模型化

对象：CONFIG.EEPROM_BUSY

原策略/输入：`"EEPROM excluded block says 2ms busy"`

候选：`{"mirror": ["CONFIG[12]", "EEPROM_UL[14]"], "complete_when": "Busy=0", "program_time_typical_ms": 7, "por_load_approx_ms": 1.5, "no_read_clear": true}`

来源：`[{"pdf_page": 30, "printed_page": "30", "table": "Table 7-10", "section": null, "excerpt": "mirror of the EEPROM busy flag (bit 12) in the configuration register. 0: Indicates that the EEPROM is ready, which means that the EEPROM has finished the last transaction and is ready to accept new commands 1: Indicates"}, {"pdf_page": 18, "printed_page": "18", "table": null, "section": "§7.5.1.2", "excerpt": "Programming a single location typically takes 7 ms to complete and consumes 230 µA. Do not perform any I2C writes until programming is complete. During programming, the EEPROM_busy flag is set. Read this flag to monitor "}]`

## TMP117_CONV_PERIOD_DESCRIPTION — TMP117

默认CONV100/AVG01周期1s，旧0.25Hz不符

对象：CONFIG.CONV

原策略/输入：`"CONV desc default100 T/nA0 0.25Hz"`

候选：`{"legal_values": [0, 1, 2, 3, 4, 5, 6, 7], "cycle_ms_by_avg": [[15.5, 125, 500, 1000], [125, 125, 500, 1000], [250, 250, 500, 1000], [500, 500, 500, 1000], [1000, 1000, 1000, 1000], [4000, 4000, 4000, 4000], [8000, 8000, 8000, 8000], [16000, 16000, 16000, 16000]]}`

来源：`[{"pdf_page": 28, "printed_page": "28", "table": "Table 7-7", "section": null, "excerpt": "Conversion Cycle Time in CC Mode CONV[2:0] AVG[1:0] = 00 AVG[1:0] = 01 AVG[1:0] = 10 AVG[1:0] = 11 000 15.5 ms 125 ms 500 ms 1 s 001 125 ms 125 ms 500 ms 1 s 010 250 ms 250 ms 500 ms 1 s 011 500 ms 500 ms 500 ms 1 s 100 "}, {"pdf_page": 15, "printed_page": "15", "table": null, "section": "§7.4.3", "excerpt": "CONV bits do not affect the duration of a one-shot conversion. Figure 7-4 shows a timing diagram for this mode with an AVG setting of 00. At the end of a one-shot conversion, the Data_Ready and ALERT flag in the configur"}]`

## TMP117_MOD_ONE_SHOT_BOUNDARY — TMP117

shutdown operating state不支持自创MOD读回1

对象：CONFIG.MOD

原策略/输入：`"MOD3 omitted persistence but completion readback not defined"`

候选：`{"legal_values": [0, 1, 2, 3], "readback_values": {"2": 0}, "completion_event": "temperature update / Data_Ready", "post_completion_operating_state": "shutdown", "post_completion_MOD_readback": "not explicitly established; exclude numerical oracle", "exclude_unbounded_persistence_for_3": true}`

来源：`[{"pdf_page": 27, "printed_page": "27", "table": "Table 7-6", "section": null, "excerpt": "reads back = 00) 11: One-shot conversion (OS) 9:7 CONV[2:0] R/W 100 Conversion cycle bit. See Table 7-7 for the standby time between conversions. 6:5 AVG[1:0] R/W 01 Conversion averaging modes. Determines the number of c"}, {"pdf_page": 15, "printed_page": "15", "table": null, "section": "§7.4.3", "excerpt": "After the device completes a one-shot conversion, the device goes to the low-power shutdown mode. A one-shot conversion cycle, unlike the continuous conversion mode, only consists of the active conversion time and no sta"}]`

## TMP117_SOFT_RESET_SOURCE_CONFLICT — TMP117

图R/tableR/W冲突不得称已官方确认勘误

对象：CONFIG.SOFT_RESET

原策略/输入：`"proofread_record erratum_found says manual erratum"`

候选：`{"diagram_access": "R", "table_access": "R/W", "recommended_separate_exploratory_profile": "table_text_priority", "main_claim": "retain conflict; no official erratum asserted"}`

来源：`[{"pdf_page": 27, "printed_page": "27", "table": "Figure 7-14", "section": null, "excerpt": "Soft_Reset — R/W-0 R/W-0 R/W-1 R/W-0 R/W-0 R/W-0 R-0 R-0 Table 7-6. Configuration Register Field Descriptions BIT FIELD TYPE RESET DESCRIPTION 15 HIGH_Alert R 0 High Alert flag: 1: Set when the conversion result is highe"}, {"pdf_page": 28, "printed_page": "28", "table": "Table 7-6 continued", "section": null, "excerpt": "Software reset bit. When set to 1 it triggers software reset with a duration of 2 ms This bit will always read back 0 0 — R 0 Not used (1) These bits can be stored in EEPROM. The factory setting for this register is 0220"}]`

## TMP117_REV_RESET_CONFLICT — TMP117

保留既有高4bit来源冲突和统一mask

对象：DEVICE_ID.ID

原策略/输入：`"candidate ID fullreset0117"`

候选：`{"known_mask": "0x0fff", "expected_register": "0x0117", "exclude_mask": "0xf000", "apply_mask_to_all_reset_and_snapshot_oracles": true}`

来源：`[{"pdf_page": 32, "printed_page": "32", "table": "Figure 7-22", "section": null, "excerpt": "Rev3 Rev2 Rev1 Rev0 DID11 DID10 DID9 DID8 R-x R-x R-x R-x R-0 R-0 R-0 R-1 7 6 5 4 3 2 1 0 DID7 DID6 DID5 DID4 DID3 DID2 DID1 DID0 R-0 R-0 R-0 R-1 R-0 R-1 R-1 R-1 Table 7-15. Device ID Register Field Descriptions BIT FIEL"}, {"pdf_page": 32, "printed_page": "32", "table": "Table 7-15", "section": null, "excerpt": "Indicates the revision number. 11:0 DID[11:0] R 117h Indicates the device ID. 32 Submit Document Feedback Copyright © 2022 Texas Instruments Incorporated Product Folder Links: TMP117"}]`

## TMP117_EEPROM2_RESET_SOURCE_CONFLICT — TMP117

标题0000 vs 总表/详细表xxxx及图R/W-x

对象：EEPROM2

原策略/输入：`"runtime0 placeholder hides conflicting header"`

候选：`{"candidate_field": {"name": "D", "bits": "15:0", "source_access": "R/W"}, "reset_known_mask": "0x0", "EUN0": "volatile write persists until reset, not EEPROM programming", "EUN1": "program backing cell only when Busy=0; wait completion before next write", "reset": "reload persistent contents", "program_typical_ms": 7, "busy_mirrors": ["CONFIG[12]", "EEPROM_UL[14]"], "no_assertion_on_prohibited_busy_writes": true}`

来源：`[{"pdf_page": 31, "printed_page": "31", "table": "Table 7-12", "section": null, "excerpt": "Table 7-12. EEPROM2 Register Field Descriptions BIT FIELD TYPE RESET DESCRIPTION 15:0 D[15:0] R/W xxxxh This 16-bit register can be used as a scratch pad. 7.6.9 Temperature Offset Register (address = 07h) [reset = 0000h]"}, {"pdf_page": 30, "printed_page": "30", "table": null, "section": "§7.6.7", "excerpt": "Writes to this address when the EEPROM is locked write data into the register and not to the EEPROM. Writes to this register when the EEPROM is unlocked causes the corresponding EEPROM location to be programmed. See the "}, {"pdf_page": 18, "printed_page": "18", "table": null, "section": "§7.5.1.2", "excerpt": "Programming a single location typically takes 7 ms to complete and consumes 230 µA. Do not perform any I2C writes until programming is complete. During programming, the EEPROM_busy flag is set. Read this flag to monitor "}, {"pdf_page": 31, "printed_page": "31", "table": null, "section": "§7.6.8 title", "excerpt": "[reset = 0000h] This register function the same as the EEPROM1 register. Return to Register Map. Figure 7-19. EEPROM2 Register 15 14 13 12 11 10 9 8 D15 D14 D13 D12 D11 D10 D9 D8 R/W-x R/W-x R/W-x R/W-x R/W-x R/W-x R/W-x"}, {"pdf_page": 25, "printed_page": "25", "table": "Table 7-3", "section": null, "excerpt": "EEPROM2 EEPROM2 register Go 07h R/W 0000h(1) Temp_Offset Temperature offset register Go 08h R/W xxxxh(1) EEPROM3 EEPROM3 register Go 0Fh R 0117h Device_ID Device ID register Go (1) This value is stored in Electrically-Er"}]`

## INA219_VOLTAGE_NUMERIC_RESET_UNSUPPORTED — INA219

Table2测量值/HEX横线不是0reset

对象：SHUNT_VOLTAGE.SV

原策略/输入：`"SHUNT/BUS all fields reset0"`

候选：`{"known_reset_mask": "0x0", "exclude_fixed_numeric_reset": true, "zero_analog_input_if_used": "an external input assumption, not POR fact"}`

来源：`[{"pdf_page": 18, "printed_page": "18", "table": "Table 2", "section": null, "excerpt": "Shunt voltage Shunt voltage measurement data. Shunt voltage — R 02 Bus voltage Bus voltage measurement data. Bus voltage — R 03 Power(2) Power measurement data. 00000000 00000000 0000 R Contains the value of the current "}, {"pdf_page": 23, "printed_page": "23", "table": "Figure 24", "section": null, "excerpt": "Figure 24. Bus Voltage Register 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0 BD12 BD11 BD10 BD9 BD8 BD7 BD6 BD5 BD4 BD3 BD2 BD1 BD0 — CNVR OVF At full-scale range = 16 V (decimal = 4000, hex = 0FA0), and LSB = 4 mV. CNVR: Conve"}]`

## INA219_CNVR_CLEAR_SOURCE_CONFLICT — INA219

p10Status/convert pin vs p23Power/newMODE应登记冲突

对象：BUS_VOLTAGE.CNVR

原策略/输入：`"CNVR no read_action and static0"`

候选：`{"main_profile": "source conflict retained; read-clear excluded until policy interpretation frozen", "optional_register_detail_priority": "reading POWER clears BUS_VOLTAGE.CNVR", "not_same_register_read_clear": true, "require_asserted_CNVR_event": true}`

来源：`[{"pdf_page": 23, "printed_page": "23", "table": null, "section": "§8.6.3.2", "excerpt": "Reading the Power Register OVF: Math Overflow Flag Bit 0 The Math Overflow Flag (OVF) is set when the Power or Current calculations are out of range. It indicates that current and power data may be meaningless. 8.6.3.3 P"}, {"pdf_page": 10, "printed_page": "10", "table": null, "section": "§8.3.1", "excerpt": "Reading the Status register • Triggering a single-shot conversion with the convert pin 8.3.1.1 Power Measurement Current and bus voltage are converted at different points in time, depending on the resolution and averagin"}]`

## INA219_RSV2_CONSTANT_ZERO_UNSUPPORTED — INA219

未命名图位不能推出恒零

对象：BUS_VOLTAGE.RSV_2

原策略/输入：`"RSV_2 RO reset0 and description恒读0"`

候选：`{"source_access": "register-level RO", "exclude_constant_zero_oracle": true, "do_not_write_nondefault_reserved_bits": true}`

来源：`[{"pdf_page": 23, "printed_page": "23", "table": "Figure 24", "section": null, "excerpt": "Figure 24. Bus Voltage Register 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0 BD12 BD11 BD10 BD9 BD8 BD7 BD6 BD5 BD4 BD3 BD2 BD1 BD0 — CNVR OVF At full-scale range = 16 V (decimal = 4000, hex = 0FA0), and LSB = 4 mV. CNVR: Conve"}, {"pdf_page": 18, "printed_page": "18", "table": "Table 2", "section": null, "excerpt": "Bus voltage Bus voltage measurement data. Bus voltage — R 03 Power(2) Power measurement data. 00000000 00000000 0000 R Contains the value of the current flowing 04 Current(2) 00000000 00000000 0000 R through the shunt re"}]`

## INA219_RST_COMPLETION_SCOPE — INA219

self-clears不是任意瞬时always0

对象：CONFIGURATION.RST

原策略/输入：`"read_as0 / desc reads always0"`

候选：`{"write_value": 1, "after_reset_completed": "all defined defaults restored and RST=0", "atomic_reset_abstraction": "explicit protocol assumption; no silicon timing proof", "exclude_during_reset_readback_oracle": true}`

来源：`[{"pdf_page": 19, "printed_page": "19", "table": "Table 3 / Figure 19", "section": null, "excerpt": "Reset Bit Bit 15 Setting this bit to '1' generates a system reset that is the same as power-on reset. Resets all registers to default values; this bit self-clears. BRNG: Bus Voltage Range Bit 13 0 = 16V FSR 1 = 32V FSR ("}]`

## INA226_RST_COMPLETION_SCOPE — INA226

self-clears不是任意瞬时always0

对象：CONFIG.RST

原策略/输入：`"read_as0 / desc reads always0"`

候选：`{"write_value": 1, "after_reset_completed": "all defined defaults restored and RST=0", "atomic_reset_abstraction": "explicit protocol assumption; no silicon timing proof", "exclude_during_reset_readback_oracle": true}`

来源：`[{"pdf_page": 23, "printed_page": "23", "table": "§7.1.1 RST", "section": null, "excerpt": "Reset Bit Bit 15 Setting this bit to '1' generates a system reset that is the same as power-on reset. Resets all registers to default values; this bit self-clears. AVG: Averaging Mode Bits 9–11 Determines the number of s"}]`

## INA3221_RST_COMPLETION_SCOPE — INA3221

self-clears不是任意瞬时always0

对象：CONFIG.RST

原策略/输入：`"read_as0 / desc reads always0"`

候选：`{"write_value": 1, "after_reset_completed": "all defined defaults restored and RST=0", "atomic_reset_abstraction": "explicit protocol assumption; no silicon timing proof", "exclude_during_reset_readback_oracle": true}`

来源：`[{"pdf_page": 26, "printed_page": "26", "table": "Table 8-4", "section": null, "excerpt": "Reset bit. Set this bit = 1 to generate a system reset that is the same as a power-on reset (POR). This bit resets all registers to default values and self-clears. 14 CH1en R/W 7h Channel enable mode. These bits allow ea"}]`

## INA226_UNNAMED_ACCESS_UNDEFINED — INA226

三组未命名位逐位RO未在来源定义

对象：CONFIG.UNNAMED_14_12

原策略/输入：`"CONFIG14:12/CAL15/MASK9:5 all RO"`

候选：`{"exclude_access_oracle": true, "keep_reset_value_in_all_legal_writes": true, "retain_known_por": true}`

来源：`[{"pdf_page": 22, "printed_page": "22", "table": "Table 7-2", "section": null, "excerpt": "Configuration Register (00h) (Read/Write) Descriptions BIT NO. D15 D14 D13 D12 D11 D10 D9 D8 D7 D6 D5 D4 D3 D2 D1 D0 BIT RST — — — AVG2 AVG1 AVG0 VBUSCT2 VBUSCT1 VBUSCT0 VSHCT2 VSHCT1 VSHCT0 MODE3 MODE2 MODE1 NAME POR 0 "}]`

## INA226_CVRF_CLEAR_EVENTS — INA226

必须控制完成事件后检验MASK读清和CONFIG例外

对象：MASK_ENABLE.CVRF

原策略/输入：`"CVRF no read_action static0"`

候选：`{"on_read": "MASK_ENABLE", "on_write": "CONFIG with MODE not 0 or 4", "set_event": "all conversions, averaging, multiplications complete", "require_nonzero_event": true}`

来源：`[{"pdf_page": 27, "printed_page": "27", "table": null, "section": "§7.1.7 CVRF", "excerpt": "Conversion Ready Flag bit clears under the following conditions: 1.) Writing to the Configuration Register (except for Power-Down selection) 2.) Reading the Mask/Enable Register OVF: Math Overflow Flag Bit 2 This bit is "}, {"pdf_page": 11, "printed_page": "11", "table": null, "section": "§6.3.1", "excerpt": "Conversion Ready flag (CVRF) bit is set after all conversions, averaging, and multiplication operations are complete. The Conversion Ready flag (CVRF) bit clears under these conditions: • Writing to the Configuration Reg"}]`

## INA226_AFF_LATCH_CLEAR — INA226

AFF清除受LEN模式限制

对象：MASK_ENABLE.AFF

原策略/输入：`"AFF no read_action static0"`

候选：`{"if_LEN1_on_read": "MASK_ENABLE", "if_LEN0_clear": "next conversion without alert", "require_controlled_alert": true}`

来源：`[{"pdf_page": 27, "printed_page": "27", "table": null, "section": "§7.1.7 AFF", "excerpt": "When the Alert Latch Enable bit is set to Latch mode, the Alert Function Flag bit clears only when the Mask/Enable Register is read. When the Alert Latch Enable bit is set to Transparent mode, the Alert Function Flag bit"}]`

## INA226_AFF_CONFIG_CLEAR_SOURCE_CONFLICT — INA226

p13CONFIG写清 vs p27onlyMASK读清未解决

对象：MASK_ENABLE.AFF

原策略/输入：`"not registered"`

候选：`{"CONFIG_write_clear_AFF": "excluded main profile; text disagreement retained", "MASK_read_clear_AFF": "supported when LEN=1"}`

来源：`[{"pdf_page": 13, "printed_page": "13", "table": null, "section": "§6.3.1.2", "excerpt": "until either the Configuration Register (00h) is written to or the Mask/Enable Register is read. The Bus Voltage alert functions compare the measured bus voltage to the Alert Limit Register following every bus voltage co"}, {"pdf_page": 27, "printed_page": "27", "table": null, "section": "§7.1.7 AFF", "excerpt": "clears only when the Mask/Enable Register is read. When the Alert Latch Enable bit is set to Transparent mode, the Alert Function Flag bit is cleared following the next conversion that does not result in an Alert conditi"}]`

## INA226_DIE_ID_RESET_SOURCE_CONFLICT — INA226

Table7-15零POR与Table7-1 2260/61不一致

对象：DIE_ID.ID

原策略/输入：`"runtime2260 variants only"`

候选：`{"main_reset_known_mask": "0x0", "exclude_fixed_ID_reset": true, "optional_summary_priority_expected_set": ["0x2260", "0x2261"], "split_device_and_revision_fields": true}`

来源：`[{"pdf_page": 22, "printed_page": "22", "table": "Table 7-1 note (3)", "section": null, "excerpt": "Die COO: 2260 = USA or Japan, 2261 = USA 7.1.1 Configuration Register (00h) (Read/Write) Table 7-2. Configuration Register (00h) (Read/Write) Descriptions BIT NO. D15 D14 D13 D12 D11 D10 D9 D8 D7 D6 D5 D4 D3 D2 D1 D0 BIT"}, {"pdf_page": 28, "printed_page": "28", "table": "Table 7-15", "section": null, "excerpt": "POR 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 VALUE DID: Device ID Bits Bits 4-15 Stores the device identification bits RID: Die Revision ID Bits Bit 0-3 Stores the device revision identification bits 28 Submit Document Feedback C"}]`

## INA3221_0E_SOURCE_CONFLICT — INA3221

维持0E reset/access来源冲突，不用图优先当事实

对象：SHUNT_SUM_LIMIT.SVL

原策略/输入：`"SVL candidate16383"`

候选：`{"register_known_mask": "0x8001", "expected_register": "0x0000", "field_known_mask": "0x8000", "exclude_register_mask": "0x7ffe", "do_not_promote_16383_to_unconditional_fact": true}`

来源：`[{"pdf_page": 33, "printed_page": "33", "table": "Tables 8-31 / 8-32", "section": null, "excerpt": "Shunt-Voltage Sum-Limit Register (address = 0Eh) [reset = 7FFEh] This register contains the value that is compared to the Shunt-Voltage Sum register value following each completed cycle of all selected channels to detect"}, {"pdf_page": 33, "printed_page": "33", "table": "Table 8-31", "section": null, "excerpt": "Table 8-31. Shunt-Voltage Sum-Limit Register 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0 SIGN SVL13 SVL12 SVL11 SVL10 SVL9 SVL8 SVL7 SVL6 SVL5 SVL4 SVL3 SVL2 SVL1 SVL0 — RW-0 RW-1 RW-1 RW-1 RW-1 RW-1 RW-1 RW-1 RW-1 RW-1 RW-1 R"}, {"pdf_page": 33, "printed_page": "33", "table": "Table 8-32", "section": null, "excerpt": "Table 8-32. Shunt-Voltage Sum-Limit Register Field Descriptions Bit Field Type Reset Description 15 SIGN R 0h Sign bit. 0 = positive number 1 = negative number in twos complement format 14-1 SVL13-0 R 0h Shunt-voltage su"}]`

## INA3221_CVRF_CONFIG_POWERDOWN_EXCEPTION — INA3221

CONFIG写清CVRF有powerdown/disable例外

对象：MASK_ENABLE.CVRF

原策略/输入：`"writeCONFIG clears unconditionally desc"`

候选：`{"on_read": "MASK_ENABLE", "on_CONFIG_write_clear_if_MODE_not": [0, 4], "set_event": "all enabled channel conversions complete", "require_nonzero_event": true}`

来源：`[{"pdf_page": 35, "printed_page": "35", "table": "Table 8-34 continued", "section": null, "excerpt": "Conversion ready clears under the following conditions: 1. Writing the Configuration register (except for power-down or disable-mode selections). 2. Reading the Mask/Enable register. 8.2.17 Power-valid Upper-limit Regist"}]`

## INA3221_TCF_SOFT_RESET_AND_LITERAL — INA3221

soft reset重新初始化遗漏；reset列11h另有单比特表达冲突

对象：MASK_ENABLE.TCF

原策略/输入：`"TCF desc only powercycle clear"`

候选：`{"no_read_clear": true, "reinitialize_event": ["power cycle", "software reset"], "do_not_keep_forever_constant_1": true}`

来源：`[{"pdf_page": 34, "printed_page": "34", "table": "Table 8-34", "section": null, "excerpt": "unless the power is recycled or a software reset is issued. The default state for the timing control alert flag is high. 34 Submit Document Feedback Copyright © 2026 Texas Instruments Incorporated Product Folder Links: I"}]`

## INA3221_TCF_RESET_LITERAL_CONFLICT — INA3221

11h超字段范围与RW1/0002冲突

对象：MASK_ENABLE.TCF

原策略/输入：`"not registered"`

候选：`{"main_por_expected_bit": 1, "support": "register header, bitmap, default-high prose", "table_literal": "11h", "classification": "source representation conflict, not official erratum"}`

来源：`[{"pdf_page": 34, "printed_page": "34", "table": "Table 8-33", "section": null, "excerpt": "RW-1 RW-0 LEGEND: R/W = Read/Write; R = Read only; -n = value after reset Table 8-34. Mask/Enable Register Field Descriptions Bit Field Type Reset Description 15 Reserved R/W 0h Reserved 14-12 SCC1-3 R/W 0h Summation cha"}, {"pdf_page": 34, "printed_page": "34", "table": "Table 8-34", "section": null, "excerpt": "11h Timing-control-alert flag indicator. Use this bit to determine if the timing control (TC) alert pin has been asserted through software rather than hardware. The bit setting corresponds to the status of the TC pin. Th"}]`

## INA3221_EARLY_CONFIG_DISABLES_TIMING — INA3221

CONFIG写不止换模式/重启，还会提前停止timing功能

对象：CONFIG.MODE

原策略/输入：`"CONFIG write halts conversion only"`

候选：`{"on_write": "halt/restart conversion", "CVRF_clear_unless_powerdown": true, "TC_sequence_early_CONFIG_write": "disables timing control until power cycle/software reset"}`

来源：`[{"pdf_page": 26, "printed_page": "26", "table": null, "section": "§8.2.1", "excerpt": "Writing to this register halts any conversion in progress until the write sequence is completed, resulting in a new conversion starting, based on the new Configuration register contents. This architecture prevents any un"}, {"pdf_page": 15, "printed_page": "15", "table": null, "section": "§7.3.2.4", "excerpt": "Writing to the Configuration register before the timing control alert function completes the full sequence results in disabling the timing control alert until power is cycled or a software reset is issued. 7.3.2.5 Defaul"}]`

## INA3221_FLAGS_RW_LABEL_ABSTRACTION — INA3221

硬件标志的RO是抽象；保留原表RW码及写不清状态

对象：MASK_ENABLE.CF

原策略/输入：`"CF/SF/WF/PVF/TCF/CVRF codedRO"`

候选：`{"source_label": "R/W", "effective_role": "hardware managed status", "exclude_ordinary_RW_persistence": true, "software_ignores_write_to_status": "abstraction assumption, not a quoted RO code"}`

来源：`[{"pdf_page": 34, "printed_page": "34", "table": "Table 8-34", "section": null, "excerpt": "Writing to this register does not clear the flag bit status. To make sure that there is no uncertainty in the warning function setting that resulted in a flag bit being set, the Mask/Enable register must be read from to "}, {"pdf_page": 34, "printed_page": "34", "table": "Table 8-34", "section": null, "excerpt": "Critical-alert flag indicator. These bits are asserted if the corresponding channel measurement has exceeded the critical alert limit resulting in the Critical alert pin being asserted. Read these bits to determine which"}]`

## ADS1115_OS_TRIGGER_STATUS_GATE — ADS1115

OS不是可持久写的普通RW

对象：CONFIG.OS

原策略/输入：`"OS ordinary RW, no field special policy"`

候选：`{"write0": "no effect", "write1_when_powerdown": "start one conversion", "write1_while_busy": "no effect", "read0": "conversion in progress", "read1": "idle", "exclude_storage_persistence": true}`

来源：`[{"pdf_page": 25, "printed_page": "25", "table": "Table 8-3", "section": null, "excerpt": "OS can only be written when in power-down state and has no effect when a conversion is ongoing. When writing: 15 OS R/W 1b 0b : No effect 1b : Start a single conversion (when in power-down state) When reading: 0b : Devic"}]`

## ADS1115_CONFIG_APPLIES_AFTER_OLD_CONVERSION — ADS1115

CONFIG写不中止旧转换，新配置下一次才生效

对象：CONFIG.MUX

原策略/输入：`"no condition policy"`

候选：`{"storage_readback_vs_effective_conversion_configuration": "separate", "continuous_update_applies": "after current old-config conversion completes", "OS_stimulus": "0 for ordinary field persistence baseline"}`

来源：`[{"pdf_page": 18, "printed_page": "18", "table": null, "section": "§7.4.2.2", "excerpt": "When writing new configuration settings, the currently ongoing conversion completes with the previous configuration settings. Thereafter, continuous conversions with the new configuration settings start. To switch to sin"}]`

## ADS1115_COMPARATOR_READ_CONVERSION_EFFECT — ADS1115

CONVERSION读取解除锁存输出，不是CONFIG bit读清

对象：CONFIG.COMP_LAT

原策略/输入：`"no external alert state in register contract"`

候选：`{"field_read_action": "none declared", "cross_register_side_effect": "CONVERSION read clears latched ALERT output", "condition": "COMP_LAT=1, comparator enabled and asserted", "need_alert_state_model": true}`

来源：`[{"pdf_page": 16, "printed_page": "16", "table": null, "section": "§7.3.7", "excerpt": "This latched assertion can only be cleared by issuing an SMBus alert response or by reading the Conversion register. The ALERT/RDY pin can be configured as active high or active low by the COMP_POL bit in the Config regi"}, {"pdf_page": 26, "printed_page": "26", "table": "Table 8-3 continued", "section": null, "excerpt": "remains latched until conversion data are read by the controller or an appropriate SMBus alert response is sent by the controller. The device responds with an address, and is the lowest address currently asserting the AL"}]`

## ADS1115_THRESHOLDS_FUNCTION_CONSTRAINT — ADS1115

补码HI>LO/PGA变化更新及RDY组合必须分开

对象：LO_THRESH.THRESH

原策略/输入：`"threshold unrestricted storage only"`

候选：`{"storage_data_domain": "all 16-bit patterns", "comparator_function_precondition": "signed HI > signed LO", "pga_changed": "update thresholds for desired analog limits", "RDY_mode_condition": {"HI_THRESH.MSB": 1, "LO_THRESH.MSB": 0}, "storage_only_precondition": "disable comparator (COMP_QUE=3)"}`

来源：`[{"pdf_page": 27, "printed_page": "27", "table": null, "section": "§8.1.4", "excerpt": "Hi_thresh register value must always be greater than the Lo_thresh register value. The threshold register formats are shown in Figure 8-6. When set to RDY mode, the ALERT/RDY pin outputs the OS bit when in single-shot mo"}, {"pdf_page": 27, "printed_page": "27", "table": null, "section": "§8.1.4", "excerpt": "conversion-ready function of the ALERT/RDY pin is enabled by setting the Hi_thresh register MSB to 1b and the Lo_thresh register MSB to 0b. To use the comparator function of the ALERT/RDY pin, the Hi_thresh register valu"}]`

## ADS1220_ANY_CONFIG_WRITE_RESTARTS — ADS1220

任意配置写都有conversion事件，CM1并不代替START/SYNC

对象：CONFIG1.CM

原策略/输入：`"only static register interface, commands excluded"`

候选：`{"CONFIG_write_single_shot": "start/restart one conversion", "CONFIG_write_ongoing": "restart current conversion", "CONFIG_write_from_powerdown": "wake and one conversion regardless CM", "continuous_start": "CM=1 then START/SYNC", "completion": "DRDY high-to-low / new output available", "config_readback_is_not_conversion_validation": true}`

来源：`[{"pdf_page": 34, "printed_page": "34", "table": null, "section": "§8.4.2.1-2", "excerpt": "every write access to any configuration register also starts a new conversion. Writing to any configuration register while a conversion is ongoing functions as a new START/SYNC command that stops the current conversion a"}, {"pdf_page": 35, "printed_page": "35", "table": null, "section": "§8.4.3.4", "excerpt": "Writing to any configuration register wakes up the device as well, but only starts a single conversion regardless of the selected conversion mode (CM). Copyright © 2026 Texas Instruments Incorporated Submit Document Feed"}]`

## ADS1220_TEMP_MODE_OVERRIDES_CONFIG0_VREF — ADS1220

TS1使CONFIG0无效且实际内部reference，不证明读回位改写

对象：CONFIG2.VREF

原策略/输入：`"no mode override policy"`

候选：`{"temperature_sensor_override_if": "CONFIG1.TS=1", "CONFIG0_effect": "none on temperature conversion", "effective_VREF": "internal reference regardless selection", "storage_fields": "do not fabricate readback normalization", "any_CONFIG_write": "start/restart as §8.4.2; separate command/event profile"}`

来源：`[{"pdf_page": 33, "printed_page": "33", "table": null, "section": "§8.3.13", "excerpt": "settings of configuration register 0 have no effect and the device uses the internal reference for measurement, regardless of the selected voltage reference source. Temperature readings follow the same process as the ana"}]`

## ADS1220_IDAC_STARTUP_AND_POWERDOWN — ADS1220

IDAC先设置后routing，单次完成不自动关

对象：CONFIG2.IDAC

原策略/输入：`"only legal codes defined"`

候选：`{"program_sequence": ["IDAC current", "wait startup if claiming stable current", "I1MUX/I2MUX routing"], "startup_max_us": 200, "single_shot_complete": "IDAC stays active", "POWERDOWN": "IDAC off, stored register retained"}`

来源：`[{"pdf_page": 31, "printed_page": "31", "table": null, "section": "§8.3.8", "excerpt": "IDACs require up to 200µs to start up after the IDAC current is programmed to the respective value using the IDAC[2:0] bits. Set the IDAC current to the respective value using the IDAC[2:0] bits and then select the routi"}, {"pdf_page": 31, "printed_page": "31", "table": null, "section": "§8.3.8", "excerpt": "IDACs remain active between any two conversions if the IDAC[2:0] bits are set to a value other than 000b. However, the IDACs are powered down whenever the POWERDOWN command is issued. The analog supply current increases "}]`

## ADS1220_PSW_STATE_PERSISTENCE — ADS1220

PSW1单次完成后保持关合，POWERDOWN才开

对象：CONFIG2.PSW

原策略/输入：`"PSW desc says power switch/powerdown mode"`

候选：`{"PSW0": "open", "PSW1_START_SYNC": "close", "POWERDOWN": "open", "single_shot_completion": "retain closed if PSW1", "config_write_side_effect": "separate conversion restart"}`

来源：`[{"pdf_page": 31, "printed_page": "31", "table": null, "section": "§8.3.9", "excerpt": "switch stays closed between conversions in single-shot conversion mode in case the PSW bit is set to 1b. The switch can be opened at any time by setting the PSW bit to 0b. By default, the switch is always open. 8.3.10 Se"}]`

## ADS1220_RESERVED_ALWAYS_WRITE_ZERO — ADS1220

0-only合法刺激没有可写性对照

对象：CONFIG3.RESERVED

原策略/输入：`"existing policy correct fixed0; prior IR desc reserved却可写 should not imply1"`

候选：`{"fixed_write": 0, "known_reset": true, "exclude_nonzero_write_oracle": true, "skip_writability_due_to_no_legal_alternative": true}`

来源：`[{"pdf_page": 46, "printed_page": "46", "table": "Table 8-14", "section": null, "excerpt": "Always write 0b 46 Submit Document Feedback Copyright © 2026 Texas Instruments Incorporated Product Folder Links: ADS1220"}]`

## RESERVED_NONDEFAULT_WRITE_UNDEFINED — INA3221

Reserved/RW0仅访问码与reset，不定义非零存储功能；分开保留事实与undefined操作

对象：CRIT1.UNUSED, WARN1.UNUSED, CRIT2.UNUSED, WARN2.UNUSED, CRIT3.UNUSED, WARN3.UNUSED, MASK_ENABLE.RSVD15

原策略/输入：`"6 limit RESERVED fields unrestricted ordinaryRW; RSVD15 policy already excludes"`

候选：`{"retain_source_RW_label": true, "retain_reset0": true, "main_profile_default_only": true, "exclude_nondefault_write_oracle": true}`

来源：`[{"pdf_page": 31, "printed_page": "31", "table": "Table 8-18", "section": null, "excerpt": "Table 8-18. Channel-1 Critical-Alert Limit Register Field Descriptions Bit Field Type Reset Description 15-3 C1L12-0 R/W FFFh Channel-1 critical-alert-limit data bits 2-0 Reserved R/W 0h Reserved 8.2.9 Warning-Alert Chan"}, {"pdf_page": 32, "printed_page": "32", "table": "Table 8-24", "section": null, "excerpt": "Table 8-24. Channel-2 Warning-Alert Limit Register Field Descriptions Bit Field Type Reset Description 15-3 W2L12-0 R/W FFFh Channel-2 warning-alert-limit data bits 2-0 Reserved R/W 0h Reserved 8.2.12 Channel-3 Critical-"}, {"pdf_page": 34, "printed_page": "34", "table": "Table 8-34", "section": null, "excerpt": "Reserved R/W 0h Reserved 14-12 SCC1-3 R/W 0h Summation channel control. These bits determine which shunt voltage measurement channels are enabled to fill the Shunt-Voltage Sum register. The selection of these bits does n"}]`

## MOTION-LIS2-TEMP-NIBBLE — LIS2DW12

温度低byte数据/零域上下半字节颠倒，来源图与12bit左对齐一致。

对象：OUT_T_L.TEMP_3_0, OUT_T_L.ZERO_7_4

原策略/输入：`{"TEMP_3_0.bits": "3:0", "ZERO_7_4.bits": "7:4"}`

候选：`{"TEMP_3_0.bits": "7:4", "ZERO_7_4.rename": "ZERO_3_0", "ZERO_3_0.bits": "3:0", "known_zero_mask": "0x0F"}`

来源：`[{"pdf_page": 35, "printed_page": "35", "table_or_section": "Table22; visually verified", "excerpt": "TEMP3", "source_path": "corpus/data/raw_pdf/ST/lis2dw12.pdf"}, {"pdf_page": 18, "printed_page": "18", "table_or_section": "§3.6", "excerpt": "left-justified in 12-bit mode", "source_path": "corpus/data/raw_pdf/ST/lis2dw12.pdf"}]`

## MOTION-LIS3-STATUS-DEFAULT — LIS3DH

Output总表不能覆盖Table47七个明确default0；14动态字段reset全排除措辞不准确。

对象：STATUS_REG.ZYXOR, STATUS_REG.ZOR, STATUS_REG.YOR, STATUS_REG.XOR, STATUS_REG.ZYXDA, STATUS_REG.ZDA, STATUS_REG.YDA

原策略/输入：`{"v2_status_known_reset_mask": "0x00", "report": "14 nonstatic reset fields"}`

候选：`{"known_reset_mask": "0xFE", "expected": 0, "scope": "initial default before measurement/event", "XDA_unknown": true}`

来源：`[{"pdf_page": 39, "printed_page": "39", "table_or_section": "Table47; visually verified", "excerpt": "Default value: 0", "source_path": "corpus/data/raw_pdf/ST/LIS3DH.pdf"}, {"pdf_page": 31, "printed_page": "31", "table_or_section": "Table21", "excerpt": "STATUS_REG", "source_path": "corpus/data/raw_pdf/ST/LIS3DH.pdf"}]`

## MOTION-LIS3-XDA-NO-DESCRIPTION — LIS3DH

Table46有XDA，Table47实际缺XDA行；缺少默认和clear动作不能补全。

对象：STATUS_REG.XDA

原策略/输入：`{"field_reset": 0}`

候选：`{"known_reset": false, "exclude_CoR": true, "do_not_infer_by_symmetry": true}`

来源：`[{"pdf_page": 39, "printed_page": "39", "table_or_section": "Tables46–47; visually verified", "excerpt": "XDA", "source_path": "corpus/data/raw_pdf/ST/LIS3DH.pdf"}]`

## MOTION-LIS3-FIFO-READ-EFFECT — LIS3DH

输出读取FIFO样本集会推进FIFO并在first sample set读完后清OVRN_FIFO；不等于DATA读清0或STATUS_REG旗标的清除规则。

对象：OUT_X/Y/Z, FIFO_SRC_REG.OVRN_FIFO

原策略/输入：`{"v2": "no FIFO/read transaction model"}`

候选：`{"cross_register_clear": "OVRN_FIFO after first sample set read", "sample_pop": true, "exclude_unmodelled_FIFO_function": true}`

来源：`[{"pdf_page": 23, "printed_page": "23", "table_or_section": "§5.1.5", "excerpt": "Each time data is read from the FIFO", "source_path": "corpus/data/raw_pdf/ST/LIS3DH.pdf"}, {"pdf_page": 41, "printed_page": "41", "table_or_section": "Table52", "excerpt": "The OVRN bit is set to 0", "source_path": "corpus/data/raw_pdf/ST/LIS3DH.pdf"}]`

## MOTION-LIS3-ST-ACCESS — LIS3DH

UNSPEC是旧IR排除标记，不能当厂商访问事实。原始rw表和合法自检编码支持限定RW。

对象：CTRL_REG4.ST

原策略/输入：`{"ir_access": "UNSPEC"}`

候选：`{"access": "RW", "legal_values": [0, 1, 2], "exclude_values": [3], "exclude_analog_response": true}`

来源：`[{"pdf_page": 31, "printed_page": "31", "table_or_section": "Table21", "excerpt": "CTRL_REG4", "source_path": "corpus/data/raw_pdf/ST/LIS3DH.pdf"}, {"pdf_page": 37, "printed_page": "37", "table_or_section": "Tables38–39", "excerpt": "Self-test enable", "source_path": "corpus/data/raw_pdf/ST/LIS3DH.pdf"}]`

## MOTION-LIS3-AUX-ADC-BDU — LIS3DH

辅助ADC/温度功能必须BDU1/ADC_EN1，现policy未列功能前置条件。

对象：TEMP_CFG_REG.ADC_EN, TEMP_CFG_REG.TEMP_EN, CTRL_REG4.BDU

原策略/输入：`{"v2": "no auxiliary ADC condition"}`

候选：`{"ADC_function_requires": {"BDU": 1, "ADC_EN": 1}, "TEMP_function": "ADC channel3 selected with TEMP_EN1; output OUT_ADC3", "function_without_dependencies": "EXCLUDE"}`

来源：`[{"pdf_page": 19, "printed_page": "19", "table_or_section": "§3.7", "excerpt": "the user must set the BDU bit", "source_path": "corpus/data/raw_pdf/ST/LIS3DH.pdf"}, {"pdf_page": 19, "printed_page": "19", "table_or_section": "§3.7", "excerpt": "Channel 3 of the ADC can be connected", "source_path": "corpus/data/raw_pdf/ST/LIS3DH.pdf"}]`

## MOTION-LIS2-MBZ-ACCESS — LIS2DW12

脚注must0不证明RO hardwire；现policy虽排除非法写但IR未来生成仍误导。

对象：CTRL2.MUST_BE_ZERO

原策略/输入：`{"ir_access": "RO"}`

候选：`{"access": "UNSPEC", "fixed_write": 0, "known_reset": true, "exclude_illegal_write_oracle": true}`

来源：`[{"pdf_page": 37, "printed_page": "37", "table_or_section": "Table32 footnote", "excerpt": "This bit must be set to 0", "source_path": "corpus/data/raw_pdf/ST/lis2dw12.pdf"}]`

## MOTION-LIS2-WAKE-CLEAR — LIS2DW12

FF_IA“自读清”未在§8.28规定；明确可核的clear操作是ALL_INT_SRC对related routed interrupt flags。

对象：WAKE_UP_SRC.FF_IA, WAKE_UP_SRC, ALL_INT_SRC

原策略/输入：`{"FF_IA.desc": "自由落体事件标志，读清除"}`

候选：`{"desc": "Free-fall event status. ALL_INT_SRC read resets related routed interrupt function flags; no unqualified self-CoR guarantee", "CoR_assertion": "exclude unless relevant mapped clear semantics and fixture"}`

来源：`[{"pdf_page": 50, "printed_page": "50", "table_or_section": "§8.28", "excerpt": "Free-fall event detection status", "source_path": "corpus/data/raw_pdf/ST/lis2dw12.pdf"}, {"pdf_page": 53, "printed_page": "53", "table_or_section": "§8.31", "excerpt": "Reading this register, all related interrupt function flags", "source_path": "corpus/data/raw_pdf/ST/lis2dw12.pdf"}]`

## MOTION-LIS2-FIFO-MODE-SOURCE — LIS2DW12

§5.3.4/5.3.5的trigger event/continuous终态与Table55的deasserted/FIFO终态不一致。

对象：FIFO_CTRL.FMODE

原策略/输入：`{"Table55.FMODE_4": "then FIFO mode", "body_FMODE_4": "continuous upon trigger event"}`

候选：`{"legal_codes": [0, 1, 3, 4, 6], "source_conflict": "UNRESOLVED", "exclude_FMODE3_4_event_oracles": true}`

来源：`[{"pdf_page": 44, "printed_page": "44", "table_or_section": "Table55", "excerpt": "then FIFO mode", "source_path": "corpus/data/raw_pdf/ST/lis2dw12.pdf"}, {"pdf_page": 25, "printed_page": "25", "table_or_section": "§5.3.4", "excerpt": "FIFO mode starts upon an internal trigger event", "source_path": "corpus/data/raw_pdf/ST/lis2dw12.pdf"}, {"pdf_page": 26, "printed_page": "26", "table_or_section": "§5.3.5", "excerpt": "starts in continuous mode upon an internal trigger event", "source_path": "corpus/data/raw_pdf/ST/lis2dw12.pdf"}, {"pdf_page": 24, "printed_page": "24", "table_or_section": "§5.3.1", "excerpt": "Bypass mode is also used to reset", "source_path": "corpus/data/raw_pdf/ST/lis2dw12.pdf"}]`

## MOTION-LIS2-FTH0 — LIS2DW12

FTH0时明确FIFO_FTH0，不能无条件DIFF≥FTH公式；FIFO切换首样discard。

对象：FIFO_CTRL.FTH, FIFO_SAMPLES.FIFO_FTH, STATUS.FIFO_THS

原策略/输入：`{"v2": "no functional FIFO rule"}`

候选：`{"FIFO_FTH": "FTH!=0 and DIFF>=FTH", "discard_first_sample_on_switch": true, "functional_scope": "requires FIFO events"}`

来源：`[{"pdf_page": 23, "printed_page": "23", "table_or_section": "§5.3", "excerpt": "If FTH[4:0] is equal to 0", "source_path": "corpus/data/raw_pdf/ST/lis2dw12.pdf"}]`

## MOTION-AD-LOCK-IDLE — AD5592R

缺跨寄存器IO_LOCK及idle无转换/无readback前置条件。

对象：GEN_CTRL_REG.IO_LOCK, ADC_CONFIG.ADC_PIN_MASK, DAC_CONFIG.DAC_PIN_MASK, PULLDWN_CONFIG.PULL_DWN_MASK

原策略/输入：`{"source_policy_constraints": []}`

候选：`{"requires_IO_LOCK": 0, "requires_idle": true, "locked_pin_config_writes": "ignored"}`

来源：`[{"pdf_page": 27, "printed_page": "27", "table_or_section": "CONFIGURING", "excerpt": "pin configuration registers are ignored", "source_path": "corpus/data/raw_pdf/ADI/ad5592r.pdf"}, {"pdf_page": 27, "printed_page": "27", "table_or_section": "CONFIGURING", "excerpt": "The I/Ox pins can be reconfigured at any time", "source_path": "corpus/data/raw_pdf/ADI/ad5592r.pdf"}]`

## MOTION-AD-READBACK-ADAPTER — AD5592R

direct memory read抽象缺厂商readback流程：selector/REG_RD_EN/next SPI，REG_RD_EN完成自清；ADC转换时其它read request ignored。

对象：all mapped control registers, CONFIG_READ_AND_LDAC.REG_RD_EN

原策略/输入：`{"register_model": "direct address read"}`

候选：`{"scope": "declared selector abstraction, not physical SPI guarantee", "adapter_requires": ["readback selector", "REG_RD_EN", "next SPI", "no active ADC for other reads"], "REG_RD_EN_clear": "read complete"}`

来源：`[{"pdf_page": 27, "printed_page": "27", "table_or_section": "READ MODE", "excerpt": "all other read requests are ignored", "source_path": "corpus/data/raw_pdf/ADI/ad5592r.pdf"}, {"pdf_page": 43, "printed_page": "43", "table_or_section": "Table21", "excerpt": "REG_RD_EN automatically clears", "source_path": "corpus/data/raw_pdf/ADI/ad5592r.pdf"}]`

## MOTION-AD-RESET-WRONGKEY — AD5592R

0x5AC有明确reset动作，但任意错key必须不复位的硬件oracle不由原文直接支持。

对象：SW_RESET.SW_RESET_CODE

原策略/输入：`{"v2": "wrong key must not reset"}`

候选：`{"recognized_key": "0x5AC", "wrong_key_oracle": "EXCLUDE as manufacturer fact; optionally separately labelled abstraction", "completion": "250us max, no write during reset"}`

来源：`[{"pdf_page": 50, "printed_page": "50", "table_or_section": "Table28", "excerpt": "10110101100: Reset", "source_path": "corpus/data/raw_pdf/ADI/ad5592r.pdf"}, {"pdf_page": 33, "printed_page": "33", "table_or_section": "RESET FUNCTION", "excerpt": "takes 250 µs maximum", "source_path": "corpus/data/raw_pdf/ADI/ad5592r.pdf"}]`

## MOTION-AD-COMMAND-FORMAT-SOURCE — AD5592R

p.26通用bits10:9保留与逐寄存器REPbit9、SWkeybits10:0不兼容。

对象：ADC_SEQ.REP, SW_RESET.SW_RESET_CODE, address_encoding.reserved_command_data_bits

原策略/输入：`{"generic_format": "bits10:9 reserved for control writes"}`

候选：`{"interpretation": "per-register-specific command bits; retain generic-format discrepancy", "official_erratum": false}`

来源：`[{"pdf_page": 26, "printed_page": "26", "table_or_section": "Table10", "excerpt": "Bits[10:9] are reserved", "source_path": "corpus/data/raw_pdf/ADI/ad5592r.pdf"}, {"pdf_page": 37, "printed_page": "37", "table_or_section": "Table16", "excerpt": "REP", "source_path": "corpus/data/raw_pdf/ADI/ad5592r.pdf"}, {"pdf_page": 50, "printed_page": "50", "table_or_section": "Table28", "excerpt": "10110101100: Reset", "source_path": "corpus/data/raw_pdf/ADI/ad5592r.pdf"}]`

## MOTION-MPU-SOURCE-IDENTITY — MPU6050

产品规格Rev3.4与寄存器地图Rev4.2必须分别锁源，不能混用页码。

对象：source_manifest.MPU6050

原策略/输入：`{"initial_source": "corpus/data/raw_pdf/InvenSense/MPU6050.pdf"}`

候选：`{"primary_source": {"chip": "MPU6050", "path": "corpus/data/raw_pdf/InvenSense/MPU-6000-Register-Map1_mirror.pdf", "sha256": "519650cbc502a3e89ddba6d6f115734b6c7060d451938c0dc36b6232daae7014", "manual_version": "RM-MPU-6000A-00 Revision 4.2; 08/19/2013", "pdf_pages": 46, "source_role": "PRIMARY_REGISTER_MAP_SOURCE", "source_depth": "full local manufacturer PDF; relevant original pages text-read; selected original pages visually inspected", "official_current_download_verified": false}, "supplementary_source": {"chip": "MPU6050", "path": "corpus/data/raw_pdf/InvenSense/MPU6050.pdf", "sha256": "a4fdf69590b8cbab1cf0a5bcd359327b0ac022061fb233855aff2e191e7e3584", "manual_version": "PS-MPU-6000A-00 Revision 3.4; 08/19/2013", "pdf_pages": 52, "source_role": "SUPPLEMENTARY_PRODUCT_SPECIFICATION", "source_depth": "full local PDF available; scope and electrical characteristics read", "official_current_download_verified": false, "note": "prepare.py initial device-name match was supplementary PS, not RM. RM p.40 and PS p.40 are different sections; never exchange their locators."}}`

来源：`[{"pdf_page": 1, "printed_page": "1", "table_or_section": "title page", "excerpt": "Revision: 4.2", "source_path": "corpus/data/raw_pdf/InvenSense/MPU-6000-Register-Map1_mirror.pdf"}]`

## MOTION-MPU-DLPF7-SOURCE — MPU6050

§4.2 DLPF_CFG0 or7 disabled与§4.3表7 Reserved不同粒度；排除7可保守但不能说其毫无定义。

对象：CONFIG.DLPF_CFG

原策略/输入：`{"v2_legal_values": [0, 1, 2, 3, 4, 5, 6]}`

候选：`{"legal_values": [0, 1, 2, 3, 4, 5, 6], "excluded_value7": "UNRESOLVED_SOURCE_AMBIGUITY"}`

来源：`[{"pdf_page": 13, "printed_page": "13", "table_or_section": "§4.3 DLPF table", "excerpt": "RESERVED", "source_path": "corpus/data/raw_pdf/InvenSense/MPU-6000-Register-Map1_mirror.pdf"}, {"pdf_page": 12, "printed_page": "12", "table_or_section": "§4.2", "excerpt": "DLPF_CFG = 0 or 7", "source_path": "corpus/data/raw_pdf/InvenSense/MPU-6000-Register-Map1_mirror.pdf"}]`

## MOTION-MPU-GYRO-ST-LAYOUT — MPU6050

总map high3bits“-”与detail named ST位的布局差异，应保留detail-first解读条件。

对象：GYRO_CONFIG.XG_ST, GYRO_CONFIG.YG_ST, GYRO_CONFIG.ZG_ST

原策略/输入：`{"overview": "- - -", "detail": "XG_ST YG_ST ZG_ST"}`

候选：`{"access": "RW detail-first provisional", "source_conflict": "UNRESOLVED_LAYOUT_DISCREPANCY", "no_official_erratum": true}`

来源：`[{"pdf_page": 6, "printed_page": "6", "table_or_section": "§3 overview GYRO_CONFIG", "excerpt": "GYRO_CONFIG", "source_path": "corpus/data/raw_pdf/InvenSense/MPU-6000-Register-Map1_mirror.pdf"}, {"pdf_page": 14, "printed_page": "14", "table_or_section": "§4.4", "excerpt": "XG_ST", "source_path": "corpus/data/raw_pdf/InvenSense/MPU-6000-Register-Map1_mirror.pdf"}]`

## MOTION-MPU-ANY-READ-CLEAR — MPU6050

INT_RD_CLEAR1时任意read清interrupt；未映射中断block使当前测试无法覆盖。

对象：all mapped reads, INT_PIN_CFG.INT_RD_CLEAR, INT_STATUS

原策略/输入：`{"v2": "no interrupt register mapping in IR"}`

候选：`{"scope_baseline": {"INT_RD_CLEAR": 0}, "dynamic_extension": ["INT_PIN_CFG", "INT_ENABLE", "INT_STATUS"], "clear_rules": {"0": "INT_STATUS read only", "1": "any read"}}`

来源：`[{"pdf_page": 26, "printed_page": "26", "table_or_section": "§4.14", "excerpt": "interrupt status bits are cleared on any read", "source_path": "corpus/data/raw_pdf/InvenSense/MPU-6000-Register-Map1_mirror.pdf"}, {"pdf_page": 28, "printed_page": "28", "table_or_section": "§4.16", "excerpt": "Each bit will clear", "source_path": "corpus/data/raw_pdf/InvenSense/MPU-6000-Register-Map1_mirror.pdf"}]`

## MOTION-MPU-CLOCK-CYCLE — MPU6050

CLKSEL7合法但clockstop，cycle依SLEEP0及LP_WAKE_CTRL；静态RW不能证明mode更新。

对象：PWR_MGMT_1.CLKSEL, PWR_MGMT_1.CYCLE, PWR_MGMT_1.SLEEP

原策略/输入：`{"legal_values": [0, 1, 2, 3, 4, 5, 7]}`

候选：`{"keep_legal7": true, "exclude_clockstop_function_without_clock_model": true, "CYCLE_requires_SLEEP": 0, "dependency": "PWR_MGMT_2.LP_WAKE_CTRL"}`

来源：`[{"pdf_page": 40, "printed_page": "40", "table_or_section": "§4.28", "excerpt": "Stops the clock", "source_path": "corpus/data/raw_pdf/InvenSense/MPU-6000-Register-Map1_mirror.pdf"}, {"pdf_page": 40, "printed_page": "40", "table_or_section": "§4.28", "excerpt": "When CYCLE is set to 1 while SLEEP is disabled", "source_path": "corpus/data/raw_pdf/InvenSense/MPU-6000-Register-Map1_mirror.pdf"}]`

## PT-HDC-TRIGGER-START — HDC2021

旧注释把开始自清写成完成自清，v2无触发完成模型时仍可能按RW持久性错判。

对象：MEAS_CONFIG.MEAS_TRIG

原策略/输入：`"self-clear on conversion complete / ordinary RW"`

候选：`{"self_clear_event": "measurement starts", "completion": "DRDY_STATUS conversion complete", "exclude_trigger1_from_storage_persistence": true}`

来源：`[{"pdf_page": 31, "printed_page": 31, "table_or_section": "Table7-38", "excerpt": "self-clears to 0 once the measurement starts."}]`

## PT-HDC-STATUS-MODES — HDC2021

漏掉DRDY多读地址清零和threshold comparator模式，旧INT_MODE描述错误。

对象：STATUS.DRDY_STATUS, STATUS.TH_STATUS, STATUS.TL_STATUS, STATUS.HH_STATUS, STATUS.HL_STATUS, DEVICE_CONFIG.INT_MODE

原策略/输入：`"no read_action; 0 data-ready/1 interrupt"`

候选：`{"DRDY_clear_reads": ["0x00", "0x01", "0x02", "0x03", "0x04"], "threshold_clear": "readSTATUS with INT_MODE0", "comparator": "INT_MODE1 current result", "pin_gate": "DRDY_INT_EN and interrupt enable; DRDY pin also INT_MODE0"}`

来源：`[{"pdf_page": 23, "printed_page": 23, "table_or_section": "§7.6.5", "excerpt": "The bit is cleared when the Status Register (0x04) is read."}, {"pdf_page": 30, "printed_page": 30, "table_or_section": "Table7-36", "excerpt": "1 = Comparator mode"}, {"pdf_page": 14, "printed_page": 14, "table_or_section": "§7.3.5.2.1", "excerpt": "reflects the current temperature conversion result."}]`

## PT-HDC-SOFTRESET — HDC2021

self clear after RESET不能推出每次读恒0；旧read_as=0隐藏动作区间。

对象：DEVICE_CONFIG.SOFT_RES

原策略/输入：`{"read_as": 0}`

候选：`{"read_zero_condition": "reset_complete", "reset_latency_max_ms": 3.5, "atomic_reset": "explicit benchmark abstraction only"}`

来源：`[{"pdf_page": 30, "printed_page": 30, "table_or_section": "Table7-36", "excerpt": "self-clears after RESET."}, {"pdf_page": 7, "printed_page": 7, "table_or_section": "tPOR", "excerpt": "3.5"}]`

## PT-TMP461-NO-POR — TMP461

Table4 STATUS与ONE_SHOT POR=N/A，候选reset=00及各字段0缺来源。

对象：STATUS.*, ONE_SHOT.START

原策略/输入：`{"register_reset": "0x00", "field_reset": 0}`

候选：`{"remove_resets": true, "runtime_status": true, "one_shot_not_stored": true}`

来源：`[{"pdf_page": 17, "printed_page": 17, "table_or_section": "Table4", "excerpt": "N/A"}]`

## PT-TMP461-CONDITIONAL-CLEAR — TMP461

read-clear遗漏cause-retired和模式条件；读STATUS不清ALERT interrupt latch。

对象：STATUS.LHIGH, STATUS.LLOW, STATUS.RHIGH, STATUS.RLOW, STATUS.OPEN, CONFIG.ALERT_THERM2

原策略/输入：`"read_action=clear unconditional"`

候选：`{"mode_dependent_clear": true, "cause_absent_required": true, "ALERT_service": "master reads sensor address only when flags reset and condition absent", "THERM2_mask": "0x04 latched read-clear only"}`

来源：`[{"pdf_page": 19, "printed_page": 19, "table_or_section": "§8.6.1.3 / Table5 note1", "excerpt": "Only bit 2 (OPEN) stays high"}, {"pdf_page": 19, "printed_page": 19, "table_or_section": "§8.6.1.3", "excerpt": "is not reset by reading the status register."}]`

## PT-TMP461-PAIR-LATCH — TMP461

单次RO读回比较不能验证conversion动态或跨字节配对锁存。

对象：TEMP_LOCAL_HIGH.*, TEMP_LOCAL_LOW.*, TEMP_REMOTE_HIGH.*, TEMP_REMOTE_LOW.*

原策略/输入：`"no paired conversion model"`

候选：`{"dynamic_masks": true, "event_injection": true, "high_then_low_next_read": true, "third_register_read_breaks_pair_guarantee": true}`

来源：`[{"pdf_page": 18, "printed_page": 18, "table_or_section": "§8.6.1.2", "excerpt": "only until another register is read."}]`

## PT-LM83-STATUS-READ — LM83

温度告警读清/输出解除条件与Figure图注粒度存在差异；OPEN缺独立read-clear定义。

对象：SR1.*, SR2.*

原策略/输入：`"no read action / RO snapshots"`

候选：`{"safe_read_clear": "inject alarm, retire fault, freeze conversion, read containing status", "active_fault_postclear_timing": "exclude", "OPEN_readclear": "exclude absent explicit source"}`

来源：`[{"pdf_page": 10, "printed_page": 9, "table_or_section": "§1.2 / §1.3 / Figures4–7", "excerpt": "Status Register Bits are reset by a read"}, {"pdf_page": 12, "printed_page": 11, "table_or_section": "§1.9", "excerpt": "INT, so long as a temperature comparison does not signal a"}]`

## PT-TPS-ALIAS-EVENTS — TPS23861

CoR返回/清零需区分五个alias与完整summary依赖；默认0的事件读0再读0没有非零覆盖。

对象：POWER_EVENT.EV, DETECT_EVENT.EV, FAULT_EVENT.EV, START_EVENT.EV, SUPPLY_EVENT.*, INTERRUPT.FLAGS

原策略/输入：`"all reset snapshots or empty readclear evidence"`

候选：`{"alias_map": {"POWER_EVENT": "0x03", "DETECT_EVENT": "0x05", "FAULT_EVENT": "0x07", "START_EVENT": "0x09", "SUPPLY_EVENT": "0x0B"}, "nonzero_event_injection": true, "clear_returns_preclear_data": true, "summary_recompute": true, "port_off_and_RESP_side_effects": true}`

来源：`[{"pdf_page": 50, "printed_page": 50, "table_or_section": "§7.5.3", "excerpt": "Clear-on-Read command clears all bits"}, {"pdf_page": 66, "printed_page": 66, "table_or_section": "§7.5.19", "excerpt": "CLRAIN clears all event registers"}]`

## PT-TPS-SUPPLY-RESET — TPS23861

原IR把UVLO说成检测未启用，且POR30h不可推广为任何RESET/RESAL都同值。

对象：SUPPLY_EVENT.VDUV, SUPPLY_EVENT.VPUV, SUPPLY_EVENT.TSD

原策略/输入：`"VDUV/VPUV detection not enabled; reset30h"`

候选：`{"POR": "0x30", "UVLO": "supply events", "RESET_pin_and_RESAL": "supply rails explicit"}`

来源：`[{"pdf_page": 54, "printed_page": 54, "table_or_section": "§7.5.7", "excerpt": "VDUV: Indicates that a VDD UVLO occurred."}, {"pdf_page": 66, "printed_page": 66, "table_or_section": "§7.5.19", "excerpt": "follow the state of VDD and VPWR supply rails."}]`

## TPS23861_R17_SOURCE_GRANULARITY_CONFLICT — TPS23861

总览80h与详细Reserved初值粒度冲突保持；ROM1功能是误释。

对象：GENERAL_MASK.RSV3, GENERAL_MASK.RSV2, GENERAL_MASK.ROM1

原策略/输入：`"numeric0 / RO / ROM revision"`

候选：`{"known_reset_mask": "0xF1", "preserve_write_mask": "0x0E", "exclude_access_mask": "0x0E", "source_conflict": "UNRESOLVED", "not_official_erratum": true}`

来源：`[{"pdf_page": 45, "printed_page": 45, "table_or_section": "Table10", "excerpt": "1000,0000"}, {"pdf_page": 63, "printed_page": 63, "table_or_section": "§7.5.16", "excerpt": "Reserved"}]`

## PT-TPS-M250-RESERVED — TPS23861

M250是250mΩ电阻选择，R27高位Reserved非ROM；名称错误可误导生成。

对象：GENERAL_MASK.M250, INTERRUPT_TIMER.ROM

原策略/输入：`"M250 250ms timer / ROM"`

候选：`{"M250": "250/255mohm sense resistor selector", "R27": "reserved reset0 fixed-write0 no illegal-write oracle"}`

来源：`[{"pdf_page": 63, "printed_page": 63, "table_or_section": "§7.5.16", "excerpt": "Current-sense-resistor-selection bit."}, {"pdf_page": 68, "printed_page": 68, "table_or_section": "§7.5.22", "excerpt": "reserved for future use."}]`

## PT-TPS-POEP-AUTO — TPS23861

Auto class识别在power-on前改POEP；普通RW恒持久oracle可能误判正确硬件。

对象：POE_PLUS.POEP

原策略/输入：`"unconditional RW persistence"`

候选：`{"freeze_manual_or_semi_auto_for_storage": true, "Auto_class4_set": true, "Auto_class0_to3_clear": true, "match_ICUT": "functional prerequisite"}`

来源：`[{"pdf_page": 77, "printed_page": 77, "table_or_section": "§7.5.29", "excerpt": "the bit is set when in Auto Mode"}, {"pdf_page": 42, "printed_page": 42, "table_or_section": "§7.4.4", "excerpt": "PoEP fields are set automatically"}]`

## PT-TPS-FIRMWARE-ADDRESS — TPS23861

候选IR地址FEh，原始手册Table10与§7.5.30为41h。

对象：FIRMWARE_REV (no inventory field)

原策略/输入：`"0xFE"`

候选：`{"address": "0x41", "runtime_revision": true, "do_not_fabricate_default": true}`

来源：`[{"pdf_page": 46, "printed_page": 46, "table_or_section": "Table10", "excerpt": "Firmware"}, {"pdf_page": 77, "printed_page": 77, "table_or_section": "§7.5.30", "excerpt": "Command = 41h with 1 Data Byte, Read Only"}]`
