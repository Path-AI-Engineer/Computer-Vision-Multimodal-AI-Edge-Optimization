# API contract

System routes expose liveness and bundle readiness. Evidence routes return immutable model,
threshold, comparison and error records. Inference accepts multipart form data with exactly
one `sample_id` or `image`; `pixel_threshold` is optional and constrained to `[0.05, 0.95]`.

Responses contain source, probability, mask, overlay and OpenCV baseline images as data URIs,
plus component counts, area, decisions, latency and warnings. Invalid image type, empty or
oversized payload, excess pixels, unknown sample, duplicate source or missing source returns
HTTP 422. Runtime failures are never converted into fabricated results.

OpenAPI is available at `/openapi.json` and interactive documentation at `/docs`.
