# Reinstall Cursor Extension Script
# This script will uninstall old version and install fresh

Write-Host "=== UNINSTALLING OLD EXTENSION ===" -ForegroundColor Yellow
code --uninstall-extension aimos.aimos-cursor-addon --force 2>&1 | Out-Null
Write-Host "✅ Old extension uninstalled" -ForegroundColor Green

Write-Host "`n=== INSTALLING NEW EXTENSION ===" -ForegroundColor Cyan
$vsixPath = Join-Path $PSScriptRoot "aimos-cursor-addon.vsix"
if (Test-Path $vsixPath) {
    code --install-extension $vsixPath --force
    Write-Host "✅ Extension installed!" -ForegroundColor Green
    Write-Host "`n=== NEXT STEPS ===" -ForegroundColor Cyan
    Write-Host "1. Reload Cursor window (Ctrl+R)" -ForegroundColor White
    Write-Host "2. Look for 'Lucid UI' icon in Activity Bar" -ForegroundColor White
    Write-Host "3. Or press Ctrl+Shift+P and type 'AIM-OS: Show Lucid Orchestrator Dashboard'" -ForegroundColor White
} else {
    Write-Host "❌ VSIX file not found: $vsixPath" -ForegroundColor Red
    Write-Host "   Run: npm run package" -ForegroundColor Yellow
    exit 1
}

