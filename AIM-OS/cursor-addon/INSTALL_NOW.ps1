# Quick Install Script for AIM-OS Extension
# Run this from cursor-addon directory

Write-Host "🚀 Installing AIM-OS Extension..." -ForegroundColor Cyan
Write-Host ""

# Step 1: Build
Write-Host "📦 Step 1: Building extension..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

# Step 2: Package
Write-Host ""
Write-Host "📦 Step 2: Packaging extension..." -ForegroundColor Yellow
npm run package
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Package failed!" -ForegroundColor Red
    exit 1
}

# Step 3: Check file exists
$vsixPath = Join-Path $PWD "aimos-cursor-addon.vsix"
if (-not (Test-Path $vsixPath)) {
    Write-Host "❌ Extension file not found!" -ForegroundColor Red
    exit 1
}

$fileSize = (Get-Item $vsixPath).Length
Write-Host ""
Write-Host "✅ Extension ready: $fileSize bytes" -ForegroundColor Green
Write-Host "📦 File: $vsixPath" -ForegroundColor Yellow
Write-Host ""

# Step 4: Try to install
Write-Host "🔧 Step 3: Installing extension..." -ForegroundColor Yellow

# Try code command first
$codeCmd = Get-Command code -ErrorAction SilentlyContinue
if ($codeCmd) {
    Write-Host "Using 'code' command..." -ForegroundColor Gray
    code --install-extension $vsixPath --force
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Extension installed successfully!" -ForegroundColor Green
        Write-Host "🔄 Please restart Cursor to see the changes." -ForegroundColor Cyan
        exit 0
    }
}

# Try Cursor.exe directly
$cursorPaths = @(
    "$env:LOCALAPPDATA\Programs\cursor\Cursor.exe",
    "$env:PROGRAMFILES\Cursor\Cursor.exe",
    "$env:PROGRAMFILES(X86)\Cursor\Cursor.exe"
)

foreach ($cursorPath in $cursorPaths) {
    if (Test-Path $cursorPath) {
        Write-Host "Using Cursor.exe at: $cursorPath" -ForegroundColor Gray
        & $cursorPath --install-extension $vsixPath --force
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Extension installed successfully!" -ForegroundColor Green
            Write-Host "🔄 Please restart Cursor to see the changes." -ForegroundColor Cyan
            exit 0
        }
        break
    }
}

# Manual installation instructions
Write-Host ""
Write-Host "⚠️  Automatic installation failed. Please install manually:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Open Cursor" -ForegroundColor White
Write-Host "2. Press Ctrl+Shift+X (or View → Extensions)" -ForegroundColor White
Write-Host "3. Click the '...' menu (top right)" -ForegroundColor White
Write-Host "4. Select 'Install from VSIX...'" -ForegroundColor White
Write-Host "5. Navigate to: $vsixPath" -ForegroundColor White
Write-Host "6. Select the file and click Install" -ForegroundColor White
Write-Host "7. Restart Cursor" -ForegroundColor White
Write-Host ""

