from __future__ import annotations

import json
import uuid

from backend.app.core.config import Settings
from ml.data.images import ImageContractError, safe_decode
from ml.inference.bundle import load_bundle
from ml.inference.predictor import ShelfPredictor


class ArtifactUnavailableError(RuntimeError):
    """Raised when the immutable detector bundle cannot be loaded."""


class DetectionService:
    def __init__(self, config: Settings) -> None:
        self.config = config
        self.bundle: dict[str, object] | None = None
        self.predictor: ShelfPredictor | None = None

    def load(self) -> None:
        if not self.config.bundle_path.is_file():
            raise ArtifactUnavailableError(
                "Detector bundle unavailable. Run scripts/build_qualification_bundle.py."
            )
        self.bundle, detector_config = load_bundle(self.config.bundle_path)
        self.predictor = ShelfPredictor(detector_config)

    @property
    def ready(self) -> bool:
        return self.predictor is not None

    def detect(self, content: bytes, confidence: float, nms_iou: float) -> dict[str, object]:
        if self.predictor is None:
            raise ArtifactUnavailableError("The detector bundle is not loaded.")
        decoded = safe_decode(content, self.config.maximum_upload_bytes)
        return self.predictor.predict(
            decoded.image,
            confidence=confidence,
            nms_iou=nms_iou,
        )

    def json_artifact(self, relative: str) -> object:
        path = self.config.root / relative
        if not path.is_file():
            raise ArtifactUnavailableError(f"Evidence artifact unavailable: {relative}")
        return json.loads(path.read_text(encoding="utf-8"))

    def samples(self) -> list[dict[str, object]]:
        gallery = self.json_artifact("reports/errors/error_gallery.json")
        return [
            {
                "image_id": item["image_id"],
                "image_url": item["image_url"],
                "overlay_url": item["overlay_url"],
                "density": item["density"],
                "truth_count": item["truth_count"],
            }
            for item in gallery["items"]
        ]

    @staticmethod
    def batch_id() -> str:
        return str(uuid.uuid4())


__all__ = ["ArtifactUnavailableError", "DetectionService", "ImageContractError"]
