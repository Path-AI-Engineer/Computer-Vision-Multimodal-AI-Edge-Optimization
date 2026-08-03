from __future__ import annotations

from time import perf_counter

import numpy as np

from multimodal.core.contracts import (
    CorpusItem,
    IndexMode,
    ScoreBreakdown,
    SearchMode,
    SearchResponse,
    SearchResult,
)
from multimodal.embeddings.store import EmbeddingStore
from multimodal.encoders.qualification import QualificationDualEncoder
from multimodal.indexes.numpy_index import NumpyInnerProductIndex, QuantizedApproximateIndex
from multimodal.retrieval.lexical import TfidfCaptionIndex


class RetrievalService:
    def __init__(self, items: tuple[CorpusItem, ...]) -> None:
        self.items = items
        self.encoder = QualificationDualEncoder()
        self.embeddings = EmbeddingStore(items, self.encoder)
        self.lexical = TfidfCaptionIndex(items)
        self.exact = NumpyInnerProductIndex(self.embeddings.matrix)
        self.approximate = QuantizedApproximateIndex(self.embeddings.matrix)

    def search_text(
        self,
        query: str,
        *,
        mode: SearchMode = "hybrid",
        index_mode: IndexMode = "exact",
        top_k: int = 6,
        alpha: float = 0.68,
        negative_terms: tuple[str, ...] = (),
        filters: dict[str, str | bool] | None = None,
    ) -> SearchResponse:
        vector = self.encoder.encode_text(query)
        return self._search(
            query,
            vector,
            mode,
            index_mode,
            top_k,
            alpha,
            negative_terms,
            filters or {},
        )

    def search_image(
        self,
        image_id: str,
        *,
        index_mode: IndexMode = "exact",
        top_k: int = 6,
    ) -> SearchResponse:
        vector = self.embeddings.vector_for(image_id)
        return self._search(
            f"similar to {image_id}", vector, "semantic", index_mode, top_k, 1.0, (), {}
        )

    def search_vector(
        self,
        vector: np.ndarray,
        *,
        query_label: str = "uploaded image",
        index_mode: IndexMode = "exact",
        top_k: int = 6,
    ) -> SearchResponse:
        normalized = self.encoder.encode_vector(tuple(float(value) for value in vector))
        return self._search(query_label, normalized, "semantic", index_mode, top_k, 1.0, (), {})

    def _search(
        self,
        query: str,
        vector: np.ndarray,
        mode: SearchMode,
        index_mode: IndexMode,
        top_k: int,
        alpha: float,
        negative_terms: tuple[str, ...],
        filters: dict[str, str | bool],
    ) -> SearchResponse:
        started = perf_counter()
        index = self.exact if index_mode == "exact" else self.approximate
        _, semantic_values = index.search(vector, len(self.items))
        semantic_by_position = self.embeddings.matrix @ vector
        if index_mode == "approximate":
            semantic_by_position = self.approximate.matrix @ np.round(vector, 1)
        semantic_by_position = self._minmax(semantic_by_position)
        lexical_values = self.lexical.score(query)
        combined = {
            "bm25": lexical_values,
            "semantic": semantic_by_position,
            "hybrid": alpha * semantic_by_position + (1 - alpha) * lexical_values,
        }[mode]
        negative = {term.lower() for term in negative_terms}
        eligible: list[int] = []
        for position, item in enumerate(self.items):
            evidence_text = " ".join(caption.text.lower() for caption in item.captions)
            if negative and any(term in evidence_text for term in negative):
                continue
            if filters.get("category") and item.category != filters["category"]:
                continue
            if "has_people" in filters and item.has_people is not filters["has_people"]:
                continue
            if filters.get("color") and filters["color"] not in item.colors:
                continue
            eligible.append(position)
        ranked = sorted(eligible, key=lambda pos: (-float(combined[pos]), self.items[pos].image_id))
        results: list[SearchResult] = []
        for position in ranked[: max(1, min(top_k, 12))]:
            item = self.items[position]
            score = float(combined[position])
            results.append(
                SearchResult(
                    rank=len(results) + 1,
                    image_id=item.image_id,
                    image_url=f"/assets/corpus/{item.filename}",
                    category=item.category,
                    colors=item.colors,
                    score=round(score, 4),
                    evidence_captions=item.captions[:2],
                    score_breakdown=ScoreBreakdown(
                        semantic=round(float(semantic_by_position[position]), 4),
                        lexical=round(float(lexical_values[position]), 4),
                        hybrid=round(
                            float(
                                alpha * semantic_by_position[position]
                                + (1 - alpha) * lexical_values[position]
                            ),
                            4,
                        ),
                        alpha=alpha,
                    ),
                    reason_codes=("CAPTION_EVIDENCE", "NORMALIZED_INNER_PRODUCT"),
                )
            )
        status = "COMPLETED" if results and results[0].score >= 0.08 else "INSUFFICIENT_RESULTS"
        citations = tuple(item.image_id for item in results)
        explanation = (
            f"Ranked {len(results)} images using {mode} retrieval. "
            f"Evidence is limited to image IDs, normalized scores and stored captions: "
            f"{', '.join(citations) if citations else 'none'}."
        )
        return SearchResponse(
            status=status,
            query=query,
            mode=mode,
            index_mode=index_mode,
            model_version=self.encoder.model_version,
            index_version="qualification-index-v1",
            latency_ms=round((perf_counter() - started) * 1000, 3),
            results=tuple(results),
            explanation=explanation,
            citations=citations,
            evidence_boundary=(
                "Qualification corpus and deterministic dual-encoder adapter; scores are "
                "ranking signals, not semantic truth or an official Flickr8k benchmark."
            ),
        )

    @staticmethod
    def _minmax(values: np.ndarray) -> np.ndarray:
        minimum = float(values.min(initial=0.0))
        maximum = float(values.max(initial=0.0))
        if maximum <= minimum:
            return np.zeros_like(values)
        return (values - minimum) / (maximum - minimum)
