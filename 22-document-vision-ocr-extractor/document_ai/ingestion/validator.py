from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError


class DocumentValidationError(ValueError):
    """Raised before untrusted document bytes reach the OCR adapter."""


ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "application/pdf"}
MAX_PIXELS = 8_000_000


def validate_upload(
    payload: bytes,
    filename: str,
    content_type: str | None,
    max_bytes: int,
) -> tuple[str, int | None, int | None]:
    if not payload:
        raise DocumentValidationError("The uploaded document is empty.")
    if len(payload) > max_bytes:
        raise DocumentValidationError(f"The document exceeds the {max_bytes} byte limit.")
    safe_name = Path(filename or "document").name
    normalized_type = (content_type or "").lower()
    if normalized_type not in ALLOWED_CONTENT_TYPES:
        raise DocumentValidationError("Only JPEG, PNG and single-page PDF files are accepted.")

    if normalized_type == "application/pdf":
        if not payload.startswith(b"%PDF-"):
            raise DocumentValidationError("The uploaded PDF signature is invalid.")
        page_markers = payload.count(b"/Type /Page") - payload.count(b"/Type /Pages")
        if page_markers > 1:
            raise DocumentValidationError("Only single-page PDF documents are supported.")
        return safe_name, None, None

    try:
        with Image.open(BytesIO(payload)) as image:
            image.verify()
        with Image.open(BytesIO(payload)) as image:
            width, height = image.size
    except (UnidentifiedImageError, OSError) as error:
        raise DocumentValidationError("The uploaded image cannot be decoded safely.") from error
    if width * height > MAX_PIXELS:
        raise DocumentValidationError(f"Image dimensions exceed the {MAX_PIXELS} pixel limit.")
    return safe_name, width, height
