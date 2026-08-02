from __future__ import annotations

import numpy as np
from PIL import Image
from skimage.color import rgb2gray
from skimage.feature import hog

from ml.data.transforms import inference_array

FEATURE_VERSION = "hog-rgb-v1"


def extract_hog_rgb(image: Image.Image) -> np.ndarray:
    array = inference_array(image)
    descriptor = hog(
        rgb2gray(array),
        orientations=9,
        pixels_per_cell=(16, 16),
        cells_per_block=(2, 2),
        block_norm="L2-Hys",
        feature_vector=True,
    ).astype(np.float32)
    means = array.mean(axis=(0, 1))
    standard_deviations = array.std(axis=(0, 1))
    lower = np.quantile(array, 0.25, axis=(0, 1))
    upper = np.quantile(array, 0.75, axis=(0, 1))
    return np.concatenate((descriptor, means, standard_deviations, lower, upper)).astype(
        np.float32
    )
