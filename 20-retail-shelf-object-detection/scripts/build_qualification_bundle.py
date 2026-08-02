from __future__ import annotations

import csv
import hashlib
import json
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.data.boxes import Box  # noqa: E402
from ml.data.fixture import generate_shelf_fixture  # noqa: E402
from ml.evaluation.metrics import density_slices, detection_summary, match_image  # noqa: E402
from ml.inference.bundle import save_bundle  # noqa: E402
from ml.inference.predictor import ShelfPredictor  # noqa: E402
from ml.models.qualification_detector import ComponentDetectorConfig  # noqa: E402
from ml.visualization.overlay import write_overlay  # noqa: E402

SAMPLES = ROOT / "data" / "samples"
MANIFESTS = ROOT / "data" / "manifests"
METRICS = ROOT / "reports" / "metrics"
PREDICTIONS = ROOT / "reports" / "predictions"
ERRORS = ROOT / "reports" / "errors"
FIGURES = ROOT / "reports" / "figures"
BUNDLES = ROOT / "models" / "bundles"
RUNS = ROOT / "reports" / "runs" / "p20-qualification-v1"


def main() -> None:
    for directory in (MANIFESTS, METRICS, PREDICTIONS, ERRORS, FIGURES, BUNDLES, RUNS):
        directory.mkdir(parents=True, exist_ok=True)
    records = generate_shelf_fixture(SAMPLES)
    config = ComponentDetectorConfig()
    bundle_path = BUNDLES / "shelf-detector-qualification.json"
    save_bundle(config, bundle_path)
    predictor = ShelfPredictor(config)
    evaluated: list[dict[str, object]] = []
    latency: list[float] = []
    for record in records:
        image_path = ROOT / str(record["path"])
        with Image.open(image_path) as image:
            prediction = predictor.predict(image.convert("RGB"))
        truth = [Box(*values) for values in record["boxes"]]
        predicted = [Box(*item["box"]) for item in prediction["detections"]]
        scores = [float(item["confidence"]) for item in prediction["detections"]]
        true_positive, false_positive, false_negative = match_image(
            truth, predicted, scores, 0.5
        )
        evaluated.append(
            {
                "image_id": record["image_id"],
                "image_url": f"/samples/{record['filename']}",
                "overlay_url": f"/overlays/{record['filename']}",
                "density": record["density"],
                "truth_count": len(truth),
                "predicted_count": len(predicted),
                "count_error": len(predicted) - len(truth),
                "true_positive": len(true_positive),
                "false_positive": len(false_positive),
                "false_negative": false_negative,
                "truth_boxes": [box.as_list() for box in truth],
                "predicted_boxes": [box.as_list() for box in predicted],
                "scores": scores,
                "latency_ms": prediction["latency_ms"],
            }
        )
        latency.append(float(prediction["latency_ms"]))
        write_overlay(image_path, truth, predicted, FIGURES / record["filename"])

    summary = detection_summary(evaluated)
    summary.update(
        {
            "artifact_version": "shelf-detection-qualification-v1",
            "model_version": config.model_version,
            "generated_at": datetime.now(UTC).isoformat(),
        }
    )
    _json(METRICS / "metrics.json", summary)
    _json(METRICS / "density_slices.json", density_slices(evaluated))
    _json(PREDICTIONS / "qualification_predictions.json", {"items": evaluated})
    _write_errors(evaluated)
    _write_manifests(records)
    _write_model_comparison(summary, bundle_path, evaluated)
    _json(
        METRICS / "latency_report.json",
        {
            "profile": "qualification_smoke",
            "runs": len(latency),
            "p50_ms": round(statistics.median(latency), 3),
            "p95_ms": round(float(np.quantile(latency, 0.95)), 3),
            "throughput_images_per_second": round(1000 / statistics.mean(latency), 3),
            "warning": "Local qualification latency is not a real-time claim.",
        },
    )
    _json(
        BUNDLES / "bundle_manifest.json",
        {
            "artifact_version": "shelf-detection-qualification-v1",
            "model_version": config.model_version,
            "bundle_path": bundle_path.relative_to(ROOT).as_posix(),
            "bundle_sha256": hashlib.sha256(bundle_path.read_bytes()).hexdigest(),
            "profile": "qualification_smoke",
            "class_name": "object",
            "preprocessing_version": "rgb-native-component-v1",
            "validation_map_50_95": summary["map_50_95"],
            "test_status": "LOCKED_NOT_ACQUIRED",
        },
    )
    _write_run_config()
    _write_model_card(summary)
    print(
        json.dumps(
            {
                "status": "passed",
                "profile": "qualification_smoke",
                "images": len(evaluated),
                "objects": sum(int(row["truth_count"]) for row in evaluated),
                "map_50_95": summary["map_50_95"],
                "count_mae": summary["count_mae"],
                "test_status": summary["test_status"],
            },
            sort_keys=True,
        )
    )


def _write_manifests(records: list[dict[str, object]]) -> None:
    _json(
        MANIFESTS / "dataset_manifest.json",
        {
            "dataset": "SKU-110K protocol / procedural qualification fixture",
            "source": "deterministic procedural shelf scenes",
            "official_source": "https://github.com/eg4000/SKU110K_CVPR19",
            "profile": "qualification_smoke",
            "images": len(records),
            "objects": sum(int(record["visible_count"]) for record in records),
            "class_count": 1,
            "class_name": "object",
            "official_dataset_status": "NOT_ACQUIRED",
            "official_test_status": "LOCKED_NOT_ACQUIRED",
            "disclosure": "Qualification scenes are not SKU-110K observations.",
        },
    )
    rows = [
        {
            "image_id": record["image_id"],
            "profile": "qualification_smoke",
            "split": "qualification_validation",
            "density": record["density"],
            "visible_count": record["visible_count"],
            "sha256": record["sha256"],
            "filename": record["filename"],
        }
        for record in records
    ]
    _csv(MANIFESTS / "profile_manifest.csv", rows)
    _json(
        MANIFESTS / "compute_profiles.json",
        {
            "profiles": [
                {"name": "smoke", "state": "QUALIFICATION_EXECUTED", "images": len(records)},
                {"name": "development", "state": "NOT_ACQUIRED", "images": None},
                {"name": "full", "state": "NOT_ACQUIRED", "images": None},
            ]
        },
    )


def _write_errors(records: list[dict[str, object]]) -> None:
    ordered = sorted(records, key=lambda row: abs(int(row["count_error"])), reverse=True)
    _json(
        ERRORS / "error_gallery.json",
        {
            "profile": "qualification_smoke",
            "items": [
                {
                    key: row[key]
                    for key in (
                        "image_id",
                        "image_url",
                        "overlay_url",
                        "density",
                        "truth_count",
                        "predicted_count",
                        "count_error",
                        "false_positive",
                        "false_negative",
                    )
                }
                for row in ordered[:9]
            ],
        },
    )


def _write_model_comparison(
    summary: dict[str, object], bundle_path: Path, records: list[dict[str, object]]
) -> None:
    observed = np.asarray([int(record["truth_count"]) for record in records], dtype=float)
    mean_count = float(observed.mean())
    baseline_errors = np.full_like(observed, mean_count) - observed
    _json(
        METRICS / "model_comparison.json",
        {
            "profile": "qualification_smoke",
            "selected_model": "qualification-component-detector",
            "models": [
                {
                    "model_id": "count-by-mean",
                    "status": "qualification_baseline_executed",
                    "visual": False,
                    "mean_count": round(mean_count, 3),
                    "count_mae": round(float(np.abs(baseline_errors).mean()), 3),
                    "count_rmse": round(float(np.sqrt(np.square(baseline_errors).mean())), 3),
                    "selection_eligible": False,
                },
                {
                    "model_id": "qualification-component-detector",
                    "status": "executed",
                    "map_50_95": summary["map_50_95"],
                    "count_mae": summary["count_mae"],
                    "artifact_bytes": bundle_path.stat().st_size,
                    "selection_eligible": True,
                },
                {"model_id": "yolo-nano", "status": "protocol_ready_not_executed"},
                {"model_id": "yolo-small", "status": "optional_not_executed"},
                {"model_id": "faster-rcnn", "status": "protocol_ready_not_executed"},
            ],
            "warning": "No SKU-110K or YOLO metrics were produced in this qualification run.",
        },
    )


def _write_run_config() -> None:
    (RUNS / "run_config.yaml").write_text(
        """run_id: p20-qualification-v1
seed: 200533
profile: qualification_smoke
dataset_mode: deterministic_procedural_shelves
model: qualification-component-detector
confidence_threshold: 0.35
nms_iou_threshold: 0.45
primary_metric: map_50_95
official_test_status: LOCKED_NOT_ACQUIRED
""",
        encoding="utf-8",
    )


def _write_model_card(summary: dict[str, object]) -> None:
    (ROOT / "model-card.md").write_text(
        f"""# Model Card - Retail Shelf Detection Console

## Active artifact

- Model: `component-detector-qualification-v1.0.0`
- Profile: `qualification_smoke`
- Class: `object`
- Input: safe RGB JPEG, PNG or WebP.
- Output: XYXY boxes, confidence, visible count, thresholds and latency.

## Evidence boundary

The active detector is a deterministic connected-component qualification model trained on no
private or official data. It validates geometry, evaluation, API and UI behavior. It is not a
YOLO model and is not evidence of SKU-110K performance.

- Qualification mAP@[.50:.95]: {summary["map_50_95"]}
- Qualification count MAE: {summary["count_mae"]}
- Official test: `LOCKED_NOT_ACQUIRED`

## Responsible use

The visible count covers detections in one image. It does not identify SKUs, infer hidden stock,
estimate inventory, guarantee planogram compliance or support consequential retail decisions.
""",
        encoding="utf-8",
    )


def _json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
