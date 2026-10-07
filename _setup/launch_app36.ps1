$py = "C:\Users\ZhuanZ\AppData\Local\Programs\Python\Python311\python.exe"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
$p = Start-Process -FilePath $py -ArgumentList @(
  '-u','eval/qa100/run.py','--model','qwen2.5:7b-instruct-q4_K_M','--loose',
  '--ds','eval/qa100/datasheet_qa100_app36.json','--temperature','0','--seed','42',
  '--tag','app36_7bloose') -RedirectStandardOutput "$root\_setup\app36.log" `
  -RedirectStandardError "$root\_setup\app36.err" -WindowStyle Hidden -PassThru
$p.Id | Out-File -Encoding ascii "$root\_setup\app36.pid"
Write-Output ("PID=" + $p.Id)
