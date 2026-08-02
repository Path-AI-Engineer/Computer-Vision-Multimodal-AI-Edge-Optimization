from __future__ import annotations

import csv
import json
from pathlib import Path

from PIL import Image

from ml.data.contracts import ARTIFACT_VERSION, BREEDS
from ml.inference.bundle import QualificationBundle
from ml.inference.predictor import PetBreedPredictor

ROOT = Path(__file__).parents[1]


def main() -> None:
    dataset = _json("data/manifests/dataset_manifest.json")
    metrics = _json("reports/metrics/metrics.json")
    comparison = _json("reports/metrics/model_comparison.json")
    bundle_manifest = _json("models/bundles/bundle_manifest.json")
    assert dataset["categories"] == 37
    assert dataset["mode"] == "QUALIFICATION_ONLY"
    assert dataset["official_test_status"] == "LOCKED_NOT_ACQUIRED"
    assert metrics["artifact_version"] == ARTIFACT_VERSION
    assert comparison["selected_model"] == "hog-linear-qualification"
    assert bundle_manifest["labels"] == list(BREEDS)
    with (ROOT / "data/manifests/split_manifest.csv").open(encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    train = {row["sample_id"] for row in rows if row["split"] == "train"}
    validation = {row["sample_id"] for row in rows if row["split"] == "validation"}
    assert train and validation and train.isdisjoint(validation)
    assert len(rows) == 222
    model = QualificationBundle.load(ROOT / "models/bundles/pet-breed-qualification.joblib")
    sample = next((ROOT / "data/samples").glob("*.png"))
    with Image.open(sample) as image:
        prediction = PetBreedPredictor(model).predict(image)
    assert len(prediction["top_k"]) == 5
    assert 0 <= prediction["confidence"] <= 1
    print(
        json.dumps(
            {
                "status": "passed",
                "classes": len(BREEDS),
                "samples": len(rows),
                "macro_f1": metrics["macro_f1"],
                "test_status": dataset["official_test_status"],
            },
            sort_keys=True,
        )
    )


def _json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
