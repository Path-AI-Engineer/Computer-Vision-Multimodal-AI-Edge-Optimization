from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from edge_ai.export.parity import parity_report
from edge_ai.inference.predictor import QualificationPredictor
from edge_ai.registry.service import RegistryError, VariantRegistry

ROOT = Path(__file__).resolve().parents[2]


def test_parity_passes_equal_logits() -> None:
    logits = np.asarray([[1.0, 0.0]])
    assert (
        parity_report(logits, logits.copy(), atol=0.001, reference_id="a", candidate_id="b")[
            "passed"
        ]
        is True
    )


def test_parity_rejects_shape_mismatch() -> None:
    with pytest.raises(ValueError, match="shape"):
        parity_report(np.ones((1, 2)), np.ones((2, 2)), atol=1, reference_id="a", candidate_id="b")


def test_registry_lists_all_versioned_variants() -> None:
    registry = VariantRegistry(ROOT / "artifacts/bundles/variant-registry.json")
    assert len(registry.list()) == 6
    assert len(registry.approved()) == 4


def test_registry_rejects_unknown_variant() -> None:
    registry = VariantRegistry(ROOT / "artifacts/bundles/variant-registry.json")
    with pytest.raises(RegistryError, match="Unknown"):
        registry.get("missing")


def test_predictor_returns_ranked_probabilities() -> None:
    registry = VariantRegistry(ROOT / "artifacts/bundles/variant-registry.json")
    result = QualificationPredictor(ROOT, registry).predict("pytorch-fp32", "edge-001")
    assert result.predictions[0]["label"] == "abyssinian"
    assert sum(float(item["probability"]) for item in result.predictions) <= 1.001


def test_predictor_rejects_not_run_variant() -> None:
    registry = VariantRegistry(ROOT / "artifacts/bundles/variant-registry.json")
    with pytest.raises(ValueError, match="not approved"):
        QualificationPredictor(ROOT, registry).predict("qat-int8", "edge-001")


def test_predictor_rejects_unknown_sample() -> None:
    registry = VariantRegistry(ROOT / "artifacts/bundles/variant-registry.json")
    with pytest.raises(ValueError, match="Unknown qualification sample"):
        QualificationPredictor(ROOT, registry).predict("pytorch-fp32", "missing")
