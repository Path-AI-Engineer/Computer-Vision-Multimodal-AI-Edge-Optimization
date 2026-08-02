from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    root: Path
    max_upload_bytes: int
    extraction_ttl_seconds: int


def load_settings() -> Settings:
    default_root = Path(__file__).resolve().parents[3]
    root = Path(os.getenv("DOCUMENT_VISION_ROOT", str(default_root))).resolve()
    return Settings(
        root=root,
        max_upload_bytes=int(os.getenv("MAX_UPLOAD_BYTES", "8388608")),
        extraction_ttl_seconds=int(os.getenv("EXTRACTION_TTL_SECONDS", "3600")),
    )


settings = load_settings()
