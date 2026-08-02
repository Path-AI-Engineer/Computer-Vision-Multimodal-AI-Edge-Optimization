from document_ai.core.contracts import OcrToken
from document_ai.extraction.layout import extract_fields


def test_layout_extractor_keeps_spatial_evidence() -> None:
    tokens = (
        OcrToken("a", "LIMA MARKET", 0.98, (10, 10, 200, 40), 0),
        OcrToken("b", "Address: Av. Arequipa 1420", 0.95, (10, 60, 300, 90), 1),
        OcrToken("c", "Date: 2026-07-18", 0.96, (10, 110, 220, 140), 2),
        OcrToken("d", "TOTAL $ 54.80", 0.97, (250, 600, 400, 640), 3),
    )
    fields = {field.field: field for field in extract_fields(tokens, 720, 960)}
    assert fields["company"].normalized_value == "Lima Market"
    assert fields["total"].normalized_value == "54.80"
    assert fields["total"].token_ids == ("d",)
    assert fields["total"].boxes == ((250, 600, 400, 640),)


def test_low_ocr_confidence_routes_field_to_review() -> None:
    tokens = (
        OcrToken("a", "LIMA MARKET", 0.98, (10, 10, 200, 40), 0),
        OcrToken("b", "Address: Av. Arequipa 1420", 0.60, (10, 60, 300, 90), 1),
        OcrToken("c", "Date: 2026-07-18", 0.96, (10, 110, 220, 140), 2),
        OcrToken("d", "TOTAL $ 54.80", 0.97, (250, 600, 400, 640), 3),
    )
    address = {field.field: field for field in extract_fields(tokens, 720, 960)}["address"]
    assert address.review_required is True
    assert "LOW_OCR_CONFIDENCE" in address.reason_codes
