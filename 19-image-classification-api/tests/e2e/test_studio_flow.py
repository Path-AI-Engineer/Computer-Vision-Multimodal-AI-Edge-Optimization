from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app

ROOT = Path(__file__).parents[2]


def test_studio_static_shell_and_prediction_flow() -> None:
    with TestClient(app) as client:
        studio = client.get("/app/")
        assert studio.status_code == 200
        assert '<div id="root"></div>' in studio.text

        samples = client.get("/v1/samples").json()
        assert samples["count"] > 0
        sample_path = ROOT / "data" / "samples" / f"{samples['items'][0]['sample_id']}.png"
        with sample_path.open("rb") as stream:
            prediction = client.post(
                "/v1/predictions?top_k=5",
                files={"image": (sample_path.name, stream, "image/png")},
            )

    assert prediction.status_code == 200
    assert prediction.json()["top_k"]
