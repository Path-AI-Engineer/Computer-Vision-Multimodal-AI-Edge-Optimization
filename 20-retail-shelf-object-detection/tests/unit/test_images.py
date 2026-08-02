import io

import pytest
from PIL import Image

from ml.data.images import ImageContractError, safe_decode


def encoded_image(image_format: str = "PNG") -> bytes:
    stream = io.BytesIO()
    Image.new("RGB", (24, 16), (12, 34, 56)).save(stream, format=image_format)
    return stream.getvalue()


def test_safe_decode_normalizes_supported_image() -> None:
    decoded = safe_decode(encoded_image())
    assert (decoded.width, decoded.height, decoded.image.mode) == (24, 16, "RGB")
    assert decoded.image_format == "PNG"


@pytest.mark.parametrize("payload", [b"", b"not-an-image"])
def test_safe_decode_rejects_invalid_payload(payload: bytes) -> None:
    with pytest.raises(ImageContractError):
        safe_decode(payload)


def test_safe_decode_enforces_byte_limit() -> None:
    with pytest.raises(ImageContractError, match="byte limit"):
        safe_decode(encoded_image(), maximum_bytes=10)
