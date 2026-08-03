from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Literal

SearchMode = Literal["bm25", "semantic", "hybrid"]
IndexMode = Literal["exact", "approximate"]


@dataclass(frozen=True)
class Caption:
    caption_id: str
    text: str


@dataclass(frozen=True)
class CorpusItem:
    image_id: str
    filename: str
    split: str
    category: str
    colors: tuple[str, ...]
    has_people: bool
    captions: tuple[Caption, ...]
    vector: tuple[float, ...]
    checksum: str

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["captions"] = [asdict(caption) for caption in self.captions]
        return payload


@dataclass(frozen=True)
class ScoreBreakdown:
    semantic: float
    lexical: float
    hybrid: float
    alpha: float


@dataclass(frozen=True)
class SearchResult:
    rank: int
    image_id: str
    image_url: str
    category: str
    colors: tuple[str, ...]
    score: float
    evidence_captions: tuple[Caption, ...]
    score_breakdown: ScoreBreakdown
    reason_codes: tuple[str, ...]

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["evidence_captions"] = [asdict(item) for item in self.evidence_captions]
        return payload


@dataclass
class SearchState:
    session_id: str
    positive_query: str = ""
    negative_terms: list[str] = field(default_factory=list)
    filters: dict[str, str | bool] = field(default_factory=dict)
    previous_result_ids: list[str] = field(default_factory=list)
    selected_image_id: str | None = None
    model_version: str = "qualification-dual-encoder-v1"
    index_version: str = "qualification-index-v1"
    top_k: int = 6
    mode: SearchMode = "hybrid"
    index_mode: IndexMode = "exact"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class SearchResponse:
    status: Literal["COMPLETED", "INSUFFICIENT_RESULTS"]
    query: str
    mode: SearchMode
    index_mode: IndexMode
    model_version: str
    index_version: str
    latency_ms: float
    results: tuple[SearchResult, ...]
    explanation: str
    citations: tuple[str, ...]
    evidence_boundary: str

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["results"] = [item.to_dict() for item in self.results]
        return payload
