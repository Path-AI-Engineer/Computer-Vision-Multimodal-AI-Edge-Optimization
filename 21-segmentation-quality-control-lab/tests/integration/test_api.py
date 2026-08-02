from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

pytest.importorskip("multipart", reason="python-multipart is required for HTTP form tests")

from backend.app.main import app


def test_system_and_evidence_routes() -> None:
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "healthy"
        ready = client.get("/ready")
        assert ready.status_code == 200
        assert (
            client.get("/v1/models/current").json()["official_test_status"]
            == "LOCKED_NOT_ACQUIRED"
        )
        assert len(client.get("/v1/samples").json()) == 8
        assert client.get("/v1/evaluation/summary").json()["images"] == 12
        assert len(client.get("/v1/evaluation/thresholds").json()) > 1


def test_sample_inspection_and_threshold_are_real() -> None:
    with TestClient(app) as client:
        sample_id = client.get("/v1/samples").json()[0]["sample_id"]
        low = client.post(
            "/v1/inspections",
            data={"sample_id": sample_id, "pixel_threshold": "0.2"},
        )
        high = client.post(
            "/v1/segmentations",
            data={"sample_id": sample_id, "pixel_threshold": "0.9"},
        )
        assert low.status_code == high.status_code == 200
        assert low.json()["pixel_threshold"] == 0.2
        assert high.json()["pixel_threshold"] == 0.9
        assert low.json()["defect_area_px"] >= high.json()["defect_area_px"]
        assert low.json()["mask_probability_uri"].startswith("data:image/png;base64,")


def test_source_contract_and_upload_validation() -> None:
    with TestClient(app) as client:
        missing = client.post("/v1/inspections")
        invalid = client.post(
            "/v1/inspections",
            files={"image": ("payload.txt", b"not an image", "text/plain")},
        )
        assert missing.status_code == 422
        assert invalid.status_code == 422
