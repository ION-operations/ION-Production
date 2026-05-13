param(
    [Parameter(Mandatory = $true)]
    [string]$Agent,

    [Parameter(Mandatory = $true)]
    [string]$ActivationBrief,

    [Parameter(Mandatory = $true)]
    [string]$MissionPacket,

    [Parameter(Mandatory = $true)]
    [string]$Deliverable,

    [string]$RepoRoot = ""
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false

function Get-Slug {
    param([string]$Value)
    return (($Value.ToLowerInvariant() -replace "[^a-z0-9._-]+", "_").Trim("_"))
}

function Resolve-RepoPath {
    param(
        [string]$Root,
        [string]$PathValue
    )

    if ([System.IO.Path]::IsPathRooted($PathValue)) {
        return [System.IO.Path]::GetFullPath($PathValue)
    }

    return [System.IO.Path]::GetFullPath((Join-Path $Root $PathValue))
}

function Require-Path {
    param([string]$PathValue, [string]$Label)
    if (-not (Test-Path -LiteralPath $PathValue)) {
        throw "$Label not found: $PathValue"
    }
}

if ([string]::IsNullOrWhiteSpace($RepoRoot)) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\\..")).Path
}

$repoRootResolved = [System.IO.Path]::GetFullPath($RepoRoot)
$activationBriefPath = Resolve-RepoPath -Root $repoRootResolved -PathValue $ActivationBrief
$missionPacketPath = Resolve-RepoPath -Root $repoRootResolved -PathValue $MissionPacket
$deliverablePath = Resolve-RepoPath -Root $repoRootResolved -PathValue $Deliverable

Require-Path -PathValue $repoRootResolved -Label "Repo root"
Require-Path -PathValue $activationBriefPath -Label "Activation brief"
Require-Path -PathValue $missionPacketPath -Label "Mission packet"
Require-Path -PathValue (Join-Path $repoRootResolved "AGENTS.md") -Label "AGENTS bootstrap"
Require-Path -PathValue (Join-Path $repoRootResolved ".agent\\STARTUP.md") -Label "Startup doctrine"
Require-Path -PathValue (Join-Path $repoRootResolved ".agent\\COMMS_DOCTRINE.md") -Label "Comms doctrine"

Set-Location $repoRootResolved
$codexCommand = (Get-Command "codex.cmd" -ErrorAction Stop).Source

$deliverableDir = Split-Path -Parent $deliverablePath
if ($deliverableDir) {
    New-Item -ItemType Directory -Path $deliverableDir -Force | Out-Null
}

$agentSlug = Get-Slug -Value $Agent
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$runtimeDir = Join-Path $repoRootResolved ".agent\\runtime\\codex_cli\\$agentSlug"
New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null

$bootstrapSnapshotPath = Join-Path $runtimeDir "bootstrap_$timestamp.txt"
$promptPath = Join-Path $runtimeDir "prompt_$timestamp.md"
$execLogPath = Join-Path $runtimeDir "exec_$timestamp.log"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AIM-OS Codex CLI Agent Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Agent: $Agent" -ForegroundColor Gray
Write-Host "Repo root: $repoRootResolved" -ForegroundColor Gray
Write-Host "Codex command: $codexCommand" -ForegroundColor Gray
Write-Host ""

Write-Host "[1/5] Checking Codex CLI..." -ForegroundColor Yellow
$codexVersion = (& $codexCommand --version 2>&1 | Out-String).Trim()
if (-not $codexVersion) {
    throw "Failed to read Codex CLI version."
}
Write-Host "  $codexVersion" -ForegroundColor Green

Write-Host "[2/5] Detecting MCP mode..." -ForegroundColor Yellow
$mcpListOutput = (& $codexCommand mcp list 2>&1 | Out-String).Trim()
$mcpMode = "degraded-no-mcp"
$mcpReason = "No native MCP registry and HTTP bridge unavailable."
$healthJson = $null

if ($mcpListOutput -match "(?im)^\s*lucid-mcp\b") {
    $mcpMode = "native"
    $mcpReason = "codex mcp list reported lucid-mcp."
}
else {
    try {
        $healthJson = Invoke-RestMethod -Method Get -Uri "http://localhost:5001/health" -TimeoutSec 5
        if ($healthJson.status -eq "ok" -and $healthJson.ready) {
            $mcpMode = "http-bridge"
            $mcpReason = "HTTP bridge health check returned ready=true on :5001."
        }
    }
    catch {
        $healthJson = $null
    }
}

Write-Host "  mode: $mcpMode" -ForegroundColor Green
Write-Host "  reason: $mcpReason" -ForegroundColor Gray

Write-Host "[3/5] Capturing bootstrap snapshot..." -ForegroundColor Yellow
$bootstrapOutput = (& python "scripts/agent_comms/bootstrap_agent_session.py" --repo-root $repoRootResolved --agent $Agent 2>&1 | Out-String)
$bootstrapOutput | Set-Content -LiteralPath $bootstrapSnapshotPath -Encoding utf8
Write-Host "  $bootstrapSnapshotPath" -ForegroundColor Green

Write-Host "[4/5] Rendering activation prompt..." -ForegroundColor Yellow
& python "scripts/agent_comms/render_codex_activation.py" `
    --repo-root $repoRootResolved `
    --agent $Agent `
    --activation-brief $activationBriefPath `
    --mission-packet $missionPacketPath `
    --mcp-mode $mcpMode `
    --deliverable $deliverablePath `
    --bootstrap-snapshot $bootstrapSnapshotPath `
    --output $promptPath
Write-Host "  $promptPath" -ForegroundColor Green

Write-Host "[5/5] Running codex exec..." -ForegroundColor Yellow
$promptContent = Get-Content -LiteralPath $promptPath -Raw
$execOutput = @()
$promptContent | & $codexCommand exec -C $repoRootResolved -s danger-full-access --output-last-message $deliverablePath - 2>&1 |
    Tee-Object -Variable execOutput | Out-Host
$codexExit = $LASTEXITCODE
$execOutput | Out-String | Set-Content -LiteralPath $execLogPath -Encoding utf8

$deliverableExists = Test-Path -LiteralPath $deliverablePath
$result = if ($codexExit -eq 0 -and $deliverableExists) { "PASS" } else { "FAIL" }

Write-Host ""
Write-Host "Launcher summary" -ForegroundColor Cyan
Write-Host "  codex_version=$codexVersion" -ForegroundColor Gray
Write-Host "  mcp_mode=$mcpMode" -ForegroundColor Gray
Write-Host "  deliverable=$deliverablePath" -ForegroundColor Gray
Write-Host "  prompt=$promptPath" -ForegroundColor Gray
Write-Host "  exec_log=$execLogPath" -ForegroundColor Gray
Write-Host "  result=$result" -ForegroundColor $(if ($result -eq "PASS") { "Green" } else { "Red" })

if ($result -ne "PASS") {
    exit 1
}
