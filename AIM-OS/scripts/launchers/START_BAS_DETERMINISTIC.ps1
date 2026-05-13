param(
    [int]$Port = 5002,
    [int]$TimeoutSeconds = 90,
    [switch]$RecycleStaleListener = $true
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$basDir = Join-Path $repoRoot "packages\browser-automation-service"
$healthUrl = "http://127.0.0.1:$Port/health"
$logDir = Join-Path $repoRoot "logs"
$stdoutLog = Join-Path $logDir "bas_stdout.log"
$stderrLog = Join-Path $logDir "bas_stderr.log"

New-Item -ItemType Directory -Force -Path $logDir | Out-Null

function Test-BasHealth {
    param([string]$Url)
    try {
        $res = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 3 -ErrorAction Stop
        return ($res.StatusCode -eq 200)
    } catch {
        return $false
    }
}

function Get-ListeningPidForPort {
    param([int]$PortNumber)
    try {
        $conn = Get-NetTCPConnection -State Listen -LocalPort $PortNumber -ErrorAction Stop | Select-Object -First 1
        if ($conn) { return [int]$conn.OwningProcess }
    } catch {}
    return $null
}

Write-Host "=== BAS Deterministic Launcher ===" -ForegroundColor Cyan
Write-Host "Repo root: $repoRoot" -ForegroundColor DarkGray
Write-Host "BAS dir:   $basDir" -ForegroundColor DarkGray
Write-Host "Health:    $healthUrl" -ForegroundColor DarkGray

if (Test-BasHealth -Url $healthUrl) {
    Write-Host "BAS already healthy on :$Port" -ForegroundColor Green
    exit 0
}

# If a listener already exists, prefer waiting for health rather than spawning duplicate BAS.
$existingPid = Get-ListeningPidForPort -PortNumber $Port
if ($existingPid) {
    Write-Host "Port :$Port already has listener PID=$existingPid; waiting for health..." -ForegroundColor Yellow
    $existingDeadline = (Get-Date).AddSeconds([Math]::Min($TimeoutSeconds, 30))
    while ((Get-Date) -lt $existingDeadline) {
        if (Test-BasHealth -Url $healthUrl) {
            Write-Host "BAS healthy on :$Port via existing process PID=$existingPid" -ForegroundColor Green
            exit 0
        }
        Start-Sleep -Seconds 2
    }
    Write-Host "Listener exists on :$Port but BAS health is not responding." -ForegroundColor Yellow
    if ($RecycleStaleListener) {
        Write-Host "Recycling stale listener PID=$existingPid ..." -ForegroundColor Yellow
        try {
            Stop-Process -Id $existingPid -Force -ErrorAction Stop
            Start-Sleep -Seconds 2
        } catch {
            Write-Host "Failed to stop stale listener PID=${existingPid}: $($_.Exception.Message)" -ForegroundColor Red
            exit 3
        }
        if (Get-ListeningPidForPort -PortNumber $Port) {
            Write-Host "Port :$Port still occupied after recycle attempt." -ForegroundColor Red
            exit 3
        }
    } else {
        exit 3
    }
}

if (-not (Test-Path $basDir)) {
    Write-Host "BAS directory not found: $basDir" -ForegroundColor Red
    exit 1
}

Write-Host "Starting BAS via npm start..." -ForegroundColor Yellow

# Keep a clean log window for startup diagnostics.
if (Test-Path $stdoutLog) { Remove-Item $stdoutLog -Force -ErrorAction SilentlyContinue }
if (Test-Path $stderrLog) { Remove-Item $stderrLog -Force -ErrorAction SilentlyContinue }

# On Windows, launch npm through cmd.exe for reliable process startup.
$proc = Start-Process -FilePath "cmd.exe" `
    -ArgumentList @("/c", "npm", "start") `
    -WorkingDirectory $basDir `
    -PassThru `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog

Write-Host "Spawned BAS process PID=$($proc.Id)" -ForegroundColor DarkGray

$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
while ((Get-Date) -lt $deadline) {
    if (Test-BasHealth -Url $healthUrl) {
        Write-Host "BAS healthy on :$Port" -ForegroundColor Green
        Write-Host "stdout log: $stdoutLog" -ForegroundColor DarkGray
        Write-Host "stderr log: $stderrLog" -ForegroundColor DarkGray
        exit 0
    }

    # If spawned process exited, classify quickly.
    if ($proc.HasExited) {
        $stderrText = ""
        if (Test-Path $stderrLog) {
            $stderrText = Get-Content $stderrLog -Raw -ErrorAction SilentlyContinue
        }
        if ($stderrText -match "EADDRINUSE" -and (Test-BasHealth -Url $healthUrl)) {
            Write-Host "BAS already active on :$Port (EADDRINUSE from duplicate spawn)." -ForegroundColor Green
            exit 0
        }
        Write-Host "Spawned BAS process exited before health became ready." -ForegroundColor Red
        Write-Host "stdout log: $stdoutLog" -ForegroundColor DarkGray
        Write-Host "stderr log: $stderrLog" -ForegroundColor DarkGray
        exit 4
    }

    Start-Sleep -Seconds 2
}

Write-Host "BAS did not become healthy within $TimeoutSeconds seconds." -ForegroundColor Red
Write-Host "stdout log: $stdoutLog" -ForegroundColor DarkGray
Write-Host "stderr log: $stderrLog" -ForegroundColor DarkGray
exit 2
