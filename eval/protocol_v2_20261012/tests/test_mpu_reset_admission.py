"""The source-reviewed reset trigger must survive old unverified tier metadata."""
import pytest
from test_policy_regressions import load_harness
from protocol_rules import number


def test_reviewed_mpu_reset_trigger_cannot_be_skipped(monkeypatch):
    harness = load_harness(monkeypatch, 'MPU6050')
    assert harness.CONTRACT.applicable()['test_write_trigger_fields']
    assert not harness.CONTRACT.excluded_field('PWR_MGMT_1.DEVICE_RESET')

    class StoreWithoutReset:
        def __init__(self):
            self.regs = {number(r['addr']): number(r.get('reset', '0x0'))
                         for r in harness.REGS.values()}
        def read_register(self, addr, nbytes=2):
            return self.regs[addr]
        def write_register(self, addr, data, nbytes=2):
            self.regs[addr] = data

    with pytest.raises(AssertionError, match='DEVICE_RESET'):
        harness.test_write_trigger_fields(StoreWithoutReset)
