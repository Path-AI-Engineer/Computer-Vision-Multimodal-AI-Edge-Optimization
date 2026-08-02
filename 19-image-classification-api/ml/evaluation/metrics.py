from __future__ import annotations

import numpy as np
from sklearn.metrics import confusion_matrix, f1_score, precision_recall_fscore_support

from ml.evaluation.calibration import expected_calibration_error


def classification_report(
    labels: np.ndarray, probabilities: np.ndarray, class_names: tuple[str, ...]
) -> tuple[dict[str, float | int], list[dict[str, float | int | str]], np.ndarray]:
    prediction = probabilities.argmax(axis=1)
    top_five = np.argsort(probabilities, axis=1)[:, -5:]
    precision, recall, class_f1, support = precision_recall_fscore_support(
        labels,
        prediction,
        labels=np.arange(len(class_names)),
        zero_division=0,
    )
    metrics: dict[str, float | int] = {
        "examples": int(len(labels)),
        "accuracy_top_1": round(float((prediction == labels).mean()), 5),
        "accuracy_top_5": round(
            float(np.mean([label in row for label, row in zip(labels, top_five, strict=True)])),
            5,
        ),
        "macro_f1": round(
            float(f1_score(labels, prediction, average="macro", zero_division=0)), 5
        ),
        "negative_log_likelihood": round(
            float(
                -np.log(np.clip(probabilities[np.arange(len(labels)), labels], 1e-12, 1)).mean()
            ),
            5,
        ),
        "expected_calibration_error": round(
            expected_calibration_error(probabilities, labels), 5
        ),
    }
    per_class = [
        {
            "class_id": index,
            "class_name": class_name,
            "precision": round(float(precision[index]), 5),
            "recall": round(float(recall[index]), 5),
            "f1": round(float(class_f1[index]), 5),
            "support": int(support[index]),
        }
        for index, class_name in enumerate(class_names)
    ]
    matrix = confusion_matrix(labels, prediction, labels=np.arange(len(class_names)))
    return metrics, per_class, matrix
