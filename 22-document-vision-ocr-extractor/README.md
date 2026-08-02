# Document Extraction Workbench

Project 22 of the AI Engineer path is an evidence-first document intelligence product. It
turns a single-page receipt into localized OCR lines, normalized business fields and an
auditable extraction record without hiding uncertainty behind a polished interface.

## Product vertical

1. Select one of the sealed qualification receipts or upload a JPEG/PNG document.
2. Inspect reading order, OCR confidence and preprocessing metadata.
3. Review `company`, `date`, `address` and `total` with the exact source regions used.
4. Compare raw and normalized values, make non-destructive operator edits and export JSON
   or CSV.
5. Inspect OCR, localization, field and review-rate evidence in the evaluation workspace.

The bundled samples are generated qualification fixtures, not SROIE. Official SROIE
evaluation remains locked until its files and official splits are acquired and verified.
Arbitrary uploads require the optional PaddleOCR runtime; the API returns an explicit
capability error when that runtime is absent.

## Local run

```powershell
Set-Location "C:\JeanLoa\Path-AI-Engineer\Computer-Vision-Multimodal-AI-Edge-Optimization\22-document-vision-ocr-extractor"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python scripts\build_qualification_bundle.py

Set-Location frontend
npm install
npm run build
Set-Location ..

$env:PYTHONPATH = $PWD
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8022 --reload
```

Open `http://127.0.0.1:8022/app/`; the API contract is available at
`http://127.0.0.1:8022/docs`.

## Quality gate

```powershell
.\scripts\quality_gate.ps1
```

The gate validates Python formatting/lint, unit/integration/contract tests, evidence
manifests, the frontend build and Docker Compose configuration when Docker is available.

## Repository map

- `document_ai/`: ingestion, preprocessing, OCR contracts, extraction and evaluation.
- `backend/`: thin FastAPI interface and in-memory, TTL-scoped extraction records.
- `frontend/`: React evidence workbench.
- `data/`: sealed qualification samples and manifests; `raw/` is intentionally empty.
- `models/` and `reports/`: versioned bundle metadata and reproducible evidence.
- `infra/docker/` and `infra/aws/`: container and AWS App Runner release assets.
- `docs/`: architecture, contracts, evaluation protocol and evidence boundaries.

## Status

Release candidate `v1.0.0-rc.1`. It is a portfolio qualification system, not a production
invoice processor. See `docs/project-status.md` and `docs/threats-to-validity.md`.
