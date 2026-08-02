from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PredictionItem(BaseModel):
    class_id: int
    class_name: str
    species: str
    probability: float = Field(ge=0, le=1)


class PredictionResource(BaseModel):
    request_id: str
    model_version: str
    class_id: int
    class_name: str
    species: str
    top_k: list[PredictionItem]
    confidence: float = Field(ge=0, le=1)
    abstained: bool
    threshold: float
    preprocessing_version: str
    latency_ms: float
    warnings: list[str]
    explanation: dict[str, Any]
    input: dict[str, Any]


class BatchPredictionResource(BaseModel):
    request_id: str
    count: int
    predictions: list[PredictionResource]
