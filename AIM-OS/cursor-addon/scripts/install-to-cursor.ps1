# AIM-OS Cursor Extension Installation Script (PowerShell)
# Installs the extension to Cursor/VSCode

Write-Host "🚀 Installing AIM-OS Cursor Extension..." -ForegroundColor Green
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "package.json")) {
    Write-Host "❌ Error: package.json not found. Please run this script from the cursor-addon directory." -ForegroundColor Red
    exit 1
}

# Build the extension
Write-Host "📦 Building extension..." -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

# Package the extension
Write-Host "📋 Packaging extension..." -ForegroundColor Yellow
npx vsce package --out aimos-cursor-addon.vsix

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Packaging failed!" -ForegroundColor Red
    exit 1
}

# Find Cursor executable
$cursorPath = $null
$possiblePaths = @(
    "$env:LOCALAPPDATA\Programs\cursor\Cursor.exe",
    "$env:APPDATA\Cursor\bin\cursor.cmd",
    "cursor"
)

foreach ($path in $possiblePaths) {
    if (Get-Command $path -ErrorAction SilentlyContinue) {
        $cursorPath = $path
        break
    }
}

if (-not $cursorPath) {
    Write-Host "⚠️  Cursor not found in PATH. Trying to find VS Code..." -ForegroundColor Yellow
    
    $vscodePaths = @(
        "$env:LOCALAPPDATA\Programs\Microsoft VS Code\Code.exe",
        "$env:ProgramFiles\Microsoft VS Code\Code.exe",
        "code"
    )
    
    foreach ($path in $vscodePaths) {
        if (Get-Command $path -ErrorAction SilentlyContinue) {
            $cursorPath = $path
            break
        }
    }
}

if (-not $cursorPath) {
    Write-Host "❌ Neither Cursor nor VS Code found!" -ForegroundColor Red
    Write-Host "   Please install Cursor or VS Code, or install manually:" -ForegroundColor Yellow
    Write-Host "   code --install-extension aimos-cursor-addon.vsix" -ForegroundColor Cyan
    exit 1
}

# Install the extension
Write-Host "🔌 Installing extension to $cursorPath..." -ForegroundColor Yellow
& $cursorPath --install-extension aimos-cursor-addon.vsix --force

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Extension installed successfully!" -ForegroundColor Green
    Write-Host "   Please reload Cursor/VSCode to activate the extension." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   To open the dashboard, use:" -ForegroundColor Cyan
    Write-Host "   - Command Palette (Ctrl+Shift+P) > 'AIM-OS: Show Dashboard'" -ForegroundColor Cyan
    Write-Host "   - Or click the AIM-OS icon in the Activity Bar" -ForegroundColor Cyan
} else {
    Write-Host "❌ Installation failed!" -ForegroundColor Red
    Write-Host "   Try installing manually: $cursorPath --install-extension aimos-cursor-addon.vsix --force" -ForegroundColor Yellow
    exit 1
}

