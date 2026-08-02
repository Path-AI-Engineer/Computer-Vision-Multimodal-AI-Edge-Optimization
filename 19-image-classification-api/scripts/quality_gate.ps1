$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Push-Location $root
try {
    $env:PYTHONDONTWRITEBYTECODE = "1"
    $env:PYTHONPATH = $root
    python scripts/build_qualification_bundle.py
    python scripts/validate_project.py
    python -m ruff check backend ml scripts tests
    if (-not (Test-Path "frontend/node_modules/.bin/vite.cmd")) {
        npm --prefix frontend ci --no-audit --no-fund
    }
    npm --prefix frontend run build
    python -m pytest -q -p no:cacheprovider
    docker compose config --quiet
    Write-Host "Project 19 quality gate passed."
}
finally {
    Pop-Location
}
