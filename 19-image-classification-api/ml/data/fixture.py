from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageOps

from ml.data.contracts import BREED_TO_SPECIES, BREEDS


def generate_qualification_fixture(
    destination: Path, samples_per_class: int = 6, seed: int = 190505
) -> list[dict[str, object]]:
    destination.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    for class_id, breed in enumerate(BREEDS):
        for sample_index in range(samples_per_class):
            image = _render_sample(class_id, sample_index, seed)
            filename = f"breed-{class_id:02d}-sample-{sample_index:02d}.png"
            path = destination / filename
            image.save(path, format="PNG", optimize=True)
            records.append(
                {
                    "sample_id": path.stem,
                    "path": path.as_posix(),
                    "filename": filename,
                    "class_id": class_id,
                    "class_name": breed,
                    "species": BREED_TO_SPECIES[breed],
                    "width": image.width,
                    "height": image.height,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "source": "procedural_qualification_fixture",
                }
            )
    return records


def _render_sample(class_id: int, sample_index: int, seed: int) -> Image.Image:
    rng = np.random.default_rng(seed + class_id * 1_003 + sample_index * 37)
    base = np.array(
        [
            46 + (class_id * 47) % 170,
            42 + (class_id * 71) % 170,
            54 + (class_id * 97) % 160,
        ],
        dtype=np.uint8,
    )
    image = Image.new("RGB", (180, 180), tuple(int(value) for value in base))
    draw = ImageDraw.Draw(image)
    face = tuple(int(value) for value in np.clip(base + rng.integers(-35, 55, 3), 15, 245))
    margin = 26 + class_id % 11
    draw.ellipse((margin, 35, 180 - margin, 164), fill=face, outline=(238, 242, 246), width=3)
    ear_height = 18 + (class_id * 5) % 34
    draw.polygon([(42, 62), (58, ear_height), (76, 70)], fill=face)
    draw.polygon([(104, 70), (123, ear_height + class_id % 8), (140, 62)], fill=face)
    eye_y = 88 + sample_index % 4
    eye_gap = 25 + class_id % 9
    for x in (90 - eye_gap, 90 + eye_gap):
        draw.ellipse((x - 6, eye_y - 6, x + 6, eye_y + 6), fill=(10, 18, 28))
        draw.ellipse((x - 2, eye_y - 3, x + 1, eye_y), fill=(245, 250, 255))
    nose_width = 9 + class_id % 8
    draw.polygon(
        [(90 - nose_width, 113), (90 + nose_width, 113), (90, 123 + class_id % 5)],
        fill=(24, 20, 25),
    )
    stripe_count = 2 + class_id % 6
    for stripe in range(stripe_count):
        x = 48 + stripe * (82 // max(stripe_count - 1, 1))
        offset = int(rng.integers(-5, 6))
        draw.line((x + offset, 47, 90, 106), fill=(255, 255, 255), width=2)
    if class_id % 3 == 0:
        draw.arc((55, 110, 125, 150), 15, 165, fill=(250, 250, 250), width=3)
    image = ImageEnhance.Brightness(image).enhance(0.9 + sample_index * 0.035)
    if sample_index % 2:
        image = ImageOps.mirror(image)
    return image
