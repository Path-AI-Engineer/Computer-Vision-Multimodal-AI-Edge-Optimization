from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.utils.data import Dataset

from ml.data.contracts import load_binary_mask, load_grayscale, resize_pair


class SurfaceDataset(Dataset[tuple[torch.Tensor, torch.Tensor, str]]):
    def __init__(
        self,
        root: Path,
        records: list[dict[str, Any]],
        *,
        size: tuple[int, int] = (64, 96),
        augment: bool = False,
    ) -> None:
        self.root = root
        self.records = records
        self.size = size
        self.augment = augment

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor, str]:
        record = self.records[index]
        image = load_grayscale(self.root / str(record["image_path"]))
        mask = load_binary_mask(self.root / str(record["mask_path"]))
        image, mask = resize_pair(image, mask, size=self.size)
        if self.augment and index % 2:
            image = np.flip(image, axis=1).copy()
            mask = np.flip(mask, axis=1).copy()
        normalized = (image.astype(np.float32) - 150.0) / 45.0
        image_tensor = torch.from_numpy(normalized).unsqueeze(0)
        mask_tensor = torch.from_numpy(mask.astype(np.float32)).unsqueeze(0)
        return image_tensor, mask_tensor, str(record["sample_id"])
