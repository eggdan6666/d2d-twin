from base_sensor import BaseVirtualSensor

class ADS1115_Simulator(BaseVirtualSensor):
    def __init__(self):
        super().__init__()
        self.regs = {
            0x00: 0x0,
            0x01: 0x8583,
            0x02: 0x8000,
            0x03: 0x7FFF,
        }
        self._ro_addrs = [0]
        self._write_to_read = {}
        self._aliased_reads = []
        self._writable_masks = {1: 65535, 2: 65535, 3: 65535}
        self._read_as = {}

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        if addr not in self.regs:
            return 0
        value = self.regs[addr] & 0xffff
        for field_mask, forced in self._read_as.get(addr, []):
            value = (value & ~field_mask) | (forced & field_mask)
        if nbytes == 1:
            return ((value >> 8) & 0xFF) if 16 > 8 else (value & 0xFF)
        return value

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        if addr in self._aliased_reads:
            return
        addr = self._write_to_read.get(addr, addr)
        if addr not in self.regs or addr in self._ro_addrs:
            return
        writable = self._writable_masks.get(addr, 0xffff)
        if nbytes == 1 and 16 > 8:
            value = ((data & 0xFF) << 8) | (self.regs[addr] & 0xFF)
        else:
            value = data & 0xFF if nbytes == 1 else data & 0xffff
        self.regs[addr] = ((self.regs[addr] & ~writable) | (value & writable)) & 0xffff
