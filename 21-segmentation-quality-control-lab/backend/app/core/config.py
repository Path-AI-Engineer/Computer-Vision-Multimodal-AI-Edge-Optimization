from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    root: Path
    max_upload_bytes: int
    max_image_pixels: int
    max_batch_size: int


def get_settings() -> Settings:
    default_root = Path(__file__).resolve().parents[3]
    root = Path(os.getenv("QUALITY_CONTROL_ROOT", str(default_root))).resolve()
    return Settings(
        root=root,
        max_upload_bytes=int(os.getenv("MAX_UPLOAD_BYTES", str(6 * 1024 * 1024))),
        max_image_pixels=int(os.getenv("MAX_IMAGE_PIXELS", str(4_000_000))),
        max_batch_size=int(os.getenv("MAX_BATCH_SIZE", "8")),
    )
