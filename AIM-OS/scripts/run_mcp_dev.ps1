# LUCID-MCP dev launcher: HHNI_LOCAL=1 (no Docker), MCP_MEMORY_DIR, PYTHONPATH
# Use this as the MCP server "command" in Cursor: pwsh -File path/to/run_mcp_dev.ps1
$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$aimosRoot = Split-Path -Parent $scriptDir

$env:HHNI_LOCAL = "1"
$env:MCP_MEMORY_DIR = Join-Path $aimosRoot "mcp_memory"
$env:PYTHONPATH = "$aimosRoot;$aimosRoot\packages"

Set-Location $aimosRoot
python lucid_mcp_server.py
