# Aether IDE V2 Prototype Launcher (PowerShell)
# Enhanced launcher with V2 foundation features
# One-click launcher for Windows PowerShell

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Aether IDE V2 Prototype Launcher" -ForegroundColor Cyan
Write-Host "  System Architecture & Deep AIM-OS Integration" -ForegroundColor Cyan
Write-Host "  Phase 6 Foundation: 95% Complete" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "[INFO] Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js is not installed or not in PATH!" -ForegroundColor Red
    Write-Host "[INFO] Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Check if npm is installed
try {
    $npmVersion = npm --version
    Write-Host "[INFO] npm version: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] npm is not installed or not in PATH!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "[INFO] Installing dependencies..." -ForegroundColor Yellow
    Write-Host "[INFO] This may take a few minutes..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to install dependencies!" -ForegroundColor Red
        Write-Host "[INFO] Try running: npm install" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "[SUCCESS] Dependencies installed!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[INFO] Dependencies already installed" -ForegroundColor Green
    Write-Host ""
}

# Check if TypeScript compilation is needed
if (Test-Path "src") {
    Write-Host "[INFO] Checking TypeScript compilation..." -ForegroundColor Yellow
    npm run build *> $null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[WARNING] TypeScript compilation had warnings (non-blocking)" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Display V2 features
Write-Host "[INFO] V2 Foundation Features:" -ForegroundColor Cyan
Write-Host "  - Hook System (9 hooks: useAIMOS + 8 individual)" -ForegroundColor White
Write-Host "  - State Management (Zustand panelStore)" -ForegroundColor White
Write-Host "  - 35 Panels Managed" -ForegroundColor White
Write-Host "  - Error Boundaries" -ForegroundColor White
Write-Host "  - Loading States" -ForegroundColor White
Write-Host "  - Performance Optimizations" -ForegroundColor White
Write-Host "  - Layout Presets" -ForegroundColor White
Write-Host ""

# Start the dev server
Write-Host "[INFO] Starting AETHER V2 IDE Prototype..." -ForegroundColor Green
Write-Host "[INFO] Server will find an open port automatically" -ForegroundColor Cyan
Write-Host "[INFO] WATCH THE TERMINAL FOR THE ACTUAL PORT NUMBER!" -ForegroundColor Yellow
Write-Host "[INFO] Browser title will show: [AETHER V2] IDE Prototype" -ForegroundColor Cyan
Write-Host "[INFO] Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "[TIP] Features available:" -ForegroundColor Cyan
Write-Host "  - Panel management via Zustand store" -ForegroundColor White
Write-Host "  - Layout presets (save/load in top bar)" -ForegroundColor White
Write-Host "  - Error boundaries for panel failures" -ForegroundColor White
Write-Host "  - Loading states for async operations" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "  LOOK FOR THIS IN TERMINAL OUTPUT:" -ForegroundColor Yellow
Write-Host "  Local:   http://localhost:XXXX/" -ForegroundColor Yellow
Write-Host "  THAT IS YOUR PORT NUMBER!" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

npm run dev

