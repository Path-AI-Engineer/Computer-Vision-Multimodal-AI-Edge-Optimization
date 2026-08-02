from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image


class MaskContractError(ValueError):
    """Raised when an image/mask pair violates the pixel-alignment contract."""


@dataclass(frozen=True)
class PairedSample:
    sample_id: str
    image_path: Path
    mask_path: Path
    split: str
    defective: bool
    defect_area_px: int
    defect_area_ratio: float


def load_grayscale(path: str | Path) -> np.ndarray:
    with Image.open(path) as image:
        return np.asarray(image.convert("L"), dtype=np.uint8)


def load_binary_mask(path: str | Path) -> np.ndarray:
    with Image.open(path) as image:
        raw = np.asarray(image.convert("L"), dtype=np.uint8)
    return normalize_binary_mask(raw)


def normalize_binary_mask(mask: np.ndarray) -> np.ndarray:
    if mask.ndim != 2:
        raise MaskContractError("A segmentation mask must have shape HxW.")
    values = set(np.unique(mask).tolist())
    if not values.issubset({0, 1, 255}):
        raise MaskContractError(f"Mask values must be binary; observed {sorted(values)}.")
    return (mask > 0).astype(np.uint8)


def validate_pair(image: np.ndarray, mask: np.ndarray) -> None:
    normalized = normalize_binary_mask(mask)
    if image.ndim not in {2, 3}:
        raise MaskContractError("An image must be grayscale HxW or color HxWxC.")
    if image.shape[:2] != normalized.shape:
        raise MaskContractError(
            f"Image and mask dimensions must match; got {image.shape[:2]} and {mask.shape}."
        )


def resize_pair(
    image: np.ndarray,
    mask: np.ndarray,
    *,
    size: tuple[int, int],
) -> tuple[np.ndarray, np.ndarray]:
    validate_pair(image, mask)
    height, width = size
    resized_image = np.asarray(
        Image.fromarray(image).resize((width, height), Image.Resampling.BILINEAR),
        dtype=np.uint8,
    )
    resized_mask = np.asarray(
        Image.fromarray((mask > 0).astype(np.uint8)).resize(
            (width, height), Image.Resampling.NEAREST
        ),
        dtype=np.uint8,
    )
    return resized_image, normalize_binary_mask(resized_mask)


def restore_mask(mask: np.ndarray, *, original_size: tuple[int, int]) -> np.ndarray:
    normalized = normalize_binary_mask(mask)
    height, width = original_size
    restored = np.asarray(
        Image.fromarray(normalized).resize((width, height), Image.Resampling.NEAREST),
        dtype=np.uint8,
    )
    return normalize_binary_mask(restored)
