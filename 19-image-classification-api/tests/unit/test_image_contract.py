from __future__ import annotations

import io

import pytest
from PIL import Image

from ml.data.transforms import ImageContractError, safe_decode_image


def image_bytes(mode: str = "RGB", image_format: str = "PNG") -> bytes:
    stream = io.BytesIO()
    Image.new(mode, (32, 24), color=(20, 180, 130)).save(stream, format=image_format)
    return stream.getvalue()


def test_safe_decode_normalizes_rgb_and_hashes_input() -> None:
    decoded = safe_decode_image(image_bytes())
    assert decoded.image.mode == "RGB"
    assert (decoded.width, decoded.height) == (32, 24)
    assert decoded.original_format == "PNG"
    assert len(decoded.sha256) == 64


@pytest.mark.parametrize("payload", [b"", b"not-an-image"])
def test_safe_decode_rejects_invalid_payload(payload: bytes) -> None:
    with pytest.raises(ImageContractError):
        safe_decode_image(payload)


def test_safe_decode_enforces_byte_limit() -> None:
    with pytest.raises(ImageContractError, match="byte limit"):
        safe_decode_image(image_bytes(), max_bytes=10)
