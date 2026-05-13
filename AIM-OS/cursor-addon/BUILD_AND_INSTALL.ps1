# Build and Install Script for Testing
Write-Host "🚀 Building AIM-OS Cursor Extension with Test Panel..." -ForegroundColor Cyan

# Navigate to cursor-addon directory
Set-Location $PSScriptRoot

# Build the extension
Write-Host "📦 Building extension..." -ForegroundColor Yellow
npm run build

# Package the extension
Write-Host "📦 Creating VSIX package..." -ForegroundColor Yellow
npm run package

# Install the extension
Write-Host "📦 Installing extension..." -ForegroundColor Yellow
code --install-extension aimos-cursor-addon.vsix --force

Write-Host "✅ Done! Now:" -ForegroundColor Green
Write-Host "1. Press Ctrl+Shift+P" -ForegroundColor White
Write-Host "2. Type: Developer: Reload Window" -ForegroundColor White
Write-Host "3. Look for 'Test Panel' tab in bottom panel" -ForegroundColor White
Write-Host "4. Click it to test if webview works!" -ForegroundColor White
