from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PIL import Image
from scipy import ndimage

from ml.data.boxes import Box, nms


@dataclass(frozen=True, slots=True)
class ComponentDetectorConfig:
    model_version: str = "component-detector-qualification-v1.0.0"
    foreground_distance: float = 38.0
    minimum_component_area: int = 120
    confidence_threshold: float = 0.35
    nms_iou_threshold: float = 0.45
    maximum_detections: int = 250


class QualificationComponentDetector:
    def __init__(self, config: ComponentDetectorConfig) -> None:
        self.config = config

    def candidates(self, image: Image.Image) -> tuple[list[Box], list[float]]:
        pixels = np.asarray(image.convert("RGB"), dtype=np.float32)
        background = np.asarray([8.0, 13.0, 19.0], dtype=np.float32)
        distance = np.linalg.norm(pixels - background, axis=2)
        brightness = pixels.mean(axis=2)
        mask = (distance >= self.config.foreground_distance) & (brightness >= 55)
        mask = ndimage.binary_opening(mask, structure=np.ones((3, 3)))
        mask = ndimage.binary_closing(mask, structure=np.ones((3, 3)))
        labels, count = ndimage.label(mask)
        boxes: list[Box] = []
        scores: list[float] = []
        for component_id in range(1, count + 1):
            ys, xs = np.where(labels == component_id)
            if len(xs) < self.config.minimum_component_area:
                continue
            box = Box(
                float(xs.min()), float(ys.min()), float(xs.max() + 1), float(ys.max() + 1)
            )
            if box.width < 8 or box.height < 18:
                continue
            compactness = min(1.0, len(xs) / max(box.area, 1.0))
            score = min(0.99, 0.45 + 0.5 * compactness)
            if score >= self.config.confidence_threshold:
                boxes.append(box)
                scores.append(score)
        keep = nms(boxes, scores, self.config.nms_iou_threshold)
        keep = keep[: self.config.maximum_detections]
        return [boxes[index] for index in keep], [scores[index] for index in keep]
