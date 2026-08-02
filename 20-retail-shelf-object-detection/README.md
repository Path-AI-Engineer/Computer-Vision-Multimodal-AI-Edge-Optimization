# Retail Shelf Detection Console

An evidence-first object-detection API and React console for dense retail shelf images. The product exposes bounding boxes, confidence and NMS thresholds, visible-object counts, AP metrics, count error, density slices and immutable model evidence.

> Current release boundary: the shipped `qualification_smoke` artifact is evaluated on deterministic procedural shelf scenes. SKU-110K has **not** been acquired, YOLO/Faster R-CNN candidates have **not** been trained, and the official test split remains locked. Qualification numbers are not presented as retail benchmark results.

## Product surface

- Interactive shelf canvas with sample and upload workflows.
- User-visible confidence, NMS IoU and zoom controls.
- Single and bounded batch inference endpoints.
- AP50, AP75, mAP@[.50:.95], precision, recall, count MAE/RMSE/bias.
- Density slicing and visual error gallery.
- Candidate registry that distinguishes executed from unexecuted models.
- Explicit responsible-use and product-scope screen.

## Architecture

```text
frontend/                  React + Vite operations console
backend/app/               FastAPI contracts and application service
ml/data/                   image and bounding-box contracts
ml/models/                 qualification detector and lazy production adapters
ml/inference/              immutable bundle loading and prediction
ml/evaluation/             AP, count metrics and density slices
models/bundles/            hash-verifiable qualification artifact
reports/                   persisted evaluation evidence
tests/                     unit, integration and contract gates
docker/                    production multi-stage image
infra/docker/              local container instructions
infra/aws/                 Amazon ECR and App Runner release workflow
```

See [architecture.md](docs/architecture.md), [data-contract.md](docs/data-contract.md), [metrics-guide.md](docs/metrics-guide.md), [validation.md](docs/validation.md) and [project-status.md](docs/project-status.md).

## Run locally

```powershell
Set-Location "C:\JeanLoa\Path-AI-Engineer\Computer-Vision-Multimodal-AI-Edge-Optimization\20-retail-shelf-object-detection"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python scripts\build_qualification_bundle.py
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8020 --reload
```

In a second terminal:

```powershell
Set-Location "C:\JeanLoa\Path-AI-Engineer\Computer-Vision-Multimodal-AI-Edge-Optimization\20-retail-shelf-object-detection\frontend"
npm ci
npm run dev
```

Open `http://127.0.0.1:5173`. The production image serves the compiled console at `/app/` and the API contract at `/docs`.

## Quality gate

```powershell
.\scripts\quality_gate.ps1
```

The gate rebuilds qualification evidence, validates hashes and state boundaries, runs Ruff and pytest, builds React and checks Docker Compose.

## Containers and AWS

```powershell
docker compose up --build
```

Open `http://127.0.0.1:8020/app/`. To run the local, non-mutating AWS release preflight:

```powershell
.\infra\aws\release.ps1 -Region "us-east-1"
```

To validate the AWS identity and CloudFormation template without deploying:

```powershell
.\infra\aws\release.ps1 -Region "us-east-1" -ValidateAws
```

When AWS credentials are active and an actual deployment is intended, publish an immutable image
to the Plan 04 ECR namespace and reconcile the App Runner service:

```powershell
.\infra\aws\release.ps1 -Region "us-east-1" -ImageTag "v1.0.0-rc.1" -Apply
```

The service uses `/ready` for health checks and serves the console at `/app/`. Future secrets must
be referenced from AWS Secrets Manager or Systems Manager Parameter Store, not embedded in source
or passed as plain environment variables.

## Official benchmark path

1. Review the upstream license and obtain SKU-110K independently.
2. Validate the extraction with `python scripts/verify_sku110k_dataset.py <root>`.
3. Train the count baseline and candidates only on train.
4. Select candidate, thresholds and compute profile only on validation.
5. Freeze the artifact and then execute official test once.

The protocol is based on the [SKU-110K paper](https://arxiv.org/abs/1904.00853), [official dataset repository](https://github.com/eg4000/sku110k_cvpr19), [Ultralytics dataset contract](https://docs.ultralytics.com/datasets/detect/sku-110k/) and [TorchVision detection tutorial](https://docs.pytorch.org/tutorials/intermediate/torchvision_tutorial.html).

## Scope

The system detects visible instances of one class, `object`. It does not identify SKUs, estimate hidden stock, replace inventory records, or claim production real-time performance.
