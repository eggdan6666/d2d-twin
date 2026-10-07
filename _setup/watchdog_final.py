# -*- coding: utf-8 -*-
"""收官链监视器：每30分钟把进度追加到 _setup/final_monitor.log，见到 FINAL_CHAIN_DONE 就退出。
只读不改；进程死亡只记录不重启（重启由人决定）。"""
import os, sys, time, subprocess, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
CHAIN = "_setup/final_chain.log"
MON = "_setup/final_monitor.log"
SEGMENTS = ["kt3b_s1", "kt3b_s2", "kt3b_s3", "kt7b_s1", "kt7b_s2", "kt7b_s3", "v4_7bloose"]
MAX_HOURS = 10.0
INTERVAL = 1800


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def driver_alive(pid):
    try:
        out = subprocess.run(["tasklist", "/FI", "PID eq %d" % pid], capture_output=True,
                             text=True, timeout=30).stdout
        return str(pid) in out
    except Exception:
        return None


def status(pid):
    txt = ""
    if os.path.exists(CHAIN):
        txt = open(CHAIN, encoding="utf-8", errors="replace").read()
    done = [s for s in SEGMENTS if (s + ": rc=") in txt]
    frag = [s for s in SEGMENTS if s not in done and os.path.exists("_setup/final_%s.log" % s)]
    cur = ""
    if frag:
        p = "_setup/final_%s.log" % frag[0]
        try:
            n = sum(1 for _ in open(p, encoding="utf-8", errors="replace"))
            cur = "%s(%d行)" % (frag[0], n)
        except Exception:
            cur = frag[0] + "(locked)"
    return ("alive=%s done=[%s] running=%s chain_lines=%d" %
            (driver_alive(pid), " ".join(done), cur or "-", len(txt.splitlines())),
            ("FINAL_CHAIN_DONE" in txt, len(done)))


def main():
    pid = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    t0 = time.time()
    while True:
        line, (finished, ndone) = status(pid)
        with open(MON, "a", encoding="utf-8") as f:
            f.write("%s | %s\n" % (now(), line))
            f.flush()
        if finished:
            with open(MON, "a", encoding="utf-8") as f:
                f.write("%s | WATCHDOG_EXIT chain finished (%d segments)\n" % (now(), ndone))
            return 0
        if not driver_alive(pid):
            with open(MON, "a", encoding="utf-8") as f:
                f.write("%s | WATCHDOG_EXIT driver pid %s GONE but no FINAL_CHAIN_DONE "
                        "(%d/7 segments done) -> 需人工决定是否重启\n" % (now(), pid, ndone))
            return 2
        if (time.time() - t0) / 3600.0 > MAX_HOURS:
            with open(MON, "a", encoding="utf-8") as f:
                f.write("%s | WATCHDOG_EXIT exceeded %.1fh cap\n" % (now(), MAX_HOURS))
            return 3
        time.sleep(INTERVAL)


if __name__ == "__main__":
    sys.exit(main())
