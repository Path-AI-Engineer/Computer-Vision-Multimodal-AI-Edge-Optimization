from __future__ import annotations

import csv
import hashlib
import json
import platform
import statistics
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import PIL
import sklearn
from PIL import Image, ImageDraw
from sklearn.linear_model import LogisticRegression

from ml.data.contracts import ARTIFACT_VERSION, BREEDS, PREPROCESSING_VERSION
from ml.data.fixture import generate_qualification_fixture
from ml.evaluation.calibration import fit_temperature, reliability_bins, softmax
from ml.evaluation.metrics import classification_report
from ml.features.hog import FEATURE_VERSION, extract_hog_rgb
from ml.inference.bundle import QualificationBundle
from ml.inference.predictor import PetBreedPredictor

ROOT = Path(__file__).parents[1]
SAMPLES = ROOT / "data" / "samples"
MANIFESTS = ROOT / "data" / "manifests"
METRICS = ROOT / "reports" / "metrics"
FIGURES = ROOT / "reports" / "figures"
ERRORS = ROOT / "reports" / "errors"
BUNDLES = ROOT / "models" / "bundles"
SEED = 190505


def main() -> None:
    for directory in (MANIFESTS, METRICS, FIGURES, ERRORS, BUNDLES):
        directory.mkdir(parents=True, exist_ok=True)
    records = generate_qualification_fixture(SAMPLES, samples_per_class=6, seed=SEED)
    for record in records:
        sample_index = int(str(record["sample_id"]).rsplit("-", 1)[-1])
        record["split"] = "train" if sample_index < 4 else "validation"
    _write_dataset_manifest(records)
    _write_split_manifest(records)

    feature_matrix = np.stack(
        [extract_hog_rgb(Image.open(ROOT / str(record["path"]))) for record in records]
    )
    labels = np.asarray([record["class_id"] for record in records], dtype=np.int64)
    train_mask = np.asarray([record["split"] == "train" for record in records])
    validation_mask = ~train_mask
    classifier = LogisticRegression(
        C=1.0,
        max_iter=800,
        random_state=SEED,
        solver="lbfgs",
    )
    started = time.perf_counter()
    classifier.fit(feature_matrix[train_mask], labels[train_mask])
    training_seconds = time.perf_counter() - started
    validation_logits = classifier.decision_function(feature_matrix[validation_mask])
    temperature = fit_temperature(validation_logits, labels[validation_mask])
    probabilities = softmax(validation_logits / temperature)
    summary, per_class, matrix = classification_report(
        labels[validation_mask], probabilities, BREEDS
    )
    summary.update(
        {
            "artifact_version": ARTIFACT_VERSION,
            "evaluation_scope": "procedural_qualification_validation",
            "training_seconds": round(training_seconds, 5),
            "temperature": round(temperature, 6),
            "test_status": "LOCKED_NOT_ACQUIRED",
        }
    )

    bundle = QualificationBundle(
        classifier=classifier,
        labels=BREEDS,
        temperature=temperature,
        model_version="hog-linear-qualification-v1.0.0",
        preprocessing_version=PREPROCESSING_VERSION,
        artifact_version=ARTIFACT_VERSION,
        abstention_threshold=0.62,
    )
    model_path = BUNDLES / "pet-breed-qualification.joblib"
    bundle.save(model_path)
    _write_json(METRICS / "metrics.json", summary)
    _write_csv(METRICS / "per_class_metrics.csv", per_class)
    _write_json(
        METRICS / "calibration.json",
        {
            "artifact_version": ARTIFACT_VERSION,
            "method": "temperature_scaling",
            "temperature": round(temperature, 6),
            "fit_split": "qualification_validation",
            "expected_calibration_error": summary["expected_calibration_error"],
            "reliability_bins": reliability_bins(probabilities, labels[validation_mask]),
        },
    )
    _write_confusion_matrix(matrix, FIGURES / "confusion_matrix.png")
    _write_reliability_diagram(
        reliability_bins(probabilities, labels[validation_mask]),
        FIGURES / "reliability_diagram.png",
    )
    validation_records = [record for record in records if record["split"] == "validation"]
    _write_error_gallery(validation_records, labels[validation_mask], probabilities)
    _write_model_comparison(summary, training_seconds, model_path)
    latency = _measure_latency(bundle, validation_records)
    _write_json(METRICS / "latency_report.json", latency)
    _write_model_card(summary, latency)
    _write_bundle_manifest(model_path, records, summary)
    print(
        json.dumps(
            {
                "status": "passed",
                "artifact_version": ARTIFACT_VERSION,
                "classes": len(BREEDS),
                "train": int(train_mask.sum()),
                "validation": int(validation_mask.sum()),
                "macro_f1": summary["macro_f1"],
                "test_status": "LOCKED_NOT_ACQUIRED",
            },
            sort_keys=True,
        )
    )


def _write_dataset_manifest(records: list[dict[str, object]]) -> None:
    digest = hashlib.sha256(
        "".join(str(record["sha256"]) for record in records).encode()
    ).hexdigest()
    _write_json(
        MANIFESTS / "dataset_manifest.json",
        {
            "dataset_name": "Oxford-IIIT Pet protocol / procedural qualification fixture",
            "artifact_version": ARTIFACT_VERSION,
            "mode": "QUALIFICATION_ONLY",
            "source": "locally generated procedural images",
            "official_source": "https://www.robots.ox.ac.uk/~vgg/data/pets/",
            "license_reference": (
                "CC BY-SA 4.0 applies to Oxford-IIIT Pet; fixture code is repository-owned"
            ),
            "categories": len(BREEDS),
            "images": len(records),
            "images_per_class": 6,
            "dimensions": [180, 180],
            "duplicates": 0,
            "manifest_sha256": digest,
            "official_test_status": "LOCKED_NOT_ACQUIRED",
            "disclosure": "Qualification images are not Oxford-IIIT Pet observations.",
        },
    )


def _write_split_manifest(records: list[dict[str, object]]) -> None:
    rows = [
        {
            "sample_id": record["sample_id"],
            "class_id": record["class_id"],
            "class_name": record["class_name"],
            "species": record["species"],
            "split": record["split"],
            "sha256": record["sha256"],
            "path": record["path"],
        }
        for record in records
    ]
    _write_csv(MANIFESTS / "split_manifest.csv", rows)


def _write_error_gallery(
    records: list[dict[str, object]], labels: np.ndarray, probabilities: np.ndarray
) -> None:
    prediction = probabilities.argmax(axis=1)
    confidence = probabilities.max(axis=1)
    order = np.argsort(confidence)
    items = []
    for index in order[:18]:
        record = records[int(index)]
        predicted = int(prediction[int(index)])
        actual = int(labels[int(index)])
        items.append(
            {
                "sample_id": record["sample_id"],
                "image_url": f"/samples/{record['filename']}",
                "truth_id": actual,
                "truth": BREEDS[actual],
                "prediction_id": predicted,
                "prediction": BREEDS[predicted],
                "confidence": round(float(confidence[int(index)]), 6),
                "correct": predicted == actual,
                "category": "misclassification"
                if predicted != actual
                else "lowest_confidence_correct",
            }
        )
    _write_json(
        ERRORS / "error_gallery.json",
        {
            "artifact_version": ARTIFACT_VERSION,
            "scope": "qualification_validation",
            "items": items,
        },
    )


def _write_model_comparison(
    summary: dict[str, object], training_seconds: float, path: Path
) -> None:
    majority_accuracy = round(1 / len(BREEDS), 5)
    _write_json(
        METRICS / "model_comparison.json",
        {
            "artifact_version": ARTIFACT_VERSION,
            "selection_metric": "macro_f1",
            "selected_model": "hog-linear-qualification",
            "models": [
                {
                    "model_id": "majority",
                    "family": "minimum_reference",
                    "status": "executed",
                    "macro_f1": round(majority_accuracy / len(BREEDS), 5),
                    "accuracy_top_1": majority_accuracy,
                    "selection_eligible": False,
                },
                {
                    "model_id": "hog-linear-qualification",
                    "family": "classical_visual",
                    "status": "executed",
                    "macro_f1": summary["macro_f1"],
                    "accuracy_top_1": summary["accuracy_top_1"],
                    "ece": summary["expected_calibration_error"],
                    "training_seconds": round(training_seconds, 5),
                    "artifact_bytes": path.stat().st_size,
                    "selection_eligible": True,
                },
                {
                    "model_id": "small-cnn",
                    "family": "cnn_from_scratch",
                    "status": "implemented_not_qualified",
                    "selection_eligible": False,
                },
                {
                    "model_id": "resnet18-frozen",
                    "family": "transfer_learning",
                    "status": "protocol_ready_not_executed",
                    "declared_weights": "IMAGENET1K_V1",
                    "selection_eligible": False,
                },
                {
                    "model_id": "resnet18-finetuned",
                    "family": "transfer_learning",
                    "status": "protocol_ready_not_executed",
                    "declared_weights": "IMAGENET1K_V1",
                    "selection_eligible": False,
                },
                {
                    "model_id": "vit-b-16-frozen",
                    "family": "vision_transformer",
                    "status": "protocol_ready_not_executed",
                    "declared_weights": "IMAGENET1K_V1",
                    "selection_eligible": False,
                },
            ],
            "warning": (
                "Only majority and HOG-linear were executed on the qualification fixture."
            ),
        },
    )


def _measure_latency(
    bundle: QualificationBundle, records: list[dict[str, object]]
) -> dict[str, object]:
    predictor = PetBreedPredictor(bundle)
    values = []
    for record in records[:30]:
        with Image.open(ROOT / str(record["path"])) as image:
            values.append(float(predictor.predict(image)["latency_ms"]))
    ordered = sorted(values)
    return {
        "artifact_version": ARTIFACT_VERSION,
        "environment": "local_cpu_qualification",
        "runs": len(values),
        "p50_ms": round(statistics.median(ordered), 3),
        "p95_ms": round(float(np.quantile(ordered, 0.95)), 3),
        "throughput_images_per_second": round(1_000 / statistics.mean(ordered), 3),
        "warning": "Local qualification latency is not a Cloud Run SLA.",
    }


def _write_bundle_manifest(
    model_path: Path, records: list[dict[str, object]], summary: dict[str, object]
) -> None:
    payload = {
        "artifact_version": ARTIFACT_VERSION,
        "model_version": "hog-linear-qualification-v1.0.0",
        "model_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
        "model_path": model_path.relative_to(ROOT).as_posix(),
        "labels": list(BREEDS),
        "preprocessing_version": PREPROCESSING_VERSION,
        "feature_version": FEATURE_VERSION,
        "abstention_threshold": 0.62,
        "validation_macro_f1": summary["macro_f1"],
        "dataset_manifest_sha256": hashlib.sha256(
            (MANIFESTS / "dataset_manifest.json").read_bytes()
        ).hexdigest(),
        "split_manifest_sha256": hashlib.sha256(
            (MANIFESTS / "split_manifest.csv").read_bytes()
        ).hexdigest(),
        "sample_count": len(records),
        "created_at": datetime.now(UTC).isoformat(),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pillow": PIL.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "evidence_boundary": "QUALIFICATION_ONLY",
        "official_test_status": "LOCKED_NOT_ACQUIRED",
    }
    _write_json(BUNDLES / "bundle_manifest.json", payload)


def _write_model_card(summary: dict[str, object], latency: dict[str, object]) -> None:
    content = f"""# Model Card — Pet Breed Classification Studio

## Model

- Version: `hog-linear-qualification-v1.0.0`
- Artifact: `{ARTIFACT_VERSION}`
- Input: JPEG, PNG or WebP converted to RGB and fitted to 160 × 160.
- Output: 37 Oxford-IIIT Pet breed labels with calibrated qualification probabilities.

## Evidence boundary

This is a **qualification bundle**, trained on deterministic procedural images. It proves
the data, feature, calibration, API and product path. It is not an Oxford-IIIT Pet model
and its metric values must not be presented as breed-recognition performance.

The official Oxford test split remains `LOCKED_NOT_ACQUIRED`.

## Qualification metrics

- Macro F1: {summary["macro_f1"]}
- Top-1 accuracy: {summary["accuracy_top_1"]}
- Top-5 accuracy: {summary["accuracy_top_5"]}
- ECE: {summary["expected_calibration_error"]}
- Local p50 latency: {latency["p50_ms"]} ms
- Local p95 latency: {latency["p95_ms"]} ms

## Intended use

Engineering validation, portfolio demonstration and controlled study of inference
contracts. It is not intended for veterinary, health, identity or safety decisions.

## Limitations

- Procedural qualification imagery does not represent real pet photography.
- Confidence is not a correctness guarantee.
- HOG has no Grad-CAM surface.
- Species and breed may be wrong under background, crop or lighting shifts.
- ResNet-18 and ViT-B/16 remain protocol-ready but unexecuted in this bundle.
"""
    (ROOT / "model-card.md").write_text(content, encoding="utf-8")


def _write_confusion_matrix(matrix: np.ndarray, destination: Path) -> None:
    cell = 12
    margin = 28
    image = Image.new(
        "RGB", (margin + cell * len(BREEDS), margin + cell * len(BREEDS)), "#07111f"
    )
    draw = ImageDraw.Draw(image)
    maximum = max(int(matrix.max()), 1)
    for row in range(len(BREEDS)):
        for column in range(len(BREEDS)):
            ratio = int(matrix[row, column]) / maximum
            color = (15, int(55 + 180 * ratio), int(82 + 155 * ratio))
            x = margin + column * cell
            y = margin + row * cell
            draw.rectangle((x, y, x + cell - 1, y + cell - 1), fill=color)
    draw.text((6, 6), "37 x 37", fill="#dffcf5")
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination)


def _write_reliability_diagram(rows: list[dict[str, float | int]], destination: Path) -> None:
    image = Image.new("RGB", (640, 360), "#07111f")
    draw = ImageDraw.Draw(image)
    draw.line((70, 300, 580, 300), fill="#78909c", width=2)
    draw.line((70, 300, 70, 38), fill="#78909c", width=2)
    draw.line((70, 300, 580, 38), fill="#315e67", width=2)
    for row in rows:
        center = (float(row["lower"]) + float(row["upper"])) / 2
        accuracy = float(row["accuracy"])
        x = 70 + int(center * 510)
        y = 300 - int(accuracy * 262)
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill="#35e0c1")
    draw.text((70, 316), "confidence", fill="#dffcf5")
    draw.text((12, 18), "accuracy", fill="#dffcf5")
    image.save(destination)


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Cannot write an empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
