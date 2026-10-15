"""Run provisional candidate IRs against the frozen black-box harness.

The runner constructs an isolated sandbox under ``_setup/candidate_runs``;
formal ``d2d/ir`` and ``d2d/rtl`` files are never modified.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DRAFTS = ROOT / "_setup" / "ir_drafts"
SIMS = ROOT / "_setup" / "candidate_rtl"
RUN_ROOT = ROOT / "_setup" / "candidate_runs"
HARNESS = ROOT / "d2d" / "eval" / "test_d2d_blackbox.py"
BASE_SENSOR = ROOT / "d2d" / "rtl" / "base_sensor.py"

CHIPS = ("AD5592R", "LIS3DH", "MPU6050")


def run_one(chip: str) -> dict:
    run_dir = RUN_ROOT / chip
    if run_dir.exists():
        shutil.rmtree(run_dir)
    (run_dir / "d2d" / "ir").mkdir(parents=True)
    (run_dir / "d2d" / "eval").mkdir(parents=True)
    (run_dir / "d2d" / "rtl").mkdir(parents=True)

    draft = DRAFTS / f"{chip}_draft_ir.json"
    json.loads(draft.read_text(encoding="utf-8"))
    shutil.copy2(draft, run_dir / "d2d" / "ir" / f"{chip}_gold_ir.json")
    shutil.copy2(HARNESS, run_dir / "d2d" / "eval" / "test_d2d_blackbox.py")
    shutil.copy2(BASE_SENSOR, run_dir / "d2d" / "rtl" / "base_sensor.py")
    shutil.copy2(SIMS / f"{chip.lower()}_simulator.py", run_dir / "d2d" / "eval" / f"{chip.lower()}_simulator.py")

    env = dict(os.environ, D2D_IR=f"{chip}_gold_ir.json", PYTHONIOENCODING="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "test_d2d_blackbox.py", "-q", "--no-header"],
        cwd=run_dir / "d2d" / "eval",
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    log = run_dir / "pytest.log"
    log.write_text(result.stdout + ("\n" + result.stderr if result.stderr else ""), encoding="utf-8")
    passed = result.returncode == 0 and " failed" not in result.stdout
    return {"chip": chip, "passed": passed, "returncode": result.returncode, "log": str(log), "tail": result.stdout.strip().splitlines()[-1:]}


def main() -> int:
    RUN_ROOT.mkdir(parents=True, exist_ok=True)
    results = [run_one(chip) for chip in CHIPS]
    (RUN_ROOT / "summary.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    for item in results:
        print(f"{item['chip']}: {'PASS' if item['passed'] else 'FAIL'}; log={item['log']}")
    return 0 if all(item["passed"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
