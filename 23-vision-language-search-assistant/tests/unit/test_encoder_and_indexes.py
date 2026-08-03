from pathlib import Path

import numpy as np

from multimodal.data.manifest import load_manifest
from multimodal.embeddings.store import EmbeddingStore
from multimodal.encoders.qualification import QualificationDualEncoder
from multimodal.indexes.numpy_index import NumpyInnerProductIndex, QuantizedApproximateIndex

ROOT = Path(__file__).resolve().parents[2]


def test_text_encoder_is_normalized_and_reproducible() -> None:
    encoder = QualificationDualEncoder()
    first = encoder.encode_text("dog running near blue water")
    second = encoder.encode_text("dog running near blue water")
    assert np.allclose(first, second)
    assert np.isclose(np.linalg.norm(first), 1.0)
    assert first.dtype == np.float32


def test_unknown_text_produces_a_zero_vector() -> None:
    vector = QualificationDualEncoder().encode_text("quasar bureaucracy")
    assert np.count_nonzero(vector) == 0


def test_embedding_store_preserves_manifest_ids() -> None:
    items = load_manifest(ROOT / "data" / "manifests" / "qualification-corpus.json")
    store = EmbeddingStore(items, QualificationDualEncoder())
    assert store.matrix.shape == (12, 12)
    assert store.ids[0] == "vl-001"
    assert np.isclose(np.linalg.norm(store.vector_for("vl-001")), 1.0)


def test_exact_index_uses_stable_descending_scores() -> None:
    matrix = np.eye(3, dtype=np.float32)
    indexes, scores = NumpyInnerProductIndex(matrix).search(np.array([0, 1, 0]), 2)
    assert indexes.tolist() == [1, 0]
    assert scores.tolist() == [1.0, 0.0]


def test_approximate_index_has_the_same_search_contract() -> None:
    matrix = np.eye(3, dtype=np.float32)
    indexes, scores = QuantizedApproximateIndex(matrix).search(np.array([0, 0, 1]), 1)
    assert indexes.tolist() == [2]
    assert scores.shape == (1,)
