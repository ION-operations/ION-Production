# AIM-OS IDE One-Click Launcher (PowerShell)
# Automatically finds an open port and launches the IDE

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AIM-OS IDE Launcher" -ForegroundColor Cyan
Write-Host "  Finding open port and starting..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

if (-not (Test-Path "package.json")) {
    Write-Host "[ERROR] package.json not found! Make sure you're in the ide_chat_app directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "[INFO] Installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to install dependencies!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[SUCCESS] Dependencies installed!" -ForegroundColor Green
    Write-Host ""
}

# Function to check if port is available
function Test-Port {
    param([int]$Port)
    $connection = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue -InformationLevel Quiet
    return -not $connection
}

# Find an open port starting from 5173
$port = 5173
$maxPort = 6000
$found = $false

Write-Host "[INFO] Finding an open port..." -ForegroundColor Yellow

while ($port -le $maxPort) {
    if (Test-Port -Port $port) {
        Write-Host "[SUCCESS] Found open port: $port" -ForegroundColor Green
        $found = $true
        break
    } else {
        Write-Host "[INFO] Port $port is in use, trying next port..." -ForegroundColor Gray
        $port++
    }
}

if (-not $found) {
    Write-Host "[ERROR] Could not find an open port between 5173-6000!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[INFO] Starting IDE on port $port..." -ForegroundColor Yellow
Write-Host "[INFO] Server will open automatically at http://localhost:$port" -ForegroundColor Cyan
Write-Host "[INFO] Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Set port environment variable and start vite
$env:PORT = $port
npm run dev -- --port $port --host

Read-Host "Press Enter to exit"

