from __future__ import annotations

from typing import Literal


def build_resnet18(
    classes: int = 37,
    *,
    weights: Literal["IMAGENET1K_V1"] | None = None,
    frozen_backbone: bool = True,
):
    from torch import nn
    from torchvision.models import ResNet18_Weights, resnet18

    declared_weights = ResNet18_Weights.IMAGENET1K_V1 if weights else None
    model = resnet18(weights=declared_weights)
    if frozen_backbone:
        for parameter in model.parameters():
            parameter.requires_grad = False
    model.fc = nn.Linear(model.fc.in_features, classes)
    return model


def build_vit_b_16(
    classes: int = 37,
    *,
    weights: Literal["IMAGENET1K_V1"] | None = None,
    frozen_backbone: bool = True,
):
    from torch import nn
    from torchvision.models import ViT_B_16_Weights, vit_b_16

    declared_weights = ViT_B_16_Weights.IMAGENET1K_V1 if weights else None
    model = vit_b_16(weights=declared_weights)
    if frozen_backbone:
        for parameter in model.parameters():
            parameter.requires_grad = False
    model.heads.head = nn.Linear(model.heads.head.in_features, classes)
    return model


def trainable_parameters(model) -> int:
    return sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)
