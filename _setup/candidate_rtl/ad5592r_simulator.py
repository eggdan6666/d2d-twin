"""AD5592R candidate simulator for the provisional IR admission run.

The direct-register candidate contract treats the AD5592R control selector as
the address argument. SPI wire framing, timing, and DAC/ADC readback payloads
remain outside this sandbox, as recorded in the draft IR.
"""
from base_sensor import BaseVirtualSensor


class AD5592R_Simulator(BaseVirtualSensor):
    RESET = {
        0x1: 0x0000,
        0x2: 0x0000,
        0x3: 0x0000,
        0x4: 0x0000,
        0x5: 0x0000,
        0x6: 0x00FF,
        0xF: 0x0000,
    }

    def __init__(self):
        super().__init__()
        self.regs = dict(self.RESET)

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        value = self.regs.get(addr, 0) & 0xFFFF
        return ((value >> 8) & 0xFF) if nbytes == 1 else value

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        if addr == 0xF:
            if (data & 0x7FF) == 0x5AC:
                self.regs = dict(self.RESET)
            return
        if addr not in self.regs:
            return
        if nbytes == 1:
            data = ((data & 0xFF) << 8) | (self.regs[addr] & 0xFF)
        self.regs[addr] = data & 0xFFFF
