# Edge Vision Benchmark Console

Project 24 closes Plan 4 with an evidence-first laboratory for visual inference optimization.
It compares quality, latency, artifact size, sparsity and runtime parity without treating a
smaller file, more zero weights or a successful export as automatic acceleration.

## Product surface

- Decision Desk with a calculated macro-F1, latency and size Pareto frontier.
- Inference Lab over public generated fixtures and approved registry variants.
- Variant Registry with runtime, precision, preprocessing, artifact and status.
- Benchmark Matrix with p50, p90, p95, throughput, quality, size and sparsity.
- Evidence Room with environment controls, parity results and retained negative findings.
- FastAPI resources and one React/Vite console backed by the same immutable bundle.

## Evidence boundary

The included sealed qualification bundle contains 12 generated visual fixtures, four classes,
five measured NumPy adapter variants and one explicit NOT_RUN QAT variant. It validates the
data, benchmark, registry, API and interface contracts reproducibly on the current host.

It is not:

- the 7,349-image Oxford-IIIT Pet benchmark;
- MobileNetV3-Small training or final test evidence;
- a PyTorch pruning, ONNX Runtime or static PTQ performance claim;
- a Raspberry Pi, mobile, NPU or other physical edge benchmark.

Research dependencies and protocols are versioned separately. The final model variants can
replace the qualification adapters only after producing compatible manifests and passing
quality, parity and paired benchmark gates.

## Architecture

    project-owned dataset manifest
      -> baseline and optimization protocols
      -> variant artifact + manifest
      -> quality and paired latency evidence
      -> parity and Pareto policy
      -> immutable registry
      -> bounded predictor
      -> FastAPI
      -> React benchmark console

Primary responsibilities:

- edge_ai/data: dataset identity, checksums and disjoint splits.
- edge_ai/models, training and pruning: research execution boundaries.
- edge_ai/benchmark: raw timings, percentiles, environment and Pareto.
- edge_ai/export and quantization: parity and calibration contracts.
- edge_ai/registry and inference: online compatibility and approved prediction.
- artifacts and reports: generated, versioned evidence.
- backend and frontend: API and decision console.

## Run locally

From PowerShell:

    Set-Location "C:\JeanLoa\Path-AI-Engineer\Computer-Vision-Multimodal-AI-Edge-Optimization\24-edge-vision-optimization-lab"

    if (-not (Test-Path ".venv\Scripts\python.exe")) {
        py -3.12 -m venv .venv
    }

    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt -r requirements-dev.txt
    python scripts\build_qualification_bundle.py
    python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8024 --reload

In another PowerShell terminal:

    Set-Location "C:\JeanLoa\Path-AI-Engineer\Computer-Vision-Multimodal-AI-Edge-Optimization\24-edge-vision-optimization-lab\frontend"
    npm install
    npm run dev

Open:

- Console: http://127.0.0.1:5174/app/
- API documentation: http://127.0.0.1:8024/docs
- Readiness: http://127.0.0.1:8024/ready

## API

| Method | Route | Responsibility |
|---|---|---|
| GET | /health | Process liveness |
| GET | /ready | Registry and bundle readiness |
| GET | /v1/variants | Complete immutable registry |
| GET | /v1/variants/{id} | One variant contract |
| GET | /v1/samples | Public qualification fixtures |
| POST | /v1/predictions?variant_id= | Approved sample inference |
| GET | /v1/benchmarks/summary | Persisted paired measurements |
| GET | /v1/benchmarks/pareto | Derived frontier and recommendations |
| GET | /v1/benchmarks/environment | Hardware/runtime controls |
| GET | /v1/parity/summary | Oracle parity evidence |
| GET | /v1/pruning/summary | Sparsity versus observed speedup |

## Quality and deployment

Run the complete gate:

    .\scripts\quality_gate.ps1

Docker:

    docker compose up --build

AWS preparation:

    .\infra\aws\release.ps1

AWS deployment occurs only with explicit ValidateAws or Apply parameters. Project 24 uses
immutable ECR repository plan-04/p24-edge-vision-console and semantic App Runner service
ai-04-p24-edge-vision-console.

## Responsible interpretation

- Sparsity is distinct from measured speedup.
- File size is distinct from peak memory.
- INT8 is accepted only after quality and parity evidence.
- Results from different machines never share one comparison.
- host_cpu and edge_proxy never imply physical edge hardware.
- Energy remains NOT_MEASURED without a reliable meter.
- Failed parity and NOT_RUN variants remain visible.

> An optimization exists only when it reduces a measured cost without hiding what it sacrifices.
