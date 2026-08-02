from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class HealthResource(BaseModel):
    status: Literal["healthy", "ready"]
    service: str
    model_version: str | None = None
    evidence_profile: str | None = None


class SampleResource(BaseModel):
    sample_id: str
    image_url: str
    ground_truth_mask_url: str
    defective: bool
    defect_area_px: int
    defect_area_ratio: float


class InspectionResource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    model_version: str
    mask_probability_uri: str
    binary_mask_uri: str
    baseline_mask_uri: str
    image_uri: str
    overlay_uri: str
    baseline_overlay_uri: str
    defect_detected: bool
    defect_area_px: int = Field(ge=0)
    defect_area_ratio: float = Field(ge=0, le=1)
    component_count: int = Field(ge=0)
    largest_component_px: int = Field(ge=0)
    pixel_threshold: float = Field(ge=0.05, le=0.95)
    piece_threshold: float = Field(ge=0, le=1)
    decision: Literal["ACCEPT", "REVIEW", "REJECT"]
    baseline_decision: Literal["ACCEPT", "REVIEW", "REJECT"]
    latency_ms: float = Field(ge=0)
    warnings: list[str]


class EvaluationResource(BaseModel):
    model_config = ConfigDict(extra="allow")


class ModelResource(BaseModel):
    model_config = ConfigDict(extra="allow")
