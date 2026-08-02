from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal, InvalidOperation


def normalize_company(value: str) -> str:
    return " ".join(value.strip().split()).title()


def normalize_address(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", value.strip(" ,.-"))
    return cleaned.title()


def normalize_date(value: str) -> str | None:
    candidate = re.sub(r"[^0-9/.-]", "", value)
    for pattern in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(candidate, pattern).date().isoformat()
        except ValueError:
            continue
    return None


def normalize_total(value: str) -> str | None:
    numeric_parts = re.findall(r"\d[\d,.]*", value)
    if not numeric_parts:
        return None
    candidate = numeric_parts[-1]
    if candidate.count(",") == 1 and "." not in candidate:
        candidate = candidate.replace(",", ".")
    else:
        candidate = candidate.replace(",", "")
    try:
        amount = Decimal(candidate)
    except InvalidOperation:
        return None
    if amount < 0:
        return None
    return f"{amount:.2f}"
