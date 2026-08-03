import json
from pathlib import Path

import pytest

from multimodal.data.manifest import ManifestError, load_manifest, parse_manifest
from multimodal.evaluation.metrics import index_recall, retrieval_metrics

ROOT = Path(__file__).resolve().parents[2]


def test_manifest_has_unique_traceable_relations() -> None:
    items = load_manifest(ROOT / "data" / "manifests" / "qualification-corpus.json")
    assert len(items) == 12
    assert len({item.image_id for item in items}) == 12
    assert len({caption.caption_id for item in items for caption in item.captions}) == 24
    assert all(item.checksum for item in items)


def test_manifest_rejects_duplicate_image_ids() -> None:
    source = json.loads(
        (ROOT / "data" / "manifests" / "qualification-corpus.json").read_text(encoding="utf-8")
    )
    source["items"][1]["image_id"] = source["items"][0]["image_id"]
    with pytest.raises(ManifestError, match="Duplicate image_id"):
        parse_manifest(source)


def test_retrieval_metrics_are_computed_from_ranks() -> None:
    metrics = retrieval_metrics([1, 2, 6, 10])
    assert metrics["recall_at_1"] == 0.25
    assert metrics["recall_at_5"] == 0.5
    assert metrics["recall_at_10"] == 1.0
    assert metrics["median_rank"] == 4.0


def test_index_recall_is_relative_to_exact() -> None:
    assert index_recall(["a", "b", "c"], ["b", "a", "d"], 3) == 0.6667
    with pytest.raises(ValueError):
        index_recall([], [], 0)
