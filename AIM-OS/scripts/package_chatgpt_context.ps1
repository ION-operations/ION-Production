# Package ChatGPT context for Braden to send
# Run: powershell -File scripts/package_chatgpt_context.ps1
# Output: context/chatgpt_context_YYYY-MM-DD_HHMM.zip

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$zipName = "chatgpt_context_$timestamp.zip"
$contextDir = Join-Path $repoRoot "context"
$zipPath = Join-Path $contextDir $zipName

Set-Location $repoRoot

$files = @(
    "context/00_operational_definition.md",
    "context/01_current_truth.md",
    "context/02_canonical_map.md",
    "context/03_tonight_plan.md",
    "context/99_nightly_sync_capsule.md",
    "context/README.md",
    "docs/roundtable/CODEX1_DEEP_RESEARCH_SYNTHESIS_PACKET_2026-03-05.md",
    "PROJECT_TRUTH/00_evidence_ledger.md",
    "PROJECT_TRUTH/01_canonical_system_index.md",
    "PROJECT_TRUTH/02_canonical_doc_index.md",
    "PROJECT_TRUTH/03_already_built_registry.md",
    "PROJECT_TRUTH/04_breakage_and_drift_report.md",
    "PROJECT_TRUTH/05_operational_definition.md",
    "PROJECT_TRUTH/06_operational_spine.md",
    "PROJECT_TRUTH/07_next_bounded_task.md",
    "PROJECT_TRUTH/README.md"
)

# Add roundtable thread if exists
$threadPath = "docs/communications_mcp_down/threads/THREAD_aimos_roundtable_operational_convergence_2026-03-04.md"
if (Test-Path $threadPath) {
    $files += $threadPath
}

# Create zip (PowerShell 5.1 compatible)
$tempDir = Join-Path $env:TEMP "chatgpt_context_$timestamp"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

foreach ($f in $files) {
    if (Test-Path $f) {
        # Flatten into filename-only archive for quick paste workflow.
        $dest = Join-Path $tempDir (Split-Path $f -Leaf)
        Copy-Item $f $dest -Force
    }
}

Compress-Archive -Path "$tempDir\*" -DestinationPath $zipPath -Force
Remove-Item $tempDir -Recurse -Force

Write-Host "Created: $zipPath" -ForegroundColor Green
Write-Host "Send this zip to ChatGPT when needed."
