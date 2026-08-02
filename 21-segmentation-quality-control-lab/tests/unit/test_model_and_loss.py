from __future__ import annotations

import torch

from ml.losses.segmentation import BCEWithDiceLoss, soft_dice_loss
from ml.models.unet import SmallUNet, count_trainable_parameters


def test_small_unet_preserves_spatial_shape() -> None:
    model = SmallUNet()
    output = model(torch.zeros(2, 1, 64, 96))
    assert output.shape == (2, 1, 64, 96)
    assert count_trainable_parameters(model) == 29_481


def test_dice_and_combined_loss_are_finite_and_differentiable() -> None:
    logits = torch.zeros(1, 1, 4, 4, requires_grad=True)
    target = torch.zeros_like(logits)
    target[:, :, 1:3, 1:3] = 1
    dice = soft_dice_loss(logits, target)
    combined = BCEWithDiceLoss()(logits, target)
    combined.backward()
    assert torch.isfinite(dice)
    assert torch.isfinite(combined)
    assert logits.grad is not None
