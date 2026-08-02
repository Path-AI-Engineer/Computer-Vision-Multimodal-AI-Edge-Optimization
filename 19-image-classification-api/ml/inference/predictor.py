from __future__ import annotations

import time
import uuid
from dataclasses import dataclass

from PIL import Image

from ml.data.contracts import BREED_TO_SPECIES
from ml.inference.bundle import QualificationBundle


@dataclass(slots=True)
class PetBreedPredictor:
    bundle: QualificationBundle

    def predict(self, image: Image.Image, top_k: int = 5) -> dict[str, object]:
        started = time.perf_counter()
        probabilities = self.bundle.probabilities(image)
        order = probabilities.argsort()[::-1][:top_k]
        items = [
            {
                "class_id": int(index),
                "class_name": self.bundle.labels[int(index)],
                "species": BREED_TO_SPECIES[self.bundle.labels[int(index)]],
                "probability": round(float(probabilities[int(index)]), 6),
            }
            for index in order
        ]
        confidence = float(items[0]["probability"])
        return {
            "request_id": str(uuid.uuid4()),
            "model_version": self.bundle.model_version,
            "class_id": items[0]["class_id"],
            "class_name": items[0]["class_name"],
            "species": items[0]["species"],
            "top_k": items,
            "confidence": confidence,
            "abstained": confidence < self.bundle.abstention_threshold,
            "threshold": self.bundle.abstention_threshold,
            "preprocessing_version": self.bundle.preprocessing_version,
            "latency_ms": round((time.perf_counter() - started) * 1_000, 3),
            "warnings": [
                "Qualification fixture only; this output is not veterinary advice.",
                "Confidence is model probability, not a guarantee of correctness.",
            ],
            "explanation": {
                "available": False,
                "reason": (
                    "Grad-CAM applies to CNN/ResNet candidates, not the selected HOG bundle."
                ),
            },
        }
