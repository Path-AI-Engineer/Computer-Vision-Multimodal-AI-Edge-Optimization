from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np


@dataclass(frozen=True)
class PixelMetrics:
    dice: float
    iou: float
    precision: float
    recall: float


def _safe_ratio(numerator: float, denominator: float, *, empty_value: float) -> float:
    return float(numerator / denominator) if denominator else empty_value


def pixel_metrics(
    probabilities: np.ndarray,
    target: np.ndarray,
    *,
    threshold: float,
) -> PixelMetrics:
    prediction = probabilities >= threshold
    truth = target.astype(bool)
    true_positive = int(np.logical_and(prediction, truth).sum())
    false_positive = int(np.logical_and(prediction, ~truth).sum())
    false_negative = int(np.logical_and(~prediction, truth).sum())
    both_empty = not prediction.any() and not truth.any()
    dice = _safe_ratio(
        2 * true_positive,
        2 * true_positive + false_positive + false_negative,
        empty_value=1.0 if both_empty else 0.0,
    )
    iou = _safe_ratio(
        true_positive,
        true_positive + false_positive + false_negative,
        empty_value=1.0 if both_empty else 0.0,
    )
    precision = _safe_ratio(
        true_positive,
        true_positive + false_positive,
        empty_value=1.0 if not truth.any() else 0.0,
    )
    recall = _safe_ratio(
        true_positive,
        true_positive + false_negative,
        empty_value=1.0 if not truth.any() else 0.0,
    )
    return PixelMetrics(dice=dice, iou=iou, precision=precision, recall=recall)


def aggregate_pixel_metrics(
    probabilities: list[np.ndarray],
    targets: list[np.ndarray],
    *,
    threshold: float,
) -> dict[str, float]:
    rows = [
        pixel_metrics(probability, target, threshold=threshold)
        for probability, target in zip(probabilities, targets, strict=True)
    ]
    return {
        f"macro_{key}": round(float(np.mean([asdict(row)[key] for row in rows])), 6)
        for key in ("dice", "iou", "precision", "recall")
    }


def precision_recall_auc(probabilities: list[np.ndarray], targets: list[np.ndarray]) -> float:
    scores = np.concatenate([array.ravel() for array in probabilities])
    truth = np.concatenate([array.ravel().astype(bool) for array in targets])
    if not truth.any():
        return 0.0
    rows: list[tuple[float, float]] = []
    for threshold in np.linspace(0.0, 1.0, 101):
        prediction = scores >= threshold
        true_positive = np.logical_and(prediction, truth).sum()
        false_positive = np.logical_and(prediction, ~truth).sum()
        false_negative = np.logical_and(~prediction, truth).sum()
        precision = _safe_ratio(true_positive, true_positive + false_positive, empty_value=1.0)
        recall = _safe_ratio(true_positive, true_positive + false_negative, empty_value=0.0)
        rows.append((recall, precision))
    rows.sort(key=lambda row: row[0])
    recalls = np.asarray([row[0] for row in rows])
    precisions = np.asarray([row[1] for row in rows])
    return round(float(np.trapz(precisions, recalls)), 6)


def select_pixel_threshold(
    probabilities: list[np.ndarray],
    targets: list[np.ndarray],
    candidates: list[float],
) -> tuple[float, list[dict[str, float]]]:
    sweep: list[dict[str, float]] = []
    for threshold in candidates:
        aggregate = aggregate_pixel_metrics(probabilities, targets, threshold=threshold)
        sweep.append({"threshold": threshold, **aggregate})
    selected = max(sweep, key=lambda row: (row["macro_dice"], row["macro_recall"]))
    return float(selected["threshold"]), sweep


def piece_metrics(
    predicted_defect: list[bool], actual_defect: list[bool]
) -> dict[str, float | int]:
    true_positive = sum(
        predicted and actual
        for predicted, actual in zip(predicted_defect, actual_defect, strict=True)
    )
    true_negative = sum(
        not predicted and not actual
        for predicted, actual in zip(predicted_defect, actual_defect, strict=True)
    )
    false_positive = sum(
        predicted and not actual
        for predicted, actual in zip(predicted_defect, actual_defect, strict=True)
    )
    false_negative = sum(
        not predicted and actual
        for predicted, actual in zip(predicted_defect, actual_defect, strict=True)
    )
    precision = _safe_ratio(true_positive, true_positive + false_positive, empty_value=1.0)
    recall = _safe_ratio(true_positive, true_positive + false_negative, empty_value=0.0)
    f1 = _safe_ratio(2 * precision * recall, precision + recall, empty_value=0.0)
    return {
        "true_positive": true_positive,
        "true_negative": true_negative,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "defect_precision": round(precision, 6),
        "defect_recall": round(recall, 6),
        "defect_f1": round(f1, 6),
        "false_reject_rate": round(
            _safe_ratio(false_positive, false_positive + true_negative, empty_value=0.0), 6
        ),
        "false_accept_rate": round(
            _safe_ratio(false_negative, false_negative + true_positive, empty_value=0.0), 6
        ),
    }
