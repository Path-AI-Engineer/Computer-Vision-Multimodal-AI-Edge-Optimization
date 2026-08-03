from __future__ import annotations

from collections.abc import Iterable


def calibration_ids(records: Iterable[dict[str, str]], *, limit: int) -> list[str]:
    if limit < 1:
        raise ValueError("Calibration limit must be positive.")
    ids = [record["sample_id"] for record in records if record.get("split") == "train"]
    if not ids:
        raise ValueError("No train samples are available for calibration.")
    return ids[:limit]
