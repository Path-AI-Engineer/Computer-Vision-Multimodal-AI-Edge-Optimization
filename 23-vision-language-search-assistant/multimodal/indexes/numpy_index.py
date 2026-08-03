from __future__ import annotations

import numpy as np


class NumpyInnerProductIndex:
    def __init__(self, matrix: np.ndarray) -> None:
        self.matrix = np.asarray(matrix, dtype=np.float32)

    def search(self, query: np.ndarray, top_k: int) -> tuple[np.ndarray, np.ndarray]:
        scores = self.matrix @ query.astype(np.float32)
        order = np.argsort(-scores, kind="stable")[:top_k]
        return order, scores[order]


class QuantizedApproximateIndex:
    """Auditable qualification proxy for an approximate-vector index."""

    def __init__(self, matrix: np.ndarray) -> None:
        self.matrix = np.round(np.asarray(matrix, dtype=np.float32), 1)

    def search(self, query: np.ndarray, top_k: int) -> tuple[np.ndarray, np.ndarray]:
        scores = self.matrix @ np.round(query.astype(np.float32), 1)
        order = np.argsort(-scores, kind="stable")[:top_k]
        return order, scores[order]
