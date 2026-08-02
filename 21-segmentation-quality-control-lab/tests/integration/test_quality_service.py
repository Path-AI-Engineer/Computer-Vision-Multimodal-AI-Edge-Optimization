from __future__ import annotations

import asyncio
from dataclasses import replace
from pathlib import Path

from backend.app.core.config import get_settings
from backend.app.services.quality_service import QualityControlService

ROOT = Path(__file__).resolve().parents[2]


def test_service_loads_bundle_reports_and_runs_real_inference() -> None:
    service = QualityControlService(replace(get_settings(), root=ROOT))
    samples = service.samples()
    assert len(samples) == 8
    assert service.model_metadata()["official_test_status"] == "LOCKED_NOT_ACQUIRED"
    result = asyncio.run(
        service.inspect(
            sample_id=str(samples[0]["sample_id"]),
            upload=None,
            pixel_threshold=0.8,
        )
    )
    assert result["model_version"] == "small-unet-qualification-v1"
    assert result["decision"] in {"ACCEPT", "REVIEW", "REJECT"}
    assert result["binary_mask_uri"].startswith("data:image/png;base64,")
