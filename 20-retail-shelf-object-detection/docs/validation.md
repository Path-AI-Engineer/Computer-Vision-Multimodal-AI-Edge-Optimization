# Validation evidence

Executed on 2026-08-01 from the real checkout.

| Gate | Result | Evidence |
|---|---|---|
| Qualification bundle generation | Passed | 12 images, 740 objects, profile `qualification_smoke` |
| Artifact validation | Passed | Bundle hash, profile, density slices and locked test state |
| Ruff format and lint | Passed | 36 Python files checked |
| pytest | Passed | 22 tests |
| TypeScript project build | Passed | `tsc -b` |
| React dependency audit | Passed | 70 packages, 0 vulnerabilities |
| Docker Compose config | Passed | Production service and health check resolved |
| Cloud Run release preflight | Passed | Semantic service/image names and evidence validator |
| Live Uvicorn readiness | Passed | HTTP 200, `qualification_smoke` |
| Live multipart inference | Passed | HTTP 200, 30 detections on the low-density sample |

## Environment boundary

The managed Windows sandbox denied Docker Buildx access to `C:\Users\Asus\.docker\buildx\.lock` and denied Vite/esbuild process spawning with `spawn EPERM`. Docker image construction, final Vite bundling and browser E2E must therefore be rerun in the user's normal PowerShell session. TypeScript compilation passed, but it is not substituted for browser acceptance.
