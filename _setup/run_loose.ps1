$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$startIso = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
$epoch = ([DateTimeOffset](Get-Date)).ToUnixTimeSeconds()
Set-Content -Path (Join-Path $PSScriptRoot "loose_start.txt") -Value $epoch -Encoding ascii
$p = Start-Process -FilePath python `
    -ArgumentList "eval/run_longmemeval.py","--n","500","--k","3","--sysmode","loose" `
    -WorkingDirectory $root -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput (Join-Path $PSScriptRoot "lme_loose.log") `
    -RedirectStandardError (Join-Path $PSScriptRoot "lme_loose.err")
Start-Sleep 3
$p.PriorityClass = "BelowNormal"
Write-Output "pid=$($p.Id) start=$startIso epoch=$epoch root=$root"
