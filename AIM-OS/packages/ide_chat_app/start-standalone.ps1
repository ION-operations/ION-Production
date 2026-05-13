# Standalone AIM-OS Dashboard Server - PowerShell Script
# Starts the dashboard in standalone mode for browser testing

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 AIM-OS Dashboard Standalone Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "⚠️  Dependencies not installed. Installing..." -ForegroundColor Yellow
    npm install
    Write-Host ""
}

# Check if dist exists (production build)
$hasBuild = Test-Path "dist"

if ($hasBuild) {
    Write-Host "✅ Found production build (dist/)" -ForegroundColor Green
    Write-Host "📦 Starting preview server (production build)..." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🌐 Dashboard will open at: http://localhost:4173" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
    Write-Host ""
    
    # Open browser after 2 seconds
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:4173"
    
    npm run preview
} else {
    Write-Host "⚠️  No production build found. Starting dev server..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🌐 Dashboard will open at: http://localhost:3000" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
    Write-Host ""
    
    # Open browser after 2 seconds
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:3000"
    
    npm run dev
}

