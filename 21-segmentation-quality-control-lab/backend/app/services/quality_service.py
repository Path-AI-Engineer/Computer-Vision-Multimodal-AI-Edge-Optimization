from __future__ import annotations

import io
import json
from typing import Any

import numpy as np
from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

from backend.app.core.config import Settings
from ml.data.contracts import load_grayscale
from ml.data.fixture import read_manifest
from ml.inference.bundle import QualityBundle
from ml.inference.predictor import SegmentationPredictor


class ImageValidationError(ValueError):
    """Raised for safe, user-visible image validation failures."""


class QualityControlService:
    allowed_content_types = {"image/png", "image/jpeg", "image/webp"}

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.bundle = QualityBundle.load(settings.root)
        self.predictor = SegmentationPredictor(self.bundle)
        self.records = read_manifest(settings.root)

    def model_metadata(self) -> dict[str, object]:
        payload = self.bundle.public_metadata()
        training_path = (
            self.settings.root
            / "reports"
            / "runs"
            / "p21-qualification-v1"
            / "training_summary.json"
        )
        payload["training"] = json.loads(training_path.read_text(encoding="utf-8"))
        return payload

    def samples(self) -> list[dict[str, object]]:
        return [
            {
                "sample_id": record["sample_id"],
                "image_url": f"/evidence/{record['image_path']}",
                "ground_truth_mask_url": f"/evidence/{record['mask_path']}",
                "defective": record["defective"],
                "defect_area_px": record["defect_area_px"],
                "defect_area_ratio": record["defect_area_ratio"],
            }
            for record in self.records
            if record["split"] == "showcase"
        ]

    def report(self, relative_path: str) -> Any:
        path = self.settings.root / relative_path
        if not path.exists():
            raise FileNotFoundError(f"Evidence report is unavailable: {relative_path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def _sample_image(self, sample_id: str) -> np.ndarray:
        record = next(
            (record for record in self.records if record["sample_id"] == sample_id),
            None,
        )
        if record is None or record["split"] != "showcase":
            raise ImageValidationError("Unknown showcase sample_id.")
        return load_grayscale(self.settings.root / str(record["image_path"]))

    async def _upload_image(self, upload: UploadFile) -> np.ndarray:
        if upload.content_type not in self.allowed_content_types:
            raise ImageValidationError("Upload a PNG, JPEG or WebP image.")
        payload = await upload.read(self.settings.max_upload_bytes + 1)
        if len(payload) > self.settings.max_upload_bytes:
            raise ImageValidationError(
                f"Image exceeds the {self.settings.max_upload_bytes} byte upload limit."
            )
        if not payload:
            raise ImageValidationError("Uploaded image is empty.")
        try:
            with Image.open(io.BytesIO(payload)) as image:
                image.load()
                if image.width * image.height > self.settings.max_image_pixels:
                    raise ImageValidationError(
                        f"Image exceeds the {self.settings.max_image_pixels} pixel limit."
                    )
                return np.asarray(image.convert("L"), dtype=np.uint8)
        except (UnidentifiedImageError, OSError) as error:
            raise ImageValidationError("Image bytes could not be decoded safely.") from error

    async def resolve_image(
        self,
        *,
        sample_id: str | None,
        upload: UploadFile | None,
    ) -> np.ndarray:
        if bool(sample_id) == bool(upload):
            raise ImageValidationError("Provide exactly one sample_id or image upload.")
        if sample_id:
            return self._sample_image(sample_id)
        if upload is None:
            raise ImageValidationError("An image source is required.")
        return await self._upload_image(upload)

    async def inspect(
        self,
        *,
        sample_id: str | None,
        upload: UploadFile | None,
        pixel_threshold: float | None,
    ) -> dict[str, object]:
        image = await self.resolve_image(sample_id=sample_id, upload=upload)
        return self.predictor.inspect(image, pixel_threshold=pixel_threshold)
