from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

from ml.baselines.opencv import MorphologyConfig, segment_with_morphology
from ml.data.contracts import load_binary_mask, load_grayscale
from ml.data.fixture import read_manifest
from ml.evaluation.metrics import aggregate_pixel_metrics, piece_metrics
from ml.evaluation.policy import InspectionPolicy, evaluate_mask
from ml.visualization.masks import overlay_mask

ROOT = Path(__file__).resolve().parents[1]


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_data_analysis() -> dict[str, object]:
    records = read_manifest(ROOT)
    split_counts = Counter(str(row["split"]) for row in records)
    defect_areas = [float(row["defect_area_ratio"]) for row in records if row["defective"]]
    clean = sum(not bool(row["defective"]) for row in records)
    images = [load_grayscale(ROOT / str(row["image_path"])) for row in records]
    analysis = {
        "profile": "procedural_qualification",
        "images": len(records),
        "split_counts": dict(split_counts),
        "defective_images": len(records) - clean,
        "clean_images": clean,
        "clean_to_defect_ratio": round(clean / max(1, len(records) - clean), 4),
        "image_shapes": sorted({f"{image.shape[0]}x{image.shape[1]}" for image in images}),
        "defect_area_ratio": {
            "minimum": round(min(defect_areas), 8),
            "median": round(float(np.median(defect_areas)), 8),
            "maximum": round(max(defect_areas), 8),
        },
        "warning": "Procedural EDA is software evidence, not KSDD2 distribution evidence.",
    }
    _write_json(ROOT / "reports" / "metrics" / "data_analysis.json", analysis)
    return analysis


def build_contact_sheet() -> None:
    records = [row for row in read_manifest(ROOT) if row["split"] == "validation"]
    tiles: list[Image.Image] = []
    for row in records:
        image = load_grayscale(ROOT / str(row["image_path"]))
        mask = load_binary_mask(ROOT / str(row["mask_path"]))
        tile = Image.fromarray(overlay_mask(image, mask)).resize((288, 192))
        tiles.append(ImageOps.expand(tile, border=2, fill="#173d35"))
    sheet = Image.new("RGB", (4 * 292, 3 * 196), "#06100e")
    for index, tile in enumerate(tiles):
        sheet.paste(tile, ((index % 4) * 292, (index // 4) * 196))
    path = ROOT / "reports" / "figures" / "validation-contact-sheet.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(path)


def build_morphology_sensitivity() -> list[dict[str, object]]:
    records = [row for row in read_manifest(ROOT) if row["split"] == "validation"]
    images = [load_grayscale(ROOT / str(row["image_path"])) for row in records]
    targets = [load_binary_mask(ROOT / str(row["mask_path"])) for row in records]
    actual = [bool(target.any()) for target in targets]
    policy = InspectionPolicy()
    rows: list[dict[str, object]] = []
    for kernel_size in (3, 5, 7):
        predictions = [
            segment_with_morphology(image, MorphologyConfig(kernel_size=kernel_size))
            for image in images
        ]
        predicted_piece = [evaluate_mask(mask, policy).defect_detected for mask in predictions]
        rows.append(
            {
                "kernel_size": kernel_size,
                "pixel_metrics": aggregate_pixel_metrics(
                    [mask.astype(np.float32) for mask in predictions], targets, threshold=0.5
                ),
                "piece_metrics": piece_metrics(predicted_piece, actual),
            }
        )
    _write_json(ROOT / "reports" / "metrics" / "morphology_sensitivity.json", rows)
    return rows


def main() -> None:
    analysis = build_data_analysis()
    build_contact_sheet()
    morphology = build_morphology_sensitivity()
    print(
        json.dumps(
            {
                "status": "passed",
                "images": analysis["images"],
                "morphology_variants": len(morphology),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
