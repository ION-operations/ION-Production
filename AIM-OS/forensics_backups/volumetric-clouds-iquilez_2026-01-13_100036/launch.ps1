# Inigo Quilez Volumetric Clouds Launcher Script (PowerShell)
# Launches the Inigo Quilez volumetric clouds harness development server

$PROJECT_PATH = Split-Path -Parent $MyInvocation.MyCommand.Path
$PREFERRED_PORT = 5174
$MAX_ATTEMPTS = 10

Write-Host "Inigo Quilez Volumetric Clouds" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""
Write-Host "WebGL2 harness for Inigo Quilez volumetric cloud shader"
Write-Host ""

Set-Location $PROJECT_PATH

# Check if index.html exists
if (-not (Test-Path "index.html")) {
    Write-Host "Error: index.html not found in $PROJECT_PATH" -ForegroundColor Red
    exit 1
}

# Check if main.js exists
if (-not (Test-Path "main.js")) {
    Write-Host "Error: main.js not found in $PROJECT_PATH" -ForegroundColor Red
    exit 1
}

# Check if shaders directory exists
if (-not (Test-Path "shaders")) {
    Write-Host "Error: shaders directory not found in $PROJECT_PATH" -ForegroundColor Red
    exit 1
}

# Check Python version
$pythonCmd = $null
try {
    $null = python --version 2>&1
    $pythonCmd = "python"
} catch {
    try {
        $null = python3 --version 2>&1
        $pythonCmd = "python3"
    } catch {
        Write-Host "Error: Python not found. Please install Python to run this server." -ForegroundColor Red
        Write-Host "Alternatively, use any HTTP server that serves files from this directory." -ForegroundColor Yellow
        exit 1
    }
}

# Try to find available port
$actualPort = $PREFERRED_PORT
$attempt = 0
$portFound = $false

while ($attempt -lt $MAX_ATTEMPTS) {
    $listening = Get-NetTCPConnection -LocalPort $actualPort -State Listen -ErrorAction SilentlyContinue
    if (-not $listening) {
        $portFound = $true
        break
    }
    $attempt++
    $actualPort = $PREFERRED_PORT + $attempt
    if ($attempt -lt $MAX_ATTEMPTS) {
        Write-Host "Port $PREFERRED_PORT is in use. Trying port $actualPort..." -ForegroundColor Yellow
    }
}

if (-not $portFound) {
    Write-Host "Error: Could not find available port starting from $PREFERRED_PORT" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Starting HTTP server on port $actualPort..." -ForegroundColor Green
Write-Host "Open http://localhost:$actualPort in your browser" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: Requires WebGL2" -ForegroundColor Yellow
Write-Host "Drag mouse to rotate camera view." -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host ""

# Start HTTP server
Write-Host "Starting server..." -ForegroundColor Green
& $pythonCmd -m http.server $actualPort
