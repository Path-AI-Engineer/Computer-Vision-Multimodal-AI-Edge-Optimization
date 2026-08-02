# Architecture

## Runtime flow

`Input validation -> preprocessing -> OCR localization/recognition -> reading order ->
layout-aware field extraction -> normalization -> confidence/review -> export`

The `document_ai` package owns the deterministic domain pipeline. `backend` exposes thin
FastAPI routes and a bounded in-memory store. `frontend` consumes only public resources.
Model metadata, dataset manifests and reports are immutable inputs checked by the bundle
loader before readiness is reported.

## Trust boundaries

- Upload bytes are size, type, signature, pixel and page-count checked before OCR.
- The release does not persist document bytes. Extraction records expire after one hour.
- Operator edits are carried beside predictions, never written over raw OCR or model output.
- The default container runs as a non-root user with a read-only filesystem.
- Fixture OCR can only load checked-in qualification annotations by sample identifier.
- Arbitrary upload OCR fails when PaddleOCR is absent; there is no synthetic fallback.

## Deployment

The production image serves the built React client and API from one App Runner service.
This keeps the portfolio release small and consistent. It is not the final high-throughput
architecture: a production OCR system would separate asynchronous OCR workers, object
storage, malware scanning and durable audit records.
