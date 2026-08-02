import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app

ROOT = Path(__file__).parents[2]


def read_json(relative: str) -> object:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_bundle_manifest_hash_matches_immutable_artifact() -> None:
    manifest = read_json("models/bundles/bundle_manifest.json")
    bundle = ROOT / manifest["bundle_path"]
    assert hashlib.sha256(bundle.read_bytes()).hexdigest() == manifest["bundle_sha256"]
    assert manifest["test_status"] == "LOCKED_NOT_ACQUIRED"


def test_dataset_manifest_does_not_claim_sku110k() -> None:
    manifest = read_json("data/manifests/dataset_manifest.json")
    assert manifest["profile"] == "qualification_smoke"
    assert manifest["official_dataset_status"] == "NOT_ACQUIRED"
    assert manifest["source"] == "deterministic procedural shelf scenes"


def test_openapi_exposes_supported_contracts() -> None:
    with TestClient(app) as client:
        schema = client.get("/openapi.json").json()
    expected = {
        "/v1/detections",
        "/v1/detections/batch",
        "/v1/evaluation/summary",
        "/v1/evaluation/density-slices",
        "/v1/evaluation/errors",
    }
    assert expected.issubset(schema["paths"])
    assert schema["info"]["version"] == "1.0.0"
