$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$env:RUFF_CACHE_DIR = Join-Path $env:TEMP "p20-ruff-cache"
Push-Location $root
try {
    python scripts\build_qualification_bundle.py
    if ($LASTEXITCODE -ne 0) { throw "Qualification bundle generation failed." }
    python scripts\validate_project.py
    if ($LASTEXITCODE -ne 0) { throw "Project evidence validation failed." }
    python -m ruff format --check backend ml scripts tests
    if ($LASTEXITCODE -ne 0) { throw "Ruff format validation failed." }
    python -m ruff check backend ml scripts tests
    if ($LASTEXITCODE -ne 0) { throw "Ruff lint validation failed." }
    python -m pytest -q -p no:cacheprovider
    if ($LASTEXITCODE -ne 0) { throw "Pytest failed." }
    Push-Location frontend
    try {
        npm run build
        if ($LASTEXITCODE -ne 0) { throw "Frontend production build failed." }
    }
    finally { Pop-Location }
    docker compose config --quiet
    if ($LASTEXITCODE -ne 0) { throw "Docker Compose validation failed." }
    Write-Host "Project 20 quality gate passed."
}
finally {
    Pop-Location
}
