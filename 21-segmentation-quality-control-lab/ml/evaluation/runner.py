from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from ml.baselines.opencv import segment_with_morphology
from ml.data.contracts import load_binary_mask, load_grayscale
from ml.data.fixture import read_manifest
from ml.evaluation.metrics import (
    aggregate_pixel_metrics,
    piece_metrics,
    precision_recall_auc,
    select_pixel_threshold,
)
from ml.evaluation.policy import InspectionPolicy, evaluate_mask
from ml.inference.bundle import QualityBundle
from ml.inference.predictor import SegmentationPredictor
from ml.models.references import protocol_ready_candidates
from ml.visualization.masks import binary_mask_rgb, overlay_mask, probability_heatmap


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _temporary_bundle(root: Path, checkpoint_path: Path) -> QualityBundle:
    return QualityBundle(
        root=root,
        model_id="small-unet",
        model_version="small-unet-qualification-v1",
        checkpoint_path=checkpoint_path,
        checkpoint_sha256=hashlib.sha256(checkpoint_path.read_bytes()).hexdigest(),
        input_size=(64, 96),
        normalization_mean=150.0,
        normalization_std=45.0,
        pixel_threshold=0.5,
        review_area_ratio=0.001,
        reject_area_ratio=0.012,
        minimum_component_area_px=6,
        evidence_profile="procedural_qualification",
        official_test_status="LOCKED_NOT_ACQUIRED",
    )


def evaluate_qualification(
    root: Path,
    *,
    checkpoint_path: Path,
    protocol: dict[str, Any],
) -> dict[str, object]:
    records = read_manifest(root)
    validation_records = [record for record in records if record["split"] == "validation"]
    predictor = SegmentationPredictor(_temporary_bundle(root, checkpoint_path))
    probabilities: list[np.ndarray] = []
    targets: list[np.ndarray] = []
    baseline_probabilities: list[np.ndarray] = []
    latencies: list[float] = []
    for record in validation_records:
        image = load_grayscale(root / str(record["image_path"]))
        target = load_binary_mask(root / str(record["mask_path"]))
        prediction = predictor.predict_arrays(image, pixel_threshold=0.5)
        probabilities.append(prediction.probability)
        targets.append(target)
        baseline_probabilities.append(segment_with_morphology(image).astype(np.float32))
        latencies.append(prediction.latency_ms)

    selected_threshold, sweep = select_pixel_threshold(
        probabilities,
        targets,
        [float(value) for value in protocol["pixel_threshold_candidates"]],
    )
    policy = InspectionPolicy(
        review_area_ratio=float(protocol["piece_review_threshold"]),
        reject_area_ratio=float(protocol["piece_reject_threshold"]),
        minimum_component_area_px=int(protocol["minimum_component_area_px"]),
    )
    predicted_masks = [
        (probability >= selected_threshold).astype(np.uint8) for probability in probabilities
    ]
    predicted_piece = [evaluate_mask(mask, policy).defect_detected for mask in predicted_masks]
    baseline_piece = [
        evaluate_mask(mask >= 0.5, policy).defect_detected for mask in baseline_probabilities
    ]
    actual_piece = [bool(target.any()) for target in targets]
    unet_pixel = aggregate_pixel_metrics(
        probabilities,
        targets,
        threshold=selected_threshold,
    )
    baseline_pixel = aggregate_pixel_metrics(
        baseline_probabilities,
        targets,
        threshold=0.5,
    )
    summary = {
        "profile": "procedural_qualification",
        "selected_model": "small-unet",
        "selected_model_version": "small-unet-qualification-v1",
        "selection_split": "qualification_validation",
        "official_test_status": "LOCKED_NOT_ACQUIRED",
        "images": len(validation_records),
        "defective_images": sum(actual_piece),
        "clean_images": len(actual_piece) - sum(actual_piece),
        "pixel_threshold": selected_threshold,
        "piece_threshold": policy.review_area_ratio,
        "pixel_metrics": {
            **unet_pixel,
            "pr_auc": precision_recall_auc(probabilities, targets),
        },
        "piece_metrics": piece_metrics(predicted_piece, actual_piece),
        "latency": {
            "p50_ms": round(float(np.percentile(latencies, 50)), 3),
            "p95_ms": round(float(np.percentile(latencies, 95)), 3),
            "environment": "local_cpu_qualification",
            "warning": "Local qualification latency is not a production service SLA.",
        },
        "warning": "Procedural qualification results are not KSDD2 benchmark results.",
    }
    model_comparison = {
        "selection_scope": "procedural_qualification_validation",
        "candidates": [
            {
                "model_id": "always-clean",
                "status": "executed",
                "pixel_metrics": aggregate_pixel_metrics(
                    [np.zeros_like(target, dtype=np.float32) for target in targets],
                    targets,
                    threshold=0.5,
                ),
                "piece_metrics": piece_metrics([False] * len(actual_piece), actual_piece),
            },
            {
                "model_id": "opencv-morphology",
                "status": "executed",
                "pixel_metrics": baseline_pixel,
                "piece_metrics": piece_metrics(baseline_piece, actual_piece),
            },
            {
                "model_id": "small-unet",
                "status": "executed",
                "selected": True,
                "pixel_metrics": summary["pixel_metrics"],
                "piece_metrics": summary["piece_metrics"],
            },
            *[asdict(candidate) for candidate in protocol_ready_candidates()],
        ],
    }
    _write_json(root / "reports" / "metrics" / "evaluation_summary.json", summary)
    _write_json(root / "reports" / "metrics" / "threshold_sweep.json", sweep)
    _write_json(root / "reports" / "metrics" / "model_comparison.json", model_comparison)
    _write_json(root / "reports" / "metrics" / "inspection_policy.json", asdict(policy))

    errors: list[dict[str, object]] = []
    predictions: list[dict[str, object]] = []
    for record, _probability, target, predicted in zip(
        validation_records,
        probabilities,
        targets,
        predicted_masks,
        strict=True,
    ):
        outcome = evaluate_mask(predicted, policy)
        actual = bool(target.any())
        error_type = None
        if outcome.defect_detected and not actual:
            error_type = "FALSE_REJECT"
        elif not outcome.defect_detected and actual:
            error_type = "FALSE_ACCEPT"
        row = {
            "sample_id": record["sample_id"],
            "actual_defect": actual,
            "predicted_defect": outcome.defect_detected,
            "decision": outcome.decision,
            "defect_area_px": outcome.defect_area_px,
            "defect_area_ratio": outcome.defect_area_ratio,
            "error_type": error_type,
        }
        predictions.append(row)
        if error_type:
            errors.append(row)
    _write_json(root / "reports" / "predictions" / "validation_predictions.json", predictions)
    _write_json(
        root / "reports" / "errors" / "error_gallery.json",
        {
            "errors": errors,
            "false_accepts": sum(row["error_type"] == "FALSE_ACCEPT" for row in errors),
            "false_rejects": sum(row["error_type"] == "FALSE_REJECT" for row in errors),
            "scope": "qualification_validation",
        },
    )

    showcase = [record for record in records if record["split"] == "showcase"]
    showcase_root = root / "reports" / "figures"
    masks_root = root / "reports" / "masks"
    showcase_root.mkdir(parents=True, exist_ok=True)
    masks_root.mkdir(parents=True, exist_ok=True)
    final_predictor = predictor
    for record in showcase:
        image = load_grayscale(root / str(record["image_path"]))
        arrays = final_predictor.predict_arrays(image, pixel_threshold=selected_threshold)
        Image.fromarray(overlay_mask(image, arrays.binary_mask)).save(
            showcase_root / f"{record['sample_id']}-overlay.png"
        )
        Image.fromarray(probability_heatmap(arrays.probability)).save(
            showcase_root / f"{record['sample_id']}-probability.png"
        )
        Image.fromarray(binary_mask_rgb(arrays.binary_mask)).save(
            masks_root / f"{record['sample_id']}-mask.png"
        )
    return summary


def create_bundle(
    root: Path,
    *,
    checkpoint_path: Path,
    evaluation_summary: dict[str, object],
    protocol: dict[str, Any],
) -> Path:
    checkpoint_hash = hashlib.sha256(checkpoint_path.read_bytes()).hexdigest()
    payload = {
        "bundle_version": "surface-quality-control-bundle-v1",
        "model_id": "small-unet",
        "model_version": "small-unet-qualification-v1",
        "checkpoint_path": checkpoint_path.relative_to(root).as_posix(),
        "checkpoint_sha256": checkpoint_hash,
        "input_size": [64, 96],
        "normalization": {"mean": 150.0, "std": 45.0},
        "pixel_threshold": evaluation_summary["pixel_threshold"],
        "inspection_policy": {
            "review_area_ratio": protocol["piece_review_threshold"],
            "reject_area_ratio": protocol["piece_reject_threshold"],
            "minimum_component_area_px": protocol["minimum_component_area_px"],
        },
        "threshold_selection_split": "qualification_validation",
        "evidence_profile": "procedural_qualification",
        "official_dataset_status": "NOT_ACQUIRED",
        "official_test_status": "LOCKED_NOT_ACQUIRED",
        "created_from_run": "p21-qualification-v1",
    }
    path = root / "models" / "bundles" / "surface-quality-control-v1.json"
    _write_json(path, payload)
    manifest = {
        "bundle_path": path.relative_to(root).as_posix(),
        "bundle_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "checkpoint_sha256": checkpoint_hash,
        "model_version": payload["model_version"],
    }
    _write_json(root / "models" / "bundles" / "bundle_manifest.json", manifest)
    return path
