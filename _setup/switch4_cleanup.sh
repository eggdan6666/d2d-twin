#!/bin/bash
# 收尸 + 续跑：v3 在加样已点火 HDC2021 之后才杀掉本地轮询进程，
# 导致远端 gen_code 还在跑、但负责 rmdir /root/.d2d_gpu_lock 的进程已死 ⇒ 锁成孤儿。
# 这里等远端自然结束（已跑 5 分钟，再 6 分钟完，杀掉重来更贵），然后：
#   1) 手动拉回 hdc2021kt_b 结果；2) rmdir 释放锁；3) 等链 #4 点火 LIS2DW12；4) 恢复余下 5 颗加样。
set -u
cd "E:/HD-Agent·分层记忆RAG的电子Dstasheet智能问答" || exit 1
L=_out/switch4.log
PY="C:/Users/ZhuanZ/AppData/Local/Programs/Python/Python311/python.exe"
S="C:/Users/ZhuanZ/AppData/Local/Temp/ssh_dcu.py"
export SSH_DCU_PASS="${SSH_DCU_PASS:-}" SSH_DCU_PORT="${SSH_DCU_PORT:-12461}" MSYS_NO_PATHCONV=1 SSH_TIMEOUT=120 PYTHONIOENCODING=utf-8
say(){ echo "[$(date +%H:%M:%S)] $*" | tee -a "$L"; }
R(){ "$PY" -X utf8 "$S" run "$1"; }

say "v4 启动：等远端 HDC2021 生成进程自然结束（最多 20 分钟）"
for _ in $(seq 1 40); do
  if ! R 'pgrep -f "g[e]n_code.py" >/dev/null && echo YES || echo NO' | grep -q YES; then say "远端已无 gen_code 进程"; break; fi
  sleep 30
done

say "拉回 hdc2021kt_b 结果并释放孤儿锁"
R 'test -f /root/private_data/d2d/eval/results_gen_hdc2021kt_b.json && echo HAVE || echo MISSING'
"$PY" -X utf8 - <<'PY' 2>&1 | tee -a "$L"
import sys, os, json
sys.path.insert(0, '_setup'); import chip_chain as cc
ssh = cc.SSH()
rem = cc.RD2D + "/eval/results_gen_hdc2021kt_b.json"
try:
    data = ssh.get_b64(rem)
    lp = os.path.join(cc.ROOT, "d2d", "eval", "results_gen_hdc2021kt_b.json")
    if os.path.exists(lp):
        print("本地已存在，不覆盖")
    else:
        open(lp, "wb").write(data)
        rows = json.loads(data.decode("utf-8"))
        print("拉回 %d 行，全绿 %d/%d" % (len(rows), sum(1 for r in rows if r.get("rc") == 0), len(rows)))
except Exception as e:
    print("拉回失败：", str(e)[:120])
PY
R 'rmdir /root/.d2d_gpu_lock 2>/dev/null; ls -d /root/.d2d_gpu_lock 2>/dev/null || echo 锁已释放'
say "回查锁状态见上行；若仍显示锁存在则不要继续（会双重占卡）"

say "等链 #4 点火 LIS2DW12（最多 8 分钟）"
for _ in $(seq 1 24); do grep -q "LIS2DW12 k-trial 已点火" _out/chain4.log 2>/dev/null && { say "LIS2DW12 已上机"; break; }; sleep 20; done
grep -q "LIS2DW12 k-trial 已点火" _out/chain4.log || say "警告：LIS2DW12 仍未点火"

say "恢复余下 5 颗加样（TMP117 ADS1220 LM83 TPS23861 TMP126）"
nohup "$PY" -X utf8 _setup/ressample.py --hours 2.2 --parts TMP117 ADS1220 LM83 TPS23861 TMP126 >> _out/ressample_run4.log 2>&1 &
say "恢复进程 PID=$!（带 yield 标志支持）"
say "v4 完成"
