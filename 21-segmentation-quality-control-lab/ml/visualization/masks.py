from __future__ import annotations

import base64
import io

import numpy as np
from PIL import Image
from scipy import ndimage


def probability_heatmap(probability: np.ndarray) -> np.ndarray:
    clipped = np.clip(probability, 0.0, 1.0)
    red = np.clip(255 * (clipped - 0.35) / 0.65, 0, 255)
    green = np.clip(255 * np.minimum(clipped / 0.6, 1.0), 0, 255)
    blue = np.clip(230 * (1.0 - clipped) + 20, 0, 255)
    return np.stack([red, green, blue], axis=2).astype(np.uint8)


def binary_mask_rgb(mask: np.ndarray) -> np.ndarray:
    binary = mask.astype(bool)
    output = np.zeros((*binary.shape, 3), dtype=np.uint8)
    output[..., 0] = np.where(binary, 255, 12)
    output[..., 1] = np.where(binary, 166, 20)
    output[..., 2] = np.where(binary, 44, 24)
    return output


def overlay_mask(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    grayscale = image if image.ndim == 2 else np.mean(image[..., :3], axis=2)
    base = np.stack([grayscale, grayscale, grayscale], axis=2).astype(np.float32)
    binary = mask.astype(bool)
    color = np.zeros_like(base)
    color[..., 0] = 255
    color[..., 1] = 116
    color[..., 2] = 48
    output = np.where(binary[..., None], base * 0.35 + color * 0.65, base)
    boundary = binary ^ ndimage.binary_erosion(binary)
    output[boundary] = np.array([255, 235, 170], dtype=np.float32)
    return np.clip(output, 0, 255).astype(np.uint8)


def image_data_uri(image: np.ndarray) -> str:
    array = image
    if array.dtype != np.uint8:
        array = np.clip(array, 0, 255).astype(np.uint8)
    mode = "L" if array.ndim == 2 else "RGB"
    buffer = io.BytesIO()
    Image.fromarray(array, mode=mode).save(buffer, format="PNG", optimize=True)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{encoded}"
