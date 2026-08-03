from __future__ import annotations

from typing import Any


def validate_pruning_report(payload: dict[str, Any]) -> dict[str, Any]:
    sparsity = float(payload.get("effective_sparsity", -1))
    if not 0 <= sparsity < 1:
        raise ValueError("Effective sparsity must be in [0, 1).")
    if "observed_speedup" not in payload:
        raise ValueError("Pruning evidence must record observed speedup separately.")
    return payload


def validate_calibration_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("source_split") != "train":
        raise ValueError("Quantization calibration must use only the train split.")
    ids = payload.get("sample_ids")
    if not isinstance(ids, list) or not ids:
        raise ValueError("Calibration manifest requires sample IDs.")
    if len(ids) != len(set(ids)):
        raise ValueError("Calibration sample IDs must be unique.")
    return payload
