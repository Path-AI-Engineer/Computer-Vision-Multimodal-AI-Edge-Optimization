from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F


class ConvBlock(nn.Module):
    def __init__(self, in_channels: int, out_channels: int) -> None:
        super().__init__()
        self.layers = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.layers(inputs)


class SmallUNet(nn.Module):
    """Compact two-level U-Net used by the qualification profile."""

    def __init__(self, base_channels: int = 8) -> None:
        super().__init__()
        self.encoder_one = ConvBlock(1, base_channels)
        self.encoder_two = ConvBlock(base_channels, base_channels * 2)
        self.bottleneck = ConvBlock(base_channels * 2, base_channels * 4)
        self.pool = nn.MaxPool2d(2)
        self.up_two = nn.ConvTranspose2d(
            base_channels * 4,
            base_channels * 2,
            kernel_size=2,
            stride=2,
        )
        self.decoder_two = ConvBlock(base_channels * 4, base_channels * 2)
        self.up_one = nn.ConvTranspose2d(
            base_channels * 2,
            base_channels,
            kernel_size=2,
            stride=2,
        )
        self.decoder_one = ConvBlock(base_channels * 2, base_channels)
        self.head = nn.Conv2d(base_channels, 1, kernel_size=1)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        skip_one = self.encoder_one(inputs)
        skip_two = self.encoder_two(self.pool(skip_one))
        encoded = self.bottleneck(self.pool(skip_two))
        decoded_two = self.up_two(encoded)
        if decoded_two.shape[-2:] != skip_two.shape[-2:]:
            decoded_two = F.interpolate(
                decoded_two,
                size=skip_two.shape[-2:],
                mode="bilinear",
                align_corners=False,
            )
        decoded_two = self.decoder_two(torch.cat([decoded_two, skip_two], dim=1))
        decoded_one = self.up_one(decoded_two)
        if decoded_one.shape[-2:] != skip_one.shape[-2:]:
            decoded_one = F.interpolate(
                decoded_one,
                size=skip_one.shape[-2:],
                mode="bilinear",
                align_corners=False,
            )
        return self.head(self.decoder_one(torch.cat([decoded_one, skip_one], dim=1)))


def count_trainable_parameters(model: nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)
