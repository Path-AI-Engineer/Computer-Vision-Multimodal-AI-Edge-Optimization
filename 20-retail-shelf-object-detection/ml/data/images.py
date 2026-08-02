from __future__ import annotations

import io
from dataclasses import dataclass

from PIL import Image, ImageOps, UnidentifiedImageError


class ImageContractError(ValueError):
    """Raised when an uploaded shelf image is unsafe or unsupported."""


@dataclass(frozen=True, slots=True)
class DecodedImage:
    image: Image.Image
    width: int
    height: int
    image_format: str


def safe_decode(content: bytes, maximum_bytes: int = 8_388_608) -> DecodedImage:
    if not content:
        raise ImageContractError("The image payload is empty.")
    if len(content) > maximum_bytes:
        raise ImageContractError("The image exceeds the configured byte limit.")
    try:
        with Image.open(io.BytesIO(content)) as source:
            source.verify()
        with Image.open(io.BytesIO(content)) as source:
            image_format = (source.format or "").upper()
            if image_format not in {"JPEG", "PNG", "WEBP"}:
                raise ImageContractError("Only JPEG, PNG and WebP images are accepted.")
            if source.width * source.height > 30_000_000:
                raise ImageContractError("Decoded image dimensions exceed the pixel limit.")
            image = ImageOps.exif_transpose(source).convert("RGB")
            image.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as error:
        raise ImageContractError("The payload is not a safely decodable image.") from error
    return DecodedImage(image, image.width, image.height, image_format)
