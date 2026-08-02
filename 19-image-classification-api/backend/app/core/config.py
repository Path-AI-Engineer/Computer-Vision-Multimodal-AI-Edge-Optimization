from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def runtime_root() -> Path:
    configured = os.getenv("PET_STUDIO_ROOT")
    return Path(configured).resolve() if configured else Path(__file__).parents[3]


@dataclass(frozen=True, slots=True)
class Settings:
    root: Path = runtime_root()
    max_upload_bytes: int = int(os.getenv("MAX_UPLOAD_BYTES", "4194304"))
    max_batch_size: int = int(os.getenv("MAX_BATCH_SIZE", "8"))
    allowed_origins: tuple[str, ...] = tuple(
        item.strip()
        for item in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
        if item.strip()
    )

    @property
    def bundle_path(self) -> Path:
        return self.root / "models" / "bundles" / "pet-breed-qualification.joblib"


settings = Settings()
