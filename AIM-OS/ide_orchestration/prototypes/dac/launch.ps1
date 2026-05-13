# DAC IDE Prototype V2 - Launcher Script
# Quick launcher for Windows PowerShell

Write-Host "Launching DAC IDE Prototype V2..." -ForegroundColor Cyan
Write-Host ""

# Check Node.js version
$nodeVersion = node --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Node.js not found. Please install Node.js 18+ from https://nodejs.org/" -ForegroundColor Red
    exit 1
}
Write-Host "OK: Node.js version: $nodeVersion" -ForegroundColor Green

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "WARNING: node_modules not found. Installing dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install dependencies. Please run 'npm install' manually." -ForegroundColor Red
        exit 1
    }
    Write-Host ""
}

Write-Host "OK: Dependencies ready" -ForegroundColor Green
Write-Host ""

# Check Python
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
}

if (-not $pythonCmd) {
    Write-Host "WARNING: Python not found. Backend server will not start." -ForegroundColor Yellow
    Write-Host "   Install Python 3.8+ from https://www.python.org/" -ForegroundColor Gray
    Write-Host ""
} else {
    $pythonVersion = & $pythonCmd --version 2>&1
    Write-Host "OK: Python found: $pythonVersion" -ForegroundColor Green
    
    # Check if backend is already running
    $backendRunning = $false
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $backendRunning = $true
            Write-Host "OK: Backend server already running on port 8000" -ForegroundColor Green
        }
    } catch {
        # Backend not running, that's fine
    }
    
    if (-not $backendRunning) {
        Write-Host "Starting backend server (port 8000)..." -ForegroundColor Cyan
        
        # Get repo root (go up from ide_orchestration/prototypes/dac)
        $repoRoot = (Get-Location).Path
        while (-not (Test-Path (Join-Path $repoRoot "packages\cmc_service\api.py"))) {
            $parent = Split-Path $repoRoot -Parent
            if ($parent -eq $repoRoot) {
                Write-Host "WARNING: Could not find packages/cmc_service/api.py" -ForegroundColor Yellow
                break
            }
            $repoRoot = $parent
        }
        
        $backendDir = Join-Path $repoRoot "packages\cmc_service"
        
        # Try standalone IDE backend first (simpler, no dependencies)
        $ideBackendPath = Join-Path $repoRoot "ide_orchestration\prototypes\dac\backend_server.py"
        if (Test-Path $ideBackendPath) {
            # Start standalone IDE backend (run from repo root so it can find knowledge_architecture)
            $backendProcess = Start-Process -FilePath $pythonCmd -ArgumentList $ideBackendPath -WorkingDirectory $repoRoot -PassThru -WindowStyle Hidden
        } elseif (Test-Path (Join-Path $backendDir "api.py")) {
            # Fallback to CMC service API (may have dependency issues)
            $backendProcess = Start-Process -FilePath $pythonCmd -ArgumentList "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--reload" -WorkingDirectory $backendDir -PassThru -WindowStyle Hidden
            
            # Wait for backend to start
            $maxWait = 10
            $waited = 0
            while ($waited -lt $maxWait) {
                Start-Sleep -Seconds 1
                $waited++
                try {
                    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 1 -ErrorAction SilentlyContinue
                    if ($response.StatusCode -eq 200) {
                        Write-Host "OK: Backend server started successfully" -ForegroundColor Green
                        break
                    }
                } catch {
                    # Still starting
                }
            }
            
            if ($waited -ge $maxWait) {
                Write-Host "WARNING: Backend server may not have started properly" -ForegroundColor Yellow
            }
        } else {
            Write-Host "WARNING: Backend server files not found at $backendDir" -ForegroundColor Yellow
        }
    }
    Write-Host ""
}

Write-Host "Starting development server..." -ForegroundColor Cyan
Write-Host "The IDE will automatically open at http://localhost:3002" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop all servers" -ForegroundColor Gray
Write-Host ""

# Start the dev server (Vite will auto-open browser)
try {
    npm run dev
} finally {
    # Cleanup: Kill backend process if we started it
    if ($backendProcess -and -not $backendProcess.HasExited) {
        Write-Host ""
        Write-Host 'Stopping backend server...' -ForegroundColor Cyan
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    }
}

