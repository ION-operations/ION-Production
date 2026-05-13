param(
    [int]$Port = 5001,
    [string]$BindHost = "127.0.0.1",
    [string]$MemoryDir = "./mcp_memory"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

if (-not $env:PYTHONPATH) {
    $env:PYTHONPATH = "$repoRoot;$repoRoot\packages"
} else {
    $env:PYTHONPATH = "$repoRoot;$repoRoot\packages;$env:PYTHONPATH"
}

Write-Host "Starting MCP HTTP fallback bridge on http://$BindHost`:$Port" -ForegroundColor Cyan
Write-Host "Repo root: $repoRoot" -ForegroundColor DarkGray

python -u scripts/mcp_http_fallback_server.py --host $BindHost --port $Port --memory-dir $MemoryDir
