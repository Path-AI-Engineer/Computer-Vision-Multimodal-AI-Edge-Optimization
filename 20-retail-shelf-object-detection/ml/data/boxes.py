from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Box:
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def width(self) -> float:
        return max(0.0, self.x2 - self.x1)

    @property
    def height(self) -> float:
        return max(0.0, self.y2 - self.y1)

    @property
    def area(self) -> float:
        return self.width * self.height

    def validate(self) -> None:
        if self.x2 <= self.x1 or self.y2 <= self.y1:
            raise ValueError("Bounding boxes must have positive width and height.")

    def clip(self, width: int, height: int) -> Box:
        clipped = Box(
            max(0.0, min(float(width), self.x1)),
            max(0.0, min(float(height), self.y1)),
            max(0.0, min(float(width), self.x2)),
            max(0.0, min(float(height), self.y2)),
        )
        clipped.validate()
        return clipped

    def to_yolo(self, width: int, height: int) -> tuple[float, float, float, float]:
        self.validate()
        return (
            ((self.x1 + self.x2) / 2) / width,
            ((self.y1 + self.y2) / 2) / height,
            self.width / width,
            self.height / height,
        )

    @classmethod
    def from_yolo(
        cls, values: tuple[float, float, float, float], width: int, height: int
    ) -> Box:
        cx, cy, box_width, box_height = values
        absolute_width, absolute_height = box_width * width, box_height * height
        return cls(
            cx * width - absolute_width / 2,
            cy * height - absolute_height / 2,
            cx * width + absolute_width / 2,
            cy * height + absolute_height / 2,
        ).clip(width, height)

    def as_list(self) -> list[float]:
        return [round(self.x1, 3), round(self.y1, 3), round(self.x2, 3), round(self.y2, 3)]


def iou(left: Box, right: Box) -> float:
    intersection_width = max(0.0, min(left.x2, right.x2) - max(left.x1, right.x1))
    intersection_height = max(0.0, min(left.y2, right.y2) - max(left.y1, right.y1))
    intersection = intersection_width * intersection_height
    union = left.area + right.area - intersection
    return intersection / union if union else 0.0


def nms(boxes: list[Box], scores: list[float], threshold: float) -> list[int]:
    if len(boxes) != len(scores):
        raise ValueError("Boxes and scores must have the same length.")
    remaining = sorted(range(len(boxes)), key=lambda index: scores[index], reverse=True)
    kept: list[int] = []
    while remaining:
        selected = remaining.pop(0)
        kept.append(selected)
        remaining = [
            index for index in remaining if iou(boxes[selected], boxes[index]) <= threshold
        ]
    return kept
