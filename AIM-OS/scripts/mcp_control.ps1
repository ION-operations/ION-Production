param(
    [ValidateSet("start", "stop", "restart", "status", "test", "ensure")]
    [string]$Action = "status",
    [int]$Port = 5001,
    [string]$BindHost = "127.0.0.1",
    [string]$MemoryDir = ".\mcp_memory"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir

function Get-McpProcesses {
    $portPattern = "--port\s+$Port(\s|$)"
    Get-CimInstance Win32_Process | Where-Object {
        $_.Name -match '^python(\.exe)?$' -and
        $_.CommandLine -match 'mcp_http_fallback_server\.py' -and
        $_.CommandLine -match $portPattern
    }
}

function Get-McpHealth {
    try {
        Invoke-RestMethod -Uri "http://$BindHost`:$Port/health" -Method Get -TimeoutSec 5
    } catch {
        $null
    }
}

function Get-McpReadiness {
    $result = [ordered]@{
        HealthOk = $false
        Health = $null
        ListOk = $false
        ToolCount = $null
        ExecuteOk = $false
        TotalAtoms = $null
        Error = $null
    }

    try {
        $health = Invoke-RestMethod -Uri "http://$BindHost`:$Port/health" -Method Get -TimeoutSec 5
        $result.HealthOk = $true
        $result.Health = $health
    } catch {
        $result.Error = "health: $($_.Exception.Message)"
        return [pscustomobject]$result
    }

    try {
        $list = Invoke-RestMethod -Uri "http://$BindHost`:$Port/mcp/list" -Method Get -TimeoutSec 30
        if ($list.success) {
            $result.ListOk = $true
            $result.ToolCount = $list.count
        } else {
            $result.Error = "mcp/list: $($list.error)"
            return [pscustomobject]$result
        }
    } catch {
        $result.Error = "mcp/list: $($_.Exception.Message)"
        return [pscustomobject]$result
    }

    try {
        $payload = @{ tool = "get_memory_stats"; arguments = @{} } | ConvertTo-Json -Depth 5
        $exec = Invoke-RestMethod -Uri "http://$BindHost`:$Port/mcp/execute" -Method Post -ContentType "application/json" -Body $payload -TimeoutSec 30
        if ($exec.success) {
            $result.ExecuteOk = $true
            $result.TotalAtoms = $exec.result.stats.total_atoms
        } else {
            $result.Error = "mcp/execute: $($exec.error)"
            return [pscustomobject]$result
        }
    } catch {
        $result.Error = "mcp/execute: $($_.Exception.Message)"
        return [pscustomobject]$result
    }

    return [pscustomobject]$result
}

function Show-McpStatus {
    $procs = Get-McpProcesses
    $listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    $health = Get-McpHealth
    $readiness = Get-McpReadiness

    Write-Host "MCP Control Status" -ForegroundColor Cyan
    Write-Host "RepoRoot: $repoRoot"
    Write-Host "Endpoint: http://$BindHost`:$Port"

    if ($listeners) {
        Write-Host "Port ${Port}: LISTENING" -ForegroundColor Green
        $listeners | Select-Object LocalAddress, LocalPort, OwningProcess, State | Format-Table -AutoSize
    } else {
        Write-Host "Port ${Port}: NOT LISTENING" -ForegroundColor Yellow
    }

    if ($procs) {
        Write-Host "Fallback server processes:" -ForegroundColor Green
        $procs | Select-Object ProcessId, Name, CommandLine | Format-List
    } else {
        Write-Host "Fallback server process: NOT FOUND" -ForegroundColor Yellow
    }

    if ($health) {
        Write-Host "Health: OK (ready=$($health.ready), mode=$($health.mode))" -ForegroundColor Green
    } else {
        Write-Host "Health: UNREACHABLE" -ForegroundColor Red
    }

    if ($readiness.HealthOk -and $readiness.ListOk -and $readiness.ExecuteOk) {
        Write-Host "Tool Surface: READY (tools=$($readiness.ToolCount), total_atoms=$($readiness.TotalAtoms))" -ForegroundColor Green
    } elseif ($readiness.HealthOk) {
        Write-Host "Tool Surface: DEGRADED ($($readiness.Error))" -ForegroundColor Yellow
        Write-Host "Suggested action: scripts/mcp_control.ps1 -Action ensure" -ForegroundColor Yellow
    } else {
        Write-Host "Tool Surface: UNREACHABLE ($($readiness.Error))" -ForegroundColor Red
    }
}

function Start-Mcp {
    $existingReadiness = Get-McpReadiness
    if ($existingReadiness.HealthOk -and $existingReadiness.ListOk -and $existingReadiness.ExecuteOk) {
        Write-Host "MCP already ready at http://$BindHost`:$Port" -ForegroundColor Green
        return
    }

    $launchSteps = @(
        ('cd /d "{0}"' -f $repoRoot),
        ('set PYTHONPATH={0};{0}\packages' -f $repoRoot),
        ('set AIMOS_COLLAB_ROOT={0}' -f $repoRoot),
        'set AIMOS_HHNI_EAGER_INIT=0',
        ('python -u scripts\mcp_http_fallback_server.py --host {0} --port {1} --memory-dir "{2}"' -f $BindHost, $Port, $MemoryDir)
    )
    $launchCmd = ($launchSteps -join ' && ')
    $startCmd = 'start "" cmd /c "{0}"' -f $launchCmd

    $stale = Get-McpProcesses
    foreach ($p in $stale) {
        Write-Host "Stopping stale MCP process PID $($p.ProcessId) before start..." -ForegroundColor Yellow
        Stop-Process -Id $p.ProcessId -Force
    }

    cmd /c $startCmd | Out-Null
    Start-Sleep -Seconds 3

    $readiness = Get-McpReadiness
    if (-not ($readiness.HealthOk -and $readiness.ListOk -and $readiness.ExecuteOk)) {
        throw "MCP failed to reach tool-ready state on http://$BindHost`:$Port ($($readiness.Error))"
    }

    Write-Host "MCP started successfully at http://$BindHost`:$Port (mode=$($readiness.Health.mode), tools=$($readiness.ToolCount), total_atoms=$($readiness.TotalAtoms))" -ForegroundColor Green
}

function Stop-Mcp {
    $procs = Get-McpProcesses
    if (-not $procs) {
        Write-Host "No fallback MCP process found for port $Port." -ForegroundColor Yellow
        return
    }

    foreach ($p in $procs) {
        Write-Host "Stopping PID $($p.ProcessId)..." -ForegroundColor Cyan
        Stop-Process -Id $p.ProcessId -Force
    }

    Start-Sleep -Seconds 1
    $remaining = Get-McpProcesses
    if ($remaining) {
        throw "One or more fallback MCP processes are still running."
    }

    Write-Host "Fallback MCP processes stopped." -ForegroundColor Green
}

function Test-Mcp {
    $readiness = Get-McpReadiness
    if (-not ($readiness.HealthOk -and $readiness.ListOk -and $readiness.ExecuteOk)) {
        throw "MCP test failed: $($readiness.Error)"
    }

    Write-Host "MCP test passed." -ForegroundColor Green
    Write-Host " - Health mode: $($readiness.Health.mode), ready: $($readiness.Health.ready)"
    Write-Host " - Tool count: $($readiness.ToolCount)"
    Write-Host " - get_memory_stats total_atoms: $($readiness.TotalAtoms)"
}

function Ensure-Mcp {
    $readiness = Get-McpReadiness
    if ($readiness.HealthOk -and $readiness.ListOk -and $readiness.ExecuteOk) {
        Write-Host "MCP already ready; no action required." -ForegroundColor Green
        return
    }

    Write-Host "MCP not ready ($($readiness.Error)); restarting..." -ForegroundColor Yellow
    Stop-Mcp
    Start-Mcp
    Test-Mcp
}

switch ($Action) {
    "status" { Show-McpStatus; break }
    "start" { Start-Mcp; break }
    "stop" { Stop-Mcp; break }
    "restart" { Stop-Mcp; Start-Mcp; break }
    "test" { Test-Mcp; break }
    "ensure" { Ensure-Mcp; break }
}
