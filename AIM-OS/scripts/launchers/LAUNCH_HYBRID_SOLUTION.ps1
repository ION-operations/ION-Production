# AIM-OS Hybrid Solution Launcher
# Launches Electron app and ensures command transport is available.

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AIM-OS Hybrid Solution Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

# Step 1: Check if extension is installed.
Write-Host "[1/3] Checking extension installation..." -ForegroundColor Yellow
$extensionPath = "$env:USERPROFILE\.cursor\extensions\aimos.aimos-cursor-addon-*"
$extensionInstalled = Test-Path $extensionPath

if (-not $extensionInstalled) {
    Write-Host "   WARN: Extension not found. Building and installing..." -ForegroundColor Yellow

    Write-Host "   Building extension..." -ForegroundColor Gray
    Set-Location "cursor-addon"
    npm run compile 2>&1 | Out-Null

    if (Test-Path "out\extension.js") {
        Write-Host "   OK: Extension compiled" -ForegroundColor Green
        Write-Host "   Packaging extension..." -ForegroundColor Gray
        vsce package --out aimos-cursor-addon.vsix 2>&1 | Out-Null

        if (Test-Path "aimos-cursor-addon.vsix") {
            Write-Host "   OK: Extension packaged" -ForegroundColor Green
            Write-Host "   Installing extension..." -ForegroundColor Gray
            code --install-extension aimos-cursor-addon.vsix --force 2>&1 | Out-Null
            Write-Host "   OK: Extension installed" -ForegroundColor Green
        }
        else {
            Write-Host "   ERROR: Failed to package extension" -ForegroundColor Red
        }
    }
    else {
        Write-Host "   ERROR: Failed to compile extension" -ForegroundColor Red
    }

    Set-Location ".."
}
else {
    Write-Host "   OK: Extension already installed" -ForegroundColor Green
}

Write-Host ""

# Step 2: Check if command server is running.
Write-Host "[2/3] Checking command server status..." -ForegroundColor Yellow
$commandServerReady = $false
try {
    $healthCheck = Invoke-WebRequest -Uri "http://localhost:5001/health" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($healthCheck.StatusCode -eq 200) {
        Write-Host "   OK: Command server is running on :5001" -ForegroundColor Green
        $commandServerReady = $true
    }
    else {
        Write-Host "   WARN: Command server not responding (extension may need activation)" -ForegroundColor Yellow
        Write-Host "   INFO: Open Cursor to activate extension, then relaunch" -ForegroundColor Gray
    }
}
catch {
    Write-Host "   WARN: Command server not running (extension may need activation)" -ForegroundColor Yellow
    Write-Host "   INFO: Open Cursor to activate extension, then relaunch" -ForegroundColor Gray
}

if (-not $commandServerReady) {
    Write-Host "   Attempting MCP fallback bridge on http://localhost:5003 ..." -ForegroundColor Yellow
    $fallbackHealthUrl = "http://localhost:5003/health"
    $fallbackScript = Join-Path $PSScriptRoot "..\run_mcp_http_fallback.ps1"

    $fallbackAlreadyRunning = $false
    try {
        $fallbackHealth = Invoke-WebRequest -Uri $fallbackHealthUrl -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($fallbackHealth.StatusCode -eq 200) {
            $fallbackAlreadyRunning = $true
        }
    }
    catch {
        $fallbackAlreadyRunning = $false
    }

    if ($fallbackAlreadyRunning) {
        Write-Host "   OK: MCP fallback bridge already running on :5003" -ForegroundColor Green
    }
    elseif (Test-Path $fallbackScript) {
        Start-Process -FilePath "powershell" -ArgumentList @(
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            $fallbackScript,
            "-Port",
            "5003"
        ) -WindowStyle Hidden | Out-Null
        Start-Sleep -Seconds 2

        try {
            $fallbackHealth = Invoke-WebRequest -Uri $fallbackHealthUrl -Method GET -TimeoutSec 4 -ErrorAction SilentlyContinue
            if ($fallbackHealth.StatusCode -eq 200) {
                Write-Host "   OK: MCP fallback bridge online on :5003" -ForegroundColor Green
            }
            else {
                Write-Host "   WARN: MCP fallback bridge did not respond after startup attempt" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "   WARN: MCP fallback bridge startup failed (continuing)" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "   WARN: Fallback script not found: $fallbackScript" -ForegroundColor Yellow
    }
}

Write-Host ""

# Step 3: Launch Electron app.
Write-Host "[3/3] Launching Electron app..." -ForegroundColor Yellow
Set-Location "packages\ide_chat_app"

if (-not (Test-Path "node_modules")) {
    Write-Host "   Installing dependencies..." -ForegroundColor Gray
    npm install 2>&1 | Out-Null
}

if (Test-Path "dist") {
    Write-Host "   OK: Production build found" -ForegroundColor Green
    Write-Host "   Launching Electron app..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Dashboard will open in Electron window" -ForegroundColor Gray
    Write-Host "   Command server: http://localhost:5001 (fallback: http://localhost:5003)" -ForegroundColor Gray
    Write-Host ""

    Start-Sleep -Seconds 1
    npm run electron
}
else {
    Write-Host "   WARN: No production build found. Building..." -ForegroundColor Yellow
    npm run build 2>&1 | Out-Null

    if (Test-Path "dist") {
        Write-Host "   OK: Build complete" -ForegroundColor Green
        Write-Host "   Launching Electron app..." -ForegroundColor Cyan
        Write-Host ""

        Start-Sleep -Seconds 1
        npm run electron
    }
    else {
        Write-Host "   ERROR: Build failed. Starting dev server instead..." -ForegroundColor Red
        Write-Host "   Launching Electron app (dev mode)..." -ForegroundColor Cyan
        Write-Host ""

        Start-Sleep -Seconds 1
        npm run electron:dev
    }
}

Set-Location "..\.."
