from __future__ import annotations

import numpy as np


def parity_report(
    reference: np.ndarray,
    candidate: np.ndarray,
    *,
    atol: float,
    reference_id: str,
    candidate_id: str,
) -> dict[str, float | int | str | bool]:
    left = np.asarray(reference, dtype=np.float64)
    right = np.asarray(candidate, dtype=np.float64)
    if left.shape != right.shape or left.ndim != 2:
        raise ValueError("Parity tensors must have the same two-dimensional shape.")
    delta = np.abs(left - right)
    agreement = float(np.mean(left.argmax(axis=1) == right.argmax(axis=1)))
    maximum = float(delta.max())
    return {
        "reference_variant": reference_id,
        "candidate_variant": candidate_id,
        "samples": int(left.shape[0]),
        "max_absolute_error": round(maximum, 6),
        "mean_absolute_error": round(float(delta.mean()), 6),
        "top1_agreement": round(agreement, 4),
        "absolute_tolerance": atol,
        "passed": maximum <= atol and agreement == 1.0,
    }
