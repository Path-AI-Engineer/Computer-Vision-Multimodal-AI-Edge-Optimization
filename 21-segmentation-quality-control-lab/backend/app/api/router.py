from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile, status

from backend.app.schemas.resources import (
    EvaluationResource,
    HealthResource,
    InspectionResource,
    ModelResource,
    SampleResource,
)
from backend.app.services.quality_service import ImageValidationError, QualityControlService

router = APIRouter()


def _service(request: Request) -> QualityControlService:
    service = getattr(request.app.state, "quality_service", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Bundle unavailable."
        )
    return service


@router.get("/health", response_model=HealthResource, tags=["system"])
def health() -> HealthResource:
    return HealthResource(status="healthy", service="surface-quality-control-lab")


@router.get("/ready", response_model=HealthResource, tags=["system"])
def readiness(request: Request) -> HealthResource:
    service = _service(request)
    return HealthResource(
        status="ready",
        service="surface-quality-control-lab",
        model_version=service.bundle.model_version,
        evidence_profile=service.bundle.evidence_profile,
    )


@router.get("/v1/models/current", response_model=ModelResource, tags=["evidence"])
def current_model(request: Request) -> dict[str, object]:
    return _service(request).model_metadata()


@router.get("/v1/samples", response_model=list[SampleResource], tags=["evidence"])
def samples(request: Request) -> list[dict[str, object]]:
    return _service(request).samples()


async def _run_inspection(
    request: Request,
    sample_id: str | None,
    image: UploadFile | None,
    pixel_threshold: float | None,
) -> dict[str, object]:
    try:
        return await _service(request).inspect(
            sample_id=sample_id,
            upload=image,
            pixel_threshold=pixel_threshold,
        )
    except ImageValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
        ) from error


@router.post("/v1/segmentations", response_model=InspectionResource, tags=["inference"])
async def segment(
    request: Request,
    sample_id: Annotated[str | None, Form()] = None,
    pixel_threshold: Annotated[float | None, Form(ge=0.05, le=0.95)] = None,
    image: Annotated[UploadFile | None, File()] = None,
) -> dict[str, object]:
    return await _run_inspection(request, sample_id, image, pixel_threshold)


@router.post("/v1/inspections", response_model=InspectionResource, tags=["inference"])
async def inspect(
    request: Request,
    sample_id: Annotated[str | None, Form()] = None,
    pixel_threshold: Annotated[float | None, Form(ge=0.05, le=0.95)] = None,
    image: Annotated[UploadFile | None, File()] = None,
) -> dict[str, object]:
    return await _run_inspection(request, sample_id, image, pixel_threshold)


@router.get("/v1/evaluation/summary", response_model=EvaluationResource, tags=["evidence"])
def evaluation_summary(request: Request) -> object:
    return _service(request).report("reports/metrics/evaluation_summary.json")


@router.get(
    "/v1/evaluation/thresholds", response_model=list[EvaluationResource], tags=["evidence"]
)
def evaluation_thresholds(request: Request) -> object:
    return _service(request).report("reports/metrics/threshold_sweep.json")


@router.get("/v1/evaluation/errors", response_model=EvaluationResource, tags=["evidence"])
def evaluation_errors(request: Request) -> object:
    return _service(request).report("reports/errors/error_gallery.json")


@router.get("/v1/evaluation/models", response_model=EvaluationResource, tags=["evidence"])
def model_comparison(request: Request) -> object:
    return _service(request).report("reports/metrics/model_comparison.json")
