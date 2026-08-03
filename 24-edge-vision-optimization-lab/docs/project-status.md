# Project status

Status: `RELEASE_CANDIDATE - QUALIFICATION BUNDLE IMPLEMENTED`

## Implemented

- Dataset, training, pruning, quantization, export and benchmark contracts.
- Deterministic qualification bundle with 12 generated public fixtures.
- Six registered variants: four approved qualification adapters, one experimental
  structured-pruning proxy and one explicit `NOT_RUN` QAT boundary.
- Raw host latency samples, quality metrics, parity, pruning, calibration, environment and
  Pareto evidence.
- Immutable variant registry and a predictor that rejects unapproved variants.
- FastAPI resources and a responsive React benchmark console.
- Reproducible Docker packaging and an explicit AWS App Runner release workflow.

## Validation evidence

Validated on 2026-08-02:

- Ruff lint: passed.
- Ruff formatting: passed for 42 Python files.
- Pytest: 35 tests passed.
- Project evidence validator: passed.
- React TypeScript and Vite production build: passed.
- Docker Compose configuration: passed.
- AWS release local preflight: passed; no AWS deployment was requested or executed.

The Playwright suite is implemented but could not execute in the managed Windows session
because the operating system rejected worker creation with `spawn EPERM`. A clean `npm ci`
was blocked by the same environment policy; the existing locked dependency tree still built
the production frontend successfully. Docker runtime acceptance was not executed because the
Docker Desktop Linux engine was unavailable.

## Promotion gates not executed

- Oxford-IIIT Pet acquisition and immutable source manifest.
- MobileNetV3-Small fine-tuning and final test evaluation.
- ONNX checker and ONNX Runtime execution.
- Static PTQ and QAT research variants.
- Physical edge-device benchmark.
- Stable RSS/load measurement and instrumented energy measurement.
- AWS deployment.

Those gates remain explicit. Qualification metrics are never presented as MobileNetV3,
ONNX Runtime or physical edge evidence.
