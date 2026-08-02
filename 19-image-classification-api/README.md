# Pet Breed Classification Studio

An evidence-first computer-vision product that validates image inputs, produces calibrated Top-K
breed probabilities, abstains below a declared threshold and exposes model evidence through
FastAPI and a React Studio.

## What is real today

- a deterministic 37-class procedural qualification dataset;
- a trained HOG + logistic-regression artifact;
- temperature scaling, Top-1/Top-5, macro F1, NLL, ECE and per-class evidence;
- safe JPEG/PNG/WebP decoding with byte and pixel limits;
- single and bounded-batch inference endpoints;
- a React interface connected only to API responses and generated artifacts;
- model comparison with explicit `executed` and `not executed` states;
- Docker and Cloud Run release definitions.

The active bundle is `QUALIFICATION_ONLY`. It is not trained on Oxford-IIIT Pet, and its metrics
must not be presented as real breed-classification performance. The full map remains open until
the official dataset, deep candidates and locked test protocol are executed. See
[`docs/project-status.md`](docs/project-status.md).

## Dataset protocol

The official target is [Oxford-IIIT Pet](https://www.robots.ox.ac.uk/~vgg/data/pets/), which has
37 categories and official `trainval`/`test` partitions. The acquisition script downloads only
`trainval`; test stays locked. Torchvision documents the supported split and target contracts in
its [OxfordIIITPet dataset reference](https://docs.pytorch.org/vision/main/generated/torchvision.datasets.OxfordIIITPet.html).

## Run locally

```powershell
Set-Location "C:\JeanLoa\Path-AI-Engineer\Computer-Vision-Multimodal-AI-Edge-Optimization\19-image-classification-api"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
$env:PYTHONPATH = "$PWD"
python scripts\build_qualification_bundle.py
npm --prefix frontend install
npm --prefix frontend run build
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8019 --reload
```

Open:

- Studio: <http://127.0.0.1:8019/app/>
- API docs: <http://127.0.0.1:8019/docs>
- Readiness: <http://127.0.0.1:8019/ready>

For frontend hot reload, run `npm --prefix frontend run dev` in a second terminal and open
<http://127.0.0.1:5173>.

## Quality gate

```powershell
.\scripts\quality_gate.ps1
```

The gate regenerates qualification artifacts, validates manifests and bundle parity, runs Ruff,
pytest, the React production build and Docker Compose configuration.

## Structure

```text
backend/       FastAPI routes, resources and inference service
frontend/      React + TypeScript + Vite Studio
ml/            data, features, candidates, training, evaluation and inference
configs/       data, candidate and experiment configuration
data/          generated qualification samples and versioned manifests
models/        candidate checkpoints and immutable served bundle
reports/       generated metrics, figures, errors and run configuration
docs/          architecture, contracts, protocol, decisions and status
docker/        production multi-stage image
infra/         Docker notes and GCP Cloud Run release workflow
tests/         unit, contract and integration acceptance
```

## Responsible use

This project is a software and ML engineering demonstration. It is not veterinary advice, pet
identity verification or a safety system. A high probability is not a guarantee of correctness.
