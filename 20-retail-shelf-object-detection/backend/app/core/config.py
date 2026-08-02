from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def runtime_root() -> Path:
    configured = os.getenv("SHELF_CONSOLE_ROOT")
    return Path(configured).resolve() if configured else Path(__file__).parents[3]


@dataclass(frozen=True, slots=True)
class Settings:
    root: Path = runtime_root()
    maximum_upload_bytes: int = int(os.getenv("MAX_UPLOAD_BYTES", "8388608"))
    maximum_batch_size: int = int(os.getenv("MAX_BATCH_SIZE", "4"))
    allowed_origins: tuple[str, ...] = tuple(
        value.strip()
        for value in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
        if value.strip()
    )

    @property
    def bundle_path(self) -> Path:
        return self.root / "models" / "bundles" / "shelf-detector-qualification.json"


settings = Settings()
