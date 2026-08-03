from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class VariantStatus(StrEnum):
    APPROVED = "APPROVED_QUALIFICATION"
    EXPERIMENTAL = "EXPERIMENTAL_QUALIFICATION"
    NOT_RUN = "NOT_RUN"


@dataclass(frozen=True)
class QualityMetrics:
    macro_f1: float
    top1_accuracy: float
    top5_accuracy: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True)
class LatencyMetrics:
    p50_ms: float
    p90_ms: float
    p95_ms: float
    mean_ms: float
    throughput_per_second: float
    samples: int

    def as_dict(self) -> dict[str, float | int]:
        return asdict(self)


@dataclass(frozen=True)
class VariantManifest:
    variant_id: str
    display_name: str
    runtime: str
    precision: str
    optimization: str
    status: VariantStatus
    artifact_path: str | None
    artifact_size_mb: float | None
    parameters: int | None
    effective_sparsity: float | None
    quality: QualityMetrics | None
    latency: LatencyMetrics | None
    model_version: str
    preprocessing_version: str
    environment_id: str
    claim_boundary: str

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["status"] = self.status.value
        return payload


@dataclass(frozen=True)
class PredictionResult:
    variant_id: str
    sample_id: str
    predictions: tuple[dict[str, float | str], ...]
    observed_latency_ms: float
    model_version: str
    status: str

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["predictions"] = list(self.predictions)
        return payload
