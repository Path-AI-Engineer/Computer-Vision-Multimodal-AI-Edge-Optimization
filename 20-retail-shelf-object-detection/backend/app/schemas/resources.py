from __future__ import annotations

from pydantic import BaseModel, Field


class ThresholdResource(BaseModel):
    confidence: float = Field(ge=0, le=1)
    nms_iou: float = Field(ge=0, le=1)


class DetectionResource(BaseModel):
    detection_id: int
    class_id: int
    class_name: str
    box: list[float] = Field(min_length=4, max_length=4)
    confidence: float = Field(ge=0, le=1)


class DetectionResponse(BaseModel):
    request_id: str
    model_version: str
    profile: str
    image_width: int
    image_height: int
    detections: list[DetectionResource]
    visible_count: int
    thresholds: ThresholdResource
    latency_ms: float
    warnings: list[str]


class BatchDetectionResponse(BaseModel):
    request_id: str
    count: int
    results: list[DetectionResponse]
