$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$env:RUFF_CACHE_DIR = Join-Path $env:TEMP "p20-ruff-cache"
Push-Location $root
try {
    python scripts\build_qualification_bundle.py
    python scripts\validate_project.py
    python -m ruff format --check backend ml scripts tests
    python -m ruff check backend ml scripts tests
    python -m pytest -q -p no:cacheprovider
    Push-Location frontend
    try { npm run build } finally { Pop-Location }
    docker compose config --quiet
    Write-Host "Project 20 quality gate passed."
}
finally {
    Pop-Location
}
