from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from ml.data.boxes import Box


def write_overlay(
    image_path: Path,
    truth: list[Box],
    predicted: list[Box],
    destination: Path,
) -> None:
    with Image.open(image_path) as source:
        image = source.convert("RGB")
    draw = ImageDraw.Draw(image)
    for box in truth:
        draw.rectangle(box.as_list(), outline=(74, 222, 190), width=2)
    for box in predicted:
        draw.rectangle(box.as_list(), outline=(255, 172, 64), width=2)
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination)
