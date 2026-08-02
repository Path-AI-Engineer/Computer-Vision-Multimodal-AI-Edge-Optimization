from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_runtime_and_bundle_are_ready() -> None:
    assert client.get("/health").json()["status"] == "healthy"
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["bundle"] == "document-extractor-v1"


def test_sealed_sample_extraction_and_lookup() -> None:
    response = client.post(
        "/v1/documents/extract",
        json={"sample_id": "receipt-lima-market", "preprocessing_profile": "deskew-clahe-v1"},
    )
    assert response.status_code == 200
    extraction = response.json()
    assert len(extraction["fields"]) == 4
    assert extraction["source_kind"] == "sealed-qualification-sample"
    lookup = client.get(f"/v1/extractions/{extraction['request_id']}")
    assert lookup.status_code == 200
    assert lookup.json()["request_id"] == extraction["request_id"]


def test_export_separates_operator_edits_from_predictions() -> None:
    extraction = client.post(
        "/v1/documents/extract",
        json={"sample_id": "receipt-lima-market", "preprocessing_profile": "original-v1"},
    ).json()
    response = client.post(
        f"/v1/extractions/{extraction['request_id']}/export",
        json={"format": "json", "edits": [{"field": "company", "value": "Lima Market SAC"}]},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["predictions"]["company"] == "Lima Market"
    assert payload["operator_edits"]["company"] == "Lima Market SAC"
    assert payload["edits_are_predictions"] is False


def test_upload_without_optional_ocr_fails_explicitly() -> None:
    response = client.post(
        "/v1/documents/extract",
        content=b"not-an-image",
        headers={
            "content-type": "image/png",
            "x-document-name": "receipt.png",
            "x-preprocessing-profile": "original-v1",
        },
    )
    assert response.status_code == 422


def test_evaluation_contract_exposes_oracle_and_end_to_end() -> None:
    response = client.get("/v1/evaluation/summary")
    assert response.status_code == 200
    payload = response.json()
    assert payload["documents"] == 4
    assert "oracle_ocr" in payload
    assert "end_to_end" in payload
