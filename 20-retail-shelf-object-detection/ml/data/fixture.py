from __future__ import annotations

import hashlib
import random
from pathlib import Path

from PIL import Image, ImageDraw

from ml.data.boxes import Box

BACKGROUND = (8, 13, 19)
SHELF = (42, 51, 60)
PALETTE = (
    (225, 76, 65),
    (42, 191, 160),
    (247, 176, 59),
    (91, 120, 224),
    (191, 87, 203),
    (63, 169, 220),
)


def generate_shelf_fixture(
    destination: Path, *, scenes: int = 12, seed: int = 200533
) -> list[dict[str, object]]:
    destination.mkdir(parents=True, exist_ok=True)
    randomizer = random.Random(seed)
    records: list[dict[str, object]] = []
    for scene_index in range(scenes):
        density = ("low", "medium", "high")[scene_index % 3]
        rows = {"low": 3, "medium": 4, "high": 5}[density]
        columns = {"low": 10, "medium": 15, "high": 19}[density]
        image = Image.new("RGB", (960, 540), BACKGROUND)
        draw = ImageDraw.Draw(image)
        boxes: list[Box] = []
        top_margin = 42
        row_height = (450 - top_margin) / rows
        for row in range(rows):
            shelf_y = int(top_margin + (row + 1) * row_height)
            draw.rectangle((20, shelf_y, 940, shelf_y + 9), fill=SHELF)
            cell_width = 900 / columns
            for column in range(columns):
                jitter = randomizer.randint(-2, 2)
                width = max(18, int(cell_width * randomizer.uniform(0.62, 0.84)))
                height = max(35, int(row_height * randomizer.uniform(0.46, 0.74)))
                x1 = int(30 + column * cell_width + (cell_width - width) / 2 + jitter)
                y2 = shelf_y - 2
                y1 = y2 - height
                box = Box(x1, y1, x1 + width, y2)
                boxes.append(box)
                color = PALETTE[(row * columns + column + scene_index) % len(PALETTE)]
                draw.rounded_rectangle(
                    box.as_list(), radius=4, fill=color, outline=(236, 244, 244), width=1
                )
                label_height = max(4, height // 8)
                draw.rectangle(
                    (x1 + 4, y1 + 7, x1 + width - 4, y1 + 7 + label_height),
                    fill=(238, 236, 218),
                )
        image_id = f"qualification-shelf-{scene_index:03d}"
        filename = f"{image_id}.png"
        path = destination / filename
        image.save(path)
        records.append(
            {
                "image_id": image_id,
                "filename": filename,
                "path": path.as_posix(),
                "width": image.width,
                "height": image.height,
                "density": density,
                "boxes": [box.as_list() for box in boxes],
                "visible_count": len(boxes),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
    return records
