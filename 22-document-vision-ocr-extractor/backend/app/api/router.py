from __future__ import annotations

import csv
import io
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response

from backend.app.core.config import settings
from backend.app.schemas.resources import ExportRequestResource, SampleExtractionRequestResource
from backend.app.services.extraction_service import ExtractionService
from document_ai.artifacts.bundle import load_bundle
from document_ai.ingestion.validator import DocumentValidationError
from document_ai.preprocessing.pipeline import PROFILES

router = APIRouter()
service = ExtractionService(
    settings.root,
    settings.max_upload_bytes,
    settings.extraction_ttl_seconds,
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _record_payload(record) -> dict:
    payload = record.to_dict()
    payload["image_url"] = f"/assets/samples/{record.sample_id}.png" if record.sample_id else None
    payload["expires_in_seconds"] = settings.extraction_ttl_seconds
    return payload


async def _bounded_body(request: Request) -> bytes:
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > settings.max_upload_bytes:
            raise HTTPException(413, "The document exceeds the configured upload limit.")
    return bytes(body)


@router.get("/health", tags=["runtime"])
def health() -> dict[str, str]:
    return {"status": "healthy", "service": "document-vision-ocr-extractor"}


@router.get("/ready", tags=["runtime"])
def ready() -> dict[str, str]:
    load_bundle(settings.root)
    return {"status": "ready", "bundle": "document-extractor-v1"}


@router.get("/v1/models/current", tags=["model"])
def current_model() -> dict:
    bundle = load_bundle(settings.root)
    bundle["evidence_boundary"] = {
        "dataset": "generated-receipt-qualification-v1",
        "official_sroie": "LOCKED_NOT_ACQUIRED",
        "arbitrary_uploads": "PaddleOCR optional runtime required",
    }
    return bundle


@router.get("/v1/documents/samples", tags=["documents"])
def samples() -> dict[str, list[dict[str, object]]]:
    return {"samples": service.list_samples()}


@router.post("/v1/documents/extract", tags=["documents"])
async def extract_document(request: Request) -> dict:
    content_type = request.headers.get("content-type", "").split(";", 1)[0].lower()
    if content_type == "application/json":
        resource = SampleExtractionRequestResource.model_validate(await request.json())
        preprocessing_profile = resource.preprocessing_profile
    else:
        resource = None
        preprocessing_profile = request.headers.get("x-preprocessing-profile", "deskew-clahe-v1")
    if preprocessing_profile not in PROFILES:
        raise HTTPException(422, f"Unknown preprocessing profile: {preprocessing_profile}")
    try:
        if resource:
            record = service.extract_sample(resource.sample_id, preprocessing_profile)
        else:
            if content_type not in {"image/jpeg", "image/png", "application/pdf"}:
                raise HTTPException(
                    415,
                    "Use application/json for a sealed sample or a supported "
                    "document content type.",
                )
            payload = await _bounded_body(request)
            record = service.extract_upload(
                payload,
                request.headers.get("x-document-name", "document"),
                content_type,
                preprocessing_profile,
            )
    except FileNotFoundError as error:
        raise HTTPException(404, str(error)) from error
    except DocumentValidationError as error:
        raise HTTPException(422, str(error)) from error
    return _record_payload(record)


@router.get("/v1/extractions/{request_id}", tags=["extractions"])
def extraction_detail(request_id: str) -> dict:
    record = service.store.get(request_id)
    if record is None:
        raise HTTPException(404, "The extraction does not exist or its TTL has expired.")
    return _record_payload(record)


@router.post("/v1/extractions/{request_id}/export", tags=["extractions"])
def export_extraction(request_id: str, resource: ExportRequestResource) -> Response:
    record = service.store.get(request_id)
    if record is None:
        raise HTTPException(404, "The extraction does not exist or its TTL has expired.")
    predictions = {field.field: field.normalized_value for field in record.fields}
    edits = {edit.field: edit.value for edit in resource.edits}
    resolved = {key: edits.get(key, value) for key, value in predictions.items()}
    audit = {
        "request_id": request_id,
        "pipeline_version": record.pipeline_version,
        "predictions": predictions,
        "operator_edits": edits,
        "resolved_values": resolved,
        "edits_are_predictions": False,
    }
    if resource.format == "json":
        content = json.dumps(audit, indent=2) + "\n"
        return Response(
            content,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="extraction-{request_id}.json"'},
        )
    stream = io.StringIO()
    writer = csv.DictWriter(stream, fieldnames=["field", "predicted", "operator_edit", "resolved"])
    writer.writeheader()
    for field, prediction in predictions.items():
        writer.writerow(
            {
                "field": field,
                "predicted": prediction or "",
                "operator_edit": edits.get(field, ""),
                "resolved": resolved.get(field, "") or "",
            }
        )
    return Response(
        stream.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="extraction-{request_id}.csv"'},
    )


@router.get("/v1/evaluation/summary", tags=["evaluation"])
def evaluation_summary() -> dict:
    return _json(settings.root / "reports" / "metrics" / "evaluation-summary.json")


@router.get("/v1/evaluation/errors", tags=["evaluation"])
def evaluation_errors() -> dict:
    return _json(settings.root / "reports" / "errors" / "error-gallery.json")
