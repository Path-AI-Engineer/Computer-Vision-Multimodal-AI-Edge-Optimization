from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_runtime_and_bundle_readiness() -> None:
    assert client.get("/health").json()["status"] == "healthy"
    ready = client.get("/ready")
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"
    assert ready.json()["corpus_images"] == 12


def test_text_and_image_search_contracts() -> None:
    text = client.post(
        "/v1/search/text",
        json={"query": "dog running on beach", "mode": "hybrid", "index_mode": "exact"},
    )
    assert text.status_code == 200
    assert text.json()["results"][0]["image_id"] == "vl-001"
    assert text.json()["results"][0]["evidence_captions"]
    image = client.post(
        "/v1/search/image", json={"image_id": "vl-005", "index_mode": "exact", "top_k": 6}
    )
    assert image.status_code == 200
    assert image.json()["results"][0]["image_id"] == "vl-005"


def test_upload_validation_is_bounded_and_explicit() -> None:
    unsupported = client.post(
        "/v1/search/image-upload", content=b"not an image", headers={"content-type": "text/plain"}
    )
    assert unsupported.status_code == 415
    invalid = client.post(
        "/v1/search/image-upload", content=b"not an image", headers={"content-type": "image/png"}
    )
    assert invalid.status_code == 422


def test_session_flow_and_deletion() -> None:
    created = client.post(
        "/v1/sessions", json={"top_k": 6, "mode": "hybrid", "index_mode": "exact"}
    )
    assert created.status_code == 201
    session_id = created.json()["state"]["session_id"]
    reply = client.post(f"/v1/sessions/{session_id}/messages", json={"message": "people in a city"})
    assert reply.status_code == 200
    assert reply.json()["search"]["citations"]
    assert client.delete(f"/v1/sessions/{session_id}").status_code == 204
    assert (
        client.post(f"/v1/sessions/{session_id}/messages", json={"message": "explain"}).status_code
        == 404
    )


def test_guardrail_error_has_a_reason_code() -> None:
    response = client.post(
        "/v1/search/text",
        json={"query": "identify this person", "mode": "hybrid", "index_mode": "exact"},
    )
    assert response.status_code == 422
    assert response.json()["reason_code"] == "SENSITIVE_INFERENCE_BLOCKED"


def test_evaluation_and_compatibility_artifacts_are_served() -> None:
    metrics = client.get("/v1/evaluation/summary").json()
    assert metrics["status"] == "QUALIFICATION_ONLY"
    assert metrics["methods"]["hybrid"]["recall_at_1"] == 1
    model = client.get("/v1/models/current").json()
    index = client.get("/v1/indexes/current").json()
    assert model["model_version"] == index["model_version"]
    assert index["dimension"] == 12
