# AWS release

Plan 04 targets AWS. Project 23 uses one immutable ECR image and one App Runner service
managed through CloudFormation.

Local preflight:

```powershell
.\infra\aws\release.ps1
```

Authenticated template validation:

```powershell
.\infra\aws\release.ps1 -Region us-east-1 -ValidateAws
```

Deployment requires explicit authorization:

```powershell
.\infra\aws\release.ps1 -Region us-east-1 -ImageTag v1.0.0-rc.1 -Apply
```

The default hosted bundle exposes the sealed qualification workflow. It does not download
Flickr8k, model weights or remote URLs at runtime.

