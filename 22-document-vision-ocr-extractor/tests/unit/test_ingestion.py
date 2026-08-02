from io import BytesIO

import pytest
from PIL import Image

from document_ai.ingestion.validator import DocumentValidationError, validate_upload


def _png() -> bytes:
    stream = BytesIO()
    Image.new("RGB", (20, 10), "white").save(stream, format="PNG")
    return stream.getvalue()


def test_validates_png_dimensions() -> None:
    assert validate_upload(_png(), "receipt.png", "image/png", 100_000) == ("receipt.png", 20, 10)


def test_rejects_content_type_outside_contract() -> None:
    with pytest.raises(DocumentValidationError, match="Only JPEG"):
        validate_upload(b"text", "receipt.txt", "text/plain", 100_000)
