from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class QualityBundle:
    root: Path
    model_id: str
    model_version: str
    checkpoint_path: Path
    checkpoint_sha256: str
    input_size: tuple[int, int]
    normalization_mean: float
    normalization_std: float
    pixel_threshold: float
    review_area_ratio: float
    reject_area_ratio: float
    minimum_component_area_px: int
    evidence_profile: str
    official_test_status: str

    @classmethod
    def load(cls, root: Path, path: Path | None = None) -> QualityBundle:
        bundle_path = path or root / "models" / "bundles" / "surface-quality-control-v1.json"
        if not bundle_path.exists():
            raise FileNotFoundError(
                "The approved surface quality-control bundle is unavailable."
            )
        payload: dict[str, Any] = json.loads(bundle_path.read_text(encoding="utf-8"))
        checkpoint_path = root / str(payload["checkpoint_path"])
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint is missing: {checkpoint_path}")
        actual_hash = hashlib.sha256(checkpoint_path.read_bytes()).hexdigest()
        if actual_hash != payload["checkpoint_sha256"]:
            raise ValueError("Checkpoint hash does not match the immutable bundle manifest.")
        return cls(
            root=root,
            model_id=str(payload["model_id"]),
            model_version=str(payload["model_version"]),
            checkpoint_path=checkpoint_path,
            checkpoint_sha256=actual_hash,
            input_size=tuple(payload["input_size"]),
            normalization_mean=float(payload["normalization"]["mean"]),
            normalization_std=float(payload["normalization"]["std"]),
            pixel_threshold=float(payload["pixel_threshold"]),
            review_area_ratio=float(payload["inspection_policy"]["review_area_ratio"]),
            reject_area_ratio=float(payload["inspection_policy"]["reject_area_ratio"]),
            minimum_component_area_px=int(
                payload["inspection_policy"]["minimum_component_area_px"]
            ),
            evidence_profile=str(payload["evidence_profile"]),
            official_test_status=str(payload["official_test_status"]),
        )

    def public_metadata(self) -> dict[str, object]:
        return {
            "model_id": self.model_id,
            "model_version": self.model_version,
            "architecture": "Small U-Net",
            "checkpoint_sha256": self.checkpoint_sha256,
            "input_size": list(self.input_size),
            "pixel_threshold": self.pixel_threshold,
            "inspection_policy": {
                "review_area_ratio": self.review_area_ratio,
                "reject_area_ratio": self.reject_area_ratio,
                "minimum_component_area_px": self.minimum_component_area_px,
            },
            "evidence_profile": self.evidence_profile,
            "official_test_status": self.official_test_status,
            "limitations": [
                "The selected checkpoint is trained on procedural qualification surfaces.",
                "KSDD2 benchmark training and the official test are not executed.",
                "Decisions are demonstration policy outputs, not industrial safety guarantees.",
            ],
        }
