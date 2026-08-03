from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TextSearchResource(BaseModel):
    query: str = Field(min_length=1, max_length=320)
    mode: Literal["bm25", "semantic", "hybrid"] = "hybrid"
    index_mode: Literal["exact", "approximate"] = "exact"
    top_k: int = Field(default=6, ge=1, le=12)
    alpha: float = Field(default=0.68, ge=0, le=1)
    negative_terms: list[str] = Field(default_factory=list, max_length=8)
    category: str | None = None
    color: str | None = None
    has_people: bool | None = None

    @field_validator("negative_terms")
    @classmethod
    def normalize_terms(cls, values: list[str]) -> list[str]:
        return [value.strip().lower() for value in values if value.strip()]


class ImageSearchResource(BaseModel):
    image_id: str = Field(pattern=r"^vl-[0-9]{3}$")
    index_mode: Literal["exact", "approximate"] = "exact"
    top_k: int = Field(default=6, ge=1, le=12)


class SessionCreateResource(BaseModel):
    top_k: int = Field(default=6, ge=1, le=12)
    mode: Literal["bm25", "semantic", "hybrid"] = "hybrid"
    index_mode: Literal["exact", "approximate"] = "exact"


class SessionMessageResource(BaseModel):
    message: str = Field(min_length=1, max_length=320)
