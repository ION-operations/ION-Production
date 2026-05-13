# Port Cleanup Script for Rev's IDE
# Checks and kills processes on ports 3000 and 5180 before launching

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Port Cleanup & Rev's IDE Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to kill process on a port
function Kill-PortProcess {
    param([int]$Port)
    
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($connections) {
        foreach ($conn in $connections) {
            $pid = $conn.OwningProcess
            $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "  Killing process on port $Port : $($process.ProcessName) (PID: $pid)" -ForegroundColor Yellow
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                Start-Sleep -Milliseconds 500
            }
        }
        Write-Host "  Port $Port cleared" -ForegroundColor Green
    } else {
        Write-Host "  Port $Port is free" -ForegroundColor Green
    }
}

# Check and clean ports
Write-Host "Checking ports..." -ForegroundColor Yellow
Write-Host ""

# Port 3000 (Sam's IDE)
Write-Host "Port 3000 (Sam's IDE):" -ForegroundColor Cyan
Kill-PortProcess -Port 3000

Write-Host ""

# Port 5180 (Rev's IDE)
Write-Host "Port 5180 (Rev's IDE):" -ForegroundColor Cyan
Kill-PortProcess -Port 5180

Write-Host ""
Write-Host "Waiting 2 seconds for ports to release..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

# Change to script directory
Set-Location $PSScriptRoot

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "Starting Rev's IDE Prototype on port 5180..." -ForegroundColor Green
Write-Host "URL: http://localhost:5180/indexRev.html" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start Vite dev server
npm run dev:rev
