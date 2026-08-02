from __future__ import annotations

import numpy as np
import pytest

from ml.data.contracts import (
    MaskContractError,
    normalize_binary_mask,
    resize_pair,
    restore_mask,
)


def test_binary_mask_normalizes_255() -> None:
    mask = np.array([[0, 255], [1, 0]], dtype=np.uint8)
    assert normalize_binary_mask(mask).tolist() == [[0, 1], [1, 0]]


def test_non_binary_mask_is_rejected() -> None:
    with pytest.raises(MaskContractError, match="binary"):
        normalize_binary_mask(np.array([[0, 12]], dtype=np.uint8))


def test_nearest_mask_resize_preserves_binary_labels() -> None:
    image = np.arange(16, dtype=np.uint8).reshape(4, 4)
    mask = np.zeros((4, 4), dtype=np.uint8)
    mask[1:3, 1:3] = 1
    _, resized = resize_pair(image, mask, size=(8, 8))
    restored = restore_mask(resized, original_size=(4, 4))
    assert set(np.unique(resized)) == {0, 1}
    assert restored.shape == mask.shape
    assert np.array_equal(restored, mask)
