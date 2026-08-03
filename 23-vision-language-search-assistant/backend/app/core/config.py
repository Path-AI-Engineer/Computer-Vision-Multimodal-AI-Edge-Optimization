from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def runtime_root() -> Path:
    configured = os.getenv("VISION_LANGUAGE_ROOT")
    return Path(configured).resolve() if configured else Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Settings:
    root: Path = runtime_root()
    session_ttl_seconds: int = int(os.getenv("SESSION_TTL_SECONDS", "3600"))
    max_upload_bytes: int = int(os.getenv("MAX_UPLOAD_BYTES", "6291456"))


settings = Settings()
