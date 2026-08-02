from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from ml.models.qualification_detector import ComponentDetectorConfig


def save_bundle(config: ComponentDetectorConfig, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "artifact_version": "shelf-detection-qualification-v1",
        "profile": "qualification_smoke",
        "class_id": 0,
        "class_name": "object",
        "preprocessing_version": "rgb-native-component-v1",
        "test_status": "LOCKED_NOT_ACQUIRED",
        "config": asdict(config),
    }
    destination.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def load_bundle(source: Path) -> tuple[dict[str, object], ComponentDetectorConfig]:
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("artifact_version") != "shelf-detection-qualification-v1":
        raise ValueError("Unsupported detector artifact version.")
    return payload, ComponentDetectorConfig(**payload["config"])
