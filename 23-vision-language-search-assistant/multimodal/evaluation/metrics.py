from __future__ import annotations

from statistics import mean, median


def retrieval_metrics(ranks: list[int]) -> dict[str, float]:
    if not ranks:
        raise ValueError("At least one rank is required.")
    return {
        "recall_at_1": round(mean(rank <= 1 for rank in ranks), 4),
        "recall_at_5": round(mean(rank <= 5 for rank in ranks), 4),
        "recall_at_10": round(mean(rank <= 10 for rank in ranks), 4),
        "mrr": round(mean(1 / rank for rank in ranks), 4),
        "median_rank": float(median(ranks)),
        "mean_rank": round(mean(ranks), 4),
    }


def index_recall(exact_ids: list[str], approximate_ids: list[str], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive.")
    expected = set(exact_ids[:k])
    observed = set(approximate_ids[:k])
    return round(len(expected & observed) / max(len(expected), 1), 4)
