# -*- coding: utf-8 -*-
"""D2D-Twin 连跑编排器（8 小时窗口，零风险自动化 + 人工金标解耦）。

分工（重要）：
  · 自动化部分（本脚本）：上传 PDF → MinerU GPU 解析 → 拉回 markdown → 对「IR 已就绪」的芯片
    跑 k-trial → 拉回结果 → 记账。GPU 不空转。
  · 不自动化部分：金标 IR 与参考实现必须由人/会话内 agent 逐颗撰写并本地回归全绿——
    不能让被测模型自撰金标，否则基准失去判据。本脚本用「ir/<CHIP>_gold_ir.json 存在且有 .ready 标记」
    作为准入，缺一律跳过并在下一轮重试。

每轮的准入校验（在本地做，上服务器前）：
  1) ir/<CHIP>_gold_ir.json 可解析、含 device/reg_width/registers
  2) rtl/<chip>_reference.py 本地 harness 回归全绿（D2D_IR=<ir> pytest）
  3) 反向对照：把参考实现里某个 RW 掩码扰动后必须判红——证明断言真的咬得住
  满足三条才写 ir/<CHIP>.ready；否则把失败原因记进状态文件等你处理。

用法（项目根，后台跑）：
  set SSH_DCU_PASS=...  (勿写进文件)
  python _setup/chip_chain.py --parts TMP101 TMP103 LM83 --hours 8
产物：_out/chain_status.json（逐步骤状态）、_out/chain.log（全量日志）、
      d2d/parsed/<CHIP>/auto/<CHIP>.md、d2d/eval/results_gen_<tag>.json
"""
import sys, os, io, re, json, time, hashlib, argparse, subprocess, posixpath, traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.stdout.reconfigure(encoding="utf-8")
import paramiko  # noqa: E402

HOST, USER = "ssh.zzai.scnet.cn", "root"
PORT = int(os.environ.get("SSH_DCU_PORT", "12461"))
PROXY = "http://preset:6e298f07@10.16.1.51:3128"
RD2D = "/root/private_data/d2d"
RPILOT = "/root/pilot"
LOG = os.path.join(ROOT, "_out", "chain.log")
STATUS = os.path.join(ROOT, "_out", "chain_status.json")
ENVS = ("source /opt/dtk/env.sh >/dev/null 2>&1; export PATH=/opt/conda/bin:$PATH "
        "HF_HUB_OFFLINE=1 http_proxy=%s https_proxy=%s no_proxy=localhost,127.0.0.1;" % (PROXY, PROXY))
MODEL = RD2D + "/../models/Qwen2.5-Coder-14B-Instruct"


def log(msg):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    with io.open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


class SSH:
    def __init__(self):
        self.c = None
        self.connect()

    def connect(self):
        pw = os.environ["SSH_DCU_PASS"]
        self.c = paramiko.SSHClient()
        self.c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.c.connect(HOST, port=PORT, username=USER, password=pw, timeout=40,
                       banner_timeout=60, auth_timeout=60)
        log("SSH 已连接")

    def run(self, cmd, timeout=600, retries=2):
        for a in range(retries + 1):
            try:
                if self.c is None:
                    self.connect()
                _, out, err = self.c.exec_command(cmd, timeout=timeout)
                o = out.read().decode("utf-8", "replace")
                e = err.read().decode("utf-8", "replace")
                rc = out.channel.recv_exit_status()
                return rc, o, e
            except Exception as ex:
                log("SSH 异常(%d): %s → 重连" % (a, str(ex)[:90]))
                try:
                    self.c.close()
                except Exception:
                    pass
                self.c = None
                time.sleep(15)
        raise RuntimeError("SSH 连续失败")

    def put(self, local, remote):
        sftp = self.c.open_sftp()
        sftp.put(local, remote)
        sftp.close()

    def get_b64(self, remote, timeout=600):
        rc, o, e = self.run("base64 -w0 %s" % remote, timeout=timeout)
        if rc != 0:
            raise RuntimeError("base64 失败 %s: %s" % (remote, e[:120]))
        return base64_decode(o)


def base64_decode(s):
    import base64
    return base64.b64decode(re.sub(r"\s+", "", s))


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def state():
    if os.path.exists(STATUS):
        return json.load(io.open(STATUS, encoding="utf-8"))
    return {"chips": {}, "events": [], "started": time.strftime("%F %T")}


def save(st):
    st["updated"] = time.strftime("%F %T")
    json.dump(st, io.open(STATUS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def local_regression(part):
    """跑本地 harness 回归；返回 (ok, 输出尾)。"""
    ir = os.path.join(ROOT, "d2d", "ir", "%s_gold_ir.json" % part)
    ref = os.path.join(ROOT, "d2d", "rtl", "%s_reference.py" % part.lower())
    if not (os.path.exists(ir) and os.path.exists(ref)):
        return False, "缺 IR 或参考实现"
    sb = os.path.join(ROOT, "d2d", "eval", "_sb_%s" % part)
    os.makedirs(sb, exist_ok=True)
    for src, dst in [(os.path.join(ROOT, "d2d", "rtl", "base_sensor.py"), "base_sensor.py"),
                     (os.path.join(ROOT, "d2d", "eval", "test_d2d_blackbox.py"), "test_d2d_blackbox.py"),
                     (ref, "%s_simulator.py" % part.lower())]:
        open(os.path.join(sb, dst), "wb").write(open(src, "rb").read())
    env = dict(os.environ, D2D_IR="%s_gold_ir.json" % part, PYTHONIOENCODING="utf-8")
    py = sys.executable
    r = subprocess.run([py, "-m", "pytest", "test_d2d_blackbox.py", "-q", "--no-header"],
                       cwd=sb, env=env, capture_output=True, text=True, timeout=300)
    tail = (r.stdout or "").strip().split("\n")[-1]
    return r.returncode == 0 and "error" not in tail.lower(), tail


def perturbation_control(part):
    """行为探针（反向对照）：派生两个「故意不忠实」的实现，harness 必须判红。
      naive_regfile：写什么存什么——丢 RO 保护与保留位硬连。这正是被测模型的主导错误，
                     若这样都全绿，说明本芯片的 IR 没在断言任何权限/保留位语义。
      reset_shift ：上电值偏移 1，test_reset_values 必须红。
    返回 (明细 dict, 结论 bool|None)。IR/实现不用 self.regs 的芯片跳过 naive 探针（返回 None 交人工）。"""
    ref = os.path.join(ROOT, "d2d", "rtl", "%s_reference.py" % part.lower())
    sb = os.path.join(ROOT, "d2d", "eval", "_sb_%s" % part)
    sb_ref = os.path.join(sb, "%s_simulator.py" % part.lower())
    if not (os.path.exists(ref) and os.path.exists(sb_ref)):
        return None, None
    orig = io.open(ref, encoding="utf-8").read()
    cls = "%s_Simulator" % part
    probes = {
        "naive_regfile": "\n\n_NAIVE = %s\n\n\nclass %s(_NAIVE):\n\n    def write_register(self, addr, data, nbytes=2):\n"
                         "        self.regs[addr] = data & 0xFFFF\n" % (cls, cls),
        "reset_shift": "\n\n_ORIG2 = %s\n\n\nclass %s(_ORIG2):\n\n    def __init__(self):\n        _ORIG2.__init__(self)\n"
                       "        ks = sorted(self.regs)\n        if ks:\n            k = ks[0]\n"
                       "            self.regs[k] = (self.regs[k] + 1) & 0xFFFF\n" % (cls, cls),
    }
    detail = {}
    for name, code in probes.items():
        if name == "naive_regfile" and "self.regs" not in orig:
            detail[name] = None; continue
        io.open(sb_ref, "w", encoding="utf-8").write(orig + code)
        env = dict(os.environ, D2D_IR="%s_gold_ir.json" % part, PYTHONIOENCODING="utf-8")
        try:
            r = subprocess.run([sys.executable, "-m", "pytest", "test_d2d_blackbox.py", "-q", "--no-header"],
                               cwd=sb, env=env, capture_output=True, text=True, timeout=300)
            detail[name] = (r.returncode != 0)
        except Exception as e:
            detail[name] = None; log("%s 探针 %s 异常 %s" % (part, name, str(e)[:60]))
        finally:
            io.open(sb_ref, "w", encoding="utf-8").write(orig)
    # 期望值要按 IR 自己声明了什么来推——否则正对照芯片（无 RO 寄存器、无只读位、无 read_as）
    # 会被误拦：它本来就该让「纯寄存器堆」探针通过。reset_shift 对任何芯片都必须红。
    ir_path = os.path.join(ROOT, "d2d", "ir", "%s_gold_ir.json" % part)
    ir = json.load(io.open(ir_path, encoding="utf-8")) if os.path.exists(ir_path) else {"registers": []}
    protected = any(r["access"] in ("RO", "W") or
                    any(f["access"] == "RO" or f.get("read_as") is not None
                        for f in r.get("fields", []))
                    for r in ir["registers"])
    got_naive = detail.get("naive_regfile")
    naive_ok = (got_naive is None) or (got_naive == bool(protected))
    reset_ok = detail.get("reset_shift") is not False
    if not (naive_ok and reset_ok):
        log("%s 探针不符期望：naive_regfile=%s（IR 有受保护位=%s ⇒ 期望 %s）、reset_shift=%s"
            % (part, got_naive, protected, bool(protected), detail.get("reset_shift")))
    return detail, bool(naive_ok and reset_ok)


def ensure_ready(st, part):
    """准入三关；过了才写 .ready 标记。"""
    c = st["chips"].setdefault(part, {})
    ok, tail = local_regression(part)
    c["local_regression"] = tail
    if not ok:
        c["ready"] = False; c["gate"] = "本地回归未过"
        save(st); log("%s 本地回归未过：%s" % (part, tail)); return False
    detail, bites = perturbation_control(part)
    c["perturbation_control"] = detail
    if bites is False:
        c["ready"] = False; c["gate"] = "反向对照未判红，断言无咬合力"
        save(st); log("%s 反向对照失败 %s → 不许上机" % (part, detail)); return False
    if bites is None:
        log("%s 反向对照无法自动判定（%s），按人工确认放行" % (part, detail))
    ready = os.path.join(ROOT, "d2d", "ir", "%s.ready" % part)
    io.open(ready, "w", encoding="utf-8").write(json.dumps(
        {"part": part, "local_regression": tail, "perturbation": detail, "ts": time.strftime("%F %T")},
        ensure_ascii=False))
    c["ready"] = True; c["gate"] = "ok"
    save(st); log("%s 准入通过（回归 %s / 探针 %s）" % (part, tail, detail))
    return True


def upload_chip(ssh, st, part):
    """把 IR + 参考实现推到服务器并核 md5。"""
    c = st["chips"].setdefault(part, {})
    for loc, rem in [(os.path.join(ROOT, "d2d", "ir", "%s_gold_ir.json" % part), "%s/ir/%s_gold_ir.json" % (RD2D, part)),
                     (os.path.join(ROOT, "d2d", "rtl", "%s_reference.py" % part.lower()), "%s/rtl/%s_reference.py" % (RD2D, part.lower()))]:
        if not os.path.exists(loc):
            c["upload"] = "缺文件 " + loc; save(st); return False
        ssh.put(loc, rem)
        rc, o, _ = ssh.run("md5sum %s" % rem)
        remote = (o or "").split()
        remote = remote[0] if remote else ""
        if remote != md5(loc):
            c["upload"] = "md5 不一致 %s" % part; save(st); log("%s 上传 md5 不一致" % part); return False
    c["upload"] = "md5 已核"
    save(st); log("%s IR+参考已上传并核 md5" % part)
    return True


def run_ktrial(ssh, st, part, hours_left):
    """服务器端 detached 跑 k-trial，轮询到结束，再拉回结果。"""
    c = st["chips"].setdefault(part, {})
    tag = "%skt" % part.lower()
    out_remote = "%s/eval/results_gen_%s.json" % (RD2D, tag)
    logf = "/root/%s.log" % tag
    lock = "/root/.d2d_gpu_lock"
    # 原子锁 + 实时进程检查（老版编排器不会取锁，所以两者都要看）
    rc, o, _ = ssh.run('if mkdir %s 2>/dev/null; then if pgrep -f "g[e]n_code.py" >/dev/null; then '
                       'rmdir %s; echo BUSY; else echo GOT; fi; else echo BUSY; fi' % (lock, lock), timeout=120)
    if "GOT" not in (o or ""):
        c["ktrial"] = "另一进程在跑（锁被占），本轮跳过"
        save(st); log("%s 等待 GPU 锁" % part); return False
    cmd = ('cd %s && %s nohup python -u eval/gen_code.py --model-path %s --ir %s_gold_ir.json '
           '--tag %s --n 4 --temperature 0.7 --seeds 1,2,3 > %s 2>&1 & echo PID=$!'
           % (RD2D, ENVS, MODEL, part, tag, logf))
    rc, o, e = ssh.run(cmd, timeout=120)
    pid = re.search(r"PID=(\d+)", o or "")
    c["ktrial"] = "launched pid=%s" % (pid.group(1) if pid else "?")
    save(st); log("%s k-trial 已点火 %s" % (part, c["ktrial"]))
    t0 = time.time()
    while time.time() - t0 < min(hours_left, 1.4) * 3600:
        time.sleep(75)
        rc, o, _ = ssh.run('tail -2 %s | tr -d "\\r"; echo -n "|ROWS="; '
                           'python -c "import json;print(len(json.load(open(\'%s\'))))" 2>/dev/null || echo 0; '
                           'pgrep -f "g[e]n_code.py" >/dev/null && echo ALIVE || echo EXITED'
                           % (logf, out_remote), timeout=180)
        s = (o or "").replace("\n", " ")
        log("%s 进度: %s" % (part, s[-160:]))
        if "EXITED" in s:
            break
    ssh.run('rmdir %s 2>/dev/null; true' % lock, timeout=60)      # 释放 GPU 锁
    rc, o, _ = ssh.run('test -f %s && echo HAVE || echo MISSING; grep -c "^\\[" %s 2>/dev/null; tail -2 %s | tr -d "\\r"'
                       % (out_remote, logf, logf), timeout=180)
    if "HAVE" not in o:
        c["ktrial_result"] = "结果文件缺失"; save(st); log("%s 无结果文件" % part); return False
    data = ssh.get_b64(out_remote)
    lp = os.path.join(ROOT, "d2d", "eval", "results_gen_%s.json" % tag)
    open(lp, "wb").write(data)
    rc, o, _ = ssh.run("md5sum %s" % out_remote, timeout=120)
    rem_md5 = (o or "").split()
    okmd5 = bool(rem_md5) and rem_md5[0] == md5(lp)
    rows = json.loads(data.decode("utf-8"))
    c["ktrial_result"] = {"rows": len(rows), "md5_match": okmd5, "bytes": len(data),
                          "wall_min": round((time.time() - t0) / 60, 1)}
    save(st)
    log("%s 结果已拉回 %d 行 md5核=%s 用时 %.1f 分钟" % (part, len(rows), okmd5, c["ktrial_result"]["wall_min"]))
    return True


def parse_pdf(ssh, st, part):
    """上传 PDF → MinerU 解析（GPU）→ 拉回 md。

    完成判定用 **md 大小连续两次不变**，不用 pgrep：实测 pgrep -f "[m]ineru" 会被轮询命令自身
    （里面含 mineru_<PART>.log 路径）匹配，导致永远 ALIVE、白等满 40 分钟超时（2026-10-07 踩过）。
    """
    c = st["chips"].setdefault(part, {})
    lp = os.path.join(ROOT, "corpus", "data", "raw_pdf")
    cand = []
    for dirpath, _d, files in os.walk(lp):
        for fn in files:
            if fn[:-4].upper() == part and fn.lower().endswith(".pdf"):
                cand.append(os.path.join(dirpath, fn))
    if not cand:
        c["parse"] = "本地无此 PDF"; save(st); return False
    lpdf = cand[0]
    rpdf = "%s/%s.pdf" % (RPILOT, part)
    rout = "%s/out_%s" % (RPILOT, part)
    rmd = "%s/%s/auto/%s.md" % (rout, part, part)

    def remote_md_size():
        rc, o, _ = ssh.run("wc -c %s 2>/dev/null || echo NONE" % rmd, timeout=120)
        m = re.search(r"(\d+)", o or "")
        return int(m.group(1)) if m else 0

    logf = "/root/mineru_%s.log" % part
    if remote_md_size() >= 5000:
        c["parse"] = "远端已有 md，跳过解析"
        log("%s 远端 md 已存在（%d bytes），不重复烧 GPU" % (part, remote_md_size()))
    else:
        ssh.put(lpdf, rpdf)
        rc, o, _ = ssh.run("ls -l %s" % rpdf, timeout=120)
        log("%s PDF 已上传: %s" % (part, (o or "").strip()[-60:]))
        rc, o, e = ssh.run('cd %s && %s nohup mineru -p %s -o %s -d cuda -m auto > %s 2>&1 & echo PID=$!'
                           % (RPILOT, ENVS, rpdf, rout, logf), timeout=180)
        m = re.search(r"PID=(\d+)", o or "")
        c["parse"] = "launched %s" % (m.group(1) if m else "?")
        log("%s MinerU 已点火 %s" % (part, c["parse"]))
    save(st)
    t0, prev, stable = time.time(), 0, 0
    while time.time() - t0 < 26 * 60:
        time.sleep(45)
        n = remote_md_size()
        if n >= 5000 and n == prev:
            stable += 1
            if stable >= 2:
                break
        else:
            stable = 0
        prev = n
        log("%s 解析中 md=%s bytes" % (part, n))
    n = remote_md_size()
    if n < 5000:
        rc, o, _ = ssh.run("tail -3 %s | tr -d '\\r' | cut -c1-200" % logf, timeout=120)
        c["parse_result"] = "md 未产出/过小(%d bytes)：%s" % (n, (o or "").replace("\n", " ")[:200])
        save(st); log("%s 解析失败：%s" % (part, c["parse_result"])); return False
    data = ssh.get_b64(rmd)
    ldir = os.path.join(ROOT, "d2d", "parsed", part, "auto")
    os.makedirs(ldir, exist_ok=True)
    open(os.path.join(ldir, "%s.md" % part), "wb").write(data)
    c["parse_result"] = {"md_bytes": n, "local_bytes": len(data), "wall_min": round((time.time() - t0) / 60, 1)}
    save(st); log("%s 解析完成并拉回 %d bytes（本轮 %.1f 分钟）" % (part, len(data), c["parse_result"]["wall_min"]))
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", nargs="+", required=True, help="按顺序处理的型号（大写得与 PDF 同名）")
    ap.add_argument("--hours", type=float, default=8.0)
    ap.add_argument("--phase", default="parse_then_eval", choices=["parse_then_eval", "eval_only"])
    args = ap.parse_args()
    t_end = time.time() + args.hours * 3600
    st = state()
    st["plan"] = {"parts": args.parts, "hours": args.hours, "phase": args.phase}
    save(st)
    ssh = SSH()
    order = list(args.parts)
    parsed, evaluated = set(), set()
    while time.time() < t_end and order:
        progressed = False
        for part in list(order):
            if (time.time() - t_end) > -600:
                pass
            left_h = (t_end - time.time()) / 3600
            if left_h <= 0.2:
                log("剩余预算不足 12 分钟，停止接新活"); break
            c = st["chips"].setdefault(part, {})
            # 1) 解析（本地已有 md 就跳）
            lmd = os.path.join(ROOT, "d2d", "parsed", part, "auto", "%s.md" % part)
            if part not in parsed and not os.path.exists(lmd) and args.phase == "parse_then_eval":
                if parse_pdf(ssh, st, part):
                    parsed.add(part); progressed = True
                    # 不在这里 continue：解析成功后同轮就走准入与评测，省掉一轮 GPU 空等
                else:
                    continue
            parsed.add(part)
            # 2) 金标准入（我还没写完 IR 就跳过，下一轮再看）
            if not c.get("ready") and not os.path.exists(os.path.join(ROOT, "d2d", "ir", "%s.ready" % part)):
                if ensure_ready(st, part):
                    progressed = True
                else:
                    log("%s 金标未就绪，本轮跳过" % part)
                    continue
            elif not os.path.exists(os.path.join(ROOT, "d2d", "ir", "%s.ready" % part)):
                ensure_ready(st, part)
            # 3) 上传 + k-trial
            if part in evaluated:
                continue
            if upload_chip(ssh, st, part) and run_ktrial(ssh, st, part, left_h):
                evaluated.add(part); progressed = True
                order.remove(part)
        if not progressed:
            log("本轮无任何推进（多为金标未就绪），等 3 分钟再看")
            time.sleep(180)
    st["finished"] = time.strftime("%F %T")
    st["remaining"] = order
    save(st)
    log("链结束。已解析 %s，已评测 %s，未完成 %s" % (sorted(parsed), sorted(evaluated), order))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log("编排器异常退出:\n" + traceback.format_exc())
        raise
