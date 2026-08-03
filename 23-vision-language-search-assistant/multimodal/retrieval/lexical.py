from __future__ import annotations

import math
from collections import Counter

import numpy as np

from multimodal.core.contracts import CorpusItem
from multimodal.encoders.qualification import tokenize


class TfidfCaptionIndex:
    def __init__(self, items: tuple[CorpusItem, ...]) -> None:
        self.documents = [tokenize(" ".join(c.text for c in item.captions)) for item in items]
        document_frequency = Counter(token for doc in self.documents for token in set(doc))
        count = len(self.documents)
        self.idf = {
            token: math.log((1 + count) / (1 + frequency)) + 1
            for token, frequency in document_frequency.items()
        }

    def score(self, query: str) -> np.ndarray:
        query_tokens = tokenize(query)
        if not query_tokens:
            return np.zeros(len(self.documents), dtype=np.float32)
        scores: list[float] = []
        for document in self.documents:
            frequencies = Counter(document)
            raw = sum(frequencies[token] * self.idf.get(token, 0.0) for token in query_tokens)
            scores.append(raw / max(len(document), 1))
        values = np.asarray(scores, dtype=np.float32)
        maximum = float(values.max(initial=0.0))
        return values / maximum if maximum else values
