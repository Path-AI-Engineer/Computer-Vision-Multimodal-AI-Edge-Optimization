# API contract

| Method | Route | Responsibility |
|---|---|---|
| GET | `/health` | process liveness |
| GET | `/ready` | hash-verified bundle readiness |
| GET | `/v1/models/current` | runtime and evidence boundary |
| GET | `/v1/documents/samples` | sealed sample catalog |
| POST | `/v1/documents/extract` | sample or upload extraction |
| GET | `/v1/extractions/{request_id}` | TTL-scoped record lookup |
| POST | `/v1/extractions/{request_id}/export` | JSON/CSV plus separate edits |
| GET | `/v1/evaluation/summary` | qualification metrics |
| GET | `/v1/evaluation/errors` | mismatch and review gallery |

The extraction command accepts either JSON (`sample_id` plus preprocessing profile) or a
direct JPEG/PNG/PDF request body. Binary requests declare `X-Document-Name` and
`X-Preprocessing-Profile`; this bounded contract avoids multipart parser ambiguity. Business
validation returns `422`; unavailable optional capabilities use RFC 7807 problem details
with `503`; missing or expired extraction IDs return `404`.
