from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image

from ml.data.contracts import load_binary_mask, validate_pair


@dataclass(frozen=True)
class KSDD2Validation:
    images: int
    masks: int
    defective: int
    clean: int
    checksum: str


def validate_ksdd2(root: Path) -> KSDD2Validation:
    if not root.exists():
        raise FileNotFoundError(f"KSDD2 root does not exist: {root}")
    image_files = sorted(
        path for path in root.rglob("*.png") if "mask" not in path.stem.lower()
    )
    if not image_files:
        raise ValueError("No KSDD2 PNG images were found.")

    digest = hashlib.sha256()
    defective = 0
    masks = 0
    for image_path in image_files:
        mask_candidates = [
            image_path.with_name(f"{image_path.stem}_mask.png"),
            image_path.parent / "masks" / image_path.name,
        ]
        mask_path = next(
            (candidate for candidate in mask_candidates if candidate.exists()), None
        )
        if mask_path is None:
            raise ValueError(f"Missing paired mask for {image_path}.")
        with Image.open(image_path) as image:
            image_array = np.asarray(image.convert("L"))
        mask = load_binary_mask(mask_path)
        validate_pair(image_array, mask)
        defective += int(mask.any())
        masks += 1
        digest.update(image_path.read_bytes())
        digest.update(mask_path.read_bytes())

    return KSDD2Validation(
        images=len(image_files),
        masks=masks,
        defective=defective,
        clean=len(image_files) - defective,
        checksum=digest.hexdigest(),
    )
