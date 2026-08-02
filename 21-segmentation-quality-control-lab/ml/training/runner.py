from __future__ import annotations

import json
import random
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.utils.data import DataLoader

from ml.data.fixture import read_manifest
from ml.losses.segmentation import BCEWithDiceLoss, soft_dice_loss
from ml.models.unet import SmallUNet, count_trainable_parameters
from ml.training.dataset import SurfaceDataset


@dataclass(frozen=True)
class TrainingResult:
    loss_name: str
    checkpoint_path: str
    best_epoch: int
    best_validation_loss: float
    training_seconds: float
    parameters: int
    history: list[dict[str, float | int]]


def _set_determinism(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
    torch.set_num_threads(max(1, min(torch.get_num_threads(), 4)))


def train_small_unet(
    root: Path,
    config: dict[str, Any],
    *,
    loss_name: str = "bce_dice",
) -> TrainingResult:
    seed = int(config["seed"])
    _set_determinism(seed)
    records = read_manifest(root)
    train_records = [record for record in records if record["split"] == "train"]
    validation_records = [record for record in records if record["split"] == "validation"]
    size = (int(config["image_height"]), int(config["image_width"]))
    train_loader = DataLoader(
        SurfaceDataset(root, train_records, size=size, augment=True),
        batch_size=int(config["batch_size"]),
        shuffle=True,
        generator=torch.Generator().manual_seed(seed),
    )
    validation_loader = DataLoader(
        SurfaceDataset(root, validation_records, size=size),
        batch_size=int(config["batch_size"]),
        shuffle=False,
    )
    model = SmallUNet()
    loss_functions = {
        "bce": torch.nn.BCEWithLogitsLoss(),
        "dice": soft_dice_loss,
        "bce_dice": BCEWithDiceLoss(),
    }
    if loss_name not in loss_functions:
        raise ValueError(f"Unknown segmentation loss: {loss_name}")
    loss_function = loss_functions[loss_name]
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(config["learning_rate"]),
        weight_decay=float(config["weight_decay"]),
    )
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=1, factor=0.5)
    history: list[dict[str, float | int]] = []
    best_loss = float("inf")
    best_epoch = 0
    best_state: dict[str, torch.Tensor] | None = None
    stale_epochs = 0
    started = time.perf_counter()
    for epoch in range(1, int(config["epochs"]) + 1):
        model.train()
        train_losses: list[float] = []
        for images, masks, _ in train_loader:
            optimizer.zero_grad(set_to_none=True)
            loss = loss_function(model(images), masks)
            loss.backward()
            optimizer.step()
            train_losses.append(float(loss.detach()))

        model.eval()
        validation_losses: list[float] = []
        with torch.inference_mode():
            for images, masks, _ in validation_loader:
                validation_losses.append(float(loss_function(model(images), masks)))
        validation_loss = float(np.mean(validation_losses))
        scheduler.step(validation_loss)
        history.append(
            {
                "epoch": epoch,
                "train_loss": round(float(np.mean(train_losses)), 6),
                "validation_loss": round(validation_loss, 6),
                "learning_rate": optimizer.param_groups[0]["lr"],
            }
        )
        if validation_loss < best_loss - 1e-5:
            best_loss = validation_loss
            best_epoch = epoch
            best_state = {
                key: value.detach().cpu().clone() for key, value in model.state_dict().items()
            }
            stale_epochs = 0
        else:
            stale_epochs += 1
            if stale_epochs >= int(config["early_stopping_patience"]):
                break

    if best_state is None:
        raise RuntimeError("Training completed without a checkpoint candidate.")
    checkpoint_root = root / "models" / "checkpoints"
    checkpoint_root.mkdir(parents=True, exist_ok=True)
    checkpoint_path = checkpoint_root / f"small-unet-{loss_name}-qualification.pt"
    payload = {
        "state_dict": best_state,
        "model_id": "small-unet",
        "model_version": "small-unet-qualification-v1",
        "input_size": list(size),
        "normalization": {"mean": 150.0, "std": 45.0},
        "training_profile": "procedural_qualification",
        "loss_name": loss_name,
        "seed": seed,
    }
    torch.save(payload, checkpoint_path)
    run_root = root / "reports" / "runs" / f"p21-{loss_name}-qualification-v1"
    run_root.mkdir(parents=True, exist_ok=True)
    (run_root / "history.json").write_text(
        json.dumps(history, indent=2) + "\n", encoding="utf-8"
    )
    result = TrainingResult(
        loss_name=loss_name,
        checkpoint_path=checkpoint_path.relative_to(root).as_posix(),
        best_epoch=best_epoch,
        best_validation_loss=round(best_loss, 6),
        training_seconds=round(time.perf_counter() - started, 4),
        parameters=count_trainable_parameters(model),
        history=history,
    )
    (run_root / "training_summary.json").write_text(
        json.dumps(asdict(result), indent=2) + "\n", encoding="utf-8"
    )
    return result
