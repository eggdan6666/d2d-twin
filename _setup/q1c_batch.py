# -*- coding: utf-8 -*-
"""Q1c 干净消融臂批跑调度器（3 颗芯片：INA3221, BME280, LIS2DW12）。

单变量：同模型(14B)、同温度 0.7、同 seeds 1,2,3、同 n=4（共 12 份/芯片）。
消融特征：剥除 reset 结构化键 + 清洗 desc 散文字符串中的数值（0x..., ...h, 纯数字替换为 —）。
彻底根除 E19 散文泄漏，给出干净的“无规格输入下的真实抽取/记忆能力”结论。
"""
import sys, os, io, re, json, time, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_setup"))
sys.stdout.reconfigure(encoding="utf-8")
from joblock import acquire

BATCH = [
    ("INA3221", "ina3221q1c"),
    ("BME280", "bme280q1c"),
    ("LIS2DW12", "lis2dw12q1c"),
]
LOG = os.path.join(ROOT, "_out", "q1c_batch.log")


def log(msg):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    with io.open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def main():
    acquire("q1c_batch")
    log("=== Q1c 干净消融批启动 ===")
    results = {}
    for part, tag in BATCH:
        lp = os.path.join(ROOT, "d2d", "eval", "results_gen_%s.json" % tag)
        if os.path.exists(lp):
            log("%s 已存在本地结果 %s，直接分析" % (part, lp))
        else:
            log(">>> 开始执行 %s (%s) <<<" % (part, tag))
            cmd = [sys.executable, "-X", "utf8", os.path.join(ROOT, "_setup", "q1_experiment.py"),
                   "--part", part, "--tag", tag, "--scrub-desc"]
            env = dict(os.environ, PYTHONIOENCODING="utf-8")
            p = subprocess.run(cmd, env=env, text=True)
            if p.returncode != 0:
                log("!! %s 执行异常 exit code %d" % (part, p.returncode))
                continue
        if os.path.exists(lp):
            data = json.load(open(lp, encoding="utf-8"))
            n_samples = len(data)
            n_reset_fail = 0
            n_all_green = 0
            for r in data:
                if r.get("rc") == 0:
                    n_all_green += 1
                t = r.get("tail") or ""
                if re.search(r"FAILED \S*::test_reset_values", t):
                    n_reset_fail += 1
            results[part] = {
                "tag": tag,
                "n_samples": n_samples,
                "reset_fail": n_reset_fail,
                "reset_fail_rate_pct": round(100.0 * n_reset_fail / n_samples, 1) if n_samples else 0.0,
                "all_green": n_all_green,
            }
            log("  [%s 完成] 样本=%d, ②复位值失败=%d/%d (%.1f%%), 全绿=%d" % (
                part, n_samples, n_reset_fail, n_samples,
                results[part]["reset_fail_rate_pct"], n_all_green))

    summary_file = os.path.join(ROOT, "d2d", "eval", "q1c_ablation_summary.json")
    json.dump(results, io.open(summary_file, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    log("=== Q1c 批完成，汇总落盘: %s ===" % summary_file)


if __name__ == "__main__":
    main()
