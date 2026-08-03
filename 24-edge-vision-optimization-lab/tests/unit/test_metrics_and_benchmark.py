from __future__ import annotations

import numpy as np
import pytest

from edge_ai.benchmark.harness import benchmark_callable
from edge_ai.benchmark.statistics import pareto_frontier, recommend_variant, summarize_latency
from edge_ai.evaluation.metrics import confusion_rows, quality_metrics


def test_quality_metrics_perfect_predictions() -> None:
    metrics = quality_metrics([0, 1, 2], np.eye(3))
    assert metrics.macro_f1 == 1.0
    assert metrics.top1_accuracy == 1.0


def test_quality_metrics_reject_empty_batch() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        quality_metrics([], np.empty((0, 2)))


def test_confusion_rows_preserve_counts() -> None:
    rows = confusion_rows([0, 1, 1], np.asarray([[2, 0], [0, 2], [2, 0]]))
    assert sum(row["count"] for row in rows) == 3


def test_latency_percentiles_and_throughput() -> None:
    metrics = summarize_latency([1, 2, 3, 4, 5])
    assert metrics.p50_ms == 3
    assert metrics.throughput_per_second == pytest.approx(333.33)


@pytest.mark.parametrize("samples", [[], [1], [1, -2, 3]])
def test_latency_rejects_invalid_samples(samples: list[float]) -> None:
    with pytest.raises(ValueError):
        summarize_latency(samples)


def test_benchmark_harness_runs_warmup_and_measurements() -> None:
    calls = 0

    def operation(value: np.ndarray) -> np.ndarray:
        nonlocal calls
        calls += 1
        return value + 1

    samples = benchmark_callable(operation, np.ones((1, 3)), warmup=2, iterations=4)
    assert calls == 6
    assert len(samples) == 4


def test_pareto_frontier_removes_dominated_variant() -> None:
    rows = [
        {"variant_id": "a", "macro_f1": 0.9, "p50_ms": 2.0, "size_mb": 2.0},
        {"variant_id": "b", "macro_f1": 0.9, "p50_ms": 3.0, "size_mb": 3.0},
    ]
    assert [item["variant_id"] for item in pareto_frontier(rows)] == ["a"]


@pytest.mark.parametrize(
    ("profile", "expected"),
    [("quality_first", "quality"), ("small_size", "small"), ("cpu_low_latency", "fast")],
)
def test_profile_recommendations(profile: str, expected: str) -> None:
    rows = [
        {"variant_id": "quality", "macro_f1": 1.0, "p50_ms": 3.0, "size_mb": 3.0},
        {"variant_id": "small", "macro_f1": 0.8, "p50_ms": 2.0, "size_mb": 1.0},
        {"variant_id": "fast", "macro_f1": 0.9, "p50_ms": 1.0, "size_mb": 2.0},
    ]
    assert recommend_variant(rows, profile) == expected
