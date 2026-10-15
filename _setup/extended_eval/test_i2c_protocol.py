from i2c_models import LIS3DHI2C, MPU6050I2C


def test_lis3dh_i2c_address_and_auto_increment():
    dev = LIS3DHI2C()
    dev.i2c_write(0x18, 0x80 | 0x20, [0x27, 0x07])
    assert dev.i2c_read(0x18, 0x80 | 0x20, 2) == bytes([0x27, 0x07])
    try:
        dev.i2c_read(0x1A, 0x0F, 1)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid LIS3DH address must NACK")


def test_lis3dh_bdu_and_ble_output_pair():
    dev = LIS3DHI2C()
    dev.set_sample(0x1122, 0x3344, 0x5566)
    assert dev.i2c_read(0x18, 0x80 | 0x28, 6) == bytes([0x22, 0x11, 0x44, 0x33, 0x66, 0x55])
    dev.i2c_write(0x18, 0x23, [0x80 | 0x40])
    dev.set_sample(0x7788, 0x99AA, 0xBBCC)
    assert dev.i2c_read(0x18, 0x80 | 0x28, 6) == bytes([0x11, 0x22, 0x33, 0x44, 0x55, 0x66])


def test_lis3dh_rejects_unsupported_odr():
    dev = LIS3DHI2C()
    try:
        dev.i2c_write(0x18, 0x20, [0xA0])
    except ValueError:
        pass
    else:
        raise AssertionError("ODR 0xA must be rejected")


def test_mpu6050_i2c_frame_and_burst_increment():
    dev = MPU6050I2C()
    data = dev.i2c_read(0x68, 0x75, 1)
    assert data == bytes([0x68])
    assert dev.last_transaction == ["START", "AD+W", "ACK", "RA", "ACK", "REPEATED_START", "AD+R", "ACK", "DATA", "NACK", "STOP"]
    dev.i2c_write(0x68, 0x19, [0x12, 0x34])
    assert dev.regs[0x19] == 0x12
    assert dev.regs[0x1A] == 0x34


def test_mpu6050_device_reset_restores_registers():
    dev = MPU6050I2C()
    dev.i2c_write(0x68, 0x19, [0x55])
    dev.i2c_write(0x68, 0x6B, [0x80])
    assert dev.regs[0x19] == 0x00
    assert dev.regs[0x6B] == 0x40
