from __future__ import annotations

from typing import Any


class ResearchDependencyUnavailable(RuntimeError):
    """Raised when optional research dependencies are not installed."""


def build_mobilenet_v3_small(class_count: int, *, pretrained: bool = True) -> Any:
    """Build the Project 24 MobileNet boundary without importing Project 19 artifacts."""
    if class_count < 2:
        raise ValueError("At least two classes are required.")
    try:
        import torch.nn as nn
        from torchvision.models import MobileNet_V3_Small_Weights, mobilenet_v3_small
    except ImportError as error:
        raise ResearchDependencyUnavailable(
            "Install requirements-research.txt before creating the MobileNet experiment."
        ) from error
    weights = MobileNet_V3_Small_Weights.DEFAULT if pretrained else None
    model = mobilenet_v3_small(weights=weights)
    input_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Linear(input_features, class_count)
    return model
