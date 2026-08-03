from __future__ import annotations

from typing import Any


def validate_training_protocol(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("selection_split") != "validation":
        raise ValueError("Model selection must use validation only.")
    if payload.get("test_policy") != "LOCKED_UNTIL_CONFIGURATION_FREEZE":
        raise ValueError("Test policy must remain locked during tuning.")
    if int(payload.get("seed", -1)) < 0:
        raise ValueError("A non-negative reproducibility seed is required.")
    return payload
