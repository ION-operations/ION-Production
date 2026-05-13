# ═══════════════════════════════════════════════════════════════════
#  J.A.R.V.I.S. — Joint AI Research & Visualization Intelligence System
#  PowerShell launcher with MCP server orchestration
# ═══════════════════════════════════════════════════════════════════

param(
    [ValidateSet("dev", "electron", "build", "full")]
    [string]$Mode = "dev",
    [switch]$WithMCP,
    [switch]$WithBAS
)

$Host.UI.RawUI.WindowTitle = "J.A.R.V.I.S. v2.0"

# ─── ASCII Art Intro ────────────────────────────────────────────
Write-Host ""
Write-Host ""
Write-Host "       ____. _____  __________  ____   ____.___.  _________" -ForegroundColor Cyan
Write-Host "      |    |/  _  \ \______   \ \   \ /   /|   |/   _____/" -ForegroundColor Cyan
Write-Host "      |    /  /_\  \ |       _/  \   Y   / |   |\_____  \ " -ForegroundColor Cyan
Write-Host "  |   |   /    |    \|    |   \   \     /  |   |/        \" -ForegroundColor DarkCyan
Write-Host "  |___|___\____|__  /|____|   /    \___/   |___/_______  /" -ForegroundColor DarkCyan
Write-Host "                  \/        \/                         \/" -ForegroundColor DarkCyan
Write-Host ""
Write-Host "   ╔═══════════════════════════════════════════════════════════╗" -ForegroundColor DarkGray
Write-Host "   ║" -NoNewline -ForegroundColor DarkGray
Write-Host "  Joint AI Research & Visualization Intelligence System  " -NoNewline -ForegroundColor White
Write-Host " ║" -ForegroundColor DarkGray
Write-Host "   ║" -NoNewline -ForegroundColor DarkGray
Write-Host "  AIM-OS Command Surface v2.0                            " -NoNewline -ForegroundColor DarkCyan
Write-Host " ║" -ForegroundColor DarkGray
Write-Host "   ║" -NoNewline -ForegroundColor DarkGray
Write-Host "                                                          " -NoNewline -ForegroundColor DarkGray
Write-Host " ║" -ForegroundColor DarkGray
Write-Host "   ║" -NoNewline -ForegroundColor DarkGray
Write-Host "  ◈ 14 Subsystems" -NoNewline -ForegroundColor Green
Write-Host " │ " -NoNewline -ForegroundColor DarkGray
Write-Host "92 MCP Tools" -NoNewline -ForegroundColor Yellow
Write-Host " │ " -NoNewline -ForegroundColor DarkGray
Write-Host "6 Agents" -NoNewline -ForegroundColor Magenta
Write-Host " │ " -NoNewline -ForegroundColor DarkGray
Write-Host "190+ Atoms  " -NoNewline -ForegroundColor Blue
Write-Host " ║" -ForegroundColor DarkGray
Write-Host "   ╚═══════════════════════════════════════════════════════════╝" -ForegroundColor DarkGray
Write-Host ""

$JocDir = Join-Path $PSScriptRoot "..\..\packages\joc"
$JocDir = (Resolve-Path $JocDir).Path
$RootDir = Join-Path $PSScriptRoot "..\.."
$RootDir = (Resolve-Path $RootDir).Path

# ─── Step 1: Dependencies ──────────────────────────────────────
Write-Host "   [1/4] " -NoNewline -ForegroundColor Yellow
Write-Host "Checking dependencies..."
if (-not (Test-Path (Join-Path $JocDir "node_modules"))) {
    Write-Host "         Installing JOC dependencies..." -ForegroundColor DarkYellow
    Push-Location $JocDir
    npm install
    Pop-Location
}
else {
    Write-Host "         Dependencies OK" -ForegroundColor Green
}

# ─── Step 2: MCP Server (optional) ─────────────────────────────
if ($WithMCP -or $Mode -eq "full") {
    Write-Host ""
    Write-Host "   [2/4] " -NoNewline -ForegroundColor Yellow
    Write-Host "Starting MCP Core Server (Port 5001)..."
    $mcpProcess = Start-Process -FilePath "node" -ArgumentList "index.js" `
        -WorkingDirectory (Join-Path $RootDir "scripts\mcp_server") `
        -PassThru -WindowStyle Minimized
    Write-Host "         MCP Server PID: $($mcpProcess.Id)" -ForegroundColor Green
    Start-Sleep -Seconds 2
}
else {
    Write-Host "   [2/4] " -NoNewline -ForegroundColor DarkGray
    Write-Host "MCP Server: Skipped (use -WithMCP)" -ForegroundColor DarkGray
}

# ─── Step 3: BAS/SEER (optional) ───────────────────────────────
if ($WithBAS -or $Mode -eq "full") {
    Write-Host ""
    Write-Host "   [3/4] " -NoNewline -ForegroundColor Yellow
    Write-Host "Starting Browser Automation Service (Port 5002)..."
    $basProcess = Start-Process -FilePath "npm" -ArgumentList "start" `
        -WorkingDirectory (Join-Path $RootDir "packages\browser-automation-service") `
        -PassThru -WindowStyle Minimized
    Write-Host "         BAS Server PID: $($basProcess.Id)" -ForegroundColor Green
    Start-Sleep -Seconds 2
}
else {
    Write-Host "   [3/4] " -NoNewline -ForegroundColor DarkGray
    Write-Host "BAS/SEER: Skipped (use -WithBAS)" -ForegroundColor DarkGray
}

# ─── Launch ─────────────────────────────────────────────────────
Write-Host ""
Write-Host "   ──────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host "   To stop: press " -NoNewline -ForegroundColor White
Write-Host "Ctrl+C" -NoNewline -ForegroundColor Yellow
Write-Host " in this window, then close it." -ForegroundColor White
Write-Host "   Do NOT close with X alone or the app keeps running." -ForegroundColor DarkGray
Write-Host "   If PC is slow later: " -NoNewline -ForegroundColor DarkGray
Write-Host "apps\KILL_ORPHAN_DEV_APPS.bat" -ForegroundColor Yellow
Write-Host "   ──────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host ""

Write-Host "   [4/4] " -NoNewline -ForegroundColor Yellow
Write-Host "Launching J.A.R.V.I.S. " -NoNewline
Write-Host "[$Mode]" -ForegroundColor Cyan
Write-Host ""

Push-Location $JocDir

switch ($Mode) {
    "electron" {
        Write-Host "   Starting Electron desktop shell..." -ForegroundColor Cyan
        npm run electron:dev
    }
    "build" {
        Write-Host "   Building production bundle..." -ForegroundColor Cyan
        npm run build
    }
    "full" {
        Write-Host "   Full stack: MCP + BAS + Electron..." -ForegroundColor Cyan
        npm run electron:dev
    }
    default {
        Write-Host "   Starting Vite dev server → " -NoNewline -ForegroundColor White
        Write-Host "http://localhost:5011" -ForegroundColor Green
        npm run dev
    }
}

Pop-Location

Write-Host ""
Write-Host "   J.A.R.V.I.S. terminated." -ForegroundColor DarkGray
