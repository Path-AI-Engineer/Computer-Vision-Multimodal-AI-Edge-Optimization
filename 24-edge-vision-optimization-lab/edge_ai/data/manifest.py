from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class ManifestError(ValueError):
    """Raised when the dataset contract is inconsistent."""


def checksum_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def validate_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise ManifestError("Dataset manifest requires records.")
    ids: set[str] = set()
    by_split: dict[str, set[str]] = {"train": set(), "validation": set(), "test": set()}
    for record in records:
        sample_id = str(record.get("sample_id", ""))
        split = str(record.get("split", ""))
        if not sample_id or sample_id in ids:
            raise ManifestError("Sample IDs must be present and unique.")
        if split not in by_split:
            raise ManifestError(f"Unsupported split: {split}")
        if not record.get("checksum") or not record.get("label"):
            raise ManifestError(f"Incomplete record: {sample_id}")
        ids.add(sample_id)
        by_split[split].add(sample_id)
    if any(
        by_split[left] & by_split[right] for left in by_split for right in by_split if left < right
    ):
        raise ManifestError("Dataset splits overlap.")
    payload["summary"] = {name: len(values) for name, values in by_split.items()}
    return payload


def load_manifest(path: Path) -> dict[str, Any]:
    return validate_manifest(json.loads(path.read_text(encoding="utf-8")))
