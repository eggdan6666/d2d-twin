"""MPU6050 candidate simulator for the provisional IR admission run."""
from base_sensor import BaseVirtualSensor


class MPU6050_Simulator(BaseVirtualSensor):
    RESET = {
        0x19: 0x00,
        0x1A: 0x00,
        0x1B: 0x00,
        0x1C: 0x00,
        0x3B: 0x00,
        0x3C: 0x00,
        0x3D: 0x00,
        0x3E: 0x00,
        0x3F: 0x00,
        0x40: 0x00,
        0x6B: 0x40,
        0x75: 0x68,
    }
    RO = {0x3B, 0x3C, 0x3D, 0x3E, 0x3F, 0x40, 0x75}

    def __init__(self):
        super().__init__()
        self.regs = dict(self.RESET)

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        value = self.regs.get(addr, 0) & 0xFF
        return value if nbytes != 1 else value

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        if addr in self.RO or addr not in self.regs:
            return
        data &= 0xFF
        if addr == 0x6B and (data & 0x80):
            self.regs = dict(self.RESET)
            return
        self.regs[addr] = data
