from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    root: Path
    max_upload_bytes: int


def load_settings() -> Settings:
    default_root = Path(__file__).resolve().parents[3]
    root = Path(os.getenv("EDGE_VISION_ROOT", default_root)).resolve()
    return Settings(root=root, max_upload_bytes=int(os.getenv("MAX_UPLOAD_BYTES", "6291456")))


settings = load_settings()
