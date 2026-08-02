# Surface Quality Control Lab

An evidence-first computer-vision laboratory that turns pixel-level surface-defect
segmentation into an auditable piece-level inspection decision. The project implements a
real compact U-Net, an OpenCV baseline, validation-only threshold selection, a FastAPI
contract and a responsive React inspection console.

> Evidence boundary: the checked-in release is a deterministic **procedural qualification**
> profile. The official KSDD2 benchmark is deliberately marked `LOCKED_NOT_ACQUIRED`; no
> synthetic result is presented as KSDD2 performance.

## Product flow

```text
surface image -> defect probability -> pixel threshold -> binary mask
              -> connected components + defect area -> ACCEPT / REVIEW / REJECT
```

The pixel threshold controls segmentation. The independent piece policy uses retained
component area to avoid conflating model calibration with an operational decision rule.

## Verified qualification evidence

| Signal | Result |
|---|---:|
| Validation images | 12 (4 defective, 8 clean) |
| Small U-Net parameters | 29,481 |
| Macro Dice / IoU | 0.947943 / 0.911008 |
| Pixel precision / recall | 0.932801 / 0.971197 |
| Piece recall / precision / F1 | 1.0 / 1.0 / 1.0 |
| False-accept / false-reject rate | 0.0 / 0.0 |
| Selected pixel threshold | 0.80, validation only |
| Official KSDD2 test | `LOCKED_NOT_ACQUIRED` |

These values are reproducible from `scripts/build_qualification_bundle.py`. They demonstrate
the software vertical and do not establish industrial or KSDD2 generalization.

## Architecture

- `ml/`: paired image/mask contracts, procedural qualification data, baselines, Small U-Net,
  training, metrics, policy, bundle verification and inference.
- `backend/`: FastAPI lifecycle, safe image ingestion and thin HTTP resources.
- `frontend/`: React/Vite quality console with synchronized source, probability, mask and
  overlay views; real threshold reruns; model comparison and evidence boundaries.
- `reports/` and `models/`: versioned generated evidence and hash-verified model bundle.
- `infra/docker/` and `infra/aws/`: local container instructions and AWS ECR/App Runner release.

See [architecture](docs/architecture.md), [mask contract](docs/mask-contract.md),
[inspection policy](docs/inspection-policy.md) and [validation record](docs/validation.md).

## Run locally

```powershell
Set-Location "C:\JeanLoa\Path-AI-Engineer\Computer-Vision-Multimodal-AI-Edge-Optimization\21-segmentation-quality-control-lab"
python -m virtualenv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
$env:PYTHONPATH = $PWD.Path
python scripts\build_qualification_bundle.py
```

Frontend:

```powershell
Set-Location frontend
npm install
npm run dev
```

API, in a second terminal:

```powershell
Set-Location "C:\JeanLoa\Path-AI-Engineer\Computer-Vision-Multimodal-AI-Edge-Optimization\21-segmentation-quality-control-lab"
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = $PWD.Path
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8021 --reload
```

Open `http://127.0.0.1:5173`. The production bundle serves the console from `/app/`.

## API

- `GET /health`, `GET /ready`
- `GET /v1/models/current`, `GET /v1/samples`
- `POST /v1/segmentations`, `POST /v1/inspections`
- `GET /v1/evaluation/summary`, `/thresholds`, `/errors`, `/models`

Use exactly one multipart source: `sample_id` or `image`. An optional `pixel_threshold`
between 0.05 and 0.95 causes a real inference rerun.

## Quality gate

```powershell
.\scripts\quality_gate.ps1
```

It regenerates the qualification bundle, validates artifacts, formats/lints Python, runs the
test suite, builds the frontend and validates Docker Compose.

## Deployment

The target for Plan 04 is AWS. The release workflow uses immutable ECR tags, scan-on-push,
CloudFormation and AWS App Runner. It does nothing remotely unless `-Apply` is provided.

```powershell
.\infra\aws\release.ps1 -Region us-east-1
.\infra\aws\release.ps1 -Region us-east-1 -ValidateAws
.\infra\aws\release.ps1 -Region us-east-1 -ImageTag v1.0.0 -Apply
```

No cloud deployment is claimed by this repository state.
