param(
    [string]$Host = "127.0.0.1",
    [int]$Port = 5013
)

$PackageDir = Resolve-Path (Join-Path $PSScriptRoot "..\..\packages\jarvis_injector")
$VenvDir = Join-Path $PackageDir ".venv"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"

if (-not (Test-Path $VenvDir)) {
    Write-Host "[window-injector] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $VenvDir
}

if (-not (Test-Path $PythonExe)) {
    throw "Python executable not found in $VenvDir"
}

Push-Location $PackageDir

Write-Host "[window-injector] Installing package..." -ForegroundColor Yellow
& $PythonExe -m pip install -e .
if ($LASTEXITCODE -ne 0) {
    Pop-Location
    throw "Editable install failed"
}

Write-Host "[window-injector] Starting runtime on http://$Host`:$Port" -ForegroundColor Green
& $PythonExe -m jarvis_injector.runtime.cli serve --host $Host --port $Port

Pop-Location

