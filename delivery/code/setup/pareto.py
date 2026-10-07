# -*- coding: utf-8 -*-
"""帕累托前沿聚合(只读): 从 results_*.json 汇总 acc / tok每问 / 延迟每问 → CSV + 双子图 PNG。

可比性口径(必须先看):
- 主前沿只收 **协议 v3.1 + temp=0 + v3 120 题** 的 6 个 run；v3.0 的 5 个 run 上下文构造不同
  (1470 vs 2975 tok/题)，只作灰色参考点画在同一张图上，不参与前沿连线。
- kt_* 是 temp=0.7×3seed 的重采样，用 mean±95%CI 画成误差棒，不与 temp=0 单点混为同一配置。
- tokens 字段是 prompt+completion 合计(run.py 存的就是和)，无法拆价目 → x 轴用 tok/题 作成本代理，
  金钱成本只在表里标 API/本地二值；延迟单列一幅图，别把两幅图的 x 轴混读。
- 延迟不可跨轮混比(模型冷热、并发污染)，本脚本按文件原样取值并在此声明。

用法: python _setup/pareto.py
输出: eval/qa100/pareto_summary.csv, eval/qa100/fig_pareto_cost.png, eval/qa100/fig_pareto_latency.png
"""
import sys, os, json, csv, statistics as st

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
QA = os.path.join(ROOT, "eval", "qa100")
sys.path.insert(0, QA)
from score2 import correct

RUNS = [
    # (配置名, 结果文件, 协议, temp, 模型, 检索)
    ("API-bare",   "results_v31_api_bare.json",   "v3.1", 0.0, "DeepSeek-V4.1-Flash", "none"),
    ("API-RAG",    "results_v31_api_rag.json",    "v3.1", 0.0, "DeepSeek-V4.1-Flash", "hierarchical"),
    ("3B-RAG",     "results_v31_rag3b.json",      "v3.1", 0.0, "qwen2.5:3b",          "hierarchical"),
    ("3B-RAG-loose", "results_v31_rag3b_loose.json", "v3.1", 0.0, "qwen2.5:3b",       "hierarchical"),
    ("7B-RAG",     "results_v31_rag7b.json",      "v3.1", 0.0, "qwen2.5:7b-q4",       "hierarchical"),
    ("7B-RAG-loose", "results_v31_rag7b_loose.json", "v3.1", 0.0, "qwen2.5:7b-q4",    "hierarchical"),
    ("3B-bare(v3.0)",   "results_m_bare3b.json",      "v3.0", 0.0, "qwen2.5:3b",     "none"),
    ("3B-RAG(v3.0)",    "results_m_rag3b.json",       "v3.0", 0.0, "qwen2.5:3b",     "hierarchical"),
    ("3B-RAG-loose(v3.0)", "results_m_rag3b_loose.json", "v3.0", 0.0, "qwen2.5:3b",  "hierarchical"),
    ("7B-RAG(v3.0)",    "results_m_rag7b.json",       "v3.0", 0.0, "qwen2.5:7b-q4",  "hierarchical"),
    ("7B-RAG-loose(v3.0)", "results_m_rag7b_loose.json", "v3.0", 0.0, "qwen2.5:7b-q4", "hierarchical"),
]
KT = {"qwen2.5:3b": ["results_kt_rag3b_s%d.json" % i for i in (1, 2, 3)],
      "qwen2.5:7b-q4": ["results_kt_rag7b_s%d.json" % i for i in (1, 2, 3)]}
T3 = 4.303  # n=3, 95% CI


def load(fn):
    d = json.load(open(os.path.join(QA, fn), encoding="utf-8"))
    acc = sum(correct(x["gold"], x["pred"]) for x in d) / len(d)
    return {"n": len(d), "acc": acc,
            "tok_per_q": st.mean(x.get("tokens", 0) for x in d),
            "lat_per_q": st.mean(x.get("latency_s", 0) or 0 for x in d)}


def frontier(pts):
    """按 tok 升序保留 acc 严格创新的点(cost,acc)。"""
    out, best = [], -1
    for c, a in sorted(pts):
        if a > best:
            out.append((c, a))
            best = a
    return out


def main():
    rows = []
    for name, fn, proto, temp, model, retr in RUNS:
        m = load(fn)
        m.update(label=name, file=fn, protocol=proto, temp=temp, model=model, retrieval=retr,
                 in_frontier=(proto == "v3.1"),
                 note="" if proto == "v3.1" else "v3.0 协议:上下文构造不同,不参与前沿")
        rows.append(m)
    ci = {}
    for model, files in KT.items():
        a = [load(f)["acc"] for f in files]
        mean = st.mean(a)
        sd = st.stdev(a) if len(a) > 1 else 0.0
        ci[model] = (mean, sd, T3 * sd / len(a) ** 0.5)
    out_csv = os.path.join(QA, "pareto_summary.csv")
    cols = ["label", "file", "protocol", "temp", "model", "retrieval", "n", "acc",
            "tok_per_q", "lat_per_q", "in_frontier", "note"]
    with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in sorted(rows, key=lambda x: x["tok_per_q"]):
            w.writerow(r)
    print("表:", out_csv, len(rows), "行")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    F = [r for r in rows if r["in_frontier"]]
    G = [r for r in rows if not r["in_frontier"]]
    front = frontier([(r["tok_per_q"], r["acc"]) for r in F])
    M = {"qwen2.5:3b": ("o", 70), "qwen2.5:7b-q4": ("s", 85), "DeepSeek-V4.1-Flash": ("*", 190)}
    OFF = {"3B": (8, 14), "7B": (10, -16), "API": (-12, 14)}
    for xlabel, key in (("total tokens per question (log)", "tok_per_q"),
                        ("wall-clock latency per question, s (log)", "lat_per_q")):
        fig, ax = plt.subplots(figsize=(7.6, 5.0))
        for r in G:
            ax.scatter(r[key], r["acc"] * 100, marker="x", s=34, c="#b0b0b0", zorder=2)
        for r in F:
            mk, s = M[r["model"]]
            y = r["acc"] * 100
            ax.scatter(r[key], y, marker=mk, s=s,
                       c="#d1495b" if "loose" in r["label"] else "#00798c",
                       edgecolor="k", linewidth=.6, zorder=4)
            short = r["label"].replace("RAG-", "").replace("(v3.0)", "v0")
            dy = 14 if "loose" not in r["label"] else -18
            ax.annotate(short, (r[key], y), xytext=(OFF.get(short[:2], (8, 10))[0], dy),
                        textcoords="offset points", fontsize=7.5, zorder=5)
        ax.plot([p[0] for p in front], [p[1] * 100 for p in front], "--", c="#555", lw=1.1,
                zorder=3, label="Pareto frontier (v3.1, temp=0)")
        for model, (mean, sd, half) in ci.items():
            r = next(x for x in F if x["model"] == model and "loose" in x["label"])
            ax.errorbar(r[key], mean * 100, yerr=half * 100, fmt="none", ecolor="#888",
                        elinewidth=1.2, capsize=4, zorder=1)
            ax.annotate("temp0.7x3 %.1f%% +-%.1f" % (mean * 100, half * 100),
                        (r[key], mean * 100 + half * 100), xytext=(-6, 6),
                        textcoords="offset points", fontsize=6.8, color="#555", ha="right")
        ax.set_xscale("log")
        ax.set_ylim(15, 48)
        ax.set_xlabel(xlabel)
        ax.set_ylabel("accuracy on Datasheet-QA-100 v3 (120 items), %")
        ax.set_title("Local 4GB-GPU RAG vs commercial API  (strict scoring, k=3)\n"
                     "gray x = protocol v3.0, not comparable", fontsize=9.5)
        ax.grid(alpha=.25)
        ax.legend(fontsize=7.5, loc="lower right")
        p = os.path.join(QA, "fig_pareto_%s.png" % ("cost" if key == "tok_per_q" else "latency"))
        fig.tight_layout()
        fig.savefig(p, dpi=150)
        plt.close(fig)
        print("图:", p)
    print("\n前沿点(按 tok/题 升序):")
    for c, a in front:
        print(f"   {c:8.0f} tok  {a:5.1%}")
    for model, (mean, sd, half) in ci.items():
        print(f"重采样 {model}: mean {mean:.1%} std {sd*100:.1f}pp 95%CI +-{half*100:.1f}pp")


if __name__ == "__main__":
    main()
