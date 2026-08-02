from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import ndimage


@dataclass(frozen=True)
class MorphologyConfig:
    residual_threshold: float = 19.0
    kernel_size: int = 3
    opening_iterations: int = 1
    closing_iterations: int = 1
    minimum_component_area: int = 6


def _remove_small_components(mask: np.ndarray, minimum_area: int) -> np.ndarray:
    labels, count = ndimage.label(mask)
    output = np.zeros_like(mask, dtype=np.uint8)
    for label_id in range(1, count + 1):
        component = labels == label_id
        if int(component.sum()) >= minimum_area:
            output[component] = 1
    return output


def segment_with_morphology(
    image: np.ndarray,
    config: MorphologyConfig | None = None,
) -> np.ndarray:
    config = config or MorphologyConfig()
    if image.ndim == 3:
        image = np.mean(image[..., :3], axis=2)
    grayscale = image.astype(np.float32)

    try:
        import cv2

        background = cv2.GaussianBlur(grayscale, (0, 0), sigmaX=4.0)
        residual = background - grayscale
        raw = (residual >= config.residual_threshold).astype(np.uint8)
        kernel = np.ones((config.kernel_size, config.kernel_size), dtype=np.uint8)
        opened = cv2.morphologyEx(
            raw,
            cv2.MORPH_OPEN,
            kernel,
            iterations=config.opening_iterations,
        )
        closed = cv2.morphologyEx(
            opened,
            cv2.MORPH_CLOSE,
            kernel,
            iterations=config.closing_iterations,
        )
    except ImportError:
        background = ndimage.gaussian_filter(grayscale, sigma=4.0)
        residual = background - grayscale
        structure = np.ones((config.kernel_size, config.kernel_size), dtype=bool)
        closed = ndimage.binary_closing(
            ndimage.binary_opening(
                residual >= config.residual_threshold,
                structure=structure,
                iterations=config.opening_iterations,
            ),
            structure=structure,
            iterations=config.closing_iterations,
        ).astype(np.uint8)
    return _remove_small_components(closed, config.minimum_component_area)


def always_clean(image: np.ndarray) -> np.ndarray:
    return np.zeros(image.shape[:2], dtype=np.uint8)
