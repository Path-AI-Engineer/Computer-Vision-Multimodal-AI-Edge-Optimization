from __future__ import annotations

import re
from collections.abc import Callable

from document_ai.core.contracts import FieldEvidence, FieldName, OcrToken
from document_ai.normalization.values import (
    normalize_address,
    normalize_company,
    normalize_date,
    normalize_total,
)

DATE_PATTERN = re.compile(r"\b(?:\d{4}[-/]\d{2}[-/]\d{2}|\d{2}[-/]\d{2}[-/]\d{4})\b")
MONEY_PATTERN = re.compile(r"(?:S/\.?|USD|\$)?\s*\d+[.,]\d{2}\b", re.IGNORECASE)
ADDRESS_WORDS = ("street", "st.", "avenue", "ave", "road", "rd.", "jr.", "calle", "av.")


def _evidence(
    field: FieldName,
    token: OcrToken | None,
    raw: str | None,
    normalizer: Callable[[str], str | None],
    extraction_score: float,
    reasons: tuple[str, ...],
) -> FieldEvidence:
    normalized = normalizer(raw) if raw else None
    confidence = round((token.confidence * extraction_score), 4) if token else 0.0
    reason_codes = list(reasons)
    if normalized is None:
        reason_codes.append("NORMALIZATION_FAILED" if raw else "FIELD_NOT_FOUND")
    if token and token.confidence < 0.84:
        reason_codes.append("LOW_OCR_CONFIDENCE")
    review = normalized is None or confidence < 0.82
    if review:
        reason_codes.append("REVIEW_REQUIRED")
    return FieldEvidence(
        field=field,
        raw_value=raw,
        normalized_value=normalized,
        confidence=confidence,
        review_required=review,
        reason_codes=tuple(dict.fromkeys(reason_codes)),
        token_ids=(token.token_id,) if token else (),
        boxes=(token.box,) if token else (),
    )


def _strip_label(text: str, label: str) -> str:
    return re.sub(rf"^\s*{label}\s*[:#-]?\s*", "", text, flags=re.IGNORECASE).strip()


def extract_fields(
    tokens: tuple[OcrToken, ...], width: int, height: int
) -> tuple[FieldEvidence, ...]:
    del width
    ordered = sorted(tokens, key=lambda item: (item.box[1], item.box[0]))
    top_tokens = [token for token in ordered if token.box[1] <= height * 0.25]

    company_token = next(
        (
            token
            for token in top_tokens
            if "receipt" not in token.text.lower()
            and not DATE_PATTERN.search(token.text)
            and len(re.sub(r"[^A-Za-z]", "", token.text)) >= 4
        ),
        None,
    )
    company_raw = company_token.text if company_token else None

    date_token = next((token for token in ordered if DATE_PATTERN.search(token.text)), None)
    date_raw = DATE_PATTERN.search(date_token.text).group(0) if date_token else None

    total_token = next(
        (
            token
            for token in reversed(ordered)
            if "total" in token.text.lower() and MONEY_PATTERN.search(token.text)
        ),
        None,
    )
    total_match = MONEY_PATTERN.search(total_token.text) if total_token else None
    total_raw = total_match.group(0) if total_match else None

    address_token = next(
        (
            token
            for token in top_tokens
            if any(word in token.text.lower() for word in ADDRESS_WORDS)
        ),
        None,
    )
    address_raw = _strip_label(address_token.text, "address") if address_token else None

    return (
        _evidence("company", company_token, company_raw, normalize_company, 0.96, ("TOP_REGION",)),
        _evidence("date", date_token, date_raw, normalize_date, 0.97, ("DATE_PATTERN",)),
        _evidence(
            "address",
            address_token,
            address_raw,
            normalize_address,
            0.91,
            ("ADDRESS_LEXICON",),
        ),
        _evidence(
            "total",
            total_token,
            total_raw,
            normalize_total,
            0.99,
            ("TOTAL_LABEL", "MONEY_PATTERN"),
        ),
    )
