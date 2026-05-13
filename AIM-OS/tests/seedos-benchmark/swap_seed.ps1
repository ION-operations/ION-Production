# SeedOS Benchmark — Seed Rotation Script
# Usage: .\swap_seed.ps1 <variant>
# Variants: kernel, v1, v4, v5

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("kernel", "v1", "v2", "v3", "v4", "v5")]
    [string]$Variant
)

$benchDir = "c:\Users\bombe\Desktop\AIM-OS\tests\seedos-benchmark"
$seedsDir = "c:\Users\bombe\Desktop\AIM-OS\docs\SeedOS\gptseeds"
$kernelDir = "c:\Users\bombe\Desktop\AIM-OS\docs\SeedOS"
$target = Join-Path $benchDir ".gemini\GEMINI.md"

$sourceMap = @{
    "kernel" = Join-Path $kernelDir "KERNEL.md"
    "v1"     = Join-Path $seedsDir "seedgpt.txt"
    "v2"     = Join-Path $seedsDir "seedgptv2.txt"
    "v3"     = Join-Path $seedsDir "seedgptv3.txt"
    "v4"     = Join-Path $seedsDir "seedgptv4.txt"
    "v5"     = Join-Path $seedsDir "seedgptv5.txt"
}

$source = $sourceMap[$Variant]
if (-not (Test-Path $source)) {
    Write-Error "Source file not found: $source"
    exit 1
}

Copy-Item $source $target -Force
$size = (Get-Item $target).Length
$lines = (Get-Content $target | Measure-Object).Count
Write-Host "Swapped to $Variant — $lines lines, $size bytes" -ForegroundColor Green
Write-Host "Run: cd $benchDir && gemini"
