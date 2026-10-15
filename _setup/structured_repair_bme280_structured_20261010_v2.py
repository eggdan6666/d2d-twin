from base_sensor import BaseVirtualSensor

class BME280_Simulator(BaseVirtualSensor):
    def __init__(self):
        super().__init__()
        self.regs = {
            0xD0: 0x60,
            0xE0: 0x0,
            0xF2: 0x0,
            0xF3: 0x0,
            0xF4: 0x0,
            0xF5: 0x0,
            0xF7: 0x80,
            0xF8: 0x0,
            0xF9: 0x0,
            0xFA: 0x80,
            0xFB: 0x0,
            0xFC: 0x0,
            0xFD: 0x80,
            0xFE: 0x0,
        }
        self._ro_addrs = [208, 243, 247, 248, 249, 250, 251, 252, 253, 254]
        self._write_to_read = {}
        self._aliased_reads = []
        self._writable_masks = {242: 7, 244: 255, 245: 255}
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
