# Quick Port Status Checker for Rev's IDE
# Run this to see what's actually running

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Port Status Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ports = @(3000, 5180, 5181)
foreach ($port in $ports) {
    $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if ($conn) {
        $processId = $conn.OwningProcess
        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        $name = if ($process) { $process.ProcessName } else { "Unknown" }
        Write-Host "Port $port : LISTENING - PID $processId ($name)" -ForegroundColor Yellow
    } else {
        Write-Host "Port $port : FREE" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Expected:" -ForegroundColor Cyan
Write-Host "  Port 3000 : Sam's IDE (or FREE)" -ForegroundColor Gray
Write-Host "  Port 5180 : Rev's IDE (LISTENING)" -ForegroundColor Gray
Write-Host "  Port 5181 : FREE (or leftover connections)" -ForegroundColor Gray
Write-Host ""

