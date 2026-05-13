param(
    [switch]$Json = $false
)

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $repoRoot

if ($Json) {
    python scripts/git/codexgit_status_report.py --json
}
else {
    python scripts/git/codexgit_status_report.py
}
