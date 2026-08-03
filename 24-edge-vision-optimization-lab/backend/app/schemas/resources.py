from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    sample_id: str = Field(min_length=1, max_length=80)
    top_k: int = Field(default=3, ge=1, le=5)


class PredictionItem(BaseModel):
    label: str
    probability: float


class PredictionResource(BaseModel):
    variant_id: str
    sample_id: str
    predictions: list[PredictionItem]
    observed_latency_ms: float
    model_version: str
    status: Literal["QUALIFICATION_ONLY"]


class HealthResource(BaseModel):
    status: str
    service: str


class ReadinessResource(BaseModel):
    status: str
    bundle_id: str
    approved_variants: int
    sample_count: int
    claim_boundary: str


class PayloadResource(BaseModel):
    data: dict[str, Any] | list[dict[str, Any]]
