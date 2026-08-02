from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app

ROOT = Path(__file__).parents[2]


def test_health_readiness_and_contract() -> None:
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"
        assert client.get("/ready").status_code == 200
        classes = client.get("/v1/classes").json()
        assert classes["count"] == 37
        assert len(classes["items"]) == 37
        openapi = client.get("/openapi.json")
        assert openapi.status_code == 200
        prediction_operation = openapi.json()["paths"]["/v1/predictions"]["post"]
        assert "multipart/form-data" in prediction_operation["requestBody"]["content"]


def test_real_artifact_prediction_has_traceability() -> None:
    sample = next((ROOT / "data" / "samples").glob("*.png"))
    with TestClient(app) as client, sample.open("rb") as stream:
        response = client.post(
            "/v1/predictions?top_k=5",
            files={"image": (sample.name, stream, "image/png")},
        )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["top_k"]) == 5
    assert payload["model_version"] == "hog-linear-qualification-v1.0.0"
    assert payload["preprocessing_version"] == "rgb-hog-160-v1"
    assert payload["input"]["format"] == "PNG"
    assert payload["warnings"]


def test_invalid_upload_returns_422_without_inference() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/v1/predictions",
            files={"image": ("broken.png", b"broken", "image/png")},
        )
    assert response.status_code == 422
    assert "safely decodable" in response.json()["detail"]


def test_evidence_surfaces_preserve_scope_and_lock() -> None:
    with TestClient(app) as client:
        summary = client.get("/v1/evaluation/summary").json()
        status = client.get("/v1/evaluation/test-status").json()
        models = client.get("/v1/evaluation/models").json()
    assert summary["evaluation_scope"] == "procedural_qualification_validation"
    assert status["status"] == "LOCKED_NOT_ACQUIRED"
    assert models["selected_model"] == "hog-linear-qualification"
    assert any(model["status"] != "executed" for model in models["models"])


def test_batch_limit_is_enforced() -> None:
    uploads = [("images", (f"sample-{index}.png", b"x", "image/png")) for index in range(9)]
    with TestClient(app) as client:
        response = client.post("/v1/predictions/batch", files=uploads)
    assert response.status_code == 422
    assert "between 1 and 8" in response.json()["detail"]
