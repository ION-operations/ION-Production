# AIM-OS Gemini Bridge — Native Messaging Host Installation (Windows)
#
# Run this script ONCE as Administrator (or current user) to register the
# native messaging host with Chrome/Edge so the extension can connect.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts\install_native_host.ps1
#

$ErrorActionPreference = "Stop"

$REPO_ROOT = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$HOST_NAME = "aimos_bridge"
$MANIFEST_PATH = Join-Path $REPO_ROOT "scripts\aimos_bridge.json"
$HOST_SCRIPT = Join-Path $REPO_ROOT "scripts\aimos_bridge_host.py"

# Find Python
$PYTHON = Get-Command python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
if (-not $PYTHON) {
    $PYTHON = Get-Command python3 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
}
if (-not $PYTHON) {
    Write-Error "Python not found in PATH. Install Python 3.10+ and try again."
    exit 1
}

Write-Host "`n[AIM-OS] Installing Gemini Bridge Native Messaging Host" -ForegroundColor Cyan
Write-Host "  Repo Root  : $REPO_ROOT"
Write-Host "  Host Script: $HOST_SCRIPT"
Write-Host "  Python     : $PYTHON"

# ── Step 1: Create the batch wrapper ────────────────────────────────
# Chrome on Windows expects an .exe or .bat, not a .py directly
$BAT_PATH = Join-Path $REPO_ROOT "scripts\aimos_bridge_host.bat"
$batContent = @"
@echo off
"$PYTHON" "$HOST_SCRIPT" %*
"@
Set-Content -Path $BAT_PATH -Value $batContent -Encoding ASCII
Write-Host "  Created    : $BAT_PATH" -ForegroundColor Green

# ── Step 2: Write the native messaging host manifest ────────────────
# NOTE: The extension ID will need to be updated after loading the extension.
# For now we use a wildcard-friendly approach via "allowed_origins".
$manifest = @{
    name            = $HOST_NAME
    description     = "AIM-OS Gemini Bridge - connects Gemini web to lucid-mcp"
    path            = $BAT_PATH
    type            = "stdio"
    allowed_origins = @(
        "chrome-extension://mpcbkjenapbapppjodecppiolifadbhl/"
    )
} | ConvertTo-Json -Depth 3

Set-Content -Path $MANIFEST_PATH -Value $manifest -Encoding UTF8
Write-Host "  Manifest   : $MANIFEST_PATH" -ForegroundColor Green

# ── Step 3: Register in Windows Registry (current user) ─────────────
$regPath = "HKCU:\Software\Google\Chrome\NativeMessagingHosts\$HOST_NAME"
if (-not (Test-Path $regPath)) {
    New-Item -Path $regPath -Force | Out-Null
}
Set-ItemProperty -Path $regPath -Name "(Default)" -Value $MANIFEST_PATH

Write-Host "  Registry   : $regPath" -ForegroundColor Green

# Also register for Edge (Chromium-based)
$edgeRegPath = "HKCU:\Software\Microsoft\Edge\NativeMessagingHosts\$HOST_NAME"
if (-not (Test-Path $edgeRegPath)) {
    New-Item -Path $edgeRegPath -Force | Out-Null
}
Set-ItemProperty -Path $edgeRegPath -Name "(Default)" -Value $MANIFEST_PATH
Write-Host "  Edge Reg   : $edgeRegPath" -ForegroundColor Green

Write-Host "`n[AIM-OS] Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "  1. Load the extension in Chrome:"
Write-Host "     chrome://extensions -> Developer mode -> Load unpacked"
Write-Host "     Point to: $REPO_ROOT\IDE\extensions\gemini-bridge"
Write-Host ""
Write-Host "  2. Copy the Extension ID from chrome://extensions"
Write-Host ""
Write-Host "  3. Update the allowed_origins in:"
Write-Host "     $MANIFEST_PATH"
Write-Host "     Replace EXTENSION_ID_PLACEHOLDER with your actual extension ID"
Write-Host ""
Write-Host "  4. Re-run this script to update the registry with the correct manifest"
Write-Host ""
Write-Host "  5. Open https://gemini.google.com and look for the AIM-OS badge!"
Write-Host ""
