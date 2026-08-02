param(
    [Parameter(Mandatory = $true)][string]$ProjectId,
    [string]$Region = "us-central1",
    [string]$ImageTag = "v1.0.0",
    [switch]$Apply
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$repository = "plan-04"
$service = "ai-04-p19-pet-breed-studio"
$image = "$Region-docker.pkg.dev/$ProjectId/$repository/pet-breed-studio:$ImageTag"
$gcloud = (Get-Command gcloud.cmd -ErrorAction SilentlyContinue).Source
if (-not $gcloud) { $gcloud = (Get-Command gcloud -ErrorAction Stop).Source }

Write-Host "Project: $ProjectId"
Write-Host "Region:  $Region"
Write-Host "Service: $service"
Write-Host "Image:   $image"
if (-not $Apply) {
    Write-Host "Preflight only. Add -Apply to build and deploy."
    exit 0
}

& $gcloud services enable artifactregistry.googleapis.com cloudbuild.googleapis.com run.googleapis.com --project=$ProjectId
if ($LASTEXITCODE -ne 0) { throw "Could not enable required Google Cloud APIs." }

& $gcloud artifacts repositories describe $repository --project=$ProjectId --location=$Region *> $null
if ($LASTEXITCODE -ne 0) {
    & $gcloud artifacts repositories create $repository --project=$ProjectId --location=$Region --repository-format=docker --description="AI Engineer Plan 04 images"
    if ($LASTEXITCODE -ne 0) { throw "Could not create Artifact Registry repository." }
}

& $gcloud builds submit $root --project=$ProjectId --region=$Region --config=(Join-Path $PSScriptRoot "cloudbuild.yaml") --substitutions="_IMAGE=$image" --quiet
if ($LASTEXITCODE -ne 0) { throw "Cloud Build failed." }

& $gcloud run deploy $service --project=$ProjectId --region=$Region --image=$image --allow-unauthenticated --port=8080 --memory=1Gi --cpu=1 --min=0 --max=1 --concurrency=20 --timeout=120 --set-env-vars="PET_STUDIO_ROOT=/app,MAX_BATCH_SIZE=8,MAX_UPLOAD_BYTES=4194304"
if ($LASTEXITCODE -ne 0) { throw "Cloud Run deployment failed." }

$url = & $gcloud run services describe $service --project=$ProjectId --region=$Region --format="value(status.url)"
$ready = Invoke-RestMethod -Uri "$url/ready" -TimeoutSec 60
if ($ready.status -ne "ready") { throw "Cloud Run readiness smoke failed." }
Write-Host "Deployment verified: $url/app/"
