param([int]$DriverPid = 0, [string]$Needle = "FINAL_CHAIN_DONE", [int]$TimeoutH = 9)
$root = (Get-Location).Path
$log = Join-Path $root "_setup\final_chain.log"
$deadline = (Get-Date).AddHours($TimeoutH)
while ((Get-Date) -lt $deadline) {
  $txt = ""
  if (Test-Path $log) { $txt = Get-Content $log -Raw -ErrorAction SilentlyContinue }
  if ($txt -match [regex]::Escape($Needle)) {
    Write-Output "NEEDLE_FOUND [$Needle]"
    Write-Output $txt
    exit 0
  }
  if ($DriverPid -gt 0 -and -not (Get-Process -Id $DriverPid -ErrorAction SilentlyContinue)) {
    Write-Output "DRIVER_GONE pid=$DriverPid needle=$Needle not_yet"
    Write-Output "chain.log so far:"
    Write-Output $txt
    exit 2
  }
  Start-Sleep -Seconds 180
}
Write-Output "CAP_${TimeoutH}h needle=$Needle"
Write-Output $txt
exit 3
