"""LIS3DH candidate simulator for the provisional IR admission run."""
from base_sensor import BaseVirtualSensor


class LIS3DH_Simulator(BaseVirtualSensor):
    RESET = {
        0x0F: 0x33,
        0x1E: 0x10,
        0x1F: 0x00,
        0x20: 0x07,
        0x23: 0x00,
        0x27: 0x00,
        0x28: 0x00,
        0x29: 0x00,
        0x2A: 0x00,
        0x2B: 0x00,
        0x2C: 0x00,
        0x2D: 0x00,
    }
    RO = {0x0F, 0x27, 0x28, 0x29, 0x2A, 0x2B, 0x2C, 0x2D}

    def __init__(self):
        super().__init__()
        self.regs = dict(self.RESET)

    def read_register(self, addr: int, nbytes: int = 2) -> int:
        value = self.regs.get(addr, 0) & 0xFF
        return value if nbytes != 1 else value

    def write_register(self, addr: int, data: int, nbytes: int = 2) -> None:
        if addr in self.RO or addr not in self.regs:
            return
        self.regs[addr] = data & 0xFF
