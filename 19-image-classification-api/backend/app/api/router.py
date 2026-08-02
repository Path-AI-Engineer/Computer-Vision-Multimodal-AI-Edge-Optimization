from __future__ import annotations

from email import policy
from email.parser import BytesParser

from fastapi import APIRouter, HTTPException, Query, Request, status

from backend.app.schemas.resources import BatchPredictionResource, PredictionResource
from backend.app.services.prediction_service import (
    ArtifactUnavailableError,
    ImageContractError,
    PredictionService,
)
from ml.data.contracts import BREED_TO_SPECIES, BREEDS

router = APIRouter()

SINGLE_IMAGE_BODY = {
    "requestBody": {
        "required": True,
        "content": {
            "multipart/form-data": {
                "schema": {
                    "type": "object",
                    "required": ["image"],
                    "properties": {"image": {"type": "string", "format": "binary"}},
                }
            }
        },
    }
}

BATCH_IMAGE_BODY = {
    "requestBody": {
        "required": True,
        "content": {
            "multipart/form-data": {
                "schema": {
                    "type": "object",
                    "required": ["images"],
                    "properties": {
                        "images": {
                            "type": "array",
                            "maxItems": 8,
                            "items": {"type": "string", "format": "binary"},
                        }
                    },
                }
            }
        },
    }
}


def service(request: Request) -> PredictionService:
    return request.app.state.prediction_service


@router.get("/health", tags=["Operations"])
def health() -> dict[str, str]:
    return {"status": "ok", "service": "pet-breed-classification-studio"}


@router.get("/ready", tags=["Operations"])
def ready(request: Request) -> dict[str, str]:
    if not service(request).ready:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Inference bundle unavailable")
    return {"status": "ready", "artifact": "pet-studio-qualification-v1"}


@router.get("/v1/classes", tags=["Catalog"])
def classes() -> dict[str, object]:
    return {
        "count": len(BREEDS),
        "items": [
            {"class_id": index, "class_name": name, "species": BREED_TO_SPECIES[name]}
            for index, name in enumerate(BREEDS)
        ],
    }


@router.get("/v1/models/current", tags=["Evidence"])
def current_model(request: Request) -> object:
    return service(request).read_json("models/bundles/bundle_manifest.json")


@router.get("/v1/samples", tags=["Catalog"])
def samples(request: Request) -> dict[str, object]:
    items = service(request).samples()
    return {"count": len(items), "items": items, "warning": "Qualification-only samples"}


@router.post(
    "/v1/predictions",
    response_model=PredictionResource,
    tags=["Inference"],
    openapi_extra=SINGLE_IMAGE_BODY,
)
async def predict(
    request: Request,
    top_k: int = Query(5, ge=1, le=10),
) -> dict[str, object]:
    try:
        parts = await image_parts(request, maximum_files=1)
        return service(request).predict_content(parts[0], top_k)
    except ImageContractError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error


@router.post(
    "/v1/predictions/batch",
    response_model=BatchPredictionResource,
    tags=["Inference"],
    openapi_extra=BATCH_IMAGE_BODY,
)
async def predict_batch(
    request: Request,
    top_k: int = Query(5, ge=1, le=10),
) -> dict[str, object]:
    current = service(request)
    try:
        parts = await image_parts(request, maximum_files=current.config.max_batch_size)
        predictions = [current.predict_content(part, top_k) for part in parts]
    except ImageContractError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error
    return {
        "request_id": current.batch_id(),
        "count": len(predictions),
        "predictions": predictions,
    }


async def image_parts(request: Request, maximum_files: int) -> list[bytes]:
    content_type = request.headers.get("content-type", "")
    if "multipart/form-data" not in content_type or "boundary=" not in content_type:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "Use multipart/form-data with an image field.",
        )
    maximum_total = maximum_files * service(request).config.max_upload_bytes + 64_000
    declared_length = int(request.headers.get("content-length", "0") or 0)
    if declared_length > maximum_total:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Upload is too large.")
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


@router.get("/v1/evaluation/summary", tags=["Evidence"])
def evaluation_summary(request: Request) -> object:
    return service(request).read_json("reports/metrics/metrics.json")


@router.get("/v1/evaluation/calibration", tags=["Evidence"])
def calibration(request: Request) -> object:
    return service(request).read_json("reports/metrics/calibration.json")


@router.get("/v1/evaluation/errors", tags=["Evidence"])
def errors(request: Request) -> object:
    return service(request).read_json("reports/errors/error_gallery.json")


@router.get("/v1/evaluation/models", tags=["Evidence"])
def models(request: Request) -> object:
    return service(request).read_json("reports/metrics/model_comparison.json")


@router.get("/v1/evaluation/latency", tags=["Evidence"])
def latency(request: Request) -> object:
    return service(request).read_json("reports/metrics/latency_report.json")


@router.get("/v1/evaluation/protocol", tags=["Evidence"])
def protocol(request: Request) -> object:
    return service(request).read_json("data/manifests/dataset_manifest.json")


@router.get("/v1/evaluation/test-status", tags=["Evidence"])
def test_status() -> dict[str, str]:
    return {
        "status": "LOCKED_NOT_ACQUIRED",
        "reason": "Official test remains closed until candidate selection and calibration.",
    }


@router.get("/v1/evaluation/confusion-matrix", tags=["Evidence"])
def confusion_matrix() -> dict[str, str]:
    return {"image_url": "/reports/confusion_matrix.png", "scope": "QUALIFICATION_ONLY"}


@router.get("/v1/evaluation/reliability-diagram", tags=["Evidence"])
def reliability_diagram() -> dict[str, str]:
    return {"image_url": "/reports/reliability_diagram.png", "scope": "QUALIFICATION_ONLY"}


def install_exception_handlers(app: object) -> None:
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    assert isinstance(app, FastAPI)

    @app.exception_handler(ArtifactUnavailableError)
    async def artifact_unavailable(_request: Request, error: ArtifactUnavailableError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": str(error), "code": "ARTIFACT_UNAVAILABLE"},
        )
