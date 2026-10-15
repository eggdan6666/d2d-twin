LIS3DH: PASS

- 核对结果：
  - `STATUS_REG` 已删除静态 `reset=0x00`，保留 `runtime_value=true`，并设置 `reset_policy=UNSPECIFIED_RUNTIME_OUTPUT`。
  - `OUT_X/Y/Z_L/H` 均无静态 reset，保留 `runtime_value=true`。
  - `OUT_*` 的 `DATA` 字段均省略静态 reset。
  - `CTRL_REG1.ODR` 明确允许 `0x0–0x9`，并将 `0xA–0xF` 标记为 unsupported 且 excluded from scoring。
- PDF 页码：
  - 地址映射及动态输出：第 31 页。
  - ODR 编码：第 35 页。
  - `STATUS_REG` 默认状态位：第 39 页。
  - `OUT_X/Y/Z_L/H` 动态输出：第 40 页。
- 若 REPAIR，给出准确修改内容：无。
- 允许进入下一步 simulator/benchmark 集成。

MPU6050: PASS

- 核对结果：
  - `CONFIG[7:6]`、`GYRO_CONFIG[2:0]`、`ACCEL_CONFIG[2:0]`、`PWR_MGMT_1[4]` 均为 `UNSPEC`、`reset=0`。
  - `DEVICE_RESET` 说明已指向寄存器图第 40–41 页。
  - 已记录 I²C 写入、读取、重复 START、ACK/NACK、STOP 和 burst auto-increment 元数据。
  - `spi_supported=false`，明确 MPU6050 不使用 MPU6000 的 SPI 主协议。
  - 本地镜像对应 `RM-MPU-6000A-00 Revision 4.2`，SHA-256 为 `519650CBC502A3E89DDBA6D6F115734B6C7060D451938C0DC36B6232DAAE7014`。
- PDF 页码：
  - 保留位及寄存器映射：第 6、8、13–15、40 页。
  - `DEVICE_RESET` 语义：第 40–41 页。
  - 镜像身份：第 1、4 页。
  - I²C/SPI 协议：`MPU6050.pdf` 第 33、35–37 页。
- 若 REPAIR，给出准确修改内容：无。
- 允许进入下一步 simulator/benchmark 集成。

最终结论：

- **两者均 PASS。**
- 本次未修改正式 Gold IR 或冻结测试文件。
