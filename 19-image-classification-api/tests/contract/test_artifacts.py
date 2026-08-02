from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).parents[2]


def load(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_dataset_manifest_and_split_are_consistent() -> None:
    manifest = load("data/manifests/dataset_manifest.json")
    with (ROOT / "data/manifests/split_manifest.csv").open(encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert manifest["mode"] == "QUALIFICATION_ONLY"
    assert manifest["categories"] == 37
    assert manifest["images"] == len(rows) == 222
    train = {row["sample_id"] for row in rows if row["split"] == "train"}
    validation = {row["sample_id"] for row in rows if row["split"] == "validation"}
    assert train.isdisjoint(validation)
    assert len(train) == 148
    assert len(validation) == 74


def test_bundle_hash_matches_manifest() -> None:
    manifest = load("models/bundles/bundle_manifest.json")
    bundle = ROOT / str(manifest["model_path"])
    assert hashlib.sha256(bundle.read_bytes()).hexdigest() == manifest["model_sha256"]
    assert manifest["official_test_status"] == "LOCKED_NOT_ACQUIRED"
