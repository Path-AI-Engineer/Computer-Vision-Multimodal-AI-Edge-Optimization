from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class OperatorEditResource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: Literal["company", "date", "address", "total"]
    value: str = Field(min_length=1, max_length=500)


class ExportRequestResource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    format: Literal["json", "csv"] = "json"
    edits: list[OperatorEditResource] = Field(default_factory=list, max_length=4)


class SampleExtractionRequestResource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sample_id: str = Field(pattern=r"^receipt-[a-z0-9-]+$", max_length=80)
    preprocessing_profile: str = "deskew-clahe-v1"
