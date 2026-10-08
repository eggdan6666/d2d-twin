# D2D-Twin 学术论文源码工程 (LaTeX)

本目录为 **D2D-Twin** 基准的官方学术论文源码工程，遵循标准 **IEEE 双栏会议/期刊模板**。

---

## 快速使用指南（推荐 Overleaf 在线编译）

### 方式一：一键导入 Overleaf（免安装环境，最推荐）
1. 将本 `paper/` 文件夹整体压缩为一个 zip 文件（例如 `d2d_twin_paper.zip`）；
2. 打开浏览器访问 [Overleaf](https://www.overleaf.com/)；
3. 点击 **「New Project」** $\to$ **「Upload Project」**，将 zip 文件上传；
4. 页面打开后，直接点击右上角绿色的 **「Recompile」** 按钮，即可瞬间生成双栏 PDF 论文！

### 方式二：本地 TeXLive / MacTeX / MikTeX 编译
在命令行进入 `paper/` 目录运行：
```bash
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

---

## 目录结构说明

- `main.tex`: 论文主文档，包含完整的数学形式化定义、8 大维度定义、三大盲区实证论证、Q1c 消融实验及主表；
- `references.bib`: 规范的 BibTeX 参考文献列表（涵盖 SWE-bench, VerilogEval, RTLLM, ChipNeMo, Qwen2.5-Coder, DeepSeek-Coder 等）；
- `figures/`: 包含 3 幅论文级高清实测结果图：
  - `fig1_per_chip_passrate.png`: 17 颗芯片两模型通过率柱状对比图；
  - `fig2_spearman_complexity.png`: 寄存器复杂度与通过率 Spearman 负相关拟合图；
  - `fig3_dimension_failure_rates.png`: 8 大行为规范维度跨模型失败率条形对比图。
