from __future__ import annotations

from fastapi import APIRouter, Query

from backend.app.schemas.resources import (
    HealthResource,
    PredictionRequest,
    PredictionResource,
    ReadinessResource,
)
from backend.app.services.runtime import runtime

router = APIRouter()


@router.get("/health", response_model=HealthResource, tags=["runtime"])
def health() -> HealthResource:
    return HealthResource(status="ok", service="edge-vision-benchmark-console")


@router.get("/ready", response_model=ReadinessResource, tags=["runtime"])
def ready() -> ReadinessResource:
    return ReadinessResource.model_validate(runtime.readiness())


@router.get("/v1/variants", tags=["registry"])
def variants() -> dict[str, object]:
    return {"data": runtime.registry.list(), "registry_id": runtime.registry.payload["registry_id"]}


@router.get("/v1/variants/{variant_id}", tags=["registry"])
def variant(variant_id: str) -> dict[str, object]:
    return {"data": runtime.registry.get(variant_id)}


@router.get("/v1/samples", tags=["inference"])
def samples() -> dict[str, object]:
    return {"data": runtime.predictor.sample_catalog(), "status": "QUALIFICATION_ONLY"}


@router.post("/v1/predictions", response_model=PredictionResource, tags=["inference"])
def predict(
    payload: PredictionRequest, variant_id: str = Query(..., min_length=1)
) -> PredictionResource:
    result = runtime.predictor.predict(variant_id, payload.sample_id, payload.top_k)
    return PredictionResource.model_validate(result.as_dict())


@router.get("/v1/benchmarks/summary", tags=["benchmark"])
def benchmark_summary() -> dict[str, object]:
    return runtime.summary


@router.get("/v1/benchmarks/pareto", tags=["benchmark"])
def benchmark_pareto() -> dict[str, object]:
    return runtime.pareto


@router.get("/v1/benchmarks/environment", tags=["benchmark"])
def benchmark_environment() -> dict[str, object]:
    return runtime.environment


@router.get("/v1/parity/summary", tags=["evidence"])
def parity_summary() -> dict[str, object]:
    return runtime.parity


@router.get("/v1/pruning/summary", tags=["evidence"])
def pruning_summary() -> dict[str, object]:
    return runtime.pruning
