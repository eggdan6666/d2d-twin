# -*- coding: utf-8 -*-
"""论文主表生成器（零 GPU，按芯片聚类做推断）。

裁决落地（2026-10-07 用户）：
  ① 主表 CI 按**芯片**聚类 bootstrap（96 = 8~10 颗 × 12 份，同颗共享一份 IR）；
     聚类数 <5 的维度**不给 CI**，改逐颗点图 + 描述性陈述；
     ② 复位值 0 失败用 rule of three 给上界，禁 ±0.0pp。
  ② ④ 拆两行：④a Documented Bitfield Persistence（relax 档仍失败的）
                ④b Undocumented Reserved Bits / Benchmark Convention（strict−relax 的差）。
  ③ 梯度不做二分类结论，只报 Spearman ρ + 精确置换 p，并附「事后分组的最好看组差」
     的 Bonferroni 校正 p，让读者看见 n=8 的功效边界。
  分母一律 passed / applicable（applicable 由 junitxml 里 PASSED+FAILED 计，SKIPPED 单列）。

用法: python _setup/main_table.py [--quick]   --quick 只跑新落分的两颗
产物: d2d/eval/main_table.json、d2d/eval/main_table.csv（带 BOM，末列留人工裁决）
"""
import sys, os, io, re, json, csv, shutil, argparse, subprocess, random, itertools
import xml.etree.ElementTree as ET
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "_setup"))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

TAGS = {"TMP1075": "kt", "BMP280": "bmp280kt", "TMP102": "tmp102kt", "BME280": "bme280kt",
        "TMP100": "tmp100kt", "INA3221": "ina3221kt", "HDC2021": "hdc2021kt",
        "TMP117": "tmp117kt", "ADS1220": "ads1220kt", "LM83": "lm83kt",
        "TPS23861": "tps23861kt",
        "TMP126": "tmp126kt"}
ORDER = ["TMP1075", "BMP280", "TMP102", "BME280", "TMP100", "INA3221", "HDC2021", "TMP117",
         "ADS1220", "LM83", "TPS23861", "TMP126"]
DIM = {  # 断言 → (编号, 论文里的名字)
    "test_reset_values": ("②", "Reset values"),
    "test_readonly_protection": ("③", "RO write protection"),
    "test_rw_field_persistence": ("④", "RW bitfield persistence"),
    "test_write_trigger_fields": ("⑤", "Write-trigger / self-clearing bits"),
    "test_single_byte_semantics": ("⑥s", "Single-byte semantics"),
    "test_read_write_alias": ("⑦", "Read/write alias registers"),
    "test_clear_on_read": ("⑧", "Clear-on-read alias"),
    "test_write_only_reset_key": ("⑥", "Soft-reset key (write-only)"),
}
MIN_CLUSTER = 5
B = 20000


def run_sample(part, code, ir_name, workdir):
    """在沙箱里对一份已生成代码跑 harness，返回 {test: PASSED|FAILED|SKIPPED}。"""
    shutil.rmtree(workdir, ignore_errors=True)
    os.makedirs(workdir)
    shutil.copy(os.path.join(ROOT, "d2d", "rtl", "base_sensor.py"), os.path.join(workdir, "base_sensor.py"))
    shutil.copy(os.path.join(ROOT, "d2d", "eval", "test_d2d_blackbox.py"), os.path.join(workdir, "test_d2d_blackbox.py"))
    io.open(os.path.join(workdir, "%s_simulator.py" % part.lower()), "w", encoding="utf-8").write(code)
    xj = os.path.join(workdir, "junit.xml")
    env = dict(os.environ, D2D_IR=ir_name, PYTHONIOENCODING="utf-8")
    subprocess.run([sys.executable, "-m", "pytest", "test_d2d_blackbox.py", "-q", "--no-header",
                    "-p", "no:cacheprovider", "--junitxml", xj],
                   cwd=workdir, env=env, capture_output=True, text=True, timeout=300)
    out = {}
    if os.path.exists(xj):
        for tc in ET.parse(xj).getroot().iter("testcase"):
            st = "PASSED"
            if tc.find("failure") is not None or tc.find("error") is not None:
                st = "FAILED"
            elif tc.find("skipped") is not None:
                st = "SKIPPED"
            out[tc.get("name")] = st
        os.remove(xj)
    return out


def make_relaxc(ir, part):
    """只翻 tier=C 的位段（确认"文档没给访问码"的那些）⇒ 与 UNVERIFIED 分开计量。"""
    import copy
    out = copy.deepcopy(ir)
    n = 0
    for r in out["registers"]:
        if r.get("access") != "RW":
            continue
        for f in r.get("fields", []):
            if f.get("tier") == "C":
                f["access"] = "RW"
                f["desc"] = "[仅 C 档变体] %s" % str(f.get("desc", ""))
                n += 1
    vpath = os.path.join(ROOT, "d2d", "ir", "%s_variant_relaxc_ir.json" % part)
    json.dump(out, io.open(vpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return vpath, n


def chip_matrix(part, tier):
    """逐颗 × 逐份 × 逐断言的状态矩阵。tier=gold|relax|relaxc"""
    rows = json.load(io.open(os.path.join(ROOT, "d2d", "eval", "results_gen_%s.json" % TAGS[part]), encoding="utf-8"))
    gp = os.path.join(ROOT, "d2d", "ir", "%s_gold_ir.json" % part)
    if tier == "gold":
        ir_file = "%s_gold_ir.json" % part
    elif tier == "relaxc":
        make_relaxc(json.load(io.open(gp, encoding="utf-8")), part)
        ir_file = "%s_variant_relaxc_ir.json" % part
    else:
        from rescore_variant import make_variant
        make_variant(json.load(io.open(gp, encoding="utf-8")), part, tier)
        ir_file = "%s_variant_%s_ir.json" % (part, tier)
    work = os.path.join(ROOT, "d2d", "eval", "_mt_%s_%s" % (part, tier))
    m = defaultdict(lambda: {"PASSED": 0, "FAILED": 0, "SKIPPED": 0})
    green = 0
    for e in rows:
        st = run_sample(part, e["code"], ir_file, work)
        if not any(v == "FAILED" for v in st.values()):
            green += 1
        for t, v in st.items():
            m[t][v] += 1
    shutil.rmtree(work, ignore_errors=True)
    return m, green, len(rows)


def rule_of_three(n):
    return round((1 - 0.05 ** (1.0 / n)) * 100, 1) if n else None


def cluster_boot(per_chip):
    """per_chip: [(fail, applicable), ...]；按芯片重抽，给 95% 百分位 CI。"""
    k = len(per_chip)
    if k == 0 or sum(n for _, n in per_chip) == 0:
        return None
    rng = random.Random(20261007)
    acc = []
    for _ in range(B):
        tot = den = 0
        for _i in range(k):
            f, n = per_chip[rng.randrange(k)]
            tot += f
            den += n
        if den:
            acc.append(tot / den)
    acc.sort()
    return {"clusters": k, "lo": round(acc[int(0.025 * len(acc))] * 100, 1),
            "hi": round(acc[int(0.975 * len(acc)) - 1] * 100, 1)}


def binomial_ci(p, n):
    if not n:
        return None
    se = (max(p * (1 - p), 1e-12) / n) ** 0.5
    return {"lo": round(max(0.0, p - 1.96 * se) * 100, 1), "hi": round(min(1.0, p + 1.96 * se) * 100, 1)}


def avg_ranks(x):
    idx = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and x[idx[j + 1]] == x[idx[i]]:
            j += 1
        rv = (i + j) / 2.0 + 1
        for k in range(i, j + 1):
            r[idx[k]] = rv
        i = j + 1
    return r


def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    da = sum((x - ma) ** 2 for x in a) ** 0.5
    db = sum((y - mb) ** 2 for y in b) ** 0.5
    return num / (da * db) if da * db else 0.0


def spearman(x, y, exact_max=8, Bmc=200000, seed=20261007):
    """并列修正的 Spearman；n≤8 用全排列精确 p，更大的 n 用 20 万次蒙特卡洛置换。"""
    import itertools, random
    rx, ry = avg_ranks(x), avg_ranks(y)
    rho = pearson(rx, ry)
    obs = abs(rho)
    n = len(x)
    if n <= exact_max:
        ge = tot = 0
        for perm in itertools.permutations(ry):
            tot += 1
            ge += abs(pearson(rx, list(perm))) >= obs - 1e-12
        return round(rho, 3), ge / tot, "exact_perm(%d)" % tot
    rng = random.Random(seed)
    ge = 0
    for _ in range(Bmc):
        y2 = list(ry)
        rng.shuffle(y2)
        ge += abs(pearson(rx, y2)) >= obs - 1e-12
    return round(rho, 3), ge / Bmc, "MC_perm(%d)" % Bmc


def declared(ir, t):
    """该芯片的 IR 为这条断言**声明了几个可断对象**；0 ⇒ 通过是白送的，不能进分母。
    实测踩到：ADS1220 无 RO 寄存器也无 RO 位域，但 harness 不 skip ③，于是白得 12 次通过。"""
    R = ir["registers"]
    F = lambda r: r.get("fields", [])
    if t == "test_reset_values":
        return sum(1 for r in R if r.get("reset") is not None)
    if t == "test_readonly_protection":
        return (sum(1 for r in R if r.get("access") == "RO") +
                sum(1 for r in R if r.get("access") == "RW" and any(f.get("access") == "RO" for f in F(r))))
    if t == "test_rw_field_persistence":
        return sum(1 for r in R if r.get("access") == "RW" and any(f.get("access") not in ("RO", "UNSPEC") for f in F(r)))
    if t == "test_write_trigger_fields":
        return sum(1 for r in R for f in F(r) if f.get("read_as") is not None)
    if t == "test_single_byte_semantics":
        return sum(1 for r in R if r.get("size") == 1 or r.get("byte_addr") or r.get("nbytes") == 1)
    if t == "test_read_write_alias":
        return sum(1 for r in R if r.get("write_addr") or any(f.get("write_addr") for f in F(r)))
    if t == "test_clear_on_read":
        return sum(1 for r in R if r.get("cor_addr") or any(f.get("cor_addr") for f in F(r)))
    if t == "test_write_only_reset_key":
        return sum(1 for r in R if r.get("write_key") is not None or r.get("access") == "W")
    return 1


def main():
    from joblock import acquire as _lock
    _lock("main_table")
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="只跑新落分的两颗（调试用）")
    args = ap.parse_args()
    chips = ["ADS1220", "LM83", "TPS23861", "TMP126"] if args.quick else ORDER
    chips = [c for c in chips if os.path.exists(os.path.join(ROOT, "d2d", "eval", "results_gen_%s.json" % TAGS[c]))]

    strict, relax, relaxc = {}, {}, {}
    per_chip_green = {}
    for c in chips:
        strict[c], g_s, n_s = chip_matrix(c, "gold")
        relax[c], g_r, _ = chip_matrix(c, "relax")
        relaxc[c], _, _ = chip_matrix(c, "relaxc")
        per_chip_green[c] = {"strict": g_s, "relax": g_r, "n": n_s}
        print("  %-8s 全绿 strict=%2d/%d relax=%2d/%d" % (c, g_s, n_s, g_r, n_s), flush=True)

    # —— 维度汇聚 ——
    dims = {}
    vac = []
    ir_cache = {c: json.load(io.open(os.path.join(ROOT, "d2d", "ir", "%s_gold_ir.json" % c), encoding="utf-8"))
                for c in chips}
    allt = sorted({t for c in chips for t in strict[c]})
    for t in allt:
        pts = []
        for c in chips:
            s = strict[c].get(t, {"PASSED": 0, "FAILED": 0, "SKIPPED": 0})
            appl = s["PASSED"] + s["FAILED"]
            if not appl:
                continue
            if declared(ir_cache[c], t) == 0 and s["FAILED"] == 0:
                vac.append({"chip": c, "test": t, "passed_for_free": s["PASSED"],
                            "why": "IR 未声明该结构，harness 不 skip ⇒ 白送通过，已从分母剔除"})
                continue
            pts.append({"chip": c, "fail": s["FAILED"], "applicable": appl, "passed": s["PASSED"]})
        if not pts:
            continue
        fail = sum(p["fail"] for p in pts)
        den = sum(p["applicable"] for p in pts)
        p_ = fail / den
        row = {"test": t, "no": DIM.get(t, ("?", t))[0], "label": DIM.get(t, ("?", t))[1],
               "clusters": len(pts), "fail": fail, "applicable": den,
               "rate": round(p_ * 100, 1), "per_chip": pts,
               "binomial_ci_if_wrongly_independent": binomial_ci(p_, den)}
        if fail == 0:
            row["ci"] = None
            row["bound"] = {"method": "rule of three", "upper_pct": rule_of_three(den)}
        elif len(pts) >= MIN_CLUSTER:
            row["ci"] = cluster_boot([(p["fail"], p["applicable"]) for p in pts])
        else:
            row["ci"] = None
            row["note"] = "聚类数 %d < %d：不给 CI，只看逐颗点图" % (len(pts), MIN_CLUSTER)
        dims[t] = row
    if vac:
        print("\n!! 白送通过（已从分母剔除）：", json.dumps(vac, ensure_ascii=False))

    # —— ④a / ④b 拆分 ——
    f4s = sum(strict[c].get("test_rw_field_persistence", {}).get("FAILED", 0) for c in chips)
    f4r = sum(relax[c].get("test_rw_field_persistence", {}).get("FAILED", 0) for c in chips)
    f4c = sum(relaxc[c].get("test_rw_field_persistence", {}).get("FAILED", 0) for c in chips)
    d4 = sum(strict[c].get("test_rw_field_persistence", {}).get("PASSED", 0) +
             strict[c].get("test_rw_field_persistence", {}).get("FAILED", 0) for c in chips)
    conv_chips = []
    tier_count = defaultdict(int)
    from rescore_variant import is_convention_bit
    for c in chips:
        segs = [f for r in ir_cache[c]["registers"] if r.get("access") == "RW"
                for f in r.get("fields", []) if is_convention_bit(f)]
        if segs:
            conv_chips.append(c)
        for f in segs:
            tier_count[f.get("tier") or "无tier字段"] += 1
    split = {"d4_applicable": d4, "strict_fail": f4s,
             "relax_c_only_fail": f4c, "relax_cu_fail": f4r,
             "4a_documented_fail": f4r,
             "4b_confirmed_convention_fail": f4s - f4c,
             "4u_unverified_fail": f4c - f4r,
             "4a_pct": round(100.0 * f4r / d4, 1) if d4 else None,
             "4b_pct": round(100.0 * (f4s - f4c) / d4, 1) if d4 else None,
             "4u_pct": round(100.0 * (f4c - f4r) / d4, 1) if d4 else None,
             "4b_note": "④b＝只翻 tier=C 就能消掉的失败（文档确实没给逐位访问码，纯 Q0 约定）；"
                        "④u＝再翻 UNVERIFIED 才多消掉的（证据未核，不计入能力结论）；"
                        "④a＝两档都翻仍失败（真读不懂）",
             "4b_tier_breakdown": dict(tier_count),
             "chips_with_convention_bits": conv_chips}

    # —— 梯度：事后分组的最优组差 + 先验指标的 Spearman ——
    score_of = {c: {"applicable": sum(p["applicable"] for r in dims.values() for p in r["per_chip"] if p["chip"] == c),
                    "passed": sum(p["passed"] for r in dims.values() for p in r["per_chip"] if p["chip"] == c)}
                for c in chips}
    rate = {c: score_of[c]["passed"] / max(score_of[c]["applicable"], 1) for c in chips}
    feats = {}
    for c in chips:
        ir = json.load(io.open(os.path.join(ROOT, "d2d", "ir", "%s_gold_ir.json" % c), encoding="utf-8"))
        R = ir["registers"]
        feats[c] = {"regs": len(R), "fields": sum(len(r.get("fields", [])) for r in R),
                    "special": sum(1 for r in R if r.get("write_key") or r.get("cor_addr") or r.get("write_addr")
                                   or r.get("access") in ("RO", "W")
                                   or any(f.get("read_as") is not None or f.get("access") == "RO" for f in r.get("fields", [])))}
    grad = {}
    PAPER_SIMPLE = {"BMP280", "TMP1075", "TMP100", "TMP102"}
    eight = [c for c in chips if c in ("TMP1075", "BMP280", "TMP102", "BME280", "TMP100",
                                       "INA3221", "HDC2021", "TMP117")]
    if len(eight) == 8:
        half = 4
        gaps = []
        for g in itertools.combinations(eight, half):
            a = [rate[c] for c in g]
            b = [rate[c] for c in eight if c not in g]
            gaps.append(sum(a) / len(a) - sum(b) / len(b))
        obs = sum(rate[c] for c in eight if c in PAPER_SIMPLE) / 4 - \
              sum(rate[c] for c in eight if c not in PAPER_SIMPLE) / 4
        best = max(abs(x) for x in gaps)
        ge = sum(1 for x in gaps if abs(x) >= abs(obs) - 1e-12)
        p_exact = ge / len(gaps)
        grad["post_hoc_4v4_on_8chips"] = {
            "observed_gap_pp": round(abs(obs) * 100, 1),
            "max_possible_gap_pp": round(best * 100, 1),
            "is_the_best_possible_split": abs(abs(obs) - best) < 1e-9,
            "exact_p_for_this_split": round(p_exact, 4),
            "bonferroni_p_over_all_splits": round(min(1.0, p_exact * len(gaps)), 3),
            "n_splits": len(gaps)}
    grad["spearman"] = {}
    for tag, grp in [("all_chips", chips), ("excl_positive_control", [c for c in chips if c != "ADS1220"])]:
        if len(grp) < 5:
            continue
        y = [rate[c] for c in grp]
        grad["spearman"][tag] = {"n_chips": len(grp), "features": {}}
        for k, nm in [("regs", "寄存器数"), ("fields", "位域数"), ("special", "特殊语义寄存器数")]:
            x = [feats[c][k] for c in grp]
            rho, p, how = spearman(x, y)
            grad["spearman"][tag]["features"][k] = {
                "label": nm, "rho": rho, "p": round(p, 4), "method": how,
                "values": {c: feats[c][k] for c in grp}}

    out = {"generated": "2026-10-07", "chips": chips, "n_samples_per_chip": 12,
           "note_denominator": "passed/applicable；SKIPPED 由 IR 声明决定，不计入分母；白送通过另列",
           "min_clusters_for_ci": MIN_CLUSTER, "bootstrap_B": B,
           "per_chip_green": per_chip_green, "per_chip_scored": score_of,
           "vacuous_excluded": vac,
           "dimensions": dims, "assertion4_split": split, "gradient": grad,
           "per_chip_rate_pct": {c: round(rate[c] * 100, 1) for c in chips}}
    dst = os.path.join(ROOT, "d2d", "eval", "main_table.json")
    json.dump(out, io.open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    csvp = os.path.join(ROOT, "d2d", "eval", "main_table.csv")
    with io.open(csvp, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["断言", "名称", "聚类数(颗)", "失败/适用", "失败率%", "推断方式", "区间",
                    "逐颗点图", "人工裁决"])
        for t, r in sorted(dims.items(), key=lambda kv: (kv[1]["no"])):
            ci = r.get("ci")
            rng = "%s–%s%%" % (ci["lo"], ci["hi"]) if ci else (
                "≤%s%%" % r["bound"]["upper_pct"] if r.get("bound") else "不给 CI")
            way = ("聚类 bootstrap" if ci else ("rule of three" if r.get("bound") else "描述性"))
            pts = " ".join("%s %d/%d" % (p["chip"], p["fail"], p["applicable"]) for p in r["per_chip"])
            w.writerow([r["no"], r["label"], r["clusters"], "%d/%d" % (r["fail"], r["applicable"]),
                        r["rate"], way, rng, pts, ""])
    print("\n%-4s %-32s %-3s %-9s %-8s %-16s %s" %
          ("#", "维度", "颗", "失败/适用", "失败率", "推断", "区间"))
    for t, r in sorted(dims.items(), key=lambda kv: (kv[1]["no"])):
        ci = r.get("ci")
        rng = "%s–%s%%" % (ci["lo"], ci["hi"]) if ci else (
            "≤%s%%" % r["bound"]["upper_pct"] if r.get("bound") else "—")
        way = "聚类boot" if ci else ("RoF" if r.get("bound") else "不给CI(k=%d)" % r["clusters"])
        print("%-4s %-32s %-3d %-9s %-8s %-16s %s" %
              (r["no"], r["label"], r["clusters"], "%d/%d" % (r["fail"], r["applicable"]),
               "%s%%" % r["rate"], way, rng))
    print("\n④ 拆分：strict 失败 %d/%d=%s%%  →  ④a 已文档化位域 %d (%s%%) ＋ ④b 确认C档 %d (%s%%) ＋ ④u 未定档 %d (%s%%)" % (
        f4s, d4, round(100.0 * f4s / d4, 1), split["4a_documented_fail"], split["4a_pct"],
        split["4b_confirmed_convention_fail"], split["4b_pct"],
        split["4u_unverified_fail"], split["4u_pct"]))
    print("带约定位的芯片：", conv_chips)
    print("梯度：", json.dumps(grad.get("post_hoc_4v4_on_8chips"), ensure_ascii=False))
    for tag, blk in grad["spearman"].items():
        print("  [%s, n=%d]" % (tag, blk["n_chips"]))
        for k, v in blk["features"].items():
            print("    %-12s rho=%+.3f p=%.4f (%s)" % (v["label"], v["rho"], v["p"], v["method"]))
    print("\n逐颗点图：", json.dumps(out["per_chip_rate_pct"], ensure_ascii=False))
    print("\n产物:", dst, "\n     ", csvp)


if __name__ == "__main__":
    main()
