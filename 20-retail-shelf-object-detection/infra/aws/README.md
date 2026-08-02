# AWS deployment

The release workflow builds the existing production Dockerfile, pushes an immutable image to
`plan-04/p20-shelf-detection-console` in Amazon ECR and provisions an AWS App Runner service
through CloudFormation.

```powershell
.\infra\aws\release.ps1 -Region "us-east-1"
.\infra\aws\release.ps1 -Region "us-east-1" -ValidateAws
.\infra\aws\release.ps1 -Region "us-east-1" -ImageTag "v1.0.0-rc.1" -Apply
```

The first command is a local non-mutating preflight. `-ValidateAws` also validates the authenticated
identity and CloudFormation template without deploying. `-Apply` creates or hardens the ECR
repository, builds and pushes the image, deploys App Runner, and verifies `/ready` plus `/app/`.

ECR tags are immutable. Use a new semantic image tag for every changed image. App Runner receives
only non-sensitive runtime settings; future secrets must use AWS Secrets Manager or Systems
Manager Parameter Store.
