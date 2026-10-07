#!/bin/bash
# 自动换挡：加样跑完当前颗后让位给新芯片 LIS2DW12（宽度优先），再恢复加样余下颗。
# 为什么需要：加样每颗约 10 分钟、跑完立刻抢下一颗的锁，链 #4 每 3 分钟才试一次，
# 撞进那 1-2 秒释放窗口的概率极低 ⇒ 新芯片会被加样饿死。
set -u
cd "E:/HD-Agent·分层记忆RAG的电子Dstasheet智能问答" || exit 1
LOG=_out/priority_switch.log
PY="C:/Users/ZhuanZ/AppData/Local/Programs/Python/Python311/python.exe"
say(){ echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

say "换挡器启动：等 BME280 加样落盘（最多 30 分钟）"
for i in $(seq 1 90); do
  grep -q "BME280 拉回" _out/ressample.log 2>/dev/null && break
  sleep 20
done
grep -q "BME280 拉回" _out/ressample.log || say "警告：等超时，仍继续换挡"

PList(){ powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Select-Object ProcessId,CommandLine | Format-List" 2>/dev/null | tr -d '\r'; }
PL=$(PList)
PID=$(printf '%s\n' "$PL" | awk '/^ProcessId/{p=$3} /ressample\.py/{if(p){print p; exit}}')
CMD=$(printf '%s\n' "$PL" | grep -A1 "^ProcessId.*: *${PID:-NONE}$" | grep 'ressample\.py' | head -1)
if [ -n "${PID:-}" ]; then
  say "确认要停的进程 $PID :: $CMD"
  case "$CMD" in *ressample.py*) kill -9 "$PID" && say "加样已停（锁会在下一次 rmdir 后释放）";; *) say "命令行不含 resample.py，放弃 kill";; esac
else
  say "没找到加样进程（可能已自然结束）"
fi

say "等链 #4 点火 LIS2DW12（最多 6 分钟）"
for i in $(seq 1 18); do
  grep -q "LIS2DW12 k-trial 已点火" _out/chain4.log 2>/dev/null && { say "LIS2DW12 已上机"; break; }
  sleep 20
done
grep -q "LIS2DW12 k-trial 已点火" _out/chain4.log || say "警告：LIS2DW12 仍未点火，检查 chain4.log"

say "恢复加样余下 8 颗（会自己等 GPU 锁）"
export PYTHONIOENCODING=utf-8
nohup "$PY" -X utf8 _setup/ressample.py --hours 3.2 \
  --parts TMP100 INA3221 HDC2021 TMP117 ADS1220 LM83 TPS23861 TMP126 \
  >> _out/ressample_run2.log 2>&1 &
say "加样恢复进程 PID=$!"
say "换挡器完成"
