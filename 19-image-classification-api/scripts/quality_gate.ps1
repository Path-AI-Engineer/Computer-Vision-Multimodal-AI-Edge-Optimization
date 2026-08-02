$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Push-Location $root
try {
    $env:PYTHONDONTWRITEBYTECODE = "1"
    $env:PYTHONPATH = $root
    python scripts/build_qualification_bundle.py
    if ($LASTEXITCODE -ne 0) { throw "Qualification bundle generation failed." }
    python scripts/validate_project.py
    if ($LASTEXITCODE -ne 0) { throw "Project evidence validation failed." }
    python -m ruff check backend ml scripts tests
    if ($LASTEXITCODE -ne 0) { throw "Ruff validation failed." }
    if (-not (Test-Path "frontend/node_modules/.bin/vite.cmd")) {
        npm --prefix frontend ci --no-audit --no-fund
        if ($LASTEXITCODE -ne 0) { throw "Frontend dependency installation failed." }
    }
    npm --prefix frontend run build
    if ($LASTEXITCODE -ne 0) { throw "Frontend production build failed." }
    python -m pytest -q -p no:cacheprovider
    if ($LASTEXITCODE -ne 0) { throw "Pytest failed." }
    docker compose config --quiet
    if ($LASTEXITCODE -ne 0) { throw "Docker Compose validation failed." }
    Write-Host "Project 19 quality gate passed."
}
finally {
    Pop-Location
}
