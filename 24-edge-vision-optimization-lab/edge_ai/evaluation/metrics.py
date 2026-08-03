from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

import numpy as np

from edge_ai.core.contracts import QualityMetrics


def quality_metrics(labels: Sequence[int], logits: np.ndarray) -> QualityMetrics:
    truth = np.asarray(labels, dtype=np.int64)
    scores = np.asarray(logits, dtype=np.float64)
    if scores.ndim != 2 or len(truth) != scores.shape[0] or len(truth) == 0:
        raise ValueError("Labels and logits must describe a non-empty classification batch.")
    predicted = scores.argmax(axis=1)
    classes = sorted(set(truth.tolist()))
    per_class: list[float] = []
    for class_id in classes:
        tp = int(np.sum((predicted == class_id) & (truth == class_id)))
        fp = int(np.sum((predicted == class_id) & (truth != class_id)))
        fn = int(np.sum((predicted != class_id) & (truth == class_id)))
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        per_class.append(
            2 * precision * recall / (precision + recall) if precision + recall else 0.0
        )
    k = min(5, scores.shape[1])
    topk = np.argsort(scores, axis=1)[:, -k:]
    return QualityMetrics(
        macro_f1=round(float(np.mean(per_class)), 4),
        top1_accuracy=round(float(np.mean(predicted == truth)), 4),
        top5_accuracy=round(
            float(np.mean([label in row for label, row in zip(truth, topk, strict=True)])), 4
        ),
    )


def confusion_rows(labels: Sequence[int], logits: np.ndarray) -> list[dict[str, int]]:
    predicted = np.asarray(logits).argmax(axis=1)
    counts: defaultdict[tuple[int, int], int] = defaultdict(int)
    for expected, actual in zip(labels, predicted, strict=True):
        counts[(int(expected), int(actual))] += 1
    return [
        {"expected": expected, "predicted": predicted_id, "count": count}
        for (expected, predicted_id), count in sorted(counts.items())
    ]
