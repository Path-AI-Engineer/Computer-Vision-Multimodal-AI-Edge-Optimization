# Project status

## Current state: QUALIFICATION RELEASE COMPLETE / OFFICIAL BENCHMARK IN PROGRESS

The software vertical is complete: contracts, deterministic artifact generation, calibrated HOG
inference, FastAPI, React Studio, persisted evidence, tests and container/deployment definitions.

The complete map cannot be marked closed yet because these evidence-producing tasks remain:

- acquire and checksum Oxford-IIIT Pet under its license;
- create stratified train/validation manifests from official `trainval`;
- execute SmallCNN, ResNet-18 frozen and fine-tuned, and ViT-B/16 runs;
- select one candidate and calibrator from validation only;
- open official test exactly once and persist the immutable report;
- generate genuine Grad-CAM evidence only if a CNN or ResNet is selected;
- run external load, security and AWS App Runner acceptance before a production claim.

No fake values substitute for these runs. `reports/metrics/model_comparison.json` is the source of
truth for executed versus protocol-ready candidates.

## Local acceptance record

- Python artifact validator: passed.
- Ruff: passed.
- Pytest: 17 passed.
- React TypeScript/Vite production build: passed with the locked dependency tree.
- Docker Compose configuration: passed.
- Live HTTP readiness and multipart inference: passed on port 8019.
- AWS release definition: ECR/App Runner CloudFormation and local release preflight implemented.
- AWS account template validation and deployment: not executed in this acceptance record.
- Browser visual walkthrough: not executed because localhost access was denied by the browser
  permission boundary.
- Docker image build: not executed because this managed session could not access the local
  BuildKit lock or Docker Desktop named pipe.
