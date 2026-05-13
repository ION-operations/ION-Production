# Shadertoy al-ro Harness Launcher Script (PowerShell)
# Launches the Shadertoy al-ro volumetric clouds harness development server

$projectPath = $PSScriptRoot
$port = 5173

if (-not (Test-Path $projectPath)) {
    Write-Host "Error: Project path not found: $projectPath" -ForegroundColor Red
    exit 1
}

Write-Host "Shadertoy al-ro Clouds Harness" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""
Write-Host "WebGL2 harness for Shadertoy-style multi-buffer pipeline" -ForegroundColor Yellow
Write-Host "(BufferA + BufferB + Image)" -ForegroundColor Yellow
Write-Host ""

Set-Location $projectPath

# Check if index.html exists
if (-not (Test-Path "index.html")) {
    Write-Host "Error: index.html not found in $projectPath" -ForegroundColor Red
    exit 1
}

# Check if main.js exists
if (-not (Test-Path "main.js")) {
    Write-Host "Error: main.js not found in $projectPath" -ForegroundColor Red
    exit 1
}

# Check if shaders directory exists
if (-not (Test-Path "shaders")) {
    Write-Host "Error: shaders directory not found in $projectPath" -ForegroundColor Red
    exit 1
}

Write-Host "Checking port availability..." -ForegroundColor Gray

# Check Python version
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Using: $pythonVersion" -ForegroundColor Gray
} catch {
    Write-Host "Warning: Python not found. Trying python3..." -ForegroundColor Yellow
    try {
        $pythonVersion = python3 --version 2>&1
        Write-Host "Using: $pythonVersion" -ForegroundColor Gray
        $pythonCmd = "python3"
    } catch {
        Write-Host "Error: Python not found. Please install Python to run this server." -ForegroundColor Red
        Write-Host "Alternatively, use any HTTP server that serves files from this directory." -ForegroundColor Yellow
        exit 1
    }
}

if (-not $pythonCmd) {
    $pythonCmd = "python"
}

# Function to check if port is available
function Test-Port {
    param([int]$Port)
    try {
        # Check if port is in LISTEN state
        $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
        return $null -eq $listener
    } catch {
        # If check fails, assume port is available (let Python try)
        return $true
    }
}

# Function to find available port
function Find-AvailablePort {
    param([int]$StartPort, [int]$MaxAttempts = 10)
    
    for ($i = 0; $i -lt $MaxAttempts; $i++) {
        $testPort = $StartPort + $i
        if (Test-Port -Port $testPort) {
            return $testPort
        }
    }
    return $null
}

# Check if preferred port is available
$preferredPort = 5173
$actualPort = Find-AvailablePort -StartPort $preferredPort

if (-not $actualPort) {
    Write-Host "Error: Could not find available port starting from $preferredPort" -ForegroundColor Red
    exit 1
}

if ($actualPort -ne $preferredPort) {
    Write-Host "Port $preferredPort is in use. Using port $actualPort instead." -ForegroundColor Yellow
    $port = $actualPort
}

# Start HTTP server
Write-Host "Starting server on port $port..." -ForegroundColor Green
& $pythonCmd -m http.server $port
