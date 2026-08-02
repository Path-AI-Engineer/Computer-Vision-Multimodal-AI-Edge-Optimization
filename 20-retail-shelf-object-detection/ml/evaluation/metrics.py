from __future__ import annotations

import math
from collections import defaultdict

import numpy as np

from ml.data.boxes import Box, iou


def match_image(
    truth: list[Box], predicted: list[Box], scores: list[float], threshold: float
) -> tuple[list[int], list[int], int]:
    matched_truth: set[int] = set()
    true_positive: list[int] = []
    false_positive: list[int] = []
    for prediction_index in sorted(
        range(len(predicted)), key=lambda index: scores[index], reverse=True
    ):
        candidates = [
            (truth_index, iou(predicted[prediction_index], truth_box))
            for truth_index, truth_box in enumerate(truth)
            if truth_index not in matched_truth
        ]
        best = max(candidates, key=lambda item: item[1], default=(-1, 0.0))
        if best[1] >= threshold:
            matched_truth.add(best[0])
            true_positive.append(prediction_index)
        else:
            false_positive.append(prediction_index)
    return true_positive, false_positive, len(truth) - len(matched_truth)


def average_precision(records: list[dict[str, object]], threshold: float) -> dict[str, float]:
    ranked: list[tuple[float, int]] = []
    total_truth = 0
    for record in records:
        truth = [Box(*values) for values in record["truth_boxes"]]
        predicted = [Box(*values) for values in record["predicted_boxes"]]
        scores = [float(value) for value in record["scores"]]
        true_positive, false_positive, _ = match_image(truth, predicted, scores, threshold)
        ranked.extend((scores[index], 1) for index in true_positive)
        ranked.extend((scores[index], 0) for index in false_positive)
        total_truth += len(truth)
    ranked.sort(reverse=True)
    if not ranked or total_truth == 0:
        return {"ap": 0.0, "precision": 0.0, "recall": 0.0}
    cumulative_tp = np.cumsum([item[1] for item in ranked])
    cumulative_fp = np.cumsum([1 - item[1] for item in ranked])
    precision = cumulative_tp / np.maximum(cumulative_tp + cumulative_fp, 1)
    recall = cumulative_tp / total_truth
    interpolated = []
    for recall_threshold in np.linspace(0, 1, 101):
        eligible = precision[recall >= recall_threshold]
        interpolated.append(float(eligible.max()) if eligible.size else 0.0)
    return {
        "ap": round(float(np.mean(interpolated)), 5),
        "precision": round(float(precision[-1]), 5),
        "recall": round(float(recall[-1]), 5),
    }


def detection_summary(records: list[dict[str, object]]) -> dict[str, object]:
    thresholds = [0.5 + 0.05 * index for index in range(10)]
    per_threshold = {
        f"{threshold:.2f}": average_precision(records, threshold) for threshold in thresholds
    }
    count_errors = np.asarray(
        [int(record["predicted_count"]) - int(record["truth_count"]) for record in records],
        dtype=np.float64,
    )
    return {
        "profile": "qualification_smoke",
        "evaluation_scope": "procedural_qualification_validation",
        "images": len(records),
        "map_50_95": round(float(np.mean([row["ap"] for row in per_threshold.values()])), 5),
        "ap50": per_threshold["0.50"]["ap"],
        "ap75": per_threshold["0.75"]["ap"],
        "precision_at_50": per_threshold["0.50"]["precision"],
        "recall_at_50": per_threshold["0.50"]["recall"],
        "count_mae": round(float(np.abs(count_errors).mean()), 5),
        "count_rmse": round(float(math.sqrt(np.square(count_errors).mean())), 5),
        "count_mean_bias": round(float(count_errors.mean()), 5),
        "iou_thresholds": per_threshold,
        "test_status": "LOCKED_NOT_ACQUIRED",
    }


def density_slices(records: list[dict[str, object]]) -> dict[str, object]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        grouped[str(record["density"])].append(record)
    return {
        "profile": "qualification_smoke",
        "thresholds": {"low": "<=40", "medium": "41-70", "high": ">=71"},
        "slices": [
            {"density": name, **detection_summary(rows)}
            for name, rows in ((name, grouped[name]) for name in ("low", "medium", "high"))
        ],
    }
