from __future__ import annotations

import numpy as np


def softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - logits.max(axis=1, keepdims=True)
    exponent = np.exp(shifted)
    return exponent / exponent.sum(axis=1, keepdims=True)


def negative_log_likelihood(
    logits: np.ndarray, labels: np.ndarray, temperature: float = 1.0
) -> float:
    probabilities = softmax(logits / temperature)
    selected = probabilities[np.arange(len(labels)), labels]
    return float(-np.log(np.clip(selected, 1e-12, 1.0)).mean())


def fit_temperature(logits: np.ndarray, labels: np.ndarray) -> float:
    candidates = np.geomspace(0.5, 5.0, 120)
    losses = [negative_log_likelihood(logits, labels, float(value)) for value in candidates]
    return float(candidates[int(np.argmin(losses))])


def expected_calibration_error(
    probabilities: np.ndarray, labels: np.ndarray, bins: int = 10
) -> float:
    confidence = probabilities.max(axis=1)
    prediction = probabilities.argmax(axis=1)
    correct = prediction == labels
    edges = np.linspace(0.0, 1.0, bins + 1)
    error = 0.0
    for lower, upper in zip(edges[:-1], edges[1:], strict=True):
        mask = (confidence > lower) & (confidence <= upper)
        if mask.any():
            error += float(mask.mean()) * abs(
                float(correct[mask].mean() - confidence[mask].mean())
            )
    return error


def reliability_bins(
    probabilities: np.ndarray, labels: np.ndarray, bins: int = 10
) -> list[dict[str, float | int]]:
    confidence = probabilities.max(axis=1)
    correct = probabilities.argmax(axis=1) == labels
    edges = np.linspace(0.0, 1.0, bins + 1)
    rows: list[dict[str, float | int]] = []
    for index, (lower, upper) in enumerate(zip(edges[:-1], edges[1:], strict=True)):
        mask = (confidence > lower) & (confidence <= upper)
        rows.append(
            {
                "bin": index,
                "lower": round(float(lower), 3),
                "upper": round(float(upper), 3),
                "count": int(mask.sum()),
                "accuracy": round(float(correct[mask].mean()), 5) if mask.any() else 0.0,
                "confidence": round(float(confidence[mask].mean()), 5) if mask.any() else 0.0,
            }
        )
    return rows
