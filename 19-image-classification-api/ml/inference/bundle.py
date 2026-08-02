from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
from PIL import Image

from ml.evaluation.calibration import softmax
from ml.features.hog import extract_hog_rgb


@dataclass(slots=True)
class QualificationBundle:
    classifier: object
    labels: tuple[str, ...]
    temperature: float
    model_version: str
    preprocessing_version: str
    artifact_version: str
    abstention_threshold: float

    def probabilities(self, image: Image.Image) -> np.ndarray:
        features = extract_hog_rgb(image).reshape(1, -1)
        logits = np.asarray(self.classifier.decision_function(features), dtype=np.float64)
        if logits.ndim == 1:
            logits = logits.reshape(1, -1)
        return softmax(logits / self.temperature)[0]

    def save(self, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, destination)

    @classmethod
    def load(cls, source: Path) -> QualificationBundle:
        bundle = joblib.load(source)
        if not isinstance(bundle, cls):
            raise TypeError("The model artifact is not a QualificationBundle.")
        return bundle
