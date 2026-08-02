from __future__ import annotations

import time
import uuid
from dataclasses import replace

from PIL import Image

from ml.models.qualification_detector import (
    ComponentDetectorConfig,
    QualificationComponentDetector,
)


class ShelfPredictor:
    def __init__(self, config: ComponentDetectorConfig) -> None:
        self.base_config = config

    def predict(
        self,
        image: Image.Image,
        *,
        confidence: float | None = None,
        nms_iou: float | None = None,
    ) -> dict[str, object]:
        selected = replace(
            self.base_config,
            confidence_threshold=(
                confidence if confidence is not None else self.base_config.confidence_threshold
            ),
            nms_iou_threshold=(
                nms_iou if nms_iou is not None else self.base_config.nms_iou_threshold
            ),
        )
        started = time.perf_counter()
        boxes, scores = QualificationComponentDetector(selected).candidates(image)
        latency = (time.perf_counter() - started) * 1_000
        return {
            "request_id": str(uuid.uuid4()),
            "model_version": selected.model_version,
            "profile": "qualification_smoke",
            "image_width": image.width,
            "image_height": image.height,
            "detections": [
                {
                    "detection_id": index,
                    "class_id": 0,
                    "class_name": "object",
                    "box": box.as_list(),
                    "confidence": round(float(scores[index]), 6),
                }
                for index, box in enumerate(boxes)
            ],
            "visible_count": len(boxes),
            "thresholds": {
                "confidence": selected.confidence_threshold,
                "nms_iou": selected.nms_iou_threshold,
            },
            "latency_ms": round(latency, 3),
            "warnings": [
                "Qualification detector only; not trained on SKU-110K.",
                "Visible count does not represent hidden stock or SKU identity.",
            ],
        }
