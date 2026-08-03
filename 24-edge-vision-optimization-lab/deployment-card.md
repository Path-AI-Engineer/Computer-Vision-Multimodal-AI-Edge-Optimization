# Deployment card

Target: AWS App Runner, one non-root container, immutable ECR tag.

Service: `ai-04-p24-edge-vision-console`
Repository: `plan-04/p24-edge-vision-console`
Port: 8080
Readiness: `/ready`
Studio: `/app/`

Promotion requires: full Python/frontend/E2E gates, successful Linux image build, semantic
readiness, approved artifact registry, no mutable image tag and explicit deployment authority.
The current release candidate serves qualification evidence only.
