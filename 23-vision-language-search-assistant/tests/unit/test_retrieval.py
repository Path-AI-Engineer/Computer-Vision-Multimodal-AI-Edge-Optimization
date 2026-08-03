from pathlib import Path

from multimodal.data.manifest import load_manifest
from multimodal.retrieval.service import RetrievalService

ROOT = Path(__file__).resolve().parents[2]


def service() -> RetrievalService:
    return RetrievalService(
        load_manifest(ROOT / "data" / "manifests" / "qualification-corpus.json")
    )


def test_hybrid_search_returns_target_and_score_components() -> None:
    response = service().search_text("dog running on beach", mode="hybrid")
    assert response.status == "COMPLETED"
    assert response.results[0].image_id == "vl-001"
    assert response.results[0].score_breakdown.alpha == 0.68
    assert response.citations[0] == "vl-001"


def test_caption_search_is_independently_available() -> None:
    response = service().search_text("chef cooking inside kitchen", mode="bm25")
    assert response.results[0].image_id == "vl-009"
    assert response.results[0].score_breakdown.lexical > 0


def test_filters_and_exclusions_are_applied_before_top_k() -> None:
    response = service().search_text(
        "animals near water",
        mode="hybrid",
        negative_terms=("dog",),
        filters={"category": "animals"},
    )
    assert all(result.category == "animals" for result in response.results)
    assert "vl-001" not in response.citations


def test_image_search_uses_the_same_index_snapshot() -> None:
    response = service().search_image("vl-005")
    assert response.results[0].image_id == "vl-005"
    assert response.model_version == "qualification-dual-encoder-v1"
    assert response.index_version == "qualification-index-v1"


def test_unknown_query_abstains() -> None:
    response = service().search_text("quasar bureaucracy")
    assert response.status == "INSUFFICIENT_RESULTS"
