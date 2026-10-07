# -*- coding: utf-8 -*-
"""Q1 实验：复位值 0/144 是在测"抽取"还是"转录"？

单变量：同一模型、同温度 0.7、同 seeds 1,2,3、同 n=4、同 IR 文件（判据侧不变），
唯一差别 = prompt 里不给 reset 字段（gen_code.py --strip-reset）。
靶芯片 INA3221：13 个非零复位值，剥掉 reset 后有 6 个在位表/desc 里也推不出来。

基线：results_gen_ina3221kt.json（reset 在 prompt 里）→ ② 0/12 失败。
判读：若 ② 失败数显著上升，说明原结论"照抄寄存器表已被解决"是**我们送分了**，
      应改写成"在给定结构化规格时转录保真度 100%"，并把"抽取"留给 Phase 1.5。
"""
import sys, os, io, re, json, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "_setup"))
sys.stdout.reconfigure(encoding="utf-8")
import chip_chain as cc
from joblock import acquire

PART = (sys.argv[sys.argv.index("--part") + 1] if "--part" in sys.argv else "INA3221")
TAG = (sys.argv[sys.argv.index("--tag") + 1] if "--tag" in sys.argv else "ina3221noreset")
SCRUB = "--scrub-desc" in sys.argv or "q1c" in TAG
LOG = os.path.join(ROOT, "_out", "q1.log")


def log(m):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), m)
    print(line, flush=True)
    io.open(LOG, "a", encoding="utf-8").write(line + "\n")


def gpu_free(ssh):
    rc, o, _ = ssh.run('if mkdir /root/.d2d_gpu_lock 2>/dev/null; then if pgrep -f "g[e]n_code.py" >/dev/null; then '
                       'rmdir /root/.d2d_gpu_lock; echo BUSY; else echo GOT; fi; else echo BUSY; fi', timeout=120)
    return "GOT" in (o or "")


def main():
    acquire("q1")
    ssh = cc.SSH()
    out_remote = "%s/eval/results_gen_%s.json" % (cc.RD2D, TAG)
    logf = "/root/%s.log" % TAG
    rc, o, _ = ssh.run("test -f %s && echo HAVE || echo MISSING" % out_remote, timeout=90)
    if "HAVE" in (o or ""):
        log("已有结果，跳过")
        return

    # 同步最新 gen_code.py 到远端以支持 scrub-desc
    local_gen = os.path.join(ROOT, "d2d", "eval", "gen_code.py")
    remote_gen = "%s/eval/gen_code.py" % cc.RD2D
    ssh.put(local_gen, remote_gen)
    log("已同步 gen_code.py 到远端")

    log("等 GPU 锁")
    for _ in range(60):
        if gpu_free(ssh):
            break
        time.sleep(30)
    else:
        log("等锁超时，退出")
        return
    extra = " --strip-reset" + (" --scrub-desc" if SCRUB else "")
    cmd = ('cd %s && %s nohup python -u eval/gen_code.py --model-path %s --ir %s_gold_ir.json '
           '--tag %s --n 4 --temperature 0.7 --seeds 1,2,3%s > %s 2>&1 & echo PID=$!'
           % (cc.RD2D, cc.ENVS, cc.MODEL, PART, TAG, extra, logf))
    rc, o, e = ssh.run(cmd, timeout=120)
    log("Q1 点火 %s（flags:%s）" % (re.search(r"PID=(\d+)", o or "").group(1) if re.search(r"PID=(\d+)", o or "") else "?", extra))
    t0 = time.time()
    while time.time() - t0 < 45 * 60:
        time.sleep(70)
        rc, o, _ = ssh.run('tail -1 %s | tr -d "\\r" | cut -c1-90; echo -n "|N="; grep -c "^\\[" %s 2>/dev/null; '
                           'pgrep -f "g[e]n_code.py" >/dev/null && echo ALIVE || echo EXITED' % (logf, logf), timeout=180)
        s = (o or "").replace("\n", " ")
        log("进度: %s" % s[-120:])
        if "EXITED" in s:
            break
    ssh.run('rmdir /root/.d2d_gpu_lock 2>/dev/null; true', timeout=60)   # 本进程负责释放，不留孤儿锁
    rc, o, _ = ssh.run('test -f %s && echo HAVE || echo MISSING; grep -oE "pytest 全绿 [0-9]+/[0-9]+" %s | tail -1'
                       % (out_remote, logf), timeout=120)
    if "HAVE" not in (o or ""):
        log("无结果文件：%s" % (o or "").replace("\n", " ")[:120])
        return
    data = ssh.get_b64(out_remote)
    lp = os.path.join(ROOT, "d2d", "eval", "results_gen_%s.json" % TAG)
    open(lp, "wb").write(data)
    rows = json.loads(data.decode("utf-8"))
    n2 = 0
    for r in rows:
        t = r.get("tail") or ""
        if re.search(r"FAILED \S*::test_reset_values", t):
            n2 += 1
    log("拉回 %d 行；**② 复位值失败 %d/%d**（基线 0/12）；全绿 %d/%d"
        % (len(rows), n2, len(rows), sum(1 for r in rows if r.get("rc") == 0), len(rows)))
    for r in rows:
        mm = re.search(r"AssertionError: .{0,80}", r.get("tail") or "")
        if mm and "复位" in mm.group(0) or (mm and "reset" in mm.group(0).lower()):
            log("  例: " + mm.group(0)[:100])
            break


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log("异常：\n" + cc.traceback.format_exc())
        raise
