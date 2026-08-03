from __future__ import annotations

import numpy as np

from multimodal.core.contracts import CorpusItem
from multimodal.encoders.qualification import QualificationDualEncoder


class EmbeddingStore:
    def __init__(self, items: tuple[CorpusItem, ...], encoder: QualificationDualEncoder) -> None:
        self.items = items
        self.ids = tuple(item.image_id for item in items)
        self.matrix = np.vstack([encoder.encode_vector(item.vector) for item in items])
        self.by_id = {item.image_id: index for index, item in enumerate(items)}

    def vector_for(self, image_id: str) -> np.ndarray:
        if image_id not in self.by_id:
            raise KeyError(image_id)
        return self.matrix[self.by_id[image_id]].copy()
