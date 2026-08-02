from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app

ROOT = Path(__file__).parents[2]
SAMPLE = ROOT / "data" / "samples" / "qualification-shelf-000.png"


def test_health_readiness_and_evidence_routes() -> None:
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"
        assert client.get("/ready").json()["status"] == "ready"
        assert client.get("/v1/evaluation/summary").json()["profile"] == "qualification_smoke"
        assert (
            client.get("/v1/evaluation/models").json()["models"][2]["status"]
            == "protocol_ready_not_executed"
        )


def test_real_multipart_detection_returns_visible_boxes() -> None:
    with TestClient(app) as client, SAMPLE.open("rb") as image:
        response = client.post(
            "/v1/detections?confidence=0.35&nms_iou=0.45",
            files={"image": (SAMPLE.name, image, "image/png")},
        )
    assert response.status_code == 200
    payload = response.json()
    assert payload["visible_count"] == 30
    assert len(payload["detections"]) == 30
    assert payload["thresholds"] == {"confidence": 0.35, "nms_iou": 0.45}
    assert "not trained on SKU-110K" in payload["warnings"][0]


def test_batch_detection_is_bounded_and_real() -> None:
    image = SAMPLE.read_bytes()
    with TestClient(app) as client:
        response = client.post(
            "/v1/detections/batch",
            files=[
                ("image", ("one.png", image, "image/png")),
                ("image", ("two.png", image, "image/png")),
            ],
        )
    assert response.status_code == 200
    assert response.json()["count"] == 2


def test_invalid_upload_and_query_are_rejected() -> None:
    with TestClient(app) as client:
        invalid = client.post(
            "/v1/detections", files={"image": ("bad.txt", b"bad", "text/plain")}
        )
        invalid_threshold = client.post(
            "/v1/detections?confidence=2",
            files={"image": (SAMPLE.name, SAMPLE.read_bytes(), "image/png")},
        )
    assert invalid.status_code == 422
    assert invalid_threshold.status_code == 422
