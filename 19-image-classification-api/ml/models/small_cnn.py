from __future__ import annotations

import torch
from torch import nn


class SmallCNN(nn.Module):
    def __init__(self, classes: int = 37) -> None:
        super().__init__()
        self.features = nn.Sequential(
            _block(3, 32),
            _block(32, 64),
            _block(64, 128),
            nn.AdaptiveAvgPool2d((1, 1)),
        )
        self.classifier = nn.Sequential(nn.Flatten(), nn.Dropout(0.25), nn.Linear(128, classes))

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(inputs))


def _block(input_channels: int, output_channels: int) -> nn.Sequential:
    return nn.Sequential(
        nn.Conv2d(input_channels, output_channels, kernel_size=3, padding=1, bias=False),
        nn.BatchNorm2d(output_channels),
        nn.ReLU(inplace=True),
        nn.MaxPool2d(2),
    )
