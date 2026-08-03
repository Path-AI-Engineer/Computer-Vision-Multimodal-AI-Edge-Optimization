from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_and_readiness() -> None:
    assert client.get("/health").json()["status"] == "ok"
    readiness = client.get("/ready")
    assert readiness.status_code == 200
    assert readiness.json()["approved_variants"] == 4


def test_variant_registry_endpoint() -> None:
    response = client.get("/v1/variants")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 6


def test_prediction_endpoint() -> None:
    response = client.post(
        "/v1/predictions?variant_id=onnx-fp32", json={"sample_id": "edge-001", "top_k": 3}
    )
    assert response.status_code == 200
    assert response.json()["predictions"][0]["label"] == "abyssinian"


def test_prediction_rejects_not_run_variant() -> None:
    response = client.post("/v1/predictions?variant_id=qat-int8", json={"sample_id": "edge-001"})
    assert response.status_code == 422


def test_evidence_endpoints_share_status() -> None:
    for path in (
        "/v1/benchmarks/summary",
        "/v1/benchmarks/pareto",
        "/v1/parity/summary",
        "/v1/pruning/summary",
    ):
        response = client.get(path)
        assert response.status_code == 200
        assert response.json()["status"] == "QUALIFICATION_ONLY"


def test_unknown_variant_returns_structured_error() -> None:
    response = client.get("/v1/variants/unknown")
    assert response.status_code == 404
    assert response.json()["code"] == "VARIANT_NOT_FOUND"
