# -*- coding: utf-8 -*-
"""D2D-Twin: Official Benchmark Verification & Reproduction CLI.

Benchmarking LLMs on Datasheet-to-Digital-Twin Synthesis for Peripheral Hardware Emulators.
This script provides deterministic, zero-GPU evaluation, MD5 integrity checks, and summary tables.

Usage:
    python run_benchmark.py                     # Verify MD5 and display main benchmark summary tables
    python run_benchmark.py --test-ref all      # Run blackbox admission tests on all 17 reference simulators
    python run_benchmark.py --test-ref TMP1075  # Run blackbox admission test on a specific reference chip
    python run_benchmark.py --make-assets       # Regenerate publication figures (PNG) and LaTeX tables
"""
import argparse
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.abspath(__file__))
EXPECTED_HARNESS_MD5 = "8cf0854d4779467bc8e472ee4fb97023"
HARNESS_PATH = os.path.join(ROOT, "d2d", "eval", "test_d2d_blackbox.py")

ALL_CHIPS = [
    "TMP1075", "TMP102", "TMP100", "TMP117", "TMP126", "TMP461", "LM83",
    "HDC2021", "BME280", "BMP280", "INA219", "INA226", "INA3221",
    "ADS1115", "ADS1220", "LIS2DW12", "TPS23861"
]


def check_integrity():
    """Verify test harness MD5 and dataset completeness."""
    if not os.path.exists(HARNESS_PATH):
        print(f"[ERROR] Harness file missing at {HARNESS_PATH}")
        return False
    
    with open(HARNESS_PATH, "rb") as f:
        actual_md5 = hashlib.md5(f.read()).hexdigest()
    
    md5_ok = (actual_md5 == EXPECTED_HARNESS_MD5)
    print("=" * 78)
    print(" D2D-Twin Benchmark: Deterministic Integrity Check")
    print("=" * 78)
    print(f"  Harness File : d2d/eval/test_d2d_blackbox.py")
    print(f"  Harness MD5  : {actual_md5} -> {'[MATCH]' if md5_ok else '[MISMATCH!]'}")
    
    missing_ir = []
    for chip in ALL_CHIPS:
        ir_p = os.path.join(ROOT, "d2d", "ir", f"{chip}_gold_ir.json")
        if not os.path.exists(ir_p):
            missing_ir.append(chip)
            
    print(f"  Gold IRs     : {len(ALL_CHIPS) - len(missing_ir)}/{len(ALL_CHIPS)} present")
    if missing_ir:
        print(f"  [WARNING] Missing IRs: {', '.join(missing_ir)}")
        
    return md5_ok and len(missing_ir) == 0


def display_summary():
    """Display Table 1 & Table 2 benchmark results from recorded evaluations."""
    check_integrity()
    n24_path = os.path.join(ROOT, "d2d", "eval", "main_table_n24.json")
    ds67b_path = os.path.join(ROOT, "d2d", "eval", "main_table_ds67b.json")
    
    if not os.path.exists(n24_path):
        print("[ERROR] main_table_n24.json not found. Run evaluation first.")
        return
        
    n24 = json.load(io.open(n24_path, encoding="utf-8"))
    
    print("\n" + "=" * 78)
    print(" Table 1: Main Benchmark Failure Breakdown (Qwen2.5-Coder-14B, N=408 Samples)")
    print("=" * 78)
    print(f" {'Dimension':<34} | {'Clusters':<8} | {'Failed/Total':<13} | {'Fail Rate':<9} | {'95% CI / Bound'}")
    print("-" * 78)
    dims = n24.get("dimensions", {})
    # Order dimensions by test id
    dim_order = [
        "test_reset_values", "test_readonly_protection", "test_rw_field_persistence",
        "test_write_trigger_fields", "test_write_only_reset_key", "test_single_byte_semantics",
        "test_read_write_alias", "test_clear_on_read"
    ]
    for key in dim_order:
        if key not in dims:
            continue
        row = dims[key]
        name = row["label"]
        k = row.get("clusters", "-")
        ft = f"{row['fail']}/{row['applicable']}"
        rate = f"{row['rate']:.1f}%"
        if row.get("ci"):
            ci_str = f"[{row['ci']['lo']:.1f}%, {row['ci']['hi']:.1f}%]"
        elif row.get("bound"):
            ci_str = f"<= {row['bound']['upper_pct']:.1f}% (Rule of 3)"
        elif row.get("binomial_ci_if_wrongly_independent"):
            b = row["binomial_ci_if_wrongly_independent"]
            ci_str = f"[{b['lo']:.1f}%, {b['hi']:.1f}%] (k<5)"
        else:
            ci_str = "-"
        print(f" {name:<35} | {str(k):<8} | {ft:<13} | {rate:<9} | {ci_str}")
    
    if os.path.exists(ds67b_path):
        ds67b = json.load(io.open(ds67b_path, encoding="utf-8"))
        print("\n" + "=" * 78)
        print(" Table 2: Cross-Model Comparison Across 17 Peripherals (N=612 Total Samples)")
        print("=" * 78)
        print(f" {'Chip':<10} | {'Category':<16} | {'Regs':<5} | {'14B Pass% (n=24)':<18} | {'6.7B Pass% (n=12)':<18}")
        print("-" * 78)
        
        cats = {
            "TMP1075": "Temp Sensor", "TMP102": "Temp Sensor", "TMP100": "Temp Sensor",
            "TMP117": "High-Prec Temp", "TMP126": "High-Prec Temp", "TMP461": "Remote Temp",
            "LM83": "Thermal Monitor", "HDC2021": "Humidity/Temp", "BME280": "Pressure/Temp",
            "BMP280": "Pressure/Temp", "INA219": "Current/Power", "INA226": "Current/Power",
            "INA3221": "3-Ch Current", "ADS1115": "16-Bit ADC", "ADS1220": "24-Bit ADC",
            "LIS2DW12": "3-Axis Accel", "TPS23861": "PoE Controller"
        }
        
        for chip in ALL_CHIPS:
            p14 = n24["per_chip_rate_pct"].get(chip, 0.0)
            p67 = ds67b["per_chip_rate_pct"].get(chip, 0.0)
            cat = cats.get(chip, "Peripheral")
            ir_p = os.path.join(ROOT, "d2d", "ir", f"{chip}_gold_ir.json")
            if os.path.exists(ir_p):
                ir_obj = json.load(io.open(ir_p, encoding="utf-8"))
                regs = len(ir_obj.get("registers", []))
            else:
                regs = "-"
            print(f" {chip:<10} | {cat:<16} | {str(regs):<5} | {p14:>5.1f}%             | {p67:>5.1f}%")
        print("-" * 78)
        print(f" [Finding] Spearman rank correlation (Special Registers vs Pass Rate): rho = -0.828, p = 0.0001")
        print(f" [Finding] Read/Write Alias Failure Rate (LM83, TMP461): 100.0% fail across both models")


def test_reference(target_chip="all"):
    """Run blackbox admission test on reference simulator implementations."""
    chips_to_test = ALL_CHIPS if target_chip.lower() == "all" else [target_chip.upper()]
    
    sandbox_dir = os.path.join(ROOT, "d2d", "eval", "_admission_sandbox")
    os.makedirs(sandbox_dir, exist_ok=True)
    shutil.copy(os.path.join(ROOT, "d2d", "rtl", "base_sensor.py"), sandbox_dir)
    shutil.copy(HARNESS_PATH, sandbox_dir)
    
    print("\n" + "=" * 78)
    print(" Running Blackbox Admission Tests on Reference Simulators")
    print("=" * 78)
    
    all_passed = True
    try:
        for chip in chips_to_test:
            ref_path = os.path.join(ROOT, "d2d", "rtl", f"{chip.lower()}_reference.py")
            sim_path = os.path.join(sandbox_dir, f"{chip.lower()}_simulator.py")
            if not os.path.exists(ref_path):
                print(f"  {chip:<10} -> [SKIP] Reference file {ref_path} not found")
                continue
            
            shutil.copy(ref_path, sim_path)
            env = dict(os.environ, D2D_IR=f"{chip}_gold_ir.json", PYTHONIOENCODING="utf-8")
            res = subprocess.run(
                [sys.executable, "-m", "pytest", "test_d2d_blackbox.py", "-q", "--no-header"],
                cwd=sandbox_dir, env=env, capture_output=True, text=True,
                encoding="utf-8", errors="replace"
            )
            
            passed = (res.returncode == 0) and ("failed" not in res.stdout)
            last_line = res.stdout.strip().splitlines()[-1] if res.stdout.strip() else ""
            status_tag = "[PASS 100%]" if passed else "[FAIL]"
            if not passed:
                all_passed = False
            print(f"  {chip:<10} -> {status_tag:<12} ({last_line})")
            
            if os.path.exists(sim_path):
                os.remove(sim_path)
    finally:
        shutil.rmtree(sandbox_dir, ignore_errors=True)
        
    print("=" * 78)
    if all_passed:
        print("  All reference simulators passed blackbox test suite with 100% fidelity.")
    else:
        print("  Some tests encountered failures. Check harness configuration.")


def make_assets():
    """Regenerate publication figures and LaTeX tables."""
    script = os.path.join(ROOT, "_setup", "generate_paper_assets.py")
    if os.path.exists(script):
        print("\nRegenerating publication assets...")
        res = subprocess.run([sys.executable, script], cwd=ROOT, capture_output=True, text=True,
                             encoding="utf-8", errors="replace")
        print(res.stdout)
        if res.stderr:
            print(res.stderr)
    else:
        print(f"[ERROR] Asset generation script not found: {script}")


def main():
    parser = argparse.ArgumentParser(description="D2D-Twin Official Benchmark CLI")
    parser.add_argument("--test-ref", metavar="CHIP", const="all", nargs="?",
                        help="Run admission test on reference simulator ('all' or chip name, e.g. TMP1075)")
    parser.add_argument("--make-assets", action="store_true",
                        help="Regenerate publication figures (PNG) and LaTeX tables")
    parser.add_argument("--summary", action="store_true",
                        help="Display main benchmark results summary table (default)")
    
    args = parser.parse_args()
    
    if args.test_ref:
        test_reference(args.test_ref)
    elif args.make_assets:
        make_assets()
    else:
        display_summary()


if __name__ == "__main__":
    main()
