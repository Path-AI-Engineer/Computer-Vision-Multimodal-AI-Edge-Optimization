# API contract

The OpenAPI document is generated at `/openapi.json`; interactive documentation is available
at `/docs`.

## Operations and catalog

- `GET /health`: process liveness.
- `GET /ready`: model-bundle readiness.
- `GET /v1/classes`: 37 stable class IDs, names and species.
- `GET /v1/models/current`: artifact manifest, versions and checksums.
- `GET /v1/samples`: public qualification samples used by the interface.

## Inference

- `POST /v1/predictions?top_k=5`: one multipart image.
- `POST /v1/predictions/batch?top_k=5`: one to eight multipart images.

Every successful prediction includes request ID, artifact and preprocessing versions, primary
class, species, Top-K probabilities, confidence, abstention status, threshold, latency, warnings
and non-sensitive input metadata. Invalid or unsafe image content returns HTTP 422. Missing
artifacts return HTTP 503.

## Evidence

- `GET /v1/evaluation/summary`
- `GET /v1/evaluation/calibration`
- `GET /v1/evaluation/confusion-matrix`
- `GET /v1/evaluation/reliability-diagram`
- `GET /v1/evaluation/errors`
- `GET /v1/evaluation/models`
- `GET /v1/evaluation/latency`
- `GET /v1/evaluation/protocol`
- `GET /v1/evaluation/test-status`
