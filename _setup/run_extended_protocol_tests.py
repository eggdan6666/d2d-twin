"""Run the non-frozen protocol/stateful software tests."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent / "extended_eval"
result = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=root, text=True)
raise SystemExit(result.returncode)
