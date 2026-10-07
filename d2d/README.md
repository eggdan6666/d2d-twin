# D2D-Twin Phase 1 MVP 工作区

数据手册 → 数字孪生基准的第一条黄金流水线（TMP1075）。

## 目录

```
d2d/
├── ir/          金标 IR（JSON，SVD 可映射）。TMP1075_gold_ir.json 含 open_questions 待校对
├── rtl/         base_sensor.py = 被测代码必须继承的基类（testbench 接口契约）
│                tmp1075_reference.py = 人工金标实现（只用于校验 testbench，不参评）
├── eval/        test_tmp1075.py = IR 驱动的黑盒断言（换芯片零改动复用）
│                gen_code.py       = DCU codegen 评测器（Coder 模型生成 → 沙盒 pytest）
├── parsed/      MinerU 解析产物（TMP1075/auto/TMP1075.md 为 IR 上游）
└── results_*.json  评测明细（code + pytest 记录）
```

## 黄金流水线（Phase 1 验证目标）

```
人工金标 IR ──┬─→ gen_code.py（Coder 模型生成）→ tmp1075_simulator.py
             └─→ test_tmp1075.py（IR 驱动断言）─→ pytest 判分
```

MVP 测的是 **IR→代码** 这一段（代码生成保真度）；Phase 3 的 A/B/C 臂再接上
**PDF→Markdown→IR** 上游，测端到端。

## 服务器命令（mineru295 机器，/root/private_data/d2d/）

```bash
source /opt/dtk/env.sh; export PATH=/opt/conda/bin:$PATH
export HF_HUB_OFFLINE=1 http_proxy=http://preset:6e298f07@10.16.1.51:3128 \
       https_proxy=http://preset:6e298f07@10.16.1.51:3128
# 冒烟（贪心 1 份）
python eval/gen_code.py --model-path /root/private_data/models/Qwen2.5-Coder-14B-Instruct --tag smoke --greedy
# 正式（temp0.7×3seeds×4样本，基准口径同 HD-Agent k-trial）
python eval/gen_code.py --model-path ... --tag kt --n 4 --temperature 0.7 --seeds 1,2,3
```

## 校对清单（IR 生效前必看 ir/TMP1075_gold_ir.json 的 open_questions）

- Q1 CFGR 低字节 / LLIM·HLIM 低 4 位：R/W（可写存储，现行为）vs 写忽略
- Q2 OS 位 read_as=0
- Q3 单字节语义是全寄存器还是仅 CFGR
- Q4 TMP1075N 变体未入 MVP
