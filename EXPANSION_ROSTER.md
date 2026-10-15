# D2D-Twin 芯片扩展清单（v1）

本清单从 `corpus/data/raw_pdf/` 已存在的真实 Datasheet 中筛选，不把没有寄存器总线的纯模拟器件直接纳入 Gold IR。当前 `d2d/ir/` 已正式收录 20 颗芯片：原始 17 颗 baseline，加上 AD5592R、LIS3DH、MPU6050 三颗扩展；第一轮扩展优先修复厂商偏斜。

## 已正式纳入的第一批扩展

| 芯片 | Gold IR | 参考 simulator | 寄存器级 admission | 协议扩展 |
|---|---|---|---|---|
| AD5592R | `d2d/ir/AD5592R_gold_ir.json` | `d2d/rtl/ad5592r_reference.py` | PASS | SPI 软件模型通过 |
| LIS3DH | `d2d/ir/LIS3DH_gold_ir.json` | `d2d/rtl/lis3dh_reference.py` | PASS | I²C 软件模型通过 |
| MPU6050 | `d2d/ir/MPU6050_gold_ir.json` | `d2d/rtl/mpu6050_reference.py` | PASS | I²C 软件模型通过 |

正式纳入日期：2026-10-10。协议扩展是补充证据，尚未进行实物电气测量。

## 第一轮新增 15 颗

| 优先级 | 芯片 | 厂商 | 原始 PDF | 预期覆盖 |
|---:|---|---|---|---|
| P0 | AD5592R | ADI | `corpus/data/raw_pdf/ADI/ad5592r.pdf` | 多通道 ADC/DAC、地址/字段掩码 |
| P0 | LIS3DH | ST | `corpus/data/raw_pdf/ST/LIS3DH.pdf` | 传感器状态位、FIFO、读清除候选 |
| P0 | LSM6DSO | ST | `corpus/data/raw_pdf/ST/LSM6DSO.pdf` | 多寄存器控制、状态与复位 |
| P0 | M24C64-W | ST | `corpus/data/raw_pdf/ST/m24c64-w.pdf` | I2C EEPROM、页写/地址语义 |
| P0 | MPU6050 | InvenSense | `corpus/data/raw_pdf/InvenSense/MPU6050.pdf` | 多 bank 寄存器、状态位 |
| P0 | MPU9250 | InvenSense | `corpus/data/raw_pdf/InvenSense/MPU9250.pdf` | 传感器配置与复合状态 |
| P0 | ICM20948 | InvenSense | `corpus/data/raw_pdf/InvenSense/ICM20948.pdf` | bank/分页地址、复杂字段 |
| P0 | W25Q32 | Winbond | `corpus/data/raw_pdf/Winbond/W25Q32.pdf` | SPI Flash 状态/写保护 |
| P0 | W25Q64 | Winbond | `corpus/data/raw_pdf/Winbond/W25Q64.pdf` | SPI Flash 状态/写使能 |
| P0 | W25Q128 | Winbond | `corpus/data/raw_pdf/Winbond/W25Q128.pdf` | SPI Flash 状态/地址宽度 |
| P0 | GD25Q64E | GigaDevice | `corpus/data/raw_pdf/GigaDevice/GD25Q64E.pdf` | 跨厂商 Flash 对照 |
| P0 | SC8815 | Southchip | `corpus/data/raw_pdf/Southchip/SC8815.pdf` | 电源管理寄存器与写触发 |
| P0 | SC89601 | Southchip | `corpus/data/raw_pdf/Southchip/SC89601.pdf` | 电源管理字段/状态 |
| P1 | ADS1015 | TI | `corpus/data/raw_pdf/TI/ADS1015.pdf` | ADC 配置、比较器、读写字段 |
| P1 | INA228 | TI | `corpus/data/raw_pdf/TI/INA228.pdf` | 电源监控、校准与状态 |

纳入前仍需逐颗确认：PDF 明确给出数字寄存器或命令字、访问权限可判定、复位/运行时语义有原文依据，并能构造 `read_register/write_register` 黑盒契约。纯模拟器件、只有 AT 命令而没有寄存器映射的 modem、以及没有清晰边界的整颗 MCU 暂不纳入第一轮。

## 目标规模与统计设计

- 当前 17 颗作为 pilot；加入本清单后为 32 颗，若保持 Qwen `n=24` 与 DeepSeek `n=12`，总量为 `32 x 36 = 1,152` 次。
- 每颗芯片保存 PDF 版本、页码/表格 provenance、Gold IR、参考模拟器和适用维度向量；参考模拟器必须先通过冻结 harness。
- 按芯片家族和厂商做留出划分，不能把同一系列的近邻型号随机拆到 train/test 两侧。
- 对 D6/D6s/D7/D8 等稀有语义设置最低覆盖目标；不能只增加普通的 reset/RW 寄存器。
- 报告芯片级和断言级两套结果，置信区间按芯片簇或厂商分层 bootstrap；seed 只作为模型随机性，不当作新的独立芯片。

## Gold IR 审核门槛

1. 一名主标注者从 PDF 原文建立 IR，并记录页码、表号和字段原文。
2. 第二名审核者独立复核地址、访问权限、复位值、别名和特殊动作。
3. 争议进入 adjudication 表；没有原文支持的行为标为 `UNSPEC` 或排除，不强行补约定。
4. 参考模拟器通过 8 维 harness 后，芯片才进入模型评测集。
5. 先固定留出清单，再生成模型代码，避免依据结果挑选芯片。

## 第二轮候选

第一轮完成后，再从 `ST/LSM6DSL.pdf`、`Espressif/ESP32-C3.pdf`、`Microchip/ATmega328P.pdf` 和更多 TI ADC/电源器件中选择，但必须先定义可评测的寄存器子集；整颗 SoC/MCU 若边界不清，会把规模增加变成标签噪声。
