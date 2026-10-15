from spi_models import AD5592RSPI


def word(value):
    return bytes([(value >> 8) & 0xFF, value & 0xFF])


def test_ad5592r_power_up_guard_and_control_selector():
    dev = AD5592RSPI()
    try:
        dev.spi_transfer(word((0x2 << 11) | 0x100))
    except RuntimeError:
        pass
    else:
        raise AssertionError("writes during the 250 us power-up interval must fail")
    dev.advance_time_us(250)
    dev.spi_transfer(word((0x2 << 11) | 0x100))
    assert dev.regs[0x2] == 0x100


def test_ad5592r_reserved_bits_are_forced_zero():
    dev = AD5592RSPI()
    dev.advance_time_us(250)
    dev.spi_transfer(word((0x2 << 11) | 0x700))
    assert dev.regs[0x2] == 0x100


def test_ad5592r_readback_uses_following_16_clocks():
    dev = AD5592RSPI()
    dev.advance_time_us(250)
    dev.spi_transfer(word((0x6 << 11) | 0x055))
    selector_payload = (1 << 6) | (0x6 << 2)
    dev.spi_transfer(word((0x7 << 11) | selector_payload))
    assert dev.spi_transfer(b"\x00\x00") == b"\x00U"


def test_ad5592r_software_reset_key_and_io_lock():
    dev = AD5592RSPI()
    dev.advance_time_us(250)
    dev.spi_transfer(word((0x3 << 11) | (1 << 7)))
    dev.spi_transfer(word((0x4 << 11) | 0x155))
    assert dev.regs[0x4] == 0
    dev.spi_transfer(word((0xF << 11) | 0x5AC))
    assert dev.regs[0x6] == 0xFF
    assert not dev.io_locked


def test_ad5592r_dac_word_uses_bit15_mode():
    dev = AD5592RSPI()
    dev.advance_time_us(250)
    dev.spi_transfer(word(0x8000 | (3 << 12) | 0x321))
    assert dev.last_dac_write == (3, 0x321)
