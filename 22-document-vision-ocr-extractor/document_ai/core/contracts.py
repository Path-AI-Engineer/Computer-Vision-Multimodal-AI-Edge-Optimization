from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Box = tuple[int, int, int, int]
FieldName = Literal["company", "date", "address", "total"]


@dataclass(frozen=True)
class OcrToken:
    token_id: str
    text: str
    confidence: float
    box: Box
    line_index: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FieldEvidence:
    field: FieldName
    raw_value: str | None
    normalized_value: str | None
    confidence: float
    review_required: bool
    reason_codes: tuple[str, ...]
    token_ids: tuple[str, ...]
    boxes: tuple[Box, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["reason_codes"] = list(self.reason_codes)
        payload["token_ids"] = list(self.token_ids)
        payload["boxes"] = [list(box) for box in self.boxes]
        return payload


@dataclass(frozen=True)
class ExtractionRecord:
    request_id: str
    sample_id: str | None
    source_name: str
    source_kind: str
    created_at: str
    pipeline_version: str
    preprocessing_profile: str
    ocr_adapter: str
    width: int
    height: int
    tokens: tuple[OcrToken, ...]
    fields: tuple[FieldEvidence, ...]
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "tokens": [token.to_dict() for token in self.tokens],
            "fields": [item.to_dict() for item in self.fields],
            "warnings": list(self.warnings),
        }
