# AWS release

The Plan 04 target is AWS App Runner backed by private ECR. Tags are immutable and scanning is
enabled on push. CloudFormation owns the service and its ECR access role.

Run local preflight first, then authenticated validation, and use `-Apply` only when ready:

```powershell
.\infra\aws\release.ps1
.\infra\aws\release.ps1 -ValidateAws
.\infra\aws\release.ps1 -ImageTag v1.0.0 -Apply
```

No remote action occurs without `-Apply`.
