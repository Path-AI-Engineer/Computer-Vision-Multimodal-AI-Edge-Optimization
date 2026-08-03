from __future__ import annotations

import pytest

from edge_ai.data.manifest import ManifestError, checksum_bytes, validate_manifest
from edge_ai.optimization.contracts import validate_calibration_manifest, validate_pruning_report
from edge_ai.quantization.calibration import calibration_ids
from edge_ai.training.protocol import validate_training_protocol


def record(sample_id: str, split: str = "train") -> dict[str, str]:
    return {"sample_id": sample_id, "split": split, "label": "cat", "checksum": "abc"}


def test_dataset_manifest_builds_split_summary() -> None:
    payload = validate_manifest(
        {"records": [record("a"), record("b", "validation"), record("c", "test")]}
    )
    assert payload["summary"] == {"train": 1, "validation": 1, "test": 1}


def test_dataset_manifest_rejects_duplicates() -> None:
    with pytest.raises(ManifestError, match="unique"):
        validate_manifest({"records": [record("a"), record("a", "test")]})


def test_checksum_is_stable() -> None:
    assert checksum_bytes(b"edge") == checksum_bytes(b"edge")


def test_calibration_uses_train_only() -> None:
    assert calibration_ids([record("a"), record("b", "test")], limit=4) == ["a"]


def test_calibration_manifest_rejects_test_source() -> None:
    with pytest.raises(ValueError, match="train"):
        validate_calibration_manifest({"source_split": "test", "sample_ids": ["x"]})


def test_pruning_requires_observed_speedup() -> None:
    with pytest.raises(ValueError, match="speedup"):
        validate_pruning_report({"effective_sparsity": 0.5})


def test_training_protocol_locks_test() -> None:
    payload = {
        "selection_split": "validation",
        "test_policy": "LOCKED_UNTIL_CONFIGURATION_FREEZE",
        "seed": 24,
    }
    assert validate_training_protocol(payload)["seed"] == 24


def test_training_protocol_rejects_test_selection() -> None:
    with pytest.raises(ValueError, match="validation"):
        validate_training_protocol(
            {
                "selection_split": "test",
                "test_policy": "LOCKED_UNTIL_CONFIGURATION_FREEZE",
                "seed": 24,
            }
        )
