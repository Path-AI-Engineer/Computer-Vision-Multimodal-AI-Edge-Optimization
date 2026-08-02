from __future__ import annotations

import json
import uuid

from backend.app.core.config import Settings
from ml.data.transforms import ImageContractError, safe_decode_image
from ml.inference.bundle import QualificationBundle
from ml.inference.predictor import PetBreedPredictor


class ArtifactUnavailableError(RuntimeError):
    """Raised when a verified inference artifact cannot be loaded."""


class PredictionService:
    def __init__(self, config: Settings) -> None:
        self.config = config
        self.predictor: PetBreedPredictor | None = None

    def load(self) -> None:
        if not self.config.bundle_path.is_file():
            raise ArtifactUnavailableError(
                "Qualification bundle unavailable. Run scripts/build_qualification_bundle.py."
            )
        self.predictor = PetBreedPredictor(QualificationBundle.load(self.config.bundle_path))

    @property
    def ready(self) -> bool:
        return self.predictor is not None

    def predict_content(self, content: bytes, top_k: int = 5) -> dict[str, object]:
        if self.predictor is None:
            raise ArtifactUnavailableError("The inference artifact is not loaded.")
        decoded = safe_decode_image(content, self.config.max_upload_bytes)
        result = self.predictor.predict(decoded.image, top_k=min(max(top_k, 1), 10))
        result["input"] = {
            "width": decoded.width,
            "height": decoded.height,
            "format": decoded.original_format,
            "sha256_prefix": decoded.sha256[:12],
        }
        return result

    def read_json(self, relative_path: str) -> object:
        path = self.config.root / relative_path
        if not path.is_file():
            raise ArtifactUnavailableError(f"Evidence artifact unavailable: {relative_path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def samples(self) -> list[dict[str, object]]:
        dataset = self.read_json("data/manifests/dataset_manifest.json")
        gallery = self.read_json("reports/errors/error_gallery.json")
        return [
            {
                "sample_id": item["sample_id"],
                "image_url": item["image_url"],
                "label": item["truth"],
                "scope": dataset["mode"],
            }
            for item in gallery["items"][:12]
        ]

    @staticmethod
    def batch_id() -> str:
        return str(uuid.uuid4())


__all__ = ["ArtifactUnavailableError", "ImageContractError", "PredictionService"]
