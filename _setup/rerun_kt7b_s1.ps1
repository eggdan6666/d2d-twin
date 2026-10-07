$root = (Get-Location).Path
$py = 'C:\Users\ZhuanZ\AppData\Local\Programs\Python\Python311\python.exe'
$argl = @('-u', 'eval/qa100/run.py', '--model', 'qwen2.5:7b-instruct-q4_K_M', '--loose',
          '--temperature', '0.7', '--ds', 'eval/qa100/datasheet_qa100_v3.json',
          '--seed', '1', '--tag', 'kt_rag7b_s1')
$d = Start-Process -FilePath $py -ArgumentList $argl -WorkingDirectory $root `
  -RedirectStandardOutput (Join-Path $root '_setup\rerun_kt7b_s1.log') `
  -RedirectStandardError (Join-Path $root '_setup\rerun_kt7b_s1.err') `
  -WindowStyle Hidden -PassThru
Set-Content -Path (Join-Path $root '_setup\rerun.pid') -Value "PID=$($d.Id)" -Encoding ascii
Write-Output "RERUN_PID=$($d.Id)"
