from __future__ import annotations

import hashlib
import io
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

from ml.data.contracts import PREPROCESSING_VERSION

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_PIXELS = 20_000_000


class ImageContractError(ValueError):
    """Raised when an uploaded image violates the inference contract."""


@dataclass(frozen=True, slots=True)
class DecodedImage:
    image: Image.Image
    width: int
    height: int
    original_format: str
    sha256: str


def safe_decode_image(content: bytes, max_bytes: int = 4_194_304) -> DecodedImage:
    if not content:
        raise ImageContractError("The image payload is empty.")
    if len(content) > max_bytes:
        raise ImageContractError(f"The image exceeds the {max_bytes} byte limit.")
    try:
        with Image.open(io.BytesIO(content)) as source:
            source.verify()
        with Image.open(io.BytesIO(content)) as source:
            image_format = (source.format or "").upper()
            if image_format not in ALLOWED_FORMATS:
                raise ImageContractError("Only JPEG, PNG and WebP images are accepted.")
            if source.width * source.height > MAX_PIXELS:
                raise ImageContractError("Decoded image dimensions exceed the pixel limit.")
            normalized = ImageOps.exif_transpose(source).convert("RGB")
            normalized.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as error:
        raise ImageContractError("The payload is not a safely decodable image.") from error
    return DecodedImage(
        image=normalized,
        width=normalized.width,
        height=normalized.height,
        original_format=image_format,
        sha256=hashlib.sha256(content).hexdigest(),
    )


def inference_array(image: Image.Image, size: int = 160) -> np.ndarray:
    fitted = ImageOps.fit(image.convert("RGB"), (size, size), method=Image.Resampling.BILINEAR)
    return np.asarray(fitted, dtype=np.float32) / 255.0


def preprocessing_signature() -> dict[str, object]:
    return {
        "version": PREPROCESSING_VERSION,
        "color_mode": "RGB",
        "resize": "aspect-preserving fit",
        "size": [160, 160],
        "exif_orientation": "normalized",
        "train_augmentations": ["horizontal_flip", "brightness", "crop_jitter"],
        "inference_augmentations": [],
    }
