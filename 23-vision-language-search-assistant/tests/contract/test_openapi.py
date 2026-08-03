from backend.app.main import app


def test_required_routes_are_present_in_openapi() -> None:
    paths = app.openapi()["paths"]
    required = {
        "/health",
        "/ready",
        "/v1/models/current",
        "/v1/indexes/current",
        "/v1/search/text",
        "/v1/search/image",
        "/v1/sessions",
        "/v1/sessions/{session_id}/messages",
        "/v1/sessions/{session_id}",
        "/v1/evaluation/summary",
        "/v1/evaluation/errors",
    }
    assert required <= set(paths)


def test_search_schema_exposes_bounded_modes() -> None:
    schema = app.openapi()["components"]["schemas"]["TextSearchResource"]
    assert schema["properties"]["mode"]["enum"] == ["bm25", "semantic", "hybrid"]
    assert schema["properties"]["index_mode"]["enum"] == ["exact", "approximate"]
