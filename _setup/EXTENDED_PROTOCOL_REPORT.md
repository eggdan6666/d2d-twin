# Extended I2C protocol test report

Date: 2026-10-10  
Command: `python _setup/run_extended_protocol_tests.py`  
Result: **10 passed**

## Covered behavior

- LIS3DH I2C address selection (`0x18`/`0x19`) and NACK for an invalid address.
- LIS3DH sub-address auto-increment for multi-byte reads/writes.
- LIS3DH BDU output-pair freezing and BLE byte order.
- LIS3DH rejection of undocumented ODR encodings `0xA`–`0xF`.
- MPU6050 I2C read transaction sequence with repeated START and final NACK.
- MPU6050 burst register auto-increment.
- MPU6050 `DEVICE_RESET` restoring register defaults.
- AD5592R 250 μs power-up guard and 16-bit control selector.
- AD5592R reserved bits 10:9 forced to zero for ordinary control writes.
- AD5592R two-phase readback using the following 16 clocks.
- AD5592R software-reset key `0x5AC`, `IO_LOCK`, and bit-15 DAC-write mode.

The implementation is a deterministic software protocol model in `_setup/extended_eval/i2c_models.py`; it does not require a physical board. It does not claim electrical-level validation, sensor noise validation, or timing validation against silicon. Those require optional hardware measurements.

The original frozen benchmark remains unchanged: `d2d/eval/test_d2d_blackbox.py` and the 17-chip Gold IR roster were not modified.
