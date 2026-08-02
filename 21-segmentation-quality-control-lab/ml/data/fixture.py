from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from PIL import Image


def _scratch_mask(
    height: int,
    width: int,
    rng: np.random.Generator,
    variant: int,
) -> np.ndarray:
    yy, xx = np.mgrid[:height, :width]
    mask = np.zeros((height, width), dtype=bool)
    if variant % 3 == 0:
        slope = rng.uniform(-0.35, 0.35)
        intercept = rng.uniform(height * 0.25, height * 0.75)
        thickness = rng.integers(1, 3)
        distance = np.abs(yy - (slope * xx + intercept))
        mask = (distance <= thickness) & (xx > width * 0.12) & (xx < width * 0.9)
    elif variant % 3 == 1:
        cx = rng.uniform(width * 0.25, width * 0.75)
        cy = rng.uniform(height * 0.25, height * 0.75)
        rx = rng.uniform(width * 0.04, width * 0.11)
        ry = rng.uniform(height * 0.04, height * 0.13)
        mask = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1
    else:
        x0 = int(rng.integers(width // 5, width * 3 // 5))
        y0 = int(rng.integers(height // 5, height * 3 // 5))
        defect_height = int(rng.integers(3, 9))
        defect_width = int(rng.integers(8, 24))
        mask[y0 : y0 + defect_height, x0 : x0 + defect_width] = True
    return mask.astype(np.uint8)


def make_surface(
    *,
    seed: int,
    defective: bool,
    variant: int,
    height: int = 96,
    width: int = 144,
) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[:height, :width]
    base = 154 + 7 * np.sin(xx / 8.0) + 4 * np.cos(yy / 13.0)
    illumination = np.linspace(-10, 12, width, dtype=np.float32)[None, :]
    grain = rng.normal(0, 5.5, size=(height, width))
    image = base + illumination + grain
    mask = np.zeros((height, width), dtype=np.uint8)
    if defective:
        mask = _scratch_mask(height, width, rng, variant)
        defect_delta = rng.uniform(48, 76)
        image = np.where(mask == 1, image - defect_delta, image)
        halo = np.roll(mask, 1, axis=0) | np.roll(mask, -1, axis=0)
        image = np.where((halo == 1) & (mask == 0), image - defect_delta * 0.15, image)
    image = np.clip(image, 0, 255).astype(np.uint8)
    return image, mask


def build_qualification_dataset(root: Path, *, seed: int = 21021) -> list[dict[str, object]]:
    samples_root = root / "data" / "samples"
    images_root = samples_root / "images"
    masks_root = samples_root / "masks"
    manifests_root = root / "data" / "manifests"
    for directory in (images_root, masks_root, manifests_root):
        directory.mkdir(parents=True, exist_ok=True)

    plan = [("train", 24, 8), ("validation", 12, 4), ("showcase", 8, 4)]
    records: list[dict[str, object]] = []
    index = 0
    for split, count, defective_count in plan:
        for offset in range(count):
            defective = offset < defective_count
            sample_id = f"surface-{index:03d}"
            image, mask = make_surface(
                seed=seed + index * 17,
                defective=defective,
                variant=index,
            )
            image_path = images_root / f"{sample_id}.png"
            mask_path = masks_root / f"{sample_id}.png"
            Image.fromarray(image, mode="L").save(image_path)
            Image.fromarray(mask * 255, mode="L").save(mask_path)
            area = int(mask.sum())
            records.append(
                {
                    "sample_id": sample_id,
                    "split": split,
                    "image_path": image_path.relative_to(root).as_posix(),
                    "mask_path": mask_path.relative_to(root).as_posix(),
                    "defective": defective,
                    "defect_area_px": area,
                    "defect_area_ratio": round(area / mask.size, 8),
                    "height": int(image.shape[0]),
                    "width": int(image.shape[1]),
                }
            )
            index += 1

    fields = list(records[0])
    with (manifests_root / "qualification_manifest.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)

    profile = {
        "profile": "procedural_qualification",
        "seed": seed,
        "images": len(records),
        "defective_images": sum(bool(row["defective"]) for row in records),
        "clean_images": sum(not bool(row["defective"]) for row in records),
        "official_dataset": "NOT_ACQUIRED",
        "official_test": "LOCKED_NOT_ACQUIRED",
        "warning": "Procedural evidence is not KSDD2 benchmark evidence.",
    }
    (manifests_root / "dataset_profile.json").write_text(
        json.dumps(profile, indent=2) + "\n", encoding="utf-8"
    )
    return records


def read_manifest(root: Path) -> list[dict[str, object]]:
    path = root / "data" / "manifests" / "qualification_manifest.csv"
    records: list[dict[str, object]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            records.append(
                {
                    **row,
                    "defective": row["defective"].lower() == "true",
                    "defect_area_px": int(row["defect_area_px"]),
                    "defect_area_ratio": float(row["defect_area_ratio"]),
                    "height": int(row["height"]),
                    "width": int(row["width"]),
                }
            )
    return records
