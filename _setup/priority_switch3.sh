#!/bin/bash
# 换挡器 v3：只用 Windows 原生工具查/杀进程（v1 用 bash kill 打不死原生进程；
# v2 把 PowerShell 的 Name='python.exe' 过滤用嵌套引号传参被 bash 吃掉 → 查成空 PID 没杀）。
# 且必须等当前颗自然落盘再换：锁由本地轮询进程负责 rmdir，中途杀掉会让远端锁永不释放。
set -u
cd "E:/HD-Agent·分层记忆RAG的电子Dstasheet智能问答" || exit 1
L=_out/switch3.log
PID=${1:-31604}
say(){ echo "[$(date +%H:%M:%S)] $*" | tee -a "$L"; }

say "v3 启动，目标加样 PID=$PID；等 INA3221 加样落盘（最多 15 分钟）"
for _ in $(seq 1 45); do grep -q "INA3221 拉回" _out/ressample.log 2>/dev/null && break; sleep 20; done
grep -q "INA3221 拉回" _out/ressample.log && say "INA3221 已落盘" || say "超时，继续换挡"

say "杀前确认：$(tasklist //FI "PID eq $PID" //FO CSV //NH 2>/dev/null | head -1)"
taskkill //PID "$PID" //F >> "$L" 2>&1 && say "taskkill 已发"
sleep 3
if tasklist //FI "PID eq $PID" //FO CSV //NH 2>/dev/null | grep -q "$PID"; then
  say "AVA 失败：$PID 仍在进程表里 —— 不要再重试，改人工处理"
  exit 1
fi
say "回查通过：$PID 已退出，锁应由其自身 rmdir 释放"

say "等链 #4 点火 LIS2DW12（最多 8 分钟）"
for _ in $(seq 1 24); do grep -q "LIS2DW12 k-trial 已点火" _out/chain4.log 2>/dev/null && { say "LIS2DW12 已上机"; break; }; sleep 20; done
grep -q "LIS2DW12 k-trial 已点火" _out/chain4.log || say "警告：LIS2DW12 仍未点火，查 chain4.log"

say "恢复加样余下 6 颗（带 yield 标志支持）"
export PYTHONIOENCODING=utf-8
nohup "C:/Users/ZhuanZ/AppData/Local/Programs/Python/Python311/python.exe" -X utf8 \
  _setup/ressample.py --hours 2.4 --parts HDC2021 TMP117 ADS1220 LM83 TPS23861 TMP126 \
  >> _out/ressample_run3.log 2>&1 &
say "恢复进程 PID=$!"
say "v3 完成"
