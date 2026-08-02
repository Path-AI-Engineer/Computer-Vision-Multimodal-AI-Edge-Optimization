from document_ai.normalization.values import (
    normalize_address,
    normalize_company,
    normalize_date,
    normalize_total,
)


def test_normalizes_supported_dates() -> None:
    assert normalize_date("Date: 21/07/2026") == "2026-07-21"
    assert normalize_date("2026-07-23") == "2026-07-23"


def test_rejects_invalid_date() -> None:
    assert normalize_date("not-a-date") is None


def test_normalizes_currency_without_hiding_raw_value() -> None:
    assert normalize_total("S/. 54.80") == "54.80"
    assert normalize_total("USD 42,35") == "42.35"


def test_normalizes_text_spacing() -> None:
    assert normalize_company("  LIMA   MARKET ") == "Lima Market"
    assert normalize_address("  av.   arequipa 1420, lima ") == "Av. Arequipa 1420, Lima"
