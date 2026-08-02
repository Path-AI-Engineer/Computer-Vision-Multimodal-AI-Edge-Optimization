from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class BundleValidationError(RuntimeError):
    """Raised when versioned runtime evidence is incomplete or changed."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65_536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_bundle(root: Path) -> dict[str, Any]:
    path = root / "models" / "bundles" / "document-extractor-v1.json"
    if not path.exists():
        raise BundleValidationError("The approved document extraction bundle is missing.")
    payload = json.loads(path.read_text(encoding="utf-8"))
    for relative, expected in payload.get("artifacts", {}).items():
        artifact = root / relative
        if not artifact.exists():
            raise BundleValidationError(f"Bundle artifact is missing: {relative}")
        if sha256_file(artifact) != expected:
            raise BundleValidationError(f"Bundle artifact hash mismatch: {relative}")
    return payload
