param([int]$Pid2Wait = 0, [int]$StallMin = 15, [int]$TimeoutH = 3)
$root = (Get-Location).Path
$log = Join-Path $root "_setup\rerun_kt7b_s1.log"
$deadline = (Get-Date).AddHours($TimeoutH)
while ((Get-Date) -lt $deadline) {
  $txt = ""
  if (Test-Path $log) { $txt = Get-Content $log -Raw -ErrorAction SilentlyContinue }
  if ($txt -match 'QA100 acc') {
    Write-Output "RERUN_OK"
    Write-Output (($txt -split "`n") | Select-Object -Last 6)
    exit 0
  }
  if ($Pid2Wait -gt 0 -and -not (Get-Process -Id $Pid2Wait -ErrorAction SilentlyContinue)) {
    Write-Output "RERUN_PROC_GONE without completion marker"
    exit 2
  }
  if (Test-Path $log) {
    $age = ((Get-Date) - (Get-Item $log).LastWriteTime).TotalMinutes
    $n = ([regex]::Matches($txt, "`n")).Count
    if ($age -gt $StallMin) {
      Write-Output "STALL log idle $([int]$age) min at line $n"
      exit 3
    }
  }
  Start-Sleep -Seconds 240
}
Write-Output "CAP_${TimeoutH}h"
exit 4
