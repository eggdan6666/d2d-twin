$root = (Get-Location).Path
$py = 'C:\Users\ZhuanZ\AppData\Local\Programs\Python\Python311\python.exe'
$d = Start-Process -FilePath $py -ArgumentList '_setup\run_final_chain.sh.py' `
  -WorkingDirectory $root `
  -RedirectStandardOutput (Join-Path $root '_setup\final_chain.log') `
  -RedirectStandardError (Join-Path $root '_setup\final_chain.err') `
  -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 3
$w = Start-Process -FilePath $py -ArgumentList '_setup\watchdog_final.py', ([string]$d.Id) `
  -WorkingDirectory $root `
  -RedirectStandardOutput (Join-Path $root '_setup\final_watchdog.out') `
  -RedirectStandardError (Join-Path $root '_setup\final_watchdog.err') `
  -WindowStyle Hidden -PassThru
Set-Content -Path (Join-Path $root '_setup\final_chain.pid') -Value "DRIVER=$($d.Id) WATCHDOG=$($w.Id)" -Encoding ascii
Write-Output "DRIVER_PID=$($d.Id)"
Write-Output "WATCHDOG_PID=$($w.Id)"
