# -*- coding: utf-8 -*-
"""Q0 保留位裁决的离线重判工具（零 GPU，几秒钟）。

作用：对同一批**已生成的代码**（results_gen_*.json 里存着 12 份 simulator 源码），
用两套 IR 约定各判一遍，直接给出"放宽保留位"对分数的真实影响——
不需要重新生成，因此这个裁决**随时可以推翻重算**，不必在信息不全时仓促定。

两套约定：
  strict（现状）：表格未给访问码的保留位编成 RO + 复位 0 → 写全 1 必须读回 0
  relax        ：同样的位编成普通 RW → 写全 1 读回全 1 也算对（纯寄存器堆免罚）

字段识别：fields 里 name 含 UNUSED/RESERVED/RES 或 desc 含"恒 0/未用/保留"的位段。
被改动但不属于保留位的字段（如 TMP102 表格里明确给访问码的 R1/R0/AL）一律不动——
那是手册写了访问码的只读位，与 Q0 无关，混进来会污染对照。

用法: python _setup/rescore_variant.py [--chips TMP102 BME280 TMP100 BMP280]
"""
import sys, os, io, re, json, csv, shutil, argparse, subprocess
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")

TAGS = {"TMP102": "tmp102kt", "BME280": "bme280kt", "TMP100": "tmp100kt",
        "BMP280": "bmp280kt", "TMP1075": "kt", "INA3221": "ina3221kt",
        "HDC2021": "hdc2021kt", "TMP117": "tmp117kt", "ADS1220": "ads1220kt",
        "LM83": "lm83kt",
        "TPS23861": "tps23861kt",
        "TMP126": "tmp126kt"}
RES_NAME = re.compile(r"UNUSED|RESERVED|_RES\b|^RES\d*$", re.I)
RES_DESC = re.compile(r"恒 0|未用|保留|tie.?0|not used", re.I)


def is_convention_bit(f):
    """只认『手册没给访问码、被我编成 RO+复位0 的保留位』。

    tier 字段（见 _setup/tier_stamp.py）优先于名字猜测：
      A/B = 手册逐位给了访问码（读 0 或 R/W）⇒ **与 Q0 裁决无关**，永远不翻转；
      C   = 手册没给访问码 ⇒ 唯一受 Q0 影响的档；
      UNVERIFIED / 无 tier 字段 = 待人工定档，暂按候选处理，落进 ④u 而不是 ④b。
    """
    if f.get("tier") in ("A", "B"):
        return False
    if f.get("tier") == "C":
        # C 的定义是"手册没给逐位访问码"，与复位值是否非零无关。
        # INA226 的 CONFIG[14:12]（POR=100b）是第一个非零 C 档实例，
        # 若仍要求 reset==0 会被静默漏算，④b 就少一份。
        return True
    return (f.get("access") == "RO" and int(str(f.get("reset", 0))) == 0
            and (RES_NAME.search(str(f.get("name", ""))) or RES_DESC.search(str(f.get("desc", "")))))


def make_variant(ir, part, tier="relax"):
    n = 0
    for r in ir["registers"]:
        if r["access"] != "RW":
            continue
        for f in r.get("fields", []):
            if is_convention_bit(f):
                f["access"] = "RW" if tier == "relax" else "UNSPEC"
                f["desc"] = "[%s 变体] %s" % (tier, str(f.get("desc", ""))); n += 1
    vpath = os.path.join(ROOT, "d2d", "ir", "%s_variant_%s_ir.json" % (part, tier))
    json.dump(ir, io.open(vpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return vpath, n


def rescore(part, tag, ir_name, workdir, diag=False):
    rows = json.load(io.open(os.path.join(ROOT, "d2d", "eval", "results_gen_%s.json" % tag), encoding="utf-8"))
    shutil.rmtree(workdir, ignore_errors=True)
    os.makedirs(workdir)
    shutil.copy(os.path.join(ROOT, "d2d", "rtl", "base_sensor.py"), workdir)
    shutil.copy(os.path.join(ROOT, "d2d", "eval", "test_d2d_blackbox.py"), workdir)
    sim = "%s_simulator.py" % part.lower()
    green = 0
    P = F = 0
    dist = Counter()
    n_diag = wrote = 0
    for e in rows:
        io.open(os.path.join(workdir, sim), "w", encoding="utf-8").write(e["code"])
        env = dict(os.environ, D2D_IR=ir_name, PYTHONIOENCODING="utf-8")
        dp = os.path.join(workdir, "d2d_diag.json")
        if diag:
            env["D2D_DIAG"] = "1"
            if os.path.exists(dp):
                os.remove(dp)
        r = subprocess.run([sys.executable, "-m", "pytest", "test_d2d_blackbox.py", "-q", "--no-header", "-p", "no:cacheprovider"],
                           cwd=workdir, env=env, capture_output=True, text=True, timeout=300)
        out = (r.stdout or "")
        mf = re.search(r"(\d+) failed", out); mp = re.search(r"(\d+) passed", out)
        nf = int(mf.group(1)) if mf else 0
        np_ = int(mp.group(1)) if mp else 0
        F += nf; P += np_
        if nf == 0:
            green += 1
        for t in re.findall(r"FAILED \S+::(\w+)", out):
            dist[t] += 1
        if diag and os.path.exists(dp):
            obs = json.load(io.open(dp, encoding="utf-8")).get("unspecified_bits", [])
            if obs:
                n_diag += 1
                if any(o["readback"] != 0 for o in obs):
                    wrote += 1
    d = dict(n=len(rows), green=green, assert_pass=P, assert_total=P + F,
             rate=round(100.0 * P / (P + F), 1) if P + F else None, fail_by_test=dict(dist))
    if diag:
        d["diagnostic"] = {"samples_observed": n_diag, "reserved_written_as_storage": wrote,
                           "pct": round(100.0 * wrote / n_diag, 1) if n_diag else None,
                           "note": "UNSPEC 档不计分：只统计模型把未文档化保留位当可写存储的比例"}
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chips", nargs="+", default=["TMP102", "BME280", "TMP100", "BMP280"])
    args = ap.parse_args()
    out = []
    print("%-9s %-20s %-20s %-20s %s" % ("chip", "strict(现状)", "relax(放宽)", "unspec(不判分+记录)", "位数"))
    for part in args.chips:
        tag = TAGS[part]
        rp = os.path.join(ROOT, "d2d", "eval", "results_gen_%s.json" % tag)
        p = os.path.join(ROOT, "d2d", "ir", "%s_gold_ir.json" % part)
        if not os.path.exists(p) or not os.path.exists(rp):
            print("%-9s 缺 IR 或结果，跳过" % part); continue
        ir = json.load(io.open(p, encoding="utf-8"))
        _, nchanged = make_variant(ir, part, "relax")
        make_variant(json.load(io.open(p, encoding="utf-8")), part, "unspec")
        work = os.path.join(ROOT, "d2d", "eval", "_rescore_%s" % part)
        a = rescore(part, tag, "%s_gold_ir.json" % part, work)
        b = rescore(part, tag, "%s_variant_relax_ir.json" % part, work)
        c = rescore(part, tag, "%s_variant_unspec_ir.json" % part, work, diag=True)
        d = c.get("diagnostic", {})
        print("%-9s 绿%2d/%d %5.1f%%   绿%2d/%d %5.1f%%   绿%2d/%d %5.1f%%  保留位被当可写存储 %s/%s   %d 段" % (
            part, a["green"], a["n"], a["rate"], b["green"], b["n"], b["rate"],
            c["green"], c["n"], c["rate"], d.get("reserved_written_as_storage", "?"),
            d.get("samples_observed", "?"), nchanged))
        out.append({"chip": part, "convention_bits": nchanged, "strict": a, "relax": b, "unspec": c})
        shutil.rmtree(work, ignore_errors=True)
    dst = os.path.join(ROOT, "d2d", "eval", "q0_rescore_compare.json")
    json.dump(out, io.open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n对照明细:", dst)


if __name__ == "__main__":
    main()
