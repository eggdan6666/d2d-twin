$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$p = Start-Process -FilePath python `
    -ArgumentList "eval/retrieval_ablation.py","--n","500" `
    -WorkingDirectory $root -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput (Join-Path $PSScriptRoot "ablation.log") `
    -RedirectStandardError (Join-Path $PSScriptRoot "ablation.err")
Start-Sleep 3
$p.PriorityClass = "BelowNormal"
Write-Output "pid=$($p.Id) prio=$($p.PriorityClass) root=$root"
