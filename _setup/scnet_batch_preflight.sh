#!/bin/bash
# Read-only HPC migration preflight. No model download or inference.
set -u
TASK_HOME=/public/home/lct3086708928
echo '=== HOST / WORKDIR ==='
hostname
pwd
echo '=== EXISTING DATA ==='
for p in "$TASK_HOME/d2d" "$TASK_HOME/models" /root/private_data/d2d; do
  if [ -d "$p" ]; then
    ls -ld "$p"
    if [ -d "$p/eval" ]; then
      for f in "$p"/eval/results_gen_qwen14b_*.json; do
        [ -f "$f" ] || continue
        ls -lh "$f"
      done
    fi
  fi
done
echo '=== PYTHON / CONTAINER TOOLS ==='
for name in python3 python conda singularity apptainer; do
  command -v "$name" || true
done
ls -l /opt/conda/bin/python 2>/dev/null || true
echo '=== AVAILABLE MODULES ==='
if type module >/dev/null 2>&1; then
  module -t avail 2>&1 | head -60
fi
echo '=== PREFLIGHT DONE: NO INFERENCE WAS STARTED ==='
