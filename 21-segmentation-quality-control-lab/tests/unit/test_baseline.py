from __future__ import annotations

import numpy as np

from ml.baselines.opencv import always_clean, segment_with_morphology


def test_baselines_return_binary_mask_with_source_shape() -> None:
    image = np.full((48, 72), 180, dtype=np.uint8)
    image[20:28, 28:45] = 35
    clean = always_clean(image)
    morphology = segment_with_morphology(image)
    assert clean.shape == morphology.shape == image.shape
    assert set(np.unique(morphology)).issubset({0, 1})
    assert not clean.any()
    assert morphology.any()
