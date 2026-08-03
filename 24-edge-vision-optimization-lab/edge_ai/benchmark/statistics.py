from __future__ import annotations

from collections.abc import Iterable

import numpy as np

from edge_ai.core.contracts import LatencyMetrics


def summarize_latency(samples_ms: Iterable[float]) -> LatencyMetrics:
    values = np.asarray(list(samples_ms), dtype=np.float64)
    if values.size < 3 or np.any(values <= 0):
        raise ValueError("Latency requires at least three positive samples.")
    mean = float(values.mean())
    return LatencyMetrics(
        p50_ms=round(float(np.percentile(values, 50)), 4),
        p90_ms=round(float(np.percentile(values, 90)), 4),
        p95_ms=round(float(np.percentile(values, 95)), 4),
        mean_ms=round(mean, 4),
        throughput_per_second=round(1000.0 / mean, 2),
        samples=int(values.size),
    )


def pareto_frontier(rows: list[dict[str, float | str]]) -> list[dict[str, float | str]]:
    """Return variants not dominated on F1 (max), latency and size (min)."""
    frontier: list[dict[str, float | str]] = []
    for candidate in rows:
        dominated = False
        for challenger in rows:
            if challenger is candidate:
                continue
            at_least_as_good = (
                float(challenger["macro_f1"]) >= float(candidate["macro_f1"])
                and float(challenger["p50_ms"]) <= float(candidate["p50_ms"])
                and float(challenger["size_mb"]) <= float(candidate["size_mb"])
            )
            strictly_better = (
                float(challenger["macro_f1"]) > float(candidate["macro_f1"])
                or float(challenger["p50_ms"]) < float(candidate["p50_ms"])
                or float(challenger["size_mb"]) < float(candidate["size_mb"])
            )
            if at_least_as_good and strictly_better:
                dominated = True
                break
        if not dominated:
            frontier.append(candidate)
    return sorted(frontier, key=lambda row: float(row["p50_ms"]))


def recommend_variant(rows: list[dict[str, float | str]], profile: str) -> str:
    if not rows:
        raise ValueError("At least one measured variant is required.")
    if profile == "quality_first":
        return str(
            max(rows, key=lambda row: (float(row["macro_f1"]), -float(row["p50_ms"])))["variant_id"]
        )
    if profile == "small_size":
        return str(
            min(rows, key=lambda row: (float(row["size_mb"]), -float(row["macro_f1"])))[
                "variant_id"
            ]
        )
    if profile == "cpu_low_latency":
        return str(
            min(rows, key=lambda row: (float(row["p50_ms"]), -float(row["macro_f1"])))["variant_id"]
        )
    raise ValueError(f"Unsupported deployment profile: {profile}")
