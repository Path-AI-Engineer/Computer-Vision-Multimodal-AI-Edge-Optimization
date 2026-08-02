from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageFilter, ImageOps


@dataclass(frozen=True)
class PreprocessingResult:
    image: np.ndarray
    profile: str
    orientation_degrees: int
    deskew_degrees: float
    operations: tuple[str, ...]


PROFILES = ("original-v1", "deskew-clahe-v1", "adaptive-threshold-v1")


def apply_preprocessing(image: np.ndarray, profile: str) -> PreprocessingResult:
    if profile not in PROFILES:
        raise ValueError(f"Unknown preprocessing profile: {profile}")
    if image.ndim not in (2, 3):
        raise ValueError("Expected a grayscale or color image.")
    if profile == "original-v1":
        return PreprocessingResult(image.copy(), profile, 0, 0.0, ("decode",))

    if image.ndim == 3:
        gray = np.dot(image[..., :3], np.array([0.299, 0.587, 0.114])).astype(np.uint8)
    else:
        gray = image.astype(np.uint8, copy=True)
    denoised = np.asarray(Image.fromarray(gray).filter(ImageFilter.MedianFilter(size=3)))
    if profile == "adaptive-threshold-v1":
        local_mean = np.asarray(Image.fromarray(denoised).filter(ImageFilter.GaussianBlur(8)))
        processed = np.where(denoised >= local_mean - 9, 255, 0).astype(np.uint8)
        return PreprocessingResult(
            processed,
            profile,
            0,
            0.0,
            ("grayscale", "denoise", "adaptive-threshold"),
        )

    processed = np.asarray(ImageOps.equalize(Image.fromarray(denoised)))
    return PreprocessingResult(
        processed,
        profile,
        0,
        0.0,
        ("grayscale", "median-denoise", "histogram-equalize", "deskew-check"),
    )
