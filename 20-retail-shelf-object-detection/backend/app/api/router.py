from __future__ import annotations

from email import policy
from email.parser import BytesParser

from fastapi import APIRouter, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse

from backend.app.schemas.resources import BatchDetectionResponse, DetectionResponse
from backend.app.services.detection_service import (
    ArtifactUnavailableError,
    DetectionService,
    ImageContractError,
)

router = APIRouter()


def service(request: Request) -> DetectionService:
    return request.app.state.detection_service


@router.get("/health", tags=["Operations"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "retail-shelf-detection-console"}


@router.get("/ready", tags=["Operations"])
def ready(request: Request) -> dict[str, str]:
    if not service(request).ready:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Detector bundle unavailable")
    return {"status": "ready", "profile": "qualification_smoke"}


@router.get("/v1/models/current", tags=["Evidence"])
def model(request: Request) -> object:
    return service(request).json_artifact("models/bundles/bundle_manifest.json")


@router.get("/v1/samples", tags=["Catalog"])
def samples(request: Request) -> dict[str, object]:
    items = service(request).samples()
    return {"count": len(items), "items": items, "warning": "Qualification-only scenes"}


@router.post("/v1/detections", response_model=DetectionResponse, tags=["Inference"])
async def detect(
    request: Request,
    confidence: float = Query(0.35, ge=0.05, le=0.95),
    nms_iou: float = Query(0.45, ge=0.1, le=0.9),
) -> dict[str, object]:
    try:
        parts = await image_parts(request, 1)
        return service(request).detect(parts[0], confidence, nms_iou)
    except ImageContractError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error


@router.post("/v1/detections/batch", response_model=BatchDetectionResponse, tags=["Inference"])
async def detect_batch(
    request: Request,
    confidence: float = Query(0.35, ge=0.05, le=0.95),
    nms_iou: float = Query(0.45, ge=0.1, le=0.9),
) -> dict[str, object]:
    current = service(request)
    try:
        parts = await image_parts(request, current.config.maximum_batch_size)
        results = [current.detect(part, confidence, nms_iou) for part in parts]
    except ImageContractError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error
    return {"request_id": current.batch_id(), "count": len(results), "results": results}


@router.get("/v1/evaluation/summary", tags=["Evidence"])
def summary(request: Request) -> object:
    return service(request).json_artifact("reports/metrics/metrics.json")


@router.get("/v1/evaluation/density-slices", tags=["Evidence"])
def slices(request: Request) -> object:
    return service(request).json_artifact("reports/metrics/density_slices.json")


@router.get("/v1/evaluation/errors", tags=["Evidence"])
def errors(request: Request) -> object:
    return service(request).json_artifact("reports/errors/error_gallery.json")


@router.get("/v1/evaluation/models", tags=["Evidence"])
def models(request: Request) -> object:
    return service(request).json_artifact("reports/metrics/model_comparison.json")


@router.get("/v1/evaluation/latency", tags=["Evidence"])
def latency(request: Request) -> object:
    return service(request).json_artifact("reports/metrics/latency_report.json")


async def image_parts(request: Request, maximum_files: int) -> list[bytes]:
    content_type = request.headers.get("content-type", "")
    if "multipart/form-data" not in content_type or "boundary=" not in content_type:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "Use multipart/form-data with image files.",
        )
    maximum_total = maximum_files * service(request).config.maximum_upload_bytes + 64_000
    body = await request.body()
    if len(body) > maximum_total:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Upload is too large.")
    message = BytesParser(policy=policy.default).parsebytes(
        f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode() + body
    )
    parts = [
        part.get_payload(decode=True) for part in message.iter_parts() if part.get_filename()
    ]
    if not parts or len(parts) > maximum_files:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"Batch size must be between 1 and {maximum_files}.",
        )
    return parts


def install_exception_handlers(app: object) -> None:
    from fastapi import FastAPI

    assert isinstance(app, FastAPI)

    @app.exception_handler(ArtifactUnavailableError)
    async def artifact_unavailable(_request: Request, error: ArtifactUnavailableError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": str(error), "code": "ARTIFACT_UNAVAILABLE"},
        )
