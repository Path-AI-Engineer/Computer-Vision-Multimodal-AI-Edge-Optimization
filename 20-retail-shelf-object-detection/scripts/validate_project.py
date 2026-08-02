from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.inference.bundle import load_bundle  # noqa: E402
from ml.inference.predictor import ShelfPredictor  # noqa: E402


def main() -> None:
    dataset = load_json("data/manifests/dataset_manifest.json")
    metrics = load_json("reports/metrics/metrics.json")
    manifest = load_json("models/bundles/bundle_manifest.json")
    comparison = load_json("reports/metrics/model_comparison.json")
    with (ROOT / "data/manifests/profile_manifest.csv").open(encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert dataset["profile"] == "qualification_smoke"
    assert dataset["official_test_status"] == "LOCKED_NOT_ACQUIRED"
    assert len(rows) == dataset["images"] == 12
    assert {row["density"] for row in rows} == {"low", "medium", "high"}
    bundle_path = ROOT / str(manifest["bundle_path"])
    assert hashlib.sha256(bundle_path.read_bytes()).hexdigest() == manifest["bundle_sha256"]
    _, config = load_bundle(bundle_path)
    sample = ROOT / "data" / "samples" / rows[0]["filename"]
    with Image.open(sample) as image:
        prediction = ShelfPredictor(config).predict(image.convert("RGB"))
    assert prediction["visible_count"] > 0
    assert prediction["model_version"] == manifest["model_version"]
    assert metrics["map_50_95"] >= 0
    assert comparison["selected_model"] == "qualification-component-detector"
    assert any(model["status"] != "executed" for model in comparison["models"])
    print(
        json.dumps(
            {
                "status": "passed",
                "images": len(rows),
                "objects": dataset["objects"],
                "map_50_95": metrics["map_50_95"],
                "count_mae": metrics["count_mae"],
                "test_status": metrics["test_status"],
            },
            sort_keys=True,
        )
    )


def load_json(relative: str) -> dict[str, object]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
