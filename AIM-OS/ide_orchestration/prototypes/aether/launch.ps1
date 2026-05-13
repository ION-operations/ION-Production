# Aether IDE Prototype Launcher (PowerShell)
# One-click launcher for Windows PowerShell

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Aether IDE Prototype Launcher" -ForegroundColor Cyan
Write-Host "  System Architecture & Deep AIM-OS Integration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

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

# Start the dev server
Write-Host "[INFO] Starting Aether IDE Prototype..." -ForegroundColor Yellow
Write-Host "[INFO] Server will open automatically at http://localhost:5173" -ForegroundColor Yellow
Write-Host "[INFO] Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

npm run dev

Read-Host "Press Enter to exit"

