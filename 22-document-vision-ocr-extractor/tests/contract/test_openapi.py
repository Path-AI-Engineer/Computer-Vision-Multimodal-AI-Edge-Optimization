from backend.app.main import app


def test_required_routes_exist_in_openapi() -> None:
    paths = set(app.openapi()["paths"])
    required = {
        "/health",
        "/ready",
        "/v1/models/current",
        "/v1/documents/extract",
        "/v1/extractions/{request_id}",
        "/v1/extractions/{request_id}/export",
        "/v1/evaluation/summary",
        "/v1/evaluation/errors",
    }
    assert required <= paths


def test_mutating_routes_declare_post_only() -> None:
    paths = app.openapi()["paths"]
    assert set(paths["/v1/documents/extract"]) == {"post"}
    assert set(paths["/v1/extractions/{request_id}/export"]) == {"post"}
