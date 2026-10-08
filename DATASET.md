---
license: apache-2.0
task_categories:
- text-to-code
- software-engineering-verification
tags:
- hardware-eda
- virtual-prototyping
- peripheral-simulation
- code-llm-benchmark
- pytest-blackbox
size_categories:
- n<1K
configs:
- config_name: gold_ir
  data_files: "d2d/ir/*_gold_ir.json"
- config_name: code_samples
  data_files: "d2d/eval/results_gen_*.json"
---

# Dataset Card: D2D-Twin (Datasheet-to-Digital-Twin Benchmark)

## 1. Dataset Summary

**D2D-Twin** is the first deterministic, zero-LLM-as-a-judge benchmark designed to evaluate Large Language Models (LLMs) on **Datasheet-to-Digital-Twin synthesis** for peripheral hardware emulators.

Given a formal hardware specification (Gold Intermediate Representation, **Gold IR**) transcribed from vendor datasheets, code LLMs are prompted to synthesize an executable register-level behavioral emulator in Python. The generated simulators are subsequently evaluated against a universal blackbox `pytest` testbench that issues bus read/write transactions and asserts hardware state transitions.

- **Peripherals Evaluated**: 17 industry-standard peripheral ICs (Sensors, ADCs, PMICs, Controllers)
- **Total Synthesized Code Samples**: 612 samples (408 from Qwen2.5-Coder-14B at $n=24$; 204 from DeepSeek-Coder-6.7B at $n=12$)
- **Deterministic Harness MD5**: `8cf0854d4779467bc8e472ee4fb97023`
- **Zero LLM-as-a-Judge**: 100% verified via objective pytest assertions and hardware state comparisons.

---

## 2. Chip Catalog (17 Integrated Circuits)

| Part Number | Manufacturer | Primary Category | Bus Interface | Register Count | Key Semantic Features |
|:---|:---|:---|:---:|:---:|:---|
| **TMP1075** | Texas Instruments | Digital Temp Sensor | I2C / SMBus | 5 | Self-clearing one-shot (`OS`), byte swapping |
| **TMP102** | Texas Instruments | Low-Power Temp Sensor | I2C / SMBus | 4 | Extended mode, reserved bit convention (Tier-C) |
| **TMP100** | Texas Instruments | Digital Temp Sensor | I2C / SMBus | 4 | Configurable ADC resolution (9–12 bit) |
| **TMP117** | Texas Instruments | High-Precision Temp Sensor | I2C / SMBus | 10 | EEPROM unlocked bits, software reset key |
| **TMP126** | Texas Instruments | High-Precision Temp Sensor | I2C / SPI | 9 | Multi-register limit alerts, slew-rate config |
| **TMP461** | Texas Instruments | High-Accuracy Remote Temp | I2C / SMBus | 24 | **Read/Write address aliasing (`write_addr`)** |
| **LM83** | National Semi / TI | 4-Channel Thermal Monitor | I2C / SMBus | 14 | **Read/Write address aliasing (`write_addr`)** |
| **HDC2021** | Texas Instruments | Humidity & Temp Sensor | I2C / SMBus | 20 | Auto-measurement triggers, interrupt status |
| **BME280** | Bosch Sensortec | Humidity, Pressure & Temp | I2C / SPI | 14 | Calibration register bank, Soft-reset key (`0xB6`) |
| **BMP280** | Bosch Sensortec | Barometric Pressure & Temp | I2C / SPI | 11 | Power mode transitions, Soft-reset key (`0xB6`) |
| **INA219** | Texas Instruments | Current & Power Monitor | I2C / SMBus | 6 | Shunt voltage scaling, calibration math |
| **INA226** | Texas Instruments | High-Side Current Monitor | I2C / SMBus | 10 | Reset self-clearing (`RST`), alert latching |
| **INA3221** | Texas Instruments | 3-Channel Current Monitor | I2C / SMBus | 20 | 3-phase shunt monitoring, reset self-clearing |
| **ADS1115** | Texas Instruments | 16-Bit Ultra-Compact ADC | I2C / SMBus | 4 | Operational status (`OS`), MUX configuration |
| **ADS1220** | Texas Instruments | 24-Bit Precision ADC | SPI | 4 | Pure register file control, Positive Control |
| **LIS2DW12** | STMicroelectronics | 3-Axis Accelerometer | I2C / SPI | 15 | Control registers, data-rate decimation |
| **TPS23861** | Texas Instruments | Quad-Port PoE Controller | I2C / SMBus | 19 | **Clear-on-read interrupt register (`read_action`)** |

---

## 3. Data Structure & Gold IR Schema

Each chip's Gold IR is stored in `d2d/ir/<PART>_gold_ir.json`. Below is the formal specification:

```json
{
  "device": "TMP1075",
  "bus_interface": "I2C",
  "reg_width": 16,
  "endianness": "big",
  "registers": [
    {
      "name": "TEMP",
      "addr": 0,
      "width": 16,
      "access": "RO",
      "reset": 0,
      "runtime_value": true,
      "desc": "Temperature register (read-only real-time sensor output)"
    },
    {
      "name": "CONFIG",
      "addr": 1,
      "width": 16,
      "access": "RW",
      "reset": 255,
      "fields": [
        {
          "name": "OS",
          "bits": [15, 15],
          "access": "RW",
          "reset": 0,
          "read_as": 0,
          "desc": "One-shot conversion trigger. Writing 1 starts conversion; always reads back 0."
        },
        {
          "name": "R",
          "bits": [14, 13],
          "access": "RW",
          "reset": 0,
          "desc": "Converter resolution control bits."
        }
      ]
    }
  ]
}
```

### Key Field Semantics

- `runtime_value: true`: Designates real-time ADC/sensor outputs; excluded from static reset value assertion.
- `read_as: 0`: Designates self-clearing / write-trigger bits. Tested under Dimension ⑤.
- `write_addr`: Designates registers with distinct read vs. write bus addresses (e.g., LM83, TMP461). Tested under Dimension ⑦.
- `read_action: "clear"`: Designates clear-on-read registers (e.g., TPS23861 interrupt status). Tested under Dimension ⑧.
- `write_key`: Designates soft-reset magic numbers written to write-only addresses. Tested under Dimension ⑥.
- `tier: "A" | "B" | "C" | "UNVERIFIED"`: Orthogonal decoupling of undocumented reserved bit conventions vs true model logic errors.

---

## 4. Evaluated Code Models and Results Data

Evaluations are recorded in `d2d/eval/results_gen_<tag>.json`:
- `results_gen_<chip>kt.json`: Primary Qwen2.5-Coder-14B generation samples (seeds 1–3, $n=12$).
- `results_gen_<chip>kt_b.json`: Secondary Qwen2.5-Coder-14B replication samples (seeds 4–6, $n=12$, total $n=24$).
- `results_gen_ds67b<chip>.json`: DeepSeek-Coder-6.7B comparison samples ($n=12$).
- `results_gen_*q1c.json`: Clean ablation arm samples (scrubbed descriptions & removed reset tags).

Each sample object contains:
```json
{
  "chip": "TMP1075",
  "seed": 1,
  "sample_idx": 0,
  "prompt_tokens": 1240,
  "code": "from base_sensor import BaseVirtualSensor\n\nclass TMP1075_Simulator(BaseVirtualSensor):\n    ...",
  "rc": 0
}
```

---

## 5. Reproduction & Verification

To reproduce benchmark results without GPU or LLM APIs:
```bash
# Clone the repository
git clone https://github.com/your-username/d2d-twin.git
cd d2d-twin

# Install dependencies
pip install -r requirements.txt

# Run deterministic verification (MD5 check & summary tables)
python run_benchmark.py

# Run admission tests on all 17 reference implementations
python run_benchmark.py --test-ref all
```
