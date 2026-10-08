# -*- coding: utf-8 -*-
"""加样批跑：同一批金标 IR 上补 seeds 4,5,6 × 4 样本（新 tag `<part>kt_b`，绝不覆盖旧产物）。

它服务哪个结论（你要求"别为加而加"，这是答案）：
  1) 逐颗断言级通过率的精度——n=12 → n=24，把每颗的 ±13~25pp 收窄；
  2) **同 IR 同模型的种子间方差**：这是聚类 CI 给不了的东西，用来支撑
     "temp=0.7 下样本间波动有多大 ⇒ 单颗分数不该被读成能力排名"。
  它**不**收窄按芯片聚类的 CI（那要更多芯片，不是更多样本），所以别拿它去救梯度结论。
"""
import sys, os, io, re, json, time, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_setup"))
sys.stdout.reconfigure(encoding="utf-8")
import chip_chain as cc
from joblock import acquire

LOG = os.path.join(ROOT, "_out", "ressample.log")
CHIPS = ["TMP1075", "BMP280", "TMP102", "BME280", "TMP100", "INA3221", "HDC2021",
         "TMP117", "ADS1220", "LM83", "TPS23861", "TMP126", "LIS2DW12", "INA226"]


def log(m):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), m)
    print(line, flush=True)
    io.open(LOG, "a", encoding="utf-8").write(line + "\n")


def one(ssh, part, seeds, n, hours_left):
    tag = "%skt_b" % part.lower()
    out_remote = "%s/eval/results_gen_%s.json" % (cc.RD2D, tag)
    logf = "/root/%s.log" % tag
    lock = "/root/.d2d_gpu_lock"
    rc, o, _ = ssh.run("test -f %s && echo HAVE || echo MISSING" % out_remote, timeout=90)
    if "HAVE" in (o or ""):
        log("%s 已有 %s，跳过" % (part, tag))
        return True
    rc, o, _ = ssh.run('if mkdir %s 2>/dev/null; then if pgrep -f "g[e]n_code.py" >/dev/null; then '
                       'rmdir %s; echo BUSY; else echo GOT; fi; else echo BUSY; fi' % (lock, lock), timeout=120)
    if "GOT" not in (o or ""):
        log("%s GPU 锁被占，等下一轮" % part)
        return False
    cmd = ('cd %s && %s nohup python -u eval/gen_code.py --model-path %s --ir %s_gold_ir.json '
           '--tag %s --n %d --temperature 0.7 --seeds %s > %s 2>&1 & echo PID=$!'
           % (cc.RD2D, cc.ENVS, cc.MODEL, part, tag, n, seeds, logf))
    rc, o, e = ssh.run(cmd, timeout=120)
    pid = re.search(r"PID=(\d+)", o or "")
    log("%s 加样点火 %s seeds=%s tag=%s" % (part, pid.group(1) if pid else "?", seeds, tag))
    t0 = time.time()
    while time.time() - t0 < min(hours_left, 1.2) * 3600:
        time.sleep(70)
        rc, o, _ = ssh.run('tail -1 %s | tr -d "\\r" | cut -c1-100; echo -n "|N="; grep -c "^\\[" %s 2>/dev/null; '
                           'pgrep -f "g[e]n_code.py" >/dev/null && echo ALIVE || echo EXITED' % (logf, logf), timeout=180)
        s = (o or "").replace("\n", " ")
        log("%s 进度: %s" % (part, s[-120:]))
        if "EXITED" in s:
            break
    ssh.run('rmdir %s 2>/dev/null; true' % lock, timeout=60)
    rc, o, _ = ssh.run('test -f %s && echo HAVE || echo MISSING' % out_remote, timeout=90)
    if "HAVE" not in (o or ""):
        log("%s 无结果文件" % part)
        return False
    data = ssh.get_b64(out_remote)
    lp = os.path.join(ROOT, "d2d", "eval", "results_gen_%s.json" % tag)
    if os.path.exists(lp):
        log("%s 本地已有，不覆盖" % part)
        return True
    open(lp, "wb").write(data)
    rows = json.loads(data.decode("utf-8"))
    log("%s 拉回 %d 行（%.1f 分钟）" % (part, len(rows), (time.time() - t0) / 60))
    return True


YIELD = os.path.join(ROOT, "_out", "yield_to_chain")


def main():
    acquire("ressample")
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=float, default=4.0)
    ap.add_argument("--seeds", default="4,5,6")
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--parts", nargs="+", default=CHIPS)
    a = ap.parse_args()
    t_end = time.time() + a.hours * 3600
    ssh = cc.SSH()
    log("加样开始 parts=%s seeds=%s n=%d" % (a.parts, a.seeds, a.n))
    pend = list(a.parts)
    while pend and time.time() < t_end - 600:
        # 优雅让位：换挡靠外部 kill 会留下孤儿 GPU 锁（2026-10-07 踩过），
        # 所以改成放一个标志文件，本进程在当前颗跑完并释放锁后自己退出。
        if os.path.exists(YIELD):
            log("检测到 yield 标志，主动让位并退出（余下 %s）" % pend)
            os.remove(YIELD)
            break
        for p in list(pend):
            if one(ssh, p, a.seeds, a.n, (t_end - time.time()) / 3600):
                pend.remove(p)
        if pend:
            time.sleep(60)
    log("加样结束，未完成 %s" % pend)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log("异常：\n" + cc.traceback.format_exc())
        raise
