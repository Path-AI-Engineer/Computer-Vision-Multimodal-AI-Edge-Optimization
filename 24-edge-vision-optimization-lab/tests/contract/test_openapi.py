from __future__ import annotations

from backend.app.main import app


def test_required_routes_exist() -> None:
    paths = app.openapi()["paths"]
    required = {
        "/health",
        "/ready",
        "/v1/variants",
        "/v1/variants/{variant_id}",
        "/v1/predictions",
        "/v1/benchmarks/summary",
        "/v1/benchmarks/pareto",
        "/v1/benchmarks/environment",
        "/v1/parity/summary",
    }
    assert required <= set(paths)


def test_prediction_contract_requires_variant_query() -> None:
    operation = app.openapi()["paths"]["/v1/predictions"]["post"]
    query = [item for item in operation["parameters"] if item["name"] == "variant_id"]
    assert query[0]["required"] is True
