param(
    [string]$Region = "us-east-1",
    [string]$ImageTag = "v1.0.0-rc.1",
    [string]$Profile = "",
    [switch]$ValidateAws,
    [switch]$Apply
)

$ErrorActionPreference = "Stop"
$env:AWS_PAGER = ""
$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$repository = "plan-04/p19-pet-breed-studio"
$service = "ai-04-p19-pet-breed-studio"
$stack = $service
$template = Join-Path $PSScriptRoot "apprunner.yaml"

function Assert-ExitCode([string]$message) {
    if ($LASTEXITCODE -ne 0) { throw $message }
}

Write-Host "Region:     $Region"
Write-Host "Repository: $repository"
Write-Host "Service:    $service"
Write-Host "Image tag:  $ImageTag"

$previousPythonPath = $env:PYTHONPATH
try {
    $env:PYTHONPATH = if ($previousPythonPath) { "$root;$previousPythonPath" } else { $root }
    & python (Join-Path $root "scripts\validate_project.py")
    Assert-ExitCode "Project evidence validation failed."
}
finally {
    $env:PYTHONPATH = $previousPythonPath
}

if (-not (Test-Path $template)) { throw "App Runner template not found." }
if (-not (Test-Path (Join-Path $root "docker\production.Dockerfile"))) {
    throw "Production Dockerfile not found."
}

if (-not $ValidateAws -and -not $Apply) {
    Write-Host "Local AWS release preflight passed. Add -ValidateAws for authenticated template validation or -Apply to deploy."
    exit 0
}

$awsCommand = Get-Command aws.exe -ErrorAction SilentlyContinue
if (-not $awsCommand) { $awsCommand = Get-Command aws -ErrorAction SilentlyContinue }
if (-not $awsCommand) {
    throw "AWS CLI is required for authenticated validation and deployment."
}
$aws = $awsCommand.Source
$awsCommon = @("--region", $Region, "--no-cli-pager")
if ($Profile) { $awsCommon += @("--profile", $Profile) }

$accountOutput = & $aws sts get-caller-identity @awsCommon --query Account --output text
Assert-ExitCode "AWS identity validation failed. Configure credentials and network access before continuing."
if (-not $accountOutput) { throw "AWS identity validation returned no account ID." }
$accountId = ([string]$accountOutput).Trim()
if ($accountId -notmatch "^\d{12}$") { throw "AWS account ID could not be resolved." }

& $aws cloudformation validate-template @awsCommon --template-body "file://$template" *> $null
Assert-ExitCode "CloudFormation template validation failed."

$registry = "$accountId.dkr.ecr.$Region.amazonaws.com"
$image = "$registry/${repository}:$ImageTag"
Write-Host "Account:    $accountId"
Write-Host "Image:      $image"

if (-not $Apply) {
    Write-Host "Authenticated AWS preflight passed. Add -Apply to build, push and deploy."
    exit 0
}

$dockerCommand = Get-Command docker.exe -ErrorAction SilentlyContinue
if (-not $dockerCommand) { $dockerCommand = Get-Command docker -ErrorAction Stop }
$docker = $dockerCommand.Source

& $aws ecr describe-repositories @awsCommon --repository-names $repository *> $null
if ($LASTEXITCODE -ne 0) {
    & $aws ecr create-repository @awsCommon `
        --repository-name $repository `
        --image-tag-mutability IMMUTABLE `
        --image-scanning-configuration scanOnPush=true `
        --tags Key=Path,Value=ai-engineer Key=Plan,Value=04 Key=Project,Value=19 *> $null
    Assert-ExitCode "ECR repository creation failed."
}
else {
    & $aws ecr put-image-tag-mutability @awsCommon `
        --repository-name $repository --image-tag-mutability IMMUTABLE *> $null
    Assert-ExitCode "Could not enforce immutable ECR tags."
    & $aws ecr put-image-scanning-configuration @awsCommon `
        --repository-name $repository --image-scanning-configuration scanOnPush=true *> $null
    Assert-ExitCode "Could not enable ECR scan-on-push."
}

& $aws ecr describe-images @awsCommon `
    --repository-name $repository --image-ids "imageTag=$ImageTag" *> $null
if ($LASTEXITCODE -eq 0) {
    throw "Image tag $ImageTag already exists in immutable ECR. Choose a new ImageTag."
}

$password = & $aws ecr get-login-password @awsCommon
Assert-ExitCode "Could not obtain the ECR login token."
$password | & $docker login --username AWS --password-stdin $registry
Assert-ExitCode "Docker login to ECR failed."

& $docker build -f (Join-Path $root "docker\production.Dockerfile") -t $image $root
Assert-ExitCode "Docker image build failed."
& $docker push $image
Assert-ExitCode "Docker image push failed."

& $aws cloudformation deploy @awsCommon `
    --template-file $template `
    --stack-name $stack `
    --parameter-overrides "ServiceName=$service" "ImageIdentifier=$image" `
    --capabilities CAPABILITY_NAMED_IAM `
    --no-fail-on-empty-changeset `
    --tags Path=ai-engineer Plan=04 Project=19 Environment=portfolio
Assert-ExitCode "App Runner CloudFormation deployment failed."

$serviceUrl = (& $aws cloudformation describe-stacks @awsCommon `
    --stack-name $stack `
    --query "Stacks[0].Outputs[?OutputKey=='ServiceUrl'].OutputValue | [0]" `
    --output text).Trim()
Assert-ExitCode "App Runner URL lookup failed."
if ($serviceUrl -notmatch "^https://") { $serviceUrl = "https://$serviceUrl" }

$ready = Invoke-RestMethod -Uri "$serviceUrl/ready" -TimeoutSec 60
if ($ready.status -ne "ready") { throw "App Runner readiness smoke failed." }
$app = Invoke-WebRequest -UseBasicParsing -Uri "$serviceUrl/app/" -TimeoutSec 60
if ($app.StatusCode -ne 200) { throw "App Runner web smoke failed." }

Write-Host "Deployment verified."
Write-Host "Studio: $serviceUrl/app/"
Write-Host "API:    $serviceUrl/docs"
