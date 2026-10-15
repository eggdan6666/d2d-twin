from base_sensor import BaseVirtualSensor

class LM83_Simulator(BaseVirtualSensor):
    def __init__(self):
        super().__init__()
        self.regs = {
            0x00: 0x0,
            0x01: 0x0,
            0x02: 0x0,
            0x03: 0x0,
            0x05: 0x7F,
            0x07: 0x7F,
            0x30: 0x0,
            0x31: 0x0,
            0x35: 0x0,
            0x38: 0x7F,
            0x3A: 0x7F,
            0x42: 0x7F,
            0xFE: 0x1,
            0xFF: 0x0,
        }
        self._ro_addrs = [0, 1, 2, 48, 49, 53, 254, 255]
        self._write_to_read = {9: 3, 11: 5, 13: 7, 80: 56, 82: 58, 90: 66}
        self._aliased_reads = [3, 5, 7, 56, 58, 66]
        self._writable_masks = {3: 190, 5: 255, 7: 255, 56: 255, 58: 255, 66: 255}
        self._read_as = {}

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        if addr not in self.regs:
            return 0
        value = self.regs[addr] & 0xff
        for field_mask, forced in self._read_as.get(addr, []):
            value = (value & ~field_mask) | (forced & field_mask)
        if nbytes == 1:
            return ((value >> 8) & 0xFF) if 8 > 8 else (value & 0xFF)
        return value

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        if addr in self._aliased_reads:
            return
        addr = self._write_to_read.get(addr, addr)
        if addr not in self.regs or addr in self._ro_addrs:
            return
        writable = self._writable_masks.get(addr, 0xff)
        if nbytes == 1 and 8 > 8:
            value = ((data & 0xFF) << 8) | (self.regs[addr] & 0xFF)
        else:
            value = data & 0xFF if nbytes == 1 else data & 0xff
        self.regs[addr] = ((self.regs[addr] & ~writable) | (value & writable)) & 0xff
