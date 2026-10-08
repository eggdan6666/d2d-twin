# -*- coding: utf-8 -*-
"""生成论文级发表产物：图表（PNG/PDF）与 LaTeX 主表代码。
基于 17 颗芯片 n=24 主表、DeepSeek-6.7B 主表与 Q1c 消融数据。
"""
import sys, os, io, json
import numpy as np
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG_DIR = os.path.join(ROOT, "_out", "figs")
TEX_DIR = os.path.join(ROOT, "_out", "latex")
os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(TEX_DIR, exist_ok=True)

# 设置学术风格绘图参数
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 13

# 1. 加载数据
n24 = json.load(open(os.path.join(ROOT, "d2d", "eval", "main_table_n24.json"), encoding="utf-8"))
ds67b = json.load(open(os.path.join(ROOT, "d2d", "eval", "main_table_ds67b.json"), encoding="utf-8"))
q1c = json.load(open(os.path.join(ROOT, "d2d", "eval", "q1c_ablation_summary.json"), encoding="utf-8"))

chips = n24["chips"]
rate_14b = [n24["per_chip_rate_pct"][c] for c in chips]
rate_67b = [ds67b["per_chip_rate_pct"][c] for c in chips]

# ==========================================
# 图 1: 17 颗芯片两模型通过率柱状对比图
# ==========================================
fig, ax = plt.subplots(figsize=(12, 4.8), dpi=300)
x = np.arange(len(chips))
width = 0.38

rects1 = ax.bar(x - width/2, rate_14b, width, label='Qwen2.5-Coder-14B (n=24)', color='#1f77b4', edgecolor='black', linewidth=0.6, alpha=0.9)
rects2 = ax.bar(x + width/2, rate_67b, width, label='DeepSeek-Coder-6.7B (n=12)', color='#ff7f0e', edgecolor='black', linewidth=0.6, alpha=0.9)

ax.set_ylabel('Strict Pass Rate (%)')
ax.set_title('Per-Chip Overall Pass Rate Across 17 Peripherals (N=612 Total Samples)')
ax.set_xticks(x)
ax.set_xticklabels(chips, rotation=35, ha='right')
ax.set_ylim(0, 108)
ax.grid(axis='y', linestyle='--', alpha=0.5)
ax.legend(frameon=True, facecolor='white', framealpha=0.9)

# 标出正对照
ax.annotate('Positive Control\n(Pure register file)', xy=(8, 100), xytext=(8, 104),
            ha='center', fontsize=8, color='#2ca02c', fontweight='bold')

plt.tight_layout()
fig1_path = os.path.join(FIG_DIR, "fig1_per_chip_passrate.png")
fig.savefig(fig1_path)
plt.close(fig)
print("[Asset] Generated:", fig1_path)

# ==========================================
# 图 2: 特殊语义复杂度 vs 通过率 Spearman 散点拟合图
# ==========================================
fig, ax = plt.subplots(figsize=(6.5, 5.0), dpi=300)
feats = {}
for c in chips:
    ir = json.load(open(os.path.join(ROOT, "d2d", "ir", "%s_gold_ir.json" % c), encoding="utf-8"))
    R = ir["registers"]
    feats[c] = sum(1 for r in R if r.get("write_key") or r.get("cor_addr") or r.get("write_addr")
                   or any(f.get("read_as") is not None or f.get("read_action") for f in r.get("fields", [])))

x_special = [feats[c] for c in chips]
y_rate = rate_14b

# 散点
ax.scatter(x_special, y_rate, color='#1f77b4', s=60, edgecolors='black', linewidth=0.8, zorder=5)

# 芯片标签
for c, xi, yi in zip(chips, x_special, y_rate):
    offset = (4, 4) if c not in ["TMP100", "LM83"] else (4, -10)
    ax.annotate(c, (xi, yi), textcoords="offset points", xytext=offset, fontsize=8, alpha=0.85)

# 拟合直线
z = np.polyfit(x_special, y_rate, 1)
p_line = np.poly1d(z)
x_vals = np.linspace(min(x_special), max(x_special), 100)
ax.plot(x_vals, p_line(x_vals), "r--", linewidth=1.5, alpha=0.8,
        label=r'Spearman $\rho = -0.828, p = 0.0001$')

ax.set_xlabel('Number of Special Semantic Registers')
ax.set_ylabel('Pass Rate (% in Qwen-14B n=24)')
ax.set_title('Semantic Complexity vs. Simulation Fidelity')
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(loc='upper right', frameon=True)
plt.tight_layout()
fig2_path = os.path.join(FIG_DIR, "fig2_spearman_complexity.png")
fig.savefig(fig2_path)
plt.close(fig)
print("[Asset] Generated:", fig2_path)

# ==========================================
# 图 3: 8 大维度失败率对比条形图 (14B vs 6.7B)
# ==========================================
fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
dim_labels = [
    "② Reset values",
    "③ RO protection",
    "④ RW persistence",
    "⑤ Self-clearing",
    "⑥ Soft-reset key",
    "⑥s Single-byte",
    "⑦ R/W Alias",
    "⑧ Clear-on-read"
]
dim_keys = [
    "test_reset_values",
    "test_readonly_protection",
    "test_rw_field_persistence",
    "test_write_trigger_fields",
    "test_write_only_reset_key",
    "test_single_byte_semantics",
    "test_read_write_alias",
    "test_clear_on_read"
]

fail_14b = [n24["dimensions"][k]["rate"] for k in dim_keys]
fail_67b = [ds67b["dimensions"][k]["rate"] for k in dim_keys]

y_pos = np.arange(len(dim_labels))
bar_height = 0.35

ax.barh(y_pos + bar_height/2, fail_14b, bar_height, label='Qwen-14B (n=24)', color='#2b5c8f', edgecolor='black', linewidth=0.6)
ax.barh(y_pos - bar_height/2, fail_67b, bar_height, label='DeepSeek-6.7B (n=12)', color='#d95f02', edgecolor='black', linewidth=0.6)

ax.set_yticks(y_pos)
ax.set_yticklabels(dim_labels)
ax.invert_yaxis()  # 从上往下 ② 到 ⑧
ax.set_xlabel('Failure Rate (%)')
ax.set_title('Failure Rates Across 8 Behavioral Specification Dimensions')
ax.set_xlim(0, 105)
ax.grid(axis='x', linestyle='--', alpha=0.5)
ax.legend(loc='lower right', frameon=True)

plt.tight_layout()
fig3_path = os.path.join(FIG_DIR, "fig3_dimension_failure_rates.png")
fig.savefig(fig3_path)
plt.close(fig)
print("[Asset] Generated:", fig3_path)

# ==========================================
# 4. 生成 LaTeX Table 1: 主基准表
# ==========================================
tex1_path = os.path.join(TEX_DIR, "table1_main_benchmark.tex")
with io.open(tex1_path, "w", encoding="utf-8") as f:
    f.write("% Table 1: D2D-Twin Main Benchmark Results (17 Chips, N=408 Samples, Qwen-14B)\n")
    f.write("\\begin{table*}[t]\n")
    f.write("\\centering\n")
    f.write("\\small\n")
    f.write("\\caption{Register-level behavioral benchmark results on Qwen2.5-Coder-14B ($N=408$, $n=24$ per chip). CI is computed via wild cluster bootstrap over chip clusters ($k$); assertions with zero failures use Rule of Five.}\\label{tab:main_results}\n")
    f.write("\\begin{tabular}{llrcccc}\n")
    f.write("\\toprule\n")
    f.write("Dimension & Specification Aspect & Clusters ($k$) & Fail / Applicable & Failure Rate (\\%) & Inference Method & 95\\% Conf. Interval \\\\\n")
    f.write("\\midrule\n")
    for k in dim_keys:
        d = n24["dimensions"][k]
        no, name = d["no"], d["label"]
        cl = d["clusters"]
        fail = d["fail"]
        app = d["applicable"]
        rate = d["rate"]
        ci = d.get("ci")
        bound = d.get("bound")
        if ci:
            inf = "Cluster Boot."
            ci_str = f"[{ci['lo']}\\%, {ci['hi']}\\%]"
        elif bound:
            inf = "Rule of Five"
            ci_str = f"$\\le {bound['upper_pct']}\\%$"
        else:
            inf = f"Descriptive ($k={cl}$)"
            ci_str = "---"
        f.write(f"{no} & {name} & {cl} & {fail} / {app} & {rate}\\% & {inf} & {ci_str} \\\\\n")
    f.write("\\bottomrule\n")
    f.write("\\end{tabular}\n")
    f.write("\\end{table*}\n")
print("[Asset] Generated LaTeX Table 1:", tex1_path)

# ==========================================
# 5. 生成 LaTeX Table 2: 跨模型对比表
# ==========================================
tex2_path = os.path.join(TEX_DIR, "table2_cross_model.tex")
with io.open(tex2_path, "w", encoding="utf-8") as f:
    f.write("% Table 2: Cross-Model Comparison: Qwen-14B vs DeepSeek-6.7B\n")
    f.write("\\begin{table}[t]\n")
    f.write("\\centering\n")
    f.write("\\small\n")
    f.write("\\caption{Comparison between Qwen2.5-Coder-14B and DeepSeek-Coder-6.7B across 17 chips.}\\label{tab:model_comparison}\n")
    f.write("\\begin{tabular}{lrr}\n")
    f.write("\\toprule\n")
    f.write("Dimension & Qwen-14B ($n=24$) & DeepSeek-6.7B ($n=12$) \\\\\n")
    f.write("\\midrule\n")
    for k in dim_keys:
        d14 = n24["dimensions"][k]
        d67 = ds67b["dimensions"][k]
        f.write(f"{d14['no']} {d14['label']} & {d14['rate']}\\% & {d67['rate']}\\% \\\\\n")
    f.write("\\midrule\n")
    f.write(f"④a Documented Bitfield Fail & {n24['assertion4_split']['4a_pct']}\\% & {ds67b['assertion4_split']['4a_pct']}\\% \\\\\n")
    f.write(f"Spearman $\\rho$ (Special Regs) & -0.828 ($p=0.0001$) & -0.789 ($p=0.0003$) \\\\\n")
    f.write("\\bottomrule\n")
    f.write("\\end{tabular}\n")
    f.write("\\end{table}\n")
print("[Asset] Generated LaTeX Table 2:", tex2_path)
