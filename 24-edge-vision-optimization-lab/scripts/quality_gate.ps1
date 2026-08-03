$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = (Get-Command python).Source }
$env:RUFF_CACHE_DIR = Join-Path $env:TEMP "ruff-p24"

Push-Location $root
try {
    & $python scripts\build_qualification_bundle.py
    if ($LASTEXITCODE -ne 0) { throw "Qualification bundle generation failed." }
    & $python -m ruff check backend edge_ai scripts tests
    if ($LASTEXITCODE -ne 0) { throw "Ruff lint failed." }
    & $python -m ruff format --check backend edge_ai scripts tests
    if ($LASTEXITCODE -ne 0) { throw "Ruff format check failed." }
    & $python -m pytest -q -p no:cacheprovider
    if ($LASTEXITCODE -ne 0) { throw "Pytest failed." }
    & $python scripts\validate_project.py
    if ($LASTEXITCODE -ne 0) { throw "Project evidence validation failed." }

    $frontend = Join-Path $root "frontend"
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -Command `
        "Set-Location -LiteralPath '$frontend'; npm.cmd run build"
    if ($LASTEXITCODE -ne 0) { throw "Frontend build failed." }
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -Command `
        "Set-Location -LiteralPath '$frontend'; npm.cmd run test:e2e"
    if ($LASTEXITCODE -ne 0) { throw "Playwright end-to-end tests failed." }

    $docker = Get-Command docker -ErrorAction SilentlyContinue
    if ($docker) {
        & $docker.Source compose config --quiet
        if ($LASTEXITCODE -ne 0) { throw "Docker Compose configuration failed." }
    }
    else { Write-Warning "Docker CLI not available; Compose validation skipped." }
    Write-Host "Project 24 quality gate passed."
}
finally { Pop-Location }
