from __future__ import annotations

from collections.abc import Iterable


def edit_distance(reference: list[str], prediction: list[str]) -> int:
    previous = list(range(len(prediction) + 1))
    for row, reference_item in enumerate(reference, start=1):
        current = [row]
        for column, prediction_item in enumerate(prediction, start=1):
            substitution = previous[column - 1] + (reference_item != prediction_item)
            current.append(min(current[-1] + 1, previous[column] + 1, substitution))
        previous = current
    return previous[-1]


def character_error_rate(reference: str, prediction: str) -> float:
    if not reference:
        return 0.0 if not prediction else 1.0
    return edit_distance(list(reference), list(prediction)) / len(reference)


def word_error_rate(reference: str, prediction: str) -> float:
    reference_words = reference.split()
    if not reference_words:
        return 0.0 if not prediction.split() else 1.0
    return edit_distance(reference_words, prediction.split()) / len(reference_words)


def intersection_over_union(left: Iterable[int], right: Iterable[int]) -> float:
    lx1, ly1, lx2, ly2 = left
    rx1, ry1, rx2, ry2 = right
    x1, y1, x2, y2 = max(lx1, rx1), max(ly1, ry1), min(lx2, rx2), min(ly2, ry2)
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    left_area = max(0, lx2 - lx1) * max(0, ly2 - ly1)
    right_area = max(0, rx2 - rx1) * max(0, ry2 - ry1)
    union = left_area + right_area - intersection
    return intersection / union if union else 0.0


def exact_match(reference: str | None, prediction: str | None) -> float:
    return float(reference == prediction)


def mean(values: Iterable[float]) -> float:
    items = list(values)
    return sum(items) / len(items) if items else 0.0
