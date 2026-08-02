from __future__ import annotations


def load_ultralytics_candidate(weights: str):
    """Load a declared YOLO candidate only when the optional runtime is installed."""
    try:
        from ultralytics import YOLO
    except ImportError as error:
        raise RuntimeError(
            "Ultralytics is optional. Install the detection extra before a YOLO run."
        ) from error
    return YOLO(weights)


def build_faster_rcnn(classes: int = 2, weights: str | None = None):
    """Build the two-stage reference without downloading weights implicitly."""
    try:
        from torch import nn
        from torchvision.models.detection import fasterrcnn_resnet50_fpn
        from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
    except ImportError as error:
        raise RuntimeError("Torchvision is required for Faster R-CNN qualification.") from error
    model = fasterrcnn_resnet50_fpn(weights=weights, weights_backbone=None)
    model.roi_heads.box_predictor = FastRCNNPredictor(
        model.roi_heads.box_predictor.cls_score.in_features, classes
    )
    assert isinstance(model.roi_heads.box_predictor.cls_score, nn.Linear)
    return model
