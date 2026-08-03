from __future__ import annotations

from collections.abc import Callable
from time import perf_counter_ns

import numpy as np


def benchmark_callable(
    operation: Callable[[np.ndarray], np.ndarray],
    payload: np.ndarray,
    *,
    warmup: int = 8,
    iterations: int = 40,
) -> list[float]:
    if warmup < 1 or iterations < 3:
        raise ValueError("Benchmark requires warmup and at least three measured iterations.")
    for _ in range(warmup):
        operation(payload)
    samples: list[float] = []
    for _ in range(iterations):
        start = perf_counter_ns()
        output = operation(payload)
        elapsed_ms = (perf_counter_ns() - start) / 1_000_000
        if output.size == 0:
            raise ValueError("Benchmark operation returned an empty tensor.")
        samples.append(max(elapsed_ms, 0.0001))
    return samples
