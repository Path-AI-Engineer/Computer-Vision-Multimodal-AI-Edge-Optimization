from __future__ import annotations

from pathlib import Path

from ml.inference.bundle import QualityBundle

ROOT = Path(__file__).resolve().parents[2]


def test_bundle_is_hash_verified_and_has_separate_thresholds() -> None:
    bundle = QualityBundle.load(ROOT)
    assert bundle.model_version == "small-unet-qualification-v1"
    assert bundle.official_test_status == "LOCKED_NOT_ACQUIRED"
    assert bundle.pixel_threshold != bundle.review_area_ratio
    assert len(bundle.checkpoint_sha256) == 64
