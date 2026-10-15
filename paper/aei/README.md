# paper/aei —— AEI 长文投稿草案（框架版）

目标期刊：**Advanced Engineering Informatics**（Elsevier，中科院一区 Top 待核实），
目标特刊：*Advanced Theories and Practices for Trustworthy Hybrid Human Agentic-AI
Empowered Engineering Systems*（VSI: ADVEI_Trustworthy...），官方征稿截止 2026-12-31。

本目录只搭**骨架**，正式结果一律从锁定 manifest 派生；`paper/main.tex` 与旧图保持不变。

## 文件结构

| 文件 | 说明 |
|---|---|
| `main.tex` | `elsarticle`（review 模式）主文档：Title / Highlights / 五段式 Abstract / Intro / Related Work / Problem Formulation \& Architecture / Upstream Extraction / Core Benchmark / Self-Repair / Discussion / Conclusion |
| `references.bib` | 与根目录 `paper/references.bib` 同源、按引用子集复制；编译时自动编号 |
| `README.md` | 本说明 |

## 已搭好的框架

- **Title**：`Source-Constrained Agentic Synthesis of Register-Level Peripheral Emulators from Datasheets with Bounded Blackbox Verification`（收敛了"This work"式的过度自居）
- **Highlights**：5 条，每条 ≤ 85 字符
- **五段式 Abstract**：Background / Objective / Methods / Results / Conclusion
- **Section 1 Introduction**：问题定义 + 贡献声明 + 边界声明
- **Section 2 Related Work**：定位对比表（HumanEval / SWE-bench / VerilogEval / RTLLM / ChipNeMo / RAG / D2D-Twin）
- **Section 3 Problem Formulation \& System Architecture**：外设总线状态机 + 单写入者 IR + 显式未知掩码 `known_mask` + 三阶段可审计闭环
- **Section 4 Upstream Source-Constrained Register Extraction**：Silver 管道 + PDF SHA-256 锚定 + L1/L2/L3 指标公式
- **Section 5 Core Benchmark \& Empirical Findings**：20 芯片 8 维度 + 3 模型 720 样本 + 四大缺陷 + 历史队列 $\rho$
- **Section 6 Reflection-Guided Structured Self-Repair**：结构化补丁门禁 + CRS 累积修复成功率 + 补丁拒绝/回归拦截 + 探索性边界
- **Section 7 Discussion**：威胁有效性（内/外部）+ 人类主权门禁（Single Writer 终审）+ CPS/数字孪生工程启示
- **Section 8 Conclusion \& Future Work**：四大贡献总结 + 11/15 范围收口后重算 20 芯片逐维度哈希 + 跨芯片多轮修复基准

## 学术表述纠偏（已按 REVIEW 意见收紧）

| 事项 | 纠偏后的口径 |
|---|---|
| 验证边界 | **「数据手册约束下的寄存器行为仿真及有界验证」**，不再自称「V&V 最高标准」「顶层数字孪生」 |
| 模型名 | Qwen2.5-Coder-3B / DeepSeek-Coder-6.7B / Qwen2.5-Coder-14B（不是「Qwen3」） |
| 影响因子 | 只写 11.5 并标注「待核实」，分区注明年份，不使用「约 8.5–11.5」 |
| 样本队列 | 历史 17 芯片 / 612 样本（两模型）与 20 芯片 / 720（三模型，每模型 240）**分列，不得互换分母** |
| 相关系数 | $\rho=-0.828$ 来自旧 17 芯片主表，**不移植**为 20 芯片三模型结论 |
| 冻结 MD5 | `8cf0854d4779467bc8e472ee4fb97023` 只证字节稳定/可重现，不证规范正确或硅片等价 |

## 证据标签（沿用 SCI-Skills）

- `已核实` —— 有来源/产物直接支撑；
- `待核实` —— 文本中以 `\unverified{...}`（橙色）标注；
- `[TODO: ...]` —— 红色占位，投稿前必须补齐。

## 编译

```bash
cd paper/aei
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

> `elsarticle` 的 `review` 模式为内部写作/评审布局；**最终投稿格式以 AEI 官方 Guide for Authors
> 为准**（本次未成功直读作者指南，需待核实）。

## 下一步（待办）

1. 落地两组实验协议（RAG 三臂消融、结构化修复）的真实数据与图，并据此回填 Discussion / Conclusion 中的 `\todo` / `\unverified` 项；
2. 依据锁定 manifest 重算全部数字与图（20 芯片队列逐维度拆分与复杂度相关系数待冻结协议后重算），移除 `\todo` / `\unverified` 占位；
3. 逐条核对 Related Work 对比表，补齐页码证据。