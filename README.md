# D2D-Twin: Benchmarking LLMs on Datasheet-to-Digital-Twin Synthesis for Register-Level Peripheral Emulators

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg" alt="Python"></a>
  <a href="DATASET.md"><img src="https://img.shields.io/badge/Chips-17_ICs-orange.svg" alt="Benchmark Suite"></a>
  <a href="d2d/eval/"><img src="https://img.shields.io/badge/Eval_Runs-612_Samples-purple.svg" alt="Evaluated Runs"></a>
  <a href="d2d/eval/test_d2d_blackbox.py"><img src="https://img.shields.io/badge/Pytest_MD5-8cf0854d-success.svg" alt="Harness MD5"></a>
  <a href="README_zh.md"><img src="https://img.shields.io/badge/Doc-%E4%B8%AD%E6%96%87%E8%AF%B4%E6%98%8E-red.svg" alt="Chinese Doc"></a>
</p>

> **Deterministic, Zero-LLM-as-a-Judge Evaluation Benchmark for Code LLMs on Hardware Virtual Prototyping.**  
> Evaluated across **17 representative peripheral ICs**, **612 synthesized code models**, and **8 behavioral specification dimensions**.

---

## 📌 News & Highlights

- **[2026-10-08] Full 17-Chip Grand Slam Released**: 408 code samples for Qwen2.5-Coder-14B ($n=24$ per chip) and 204 code samples for DeepSeek-Coder-6.7B ($n=12$ per chip), totaling 612 samples fully evaluated.
- **[2026-10-08] Zero LLM-as-a-Judge**: All evaluations are driven strictly by blackbox `pytest` total bus stimulus injection and state assertions (`MD5: 8cf0854d4779467bc8e472ee4fb97023`).
- **[2026-10-08] Clean Q1c Ablation Completed**: Proved that reset value transcribing is a structural fidelity measure rather than semantic reasoning (failure rate collapses from 0% to 75%–100% when reset keys are scrubbed).
- **[2026-10-08] Reproduce in 1 Second (Zero GPU)**: All evaluations, tables, and publication assets can be reproduced offline on CPU in seconds via `python run_benchmark.py`.

---

## 🔍 Key Scientific Discoveries

```
[Datasheet PDF] ──> [Gold IR (JSON)] ──> [LLM (14B / 6.7B)] ──> [Python Emulator]
                                                                        │
[Universal Testbench (MD5: 8cf0854d)] ─────────────────────────────────▼
                                                       [Deterministic Pytest Assertions]
```

1. **Sub-register Bitfield Persistence Deficit**:
   - Current Code LLMs predominantly model hardware registers as monolithic integers (`self.regs[addr] = val`).
   - When writing to partial bitfields, models accidentally overwrite neighboring read-only or reserved bits, yielding a **49.2% failure rate in RO protection** and **71.1% failure rate in bitfield persistence** (with 47.5% confirmed as pure bitwise logic defects).
2. **Read/Write Address Aliasing Blindness (100% Failure Rate)**:
   - In industrial chips where read and write operations use distinct register addresses (e.g., LM83, TMP461), **both 14B and 6.7B models experienced a 100.0% failure rate** (48/48 across all seeds). LLMs fundamentally overlook cross-address state synchronization.
3. **Vendor IP Template Contamination & Self-Clearing Fragility**:
   - Across the Texas Instruments current monitor family (INA219, INA226, INA3221), models suffer a **53.7% failure rate** in self-clearing reset bits (`RST`), hallucinating identical template implementations regardless of chip-specific differences.
4. **Complexity Collapse (Spearman $\rho = -0.828, p = 0.0001$)**:
   - A statistically significant negative correlation exists between the number of special semantic registers (aliasing, self-clearing, soft-reset) and overall synthesis pass rates.

---

## 📊 Benchmark Leaderboard

### Table 1: Main Benchmark Failure Breakdown (Qwen2.5-Coder-14B, $N=408$ Samples, $n=24$ per Chip)

| # | Behavioral Specification Dimension | Clusters $k$ | Failed / Applicable | Fail Rate (%) | 95% Bootstrap CI / Bound |
|:---:|:---|:---:|:---:|:---:|:---:|
| **②** | Reset values baseline | 17 | 0 / 408 | **0.0%** | $\le 0.7\%$ (Rule of Three) |
| **③** | Read-only (RO) write protection | 16 | 189 / 384 | **49.2%** | [34.9%, 62.5%] |
| **④** | RW bitfield persistence | 17 | 290 / 408 | **71.1%** | [49.8%, 89.2%] |
| **⑤** | Write-trigger / self-clearing bits | 9 | 116 / 216 | **53.7%** | [35.6%, 70.4%] |
| **⑥** | Soft-reset key (write-only) | 2 | 18 / 48 | **37.5%** | [23.8%, 51.2%] ($k < 5$) |
| **⑥s**| Single-byte bus semantics | 1 | 2 / 24 | **8.3%** | [0.0%, 19.4%] ($k < 5$) |
| **⑦** | Read/write address aliasing | 2 | 48 / 48 | **100.0%** | [100.0%, 100.0%] ($k < 5$) |
| **⑧** | Clear-on-read interrupt alias | 1 | 23 / 24 | **95.8%** | [87.8%, 100.0%] ($k < 5$) |

> *Note on Dimension ④ Decoupling*: Failure rate (71.1%) is orthogonally decomposed into **④a Documented Bitfield Defect** (47.5%), **④b Industry Convention Gap** (3.9%), and **④u Unverified Bits** (19.6%), ensuring that unstated specification conventions are never conflated with model capability deficits.

---

### Table 2: Cross-Model Comparison Across 17 Peripherals ($N=612$ Total Samples)

| Chip | Manufacturer | Primary Category | Regs | Qwen2.5-Coder-14B Pass% ($n=24$) | DeepSeek-Coder-6.7B Pass% ($n=12$) |
|:---|:---|:---|:---:|:---:|:---:|
| **TMP1075** | TI | Digital Temp Sensor | 5 | **77.5%** | 53.3% |
| **TMP102** | TI | Low-Power Temp Sensor | 4 | **66.7%** | 36.1% |
| **TMP100** | TI | Digital Temp Sensor | 4 | **72.9%** | 37.5% |
| **TMP117** | TI | High-Precision Temp Sensor | 10 | **45.8%** | 27.1% |
| **TMP126** | TI | High-Precision Temp Sensor | 9 | **49.0%** | 25.0% |
| **TMP461** | TI | High-Accuracy Remote Temp | 24 | **33.3%** | 18.8% |
| **LM83** | NSC / TI | 4-Channel Thermal Monitor | 14 | **33.3%** | 22.9% |
| **HDC2021** | TI | Humidity & Temp Sensor | 20 | **38.5%** | 17.3% |
| **BME280** | Bosch | Humidity, Pressure & Temp | 14 | **43.8%** | 29.2% |
| **BMP280** | Bosch | Barometric Pressure & Temp | 11 | **75.0%** | 44.2% |
| **INA219** | TI | Current & Power Monitor | 6 | **71.9%** | 27.1% |
| **INA226** | TI | High-Side Current Monitor | 10 | **42.7%** | 29.2% |
| **INA3221** | TI | 3-Channel Current Monitor | 20 | **54.2%** | 13.5% |
| **ADS1115** | TI | 16-Bit Compact ADC | 4 | **95.8%** | 69.4% |
| **ADS1220** | TI | 24-Bit Precision ADC (Positive Control) | 4 | **100.0%** | **100.0%** |
| **LIS2DW12** | ST | 3-Axis Accelerometer | 15 | **50.0%** | 20.8% |
| **TPS23861** | TI | Quad-Port PoE Controller | 19 | **31.2%** | 22.9% |

---

## 📈 Visual Benchmark Analysis

<p align="center">
  <img src="assets/fig1_per_chip_passrate.png" alt="Per-Chip Pass Rate" width="90%">
  <br>
  <em>Figure 1: Overall pass rate per chip across Qwen2.5-Coder-14B (n=24) and DeepSeek-Coder-6.7B (n=12).</em>
</p>

<p align="center">
  <img src="assets/fig2_spearman_complexity.png" alt="Complexity vs Pass Rate" width="70%">
  <br>
  <em>Figure 2: Negative correlation between special register semantics and model pass rate (Spearman &rho; = -0.828, p = 0.0001).</em>
</p>

<p align="center">
  <img src="assets/fig3_dimension_failure_rates.png" alt="Dimension Failure Rates" width="85%">
  <br>
  <em>Figure 3: Failure rates across 8 behavioral dimensions comparing 14B vs. 6.7B models.</em>
</p>

---

## 🚀 Quickstart: Reproduce in 1 Minute (Zero GPU)

You can verify the dataset integrity, run admission tests, and reproduce all benchmark tables directly on CPU without needing any GPU or API keys:

### 1. Installation

```bash
git clone https://github.com/your-username/d2d-twin.git
cd d2d-twin

# Install lightweight evaluation dependencies
pip install -r requirements.txt
```

### 2. Verify Harness Integrity & Print Summary Tables

```bash
# Verify harness MD5 (8cf0854d4779467bc8e472ee4fb97023) and display Table 1 & Table 2
python run_benchmark.py
```

### 3. Run Blackbox Admission Tests on Reference Implementations

```bash
# Test all 17 golden reference simulators (executes in <1 second)
python run_benchmark.py --test-ref all

# Test a specific reference chip
python run_benchmark.py --test-ref TMP1075
```

### 4. Regenerate Publication Charts & LaTeX Tables

```bash
# Regenerates PNG charts into assets/ and LaTeX tables into _out/latex/
python run_benchmark.py --make-assets
```

---

## 📂 Repository Structure

```
.
├── LICENSE                      # Apache-2.0 License
├── README.md                    # Official English documentation
├── README_zh.md                 # Full Chinese documentation
├── DATASET.md                   # Hugging Face Dataset Card & Chip Catalog
├── requirements.txt             # Lightweight test & evaluation dependencies
├── run_benchmark.py             # One-command verification and reproduction CLI
├── assets/                      # High-resolution benchmark figures
│   ├── fig1_per_chip_passrate.png
│   ├── fig2_spearman_complexity.png
│   └── fig3_dimension_failure_rates.png
├── d2d/                         # D2D-Twin Benchmark Suite
│   ├── ir/                      # 17 Gold IR JSON files (single-writer human curated)
│   │   ├── TMP1075_gold_ir.json
│   │   └── ...
│   ├── rtl/                     # Base sensor classes & 17 Golden Reference Simulators
│   │   ├── base_sensor.py
│   │   ├── tmp1075_reference.py
│   │   └── ...
│   └── eval/                    # Testbench, main tables, and 612 code samples
│       ├── test_d2d_blackbox.py # Universal pytest harness (MD5: 8cf0854d4779467bc8e472ee4fb97023)
│       ├── main_table_n24.json  # Full evaluation records (14B, n=24)
│       ├── main_table_ds67b.json# Full evaluation records (6.7B, n=12)
│       └── results_gen_*.json   # Raw synthesized Python code samples
├── rag/                         # Companion HD-Agent RAG System
└── corpus/                      # Datasheet corpus parser scripts & manifests
```

---

## 📚 Companion System: HD-Agent (Datasheet QA-100 RAG)

Before synthesizing executable emulators, understanding datasheets requires reliable retrieval. Our companion subsystem, **HD-Agent**, features:
- **Corpus**: 456 component datasheets across 7,579 section slices.
- **QA-100 Benchmark**: 120 formally reviewed questions (param 83 + cross 37) under strict numerical and unit matching (`eval/qa100/score2.py`).
- **Key Finding**: Retrieval and parsing losses account for **40%–45% of total errors**, demonstrating that LLMs cannot reliably synthesize models without structured intermediate representations (Gold IR).

---

## 📝 Citation

If you use D2D-Twin or HD-Agent in your research, please cite:

```bibtex
@misc{d2dtwin2026,
  title={D2D-Twin: Benchmarking Large Language Models on Datasheet-to-Digital-Twin Synthesis for Peripheral Hardware Emulators},
  author={D2D-Twin Contributors},
  year={2026},
  howpublished={\url{https://github.com/your-username/d2d-twin}},
  note={Deterministic Blackbox Pytest Benchmark across 17 Peripheral ICs}
}
```

---

## 📜 License & Disclaimers

- The **D2D-Twin benchmark code, testbenches, and Gold IR datasets** are licensed under the [Apache 2.0 License](LICENSE).
- Datasheet trademarks and copyright materials belong to their respective manufacturers (Texas Instruments, Bosch Sensortec, STMicroelectronics, National Semiconductor). This repository only distributes parsed structural metadata for academic evaluation and research purposes.
