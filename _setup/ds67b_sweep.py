# -*- coding: utf-8 -*-
"""第二模型（DeepSeek-Coder-6.7B）横向对照批跑器。

为什么要它：金标是唯一不可自动化的环节，我手写金标的 25-40 分钟里 GPU 本来会空转；
6.7B 复跑现成金标**不需要任何新金标**，正好把断档变成数据。它回答的是便宜但必要的问题：
"这些分数是不是 Qwen 特有的"。

纪律（重要）：
  · tag = ds67b<part>，**绝不与 14B 的 <part>kt 同名**，否则会覆盖主线产物；
  · 取同一把原子锁 /root/.d2d_gpu_lock + pgrep gen_code，与三条主链串行；
  · 先 --smoke 1 份验 Llama 架构在这套 DCU 栈上能出码，再批跑。
"""
import sys, os, io, re, json, time, argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_setup"))
import chip_chain as cc

ROOT = cc.ROOT
MODEL_DS = "/root/private_data/models/deepseek-coder-6.7b-instruct"
CHIPS = ["TMP1075", "BMP280", "TMP102", "BME280", "TMP100", "INA3221", "HDC2021",
         "TMP117", "ADS1220", "LM83", "TPS23861", "TMP126", "LIS2DW12", "INA226"]
LOG = os.path.join(ROOT, "_out", "ds67b.log")


def log(msg):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    with io.open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def acquire(ssh):
    rc, o, _ = ssh.run('if mkdir /root/.d2d_gpu_lock 2>/dev/null; then if pgrep -f "g[e]n_code.py" >/dev/null; then '
                       'rmdir /root/.d2d_gpu_lock; echo BUSY; else echo GOT; fi; else echo BUSY; fi', timeout=120)
    return "GOT" in (o or "")


def sweep(ssh, part, n, seeds, hours_left):
    tag = "ds67b%s" % part.lower()
    ir = "%s_gold_ir.json" % part
    out_remote = "%s/eval/results_gen_%s.json" % (cc.RD2D, tag)
    logf = "/root/%s.log" % tag
    rc, o, _ = ssh.run("test -f %s && echo HAVE || echo MISSING" % out_remote, timeout=60)
    if "HAVE" in (o or ""):
        log("%s 已有结果（%s），跳过" % (part, tag))
        return True
    if not acquire(ssh):
        log("%s GPU 锁被占，本轮跳过" % part)
        return False
    cmd = ('cd %s && %s nohup python -u eval/gen_code.py --model-path %s --ir %s '
           '--tag %s --n %d --temperature 0.7 --seeds %s > %s 2>&1 & echo PID=$!'
           % (cc.RD2D, cc.ENVS, MODEL_DS, ir, tag, n, seeds, logf))
    rc, o, e = ssh.run(cmd, timeout=120)
    pid = re.search(r"PID=(\d+)", o or "")
    log("%s 点火 %s tag=%s model=6.7B" % (part, pid.group(1) if pid else "?", tag))
    t0 = time.time()
    while time.time() - t0 < min(hours_left, 1.2) * 3600:
        time.sleep(60)
        rc, o, _ = ssh.run('tail -1 %s | tr -d "\\r" | cut -c1-110; echo -n "|N="; grep -c "^\\[" %s 2>/dev/null; '
                           'pgrep -f "g[e]n_code.py" >/dev/null && echo ALIVE || echo EXITED' % (logf, logf), timeout=180)
        s = (o or "").replace("\n", " ")
        log("%s 进度: %s" % (part, s[-130:]))
        if "EXITED" in s:
            break
    ssh.run('rmdir /root/.d2d_gpu_lock 2>/dev/null; true', timeout=60)
    rc, o, _ = ssh.run('test -f %s && echo HAVE || echo MISSING; tail -2 %s | tr -d "\\r" | cut -c1-140'
                       % (out_remote, logf), timeout=120)
    if "HAVE" not in (o or ""):
        log("%s 无结果文件：%s" % (part, (o or "").replace("\n", " ")[:140]))
        return False
    data = ssh.get_b64(out_remote)
    lp = os.path.join(ROOT, "d2d", "eval", "results_gen_%s.json" % tag)
    if os.path.exists(lp):
        log("%s 本地已存在，不覆盖：%s" % (part, lp))
        return True
    open(lp, "wb").write(data)
    rows = json.loads(data.decode("utf-8"))
    green = sum(1 for r in rows if r.get("rc") == 0)
    log("%s 拉回 %d 行，全绿 %d/%d（%.1f 分钟）" % (part, len(rows), green, len(rows), (time.time() - t0) / 60))
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="只跑 1 份，验证 6.7B 能出码")
    ap.add_argument("--hours", type=float, default=3.0)
    args = ap.parse_args()
    t_end = time.time() + args.hours * 3600
    ssh = cc.SSH()
    log("6.7B 批跑开始（smoke=%s）" % args.smoke)
    if args.smoke:
        ok = sweep(ssh, "TMP102", 1, "1", 0.4)
        log("smoke 结果：%s" % ("可批跑" if ok else "失败，先别批跑"))
        return
    for p in CHIPS:
        if (t_end - time.time()) / 3600 < 0.25:
            log("剩余预算不足 15 分钟，停止接新活")
            break
        sweep(ssh, p, 4, "1,2,3", (t_end - time.time()) / 3600)
    log("6.7B 批跑结束")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log("异常退出：\n" + cc.traceback.format_exc())
        raise
