# -*- coding: utf-8 -*-
"""长任务互斥锁：靠"记得先查 in-flight"不可靠（2026-10-07 我自己破了这条），改成机械的。

用法：在脚本开头 `from joblock import acquire; acquire("main_table")`。
锁文件 _out/.lock.<name> 里写 PID；若该 PID 还活着就拒绝启动（exit 3），
若是本进程上次崩溃留下的死锁则自动接管。
"""
import os, sys, io, atexit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "_out")


def _alive(pid):
    try:
        import ctypes
        h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)  # QUERY_LIMITED_INFORMATION
        if not h:
            return False
        code = ctypes.c_ulong()
        ok = ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(code))
        ctypes.windll.kernel32.CloseHandle(h)
        return ok and code.value == 259  # STILL_ACTIVE
    except Exception:
        return os.path.exists("/proc/%d" % pid)


def acquire(name, quiet=False):
    os.makedirs(DIR, exist_ok=True)
    lp = os.path.join(DIR, ".lock.%s" % name)
    if os.path.exists(lp):
        try:
            old = int((io.open(lp, encoding="utf-8").read() or "0").strip() or 0)
        except Exception:
            old = 0
        if old and old != os.getpid() and _alive(old):
            print("拒绝启动：同名任务 %s 正在运行（PID %d）。先确认它是不是你上一轮留下的。" % (name, old))
            sys.exit(3)
        if not quiet:
            print("接管死锁文件 %s（原 PID %s 已不在）" % (lp, old))
    io.open(lp, "w", encoding="utf-8").write(str(os.getpid()))
    atexit.register(lambda: os.path.exists(lp) and
                    (io.open(lp, encoding="utf-8").read().strip() == str(os.getpid())) and os.remove(lp))
    return lp
