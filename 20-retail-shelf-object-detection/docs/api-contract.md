# API contract

| Method | Route | Purpose |
|---|---|---|
| GET | `/health` | Process liveness |
| GET | `/ready` | Bundle readiness and active profile |
| GET | `/v1/models/current` | Immutable bundle manifest |
| GET | `/v1/samples` | Qualification gallery |
| POST | `/v1/detections` | Multipart single-image detection |
| POST | `/v1/detections/batch` | Bounded multipart batch |
| GET | `/v1/evaluation/summary` | Persisted overall metrics |
| GET | `/v1/evaluation/density-slices` | Low/medium/high evidence |
| GET | `/v1/evaluation/errors` | Visual error gallery |
| GET | `/v1/evaluation/models` | Candidate execution registry |
| GET | `/v1/evaluation/latency` | Qualification latency evidence |

Threshold query parameters are validated by FastAPI. Business and artifact failures return structured `detail` messages and appropriate 4xx/503 status codes. OpenAPI is available at `/docs` and `/openapi.json`.
