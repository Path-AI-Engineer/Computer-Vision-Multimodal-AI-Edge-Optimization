# AWS release

Plan 04 targets AWS. This project uses one immutable ECR image and one AWS App Runner
service managed through CloudFormation.

Local preflight:

```powershell
.\infra\aws\release.ps1
```

Authenticated template validation:

```powershell
.\infra\aws\release.ps1 -Region us-east-1 -ValidateAws
```

Deployment (explicitly authorized only):

```powershell
.\infra\aws\release.ps1 -Region us-east-1 -ImageTag v1.0.0-rc.1 -Apply
```

The default image does not include PaddleOCR. The hosted portfolio demo therefore exposes
the sealed qualification workflow and fails arbitrary uploads explicitly. A production OCR
image must be built, security scanned and requalified before that capability is enabled.
