from __future__ import annotations

import re

import numpy as np

DIMENSIONS = (
    "people",
    "animal",
    "water",
    "urban",
    "nature",
    "food",
    "transport",
    "night",
    "warm_color",
    "cool_color",
    "action",
    "indoor",
)

VOCABULARY: dict[str, tuple[str, ...]] = {
    "people": ("person", "people", "child", "chef", "hiker", "cyclist", "woman", "man"),
    "animal": ("animal", "dog", "cat", "horse", "bird", "birds"),
    "water": ("water", "beach", "sea", "harbor", "lake", "wetland", "boat"),
    "urban": ("city", "street", "market", "station", "skyline", "building"),
    "nature": ("nature", "field", "mountain", "meadow", "forest", "grass"),
    "food": ("food", "fruit", "market", "kitchen", "chef", "vegetable"),
    "transport": ("train", "bicycle", "cyclist", "boat", "station", "transport"),
    "night": ("night", "dark", "rain", "lights", "evening"),
    "warm_color": ("red", "orange", "yellow", "sunset", "warm"),
    "cool_color": ("blue", "green", "teal", "cool", "water"),
    "action": ("running", "riding", "flying", "walking", "cooking", "playing", "hiking"),
    "indoor": ("indoor", "inside", "window", "kitchen", "room"),
}


def tokenize(text: str) -> tuple[str, ...]:
    return tuple(re.findall(r"[a-z0-9]+", text.lower()))


def normalize(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    return vector / norm if norm else vector


class QualificationDualEncoder:
    """Deterministic contract adapter used when CLIP weights are not bundled.

    It exercises the shared-space, normalization and ranking contracts without
    claiming that its scores are produced by OpenAI CLIP or OpenCLIP.
    """

    model_version = "qualification-dual-encoder-v1"
    dimension = len(DIMENSIONS)
    dtype = "float32"

    def encode_text(self, text: str) -> np.ndarray:
        tokens = set(tokenize(text))
        values = np.array(
            [sum(1.0 for word in words if word in tokens) for words in VOCABULARY.values()],
            dtype=np.float32,
        )
        return normalize(values)

    def encode_vector(self, values: tuple[float, ...]) -> np.ndarray:
        vector = np.asarray(values, dtype=np.float32)
        if vector.shape != (self.dimension,):
            raise ValueError(f"Expected a {self.dimension}-dimensional embedding.")
        return normalize(vector)
