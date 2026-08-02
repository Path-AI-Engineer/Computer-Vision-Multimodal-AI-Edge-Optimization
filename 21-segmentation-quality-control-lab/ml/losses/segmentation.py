from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F


def soft_dice_loss(
    logits: torch.Tensor, targets: torch.Tensor, epsilon: float = 1e-6
) -> torch.Tensor:
    probabilities = torch.sigmoid(logits)
    dimensions = tuple(range(1, probabilities.ndim))
    intersection = torch.sum(probabilities * targets, dim=dimensions)
    denominator = torch.sum(probabilities, dim=dimensions) + torch.sum(targets, dim=dimensions)
    dice = (2 * intersection + epsilon) / (denominator + epsilon)
    return 1 - dice.mean()


class BCEWithDiceLoss(nn.Module):
    def __init__(self, bce_weight: float = 0.55, dice_weight: float = 0.45) -> None:
        super().__init__()
        if abs(bce_weight + dice_weight - 1.0) > 1e-6:
            raise ValueError("Loss weights must sum to one.")
        self.bce_weight = bce_weight
        self.dice_weight = dice_weight

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        bce = F.binary_cross_entropy_with_logits(logits, targets)
        return self.bce_weight * bce + self.dice_weight * soft_dice_loss(logits, targets)
