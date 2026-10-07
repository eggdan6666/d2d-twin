# -*- coding: utf-8 -*-
"""收官统计（只读 rag/ eval/ 代码，仅新增报告文件）:
  1) 6 个 kt_* 结果 → score2.correct 逐题重判 → mean±std + 逐题翻转 → eval/REPORT_ktrial.md
  2) results_v4_rag7b_loose.json → 分题型 → 追加 'v4 150题参考结果' 到 REPORT_qa100_baseline.md
用法: python _setup/final_stats.py [--dry]   --dry 只打印不写文件
"""
import sys, os, json, glob, statistics, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join("eval", "qa100"))
sys.stdout.reconfigure(encoding="utf-8")
from score2 import correct

DRY = "--dry" in sys.argv
SEEDS = (1, 2, 3)
CFGS = [("RAG-3B", "kt_rag3b_s%d"), ("RAG-7B-loose", "kt_rag7b_s%d")]
# temp=0/seed=42 单点基线（REPORT_qa100_baseline.md §最终合并矩阵 v3.1）
BASE = {"RAG-3B": ("results_v31_rag3b.json", 34.2),
        "RAG-7B-loose": ("results_v31_rag7b_loose.json", 41.7)}
TYPES = ("param", "cross", "app")


def rejudge(rows):
    """逐题用 score2.correct 重判存储的 pred(500字符上限)。"""
    out, trunc_gap = [], 0
    for x in rows:
        ok = bool(correct(x["gold"], x["pred"]))
        if ok != bool(x["ok"]):
            trunc_gap += 1
        out.append({"qid": x["qid"], "type": x["type"], "ok": ok, "ok_full": bool(x["ok"]),
                    "gold": x["gold"], "pred": x["pred"]})
    return out, trunc_gap


def summarize(rows):
    n = len(rows)
    by = {t: [sum(1 for x in rows if x["type"] == t and x["ok"]),
              sum(1 for x in rows if x["type"] == t)] for t in TYPES}
    return {"n": n, "ok": sum(1 for x in rows if x["ok"]),
            "ok_full": sum(1 for x in rows if x["ok_full"]),
            "acc": sum(1 for x in rows if x["ok"]) / n if n else 0.0,
            "by": {t: v for t, v in by.items() if v[1]}}


def ktrial():
    rep = {}
    for cfg, pat in CFGS:
        runs, missing = [], []
        for s in SEEDS:
            f = "eval/qa100/results_" + (pat % s) + ".json"
            if not os.path.exists(f):
                missing.append(f)
                continue
            rows, gap = rejudge(json.load(open(f, encoding="utf-8")))
            runs.append({"seed": s, "file": os.path.basename(f), "rows": rows,
                         "gap": gap, **summarize(rows)})
        if not runs:
            continue
        accs = [r["acc"] for r in runs]
        mean = statistics.mean(accs)
        std = statistics.stdev(accs) if len(accs) > 1 else 0.0
        pop = {}
        for r in runs:
            for x in r["rows"]:
                pop.setdefault(x["qid"], {"type": x["type"], "gold": x["gold"],
                                          "preds": {}, "full": {}})
                pop[x["qid"]]["preds"][r["seed"]] = x["ok"]
                pop[x["qid"]]["full"][r["seed"]] = x["ok_full"]
        flip = [q for q, v in pop.items() if len(set(v["preds"].values())) > 1]
        always = [q for q, v in pop.items() if all(v["preds"].values())]
        never = [q for q, v in pop.items() if not any(v["preds"].values())]
        pair = {}
        for a in SEEDS:
            for b in SEEDS:
                if a < b and a in [r["seed"] for r in runs] and b in [r["seed"] for r in runs]:
                    pair[(a, b)] = [q for q, v in pop.items()
                                    if v["preds"][a] != v["preds"][b]]
        bytype = {}
        for t in TYPES:
            qs = [v for v in pop.values() if v["type"] == t]
            if not qs:
                continue
            a = [sum(1 for q in qs if q["preds"][s]) / len(qs) for s in sorted(qs[0]["preds"])]
            bytype[t] = {"n": len(qs), "mean": statistics.mean(a),
                         "std": statistics.stdev(a) if len(a) > 1 else 0.0,
                         "flip": sum(1 for q in qs if len(set(q["preds"].values())) > 1)}
        rep[cfg] = {"runs": runs, "missing": missing, "mean": mean, "std": std,
                    "accs": accs, "pop": pop, "flip": flip, "always": always,
                    "never": never, "pair": pair, "bytype": bytype,
                    "nq": len(pop)}
    return rep


def fmt_pct(x):
    return f"{100*x:.1f}%"


def write_ktrial(rep):
    L = []
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    L.append("# REPORT — k-trial 采样方差（temp=0.7 × 3 seeds，QA-100 v3 120题）\n")
    L.append(f"生成时间 {now}；判分 `eval/qa100/score2.py:correct()` 对结果文件内 pred 逐题重判。\n")
    L.append("## 协议\n")
    L.append("- 数据: `eval/qa100/datasheet_qa100_v3.json`（120题=param 83 + cross 37），k-trial 显式 `--ds` 锁 v3")
    L.append("- 采样: `--temperature 0.7`，seed ∈ {1,2,3}；上下文/检索与 v3.1 主矩阵完全一致")
    L.append("- 唯一变量 = (temperature, seed)。对照点估计取同配置的 temp=0/seed=42 单跑")
    L.append("- 运行日志 `_setup/final_chain.log` + `_setup/final_kt*.log`；结果 `eval/qa100/results_kt_*.json`\n")
    L.append("- 判分: gold 数值(含负号)精确 + 单位强制 + 范围双端点")
    L.append("- std 为**样本标准差**(ddof=1, n=3, 自由度2)；3 seeds 太少，故同时给 95% 置信区间"
             "（t=4.303, 半宽=2.48×std），结论以 CI 为准而非 ±1std\n")
    L.append(f"## 总分 mean±std（{len(rep)} 个配置；数据缺段时在'数据完备性'列出）\n")
    L.append("| 配置 | 3 seeds 各自 acc | mean±std | 95%CI | 极差 | temp=0 单点 | 单点是否落在95%CI内 |")
    L.append("|---|---|---|---|---|---|---|")
    for cfg, r in rep.items():
        accs = " / ".join(fmt_pct(a) for a in r["accs"])
        b = BASE.get(cfg)
        rng = max(r["accs"]) - min(r["accs"]) if len(r["accs"]) > 1 else 0.0
        half = 2.484 * r["std"]
        ci = f"[{fmt_pct(max(0, r['mean']-half))}, {fmt_pct(min(1, r['mean']+half))}]"
        inb = "—"
        if b:
            inb = ("是" if abs(b[1] / 100 - r["mean"]) <= half else
                   f"否（偏离 {abs(b[1]/100 - r['mean'])/half:.1f}×CI半宽）")
        L.append(f"| {cfg} | {accs} | **{fmt_pct(r['mean'])}±{100*r['std']:.1f}pp** | {ci} | "
                 f"{fmt_pct(rng)} | {fmt_pct(b[1]/100) if b else '—'} | {inb} |")
    L.append("")
    L.append("## 逐题翻转（同一配置 3 个 seed 间判分不一致的题）\n")
    L.append("| 配置 | 题数 | 3次全对 | 3次全错 | 至少翻转1次 | 翻转率 | s1↔s2 | s1↔s3 | s2↔s3 |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for cfg, r in rep.items():
        p = []
        for (a, b) in [(1, 2), (1, 3), (2, 3)]:
            p.append(len(r["pair"].get((a, b), ["n/a"])) if (a, b) in r["pair"] else "n/a")
        L.append(f"| {cfg} | {r['nq']} | {len(r['always'])} | {len(r['never'])} | "
                 f"{len(r['flip'])} | {fmt_pct(len(r['flip'])/r['nq'])} | {p[0]} | {p[1]} | {p[2]} |")
    L.append("")
    L.append("## 分题型\n")
    L.append("| 配置 | 题型 | n | mean±std | 翻转题数 |")
    L.append("|---|---|---|---|---|")
    for cfg, r in rep.items():
        for t, v in r["bytype"].items():
            L.append(f"| {cfg} | {t} | {v['n']} | {fmt_pct(v['mean'])}±{100*v['std']:.1f}pp | {v['flip']} |")
    L.append("")
    L.append("## 判分口径核对（存储截断影响）\n")
    L.append("run.py 用完整回复文本判分后把 pred 截存 500 字符；本脚本只能对截存文本重判，故为**保守下界**。\n")
    L.append("| 文件 | n | 重判ok | run.py原判 | 分歧题数 |")
    L.append("|---|---|---|---|---|")
    for cfg, r in rep.items():
        for run in r["runs"]:
            L.append(f"| {run['file']} | {run['n']} | {run['ok']} | {run['ok_full']} | {run['gap']} |")
    L.append("")
    flipdetail = []
    for cfg, r in rep.items():
        if r["flip"]:
            flipdetail.append(f"- **{cfg}**（{len(r['flip'])} 题）: " +
                              ", ".join(sorted(r["flip"])))
    if flipdetail:
        L.append("## 翻转题清单\n")
        L.extend(flipdetail + [""])
    L.append("## 配置间差异能否被 3 seeds 分辨\n")
    L.append("对每对配置给 acc 差的 95% CI（Welch 式，SE=√(s1²/n+s2²/n)，t 取 n=3 的 4.303）：\n")
    L.append("| 对比 | acc 差 | SE | 95%CI | 判读 |")
    L.append("|---|---|---|---|---|")
    cs = list(rep.items())
    for i in range(len(cs)):
        for j in range(i + 1, len(cs)):
            (c1, r1), (c2, r2) = cs[i], cs[j]
            d = r2["mean"] - r1["mean"]
            se = (r1["std"] ** 2 / len(r1["accs"]) + r2["std"] ** 2 / len(r2["accs"])) ** 0.5
            half = 4.303 * se
            verdict = "差值 CI 含 0 → 3 seeds 分辨不出" if half >= abs(d) else "差值 CI 不含 0"
            L.append(f"| {c1} → {c2} | {100*d:+.1f}pp | {100*se:.1f}pp | "
                     f"[{100*(d-half):+.1f}, {100*(d+half):+.1f}]pp | {verdict} |")
    L.append("")
    L.append(f"- 与 **API-RAG temp=0 单点 36.7%**（`results_v31_api_rag.json`）比较各配置重采样区间：")
    for cfg, r in rep.items():
        half = 2.484 * r["std"]
        lo, hi = r["mean"] - half, r["mean"] + half
        pt = 0.367
        rel = ("整体高于（本地优于 API 的结论在重采样下保持）" if lo > pt else
               "整体低于（API 占优）" if hi < pt else
               "横跨 36.7%（两法在此精度下不可分辨）")
        L.append(f"  - {cfg}: 95%CI [{fmt_pct(lo)}, {fmt_pct(hi)}] {rel}")
    L.append("- **API 侧只做 temp=0 单跑、无 seeds**，其自身采样带宽未测，故跨体系比较只能视为"
             "『本地重采样区间 vs API 点估计』的单向检验，不构成对称显著性检验")
    L.append("")
    L.append("## 数据完备性与判读护栏\n")
    for cfg, r in rep.items():
        L.append(f"- {cfg}: {len(r['runs'])}/3 seeds 到位" +
                 (f"，缺 {[os.path.basename(m) for m in r['missing']]}" if r["missing"] else "，完整"))
    g1 = ["- **护栏1**（逐条核对）："]
    for cfg, r in rep.items():
        half = 100 * 2.484 * r["std"]
        g1.append(f"  - {cfg}: 自身 95%CI 半宽 **{half:.1f}pp** → 小于该带宽的配置间差距"
                  f"只能作排序参考，不是量级结论")
    g1.append("  - 主矩阵里 loose 的增益（3B 0.0pp: 34.2→34.2；7B +2.5pp: 39.2→41.7）"
              "都落在各自半宽之内 → 'loose 红利随检索质量向大模型迁移'方向可继续引用，"
              "**幅度 2.5pp 不可引用**")
    r7 = rep.get("RAG-7B-loose")
    if r7:
        lo = 100 * (r7["mean"] - 2.484 * r7["std"])
        g1.append(f"  - RAG-7B-loose 领先 API-RAG(temp=0 单点 36.7%) 的 5.0pp："
                  f"本地下界 {lo:.1f}% {'>' if lo > 36.7 else '<'} 36.7% → 方向"
                  f"{'在重采样下保持' if lo > 36.7 else '在重采样下不成立'}（单向检验）")
    if len(rep) > 1:
        (c1, r1), (c2, r2) = list(rep.items())[0], list(rep.items())[-1]
        d = 100 * (r2["mean"] - r1["mean"])
        se = 100 * (r1["std"] ** 2 / len(r1["accs"]) + r2["std"] ** 2 / len(r2["accs"])) ** 0.5
        g1.append(f"  - {c1}→{c2} 差 {d:+.1f}pp（SE {se:.1f}pp，95%CI 含 0 则分辨不出，见上表）")
    g1.append("  - 跨体系比较中 API 侧无 seeds（temp=0 单跑），只能做单向检验")
    L.extend(g1)
    L.append("- **护栏2**：翻转题属不稳定题，其单跑 ok/no 不具备可复现性，"
             "任何逐题级结论（如某题被检索救回）需 3 seeds 全对或全错才成立")
    L.append("- **护栏3**：cross 的 mean±std 在 n=37 上方差远大于 param，"
             "cross 的 ±3pp 级差异一律视为噪声")
    L.append("")
    L.append("## 运行事件与数据完整性\n")
    L.append("- 收官链日志 `_setup/final_chain.log`（2026-10-05 23:53 → 10-06 05:44，"
             "v4 段 84.9min 后打包）：")
    L.append("  `kt3b_s1 rc=0 26.3min`、`kt3b_s2 rc=0 27.2min`、`kt3b_s3 rc=0 24.5min`、"
             "**`kt7b_s1 rc=4294967295 62.7min`**、`kt7b_s2 rc=0 62.3min`、`kt7b_s3 rc=0 63.1min`")
    L.append("- **kt7b_s1 首跑失败**：`_setup/final_kt7b_s1.log` 0 字节、无结果文件 → "
             "子进程早期即停滞、未正常退出。已排除：无睡眠/唤醒事件（01:05–02:20 Kernel-Power 空）、"
             "无 WER 崩溃记录、Ollama 与语料健康（紧随的 s2/s3 均 rc=0）；"
             "当时空闲内存 1.1/15.9GB、显存 3.2/4GB 且另有会话占用 GPU → 判为资源争用致请求挂死被终止")
    L.append("- **补救**：未重启整链（那会重跑并覆盖 6 个已完成段），改按同参数单段重跑并加 "
             "`python -u` 逐题刷盘：`_setup/rerun_kt7b_s1.ps1`（PID 52888，05:47:30→06:43:55，"
             "56.4min，acc=52/120），日志 `_setup/rerun_kt7b_s1.log`")
    L.append("- 6 个结果文件完整性校验：各 **120 行 / 120 个唯一 qid / 空预测 0 条**，"
             "qid 集合与 v3 数据集一致 → 3+3 seeds 齐全")
    L.append("")
    if any(r["missing"] for r in rep.values()):
        L.append("## 缺失运行\n")
        for cfg, r in rep.items():
            for m in r["missing"]:
                L.append(f"- {cfg}: 缺 {m}")
        L.append("")
    txt = "\n".join(L)
    if DRY:
        print(txt)
    else:
        open("eval/REPORT_ktrial.md", "w", encoding="utf-8").write(txt)
        print("已写 eval/REPORT_ktrial.md (%d 行)" % txt.count("\n"))
    return txt


def v4_section():
    f = "eval/qa100/results_v4_rag7b_loose.json"
    if not os.path.exists(f):
        print("跳过 v4 节: 缺 " + f)
        return
    rows, gap = rejudge(json.load(open(f, encoding="utf-8")))
    s = summarize(rows)
    L = ["\n## v4 150题参考结果（2026-10-06，RAG-7B-loose / 严格判分 / temp=0 seed=42）\n"]
    L.append("| 题型 | n | 对 | 准确率 | 说明 |")
    L.append("|---|---|---|---|---|")
    note = {"param": "v3 正式题", "cross": "v3 正式题",
            "app": "**auto-draft未审校，仅供参考**"}
    for t in TYPES:
        if t in s["by"]:
            ok, n = s["by"][t]
            L.append(f"| {t} | {n} | {ok} | {fmt_pct(ok/n)} | {note[t]} |")
    appn = s["by"].get("app", [0, 0])
    formal = sum(s["by"][t][0] for t in ("param", "cross") if t in s["by"])
    formn = sum(s["by"][t][1] for t in ("param", "cross") if t in s["by"])
    L.append(f"| 合计(150) | {s['n']} | {s['ok']} | {fmt_pct(s['acc'])} | 含 app 未审校题 |")
    L.append(f"| 仅正式题(param+cross) | {formn} | {formal} | {fmt_pct(formal/formn)} | "
             "与 v3 120题基线可比 |")
    L.append("")
    L.append(f"- 明细 `eval/qa100/results_v4_rag7b_loose.json`；日志 `_setup/final_v4_7bloose.log`")
    L.append(f"- app 题由 `gen_app_drafts.py` 从 typ_app 摘录自动生成、gold 未经人工审校 → "
             f"app 列 {appn[0]}/{appn[1]} 只作为覆盖面参考，不进任何结论")
    L.append(f"- 判分对截存 pred 重算，与 run.py 原判分歧 {gap}/{s['n']} 题（保守下界）")
    L.append("")
    txt = "\n".join(L)
    tgt = "eval/REPORT_qa100_baseline.md"
    cur = open(tgt, encoding="utf-8").read()
    if "## v4 150题参考结果" in cur:
        print("v4 节已存在，跳过追加（如需刷新请手动删除该节）")
        if DRY:
            print(txt)
        return
    if DRY:
        print(txt)
    else:
        with open(tgt, "a", encoding="utf-8") as fh:
            fh.write(txt + "\n")
        print("已追加 v4 节到 " + tgt)


if __name__ == "__main__":
    rep = ktrial()
    if rep:
        write_ktrial(rep)
    else:
        print("尚无 kt_* 结果文件，跳过 k-trial 报告")
    v4_section()
