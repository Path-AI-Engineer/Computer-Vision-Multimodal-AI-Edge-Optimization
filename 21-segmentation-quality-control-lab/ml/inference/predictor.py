from __future__ import annotations

import time
import uuid
from dataclasses import dataclass

import numpy as np
import torch
from PIL import Image

from ml.baselines.opencv import segment_with_morphology
from ml.evaluation.policy import InspectionPolicy, evaluate_mask
from ml.inference.bundle import QualityBundle
from ml.models.unet import SmallUNet
from ml.visualization.masks import (
    binary_mask_rgb,
    image_data_uri,
    overlay_mask,
    probability_heatmap,
)


@dataclass(frozen=True)
class PredictionArrays:
    probability: np.ndarray
    binary_mask: np.ndarray
    baseline_mask: np.ndarray
    latency_ms: float


class SegmentationPredictor:
    def __init__(self, bundle: QualityBundle) -> None:
        self.bundle = bundle
        checkpoint = torch.load(bundle.checkpoint_path, map_location="cpu", weights_only=True)
        self.model = SmallUNet()
        self.model.load_state_dict(checkpoint["state_dict"])
        self.model.eval()
        torch.set_num_threads(max(1, min(torch.get_num_threads(), 4)))

    def predict_arrays(
        self,
        image: np.ndarray,
        *,
        pixel_threshold: float | None = None,
    ) -> PredictionArrays:
        if image.ndim == 3:
            image = np.mean(image[..., :3], axis=2).astype(np.uint8)
        if image.ndim != 2:
            raise ValueError("Inference expects one grayscale or RGB image.")
        threshold = self.bundle.pixel_threshold if pixel_threshold is None else pixel_threshold
        if not 0.05 <= threshold <= 0.95:
            raise ValueError("pixel_threshold must be between 0.05 and 0.95.")
        original_size = image.shape
        height, width = self.bundle.input_size
        resized = np.asarray(
            Image.fromarray(image).resize((width, height), Image.Resampling.BILINEAR),
            dtype=np.float32,
        )
        normalized = (resized - self.bundle.normalization_mean) / self.bundle.normalization_std
        tensor = torch.from_numpy(normalized).unsqueeze(0).unsqueeze(0)
        started = time.perf_counter()
        with torch.inference_mode():
            probability = torch.sigmoid(self.model(tensor))[0, 0].numpy()
        probability = np.asarray(
            Image.fromarray(probability.astype(np.float32), mode="F").resize(
                (original_size[1], original_size[0]), Image.Resampling.BILINEAR
            ),
            dtype=np.float32,
        )
        binary_mask = (probability >= threshold).astype(np.uint8)
        baseline_mask = segment_with_morphology(image)
        return PredictionArrays(
            probability=probability,
            binary_mask=binary_mask,
            baseline_mask=baseline_mask,
            latency_ms=round((time.perf_counter() - started) * 1000, 3),
        )

    def inspect(
        self,
        image: np.ndarray,
        *,
        pixel_threshold: float | None = None,
    ) -> dict[str, object]:
        threshold = self.bundle.pixel_threshold if pixel_threshold is None else pixel_threshold
        prediction = self.predict_arrays(image, pixel_threshold=threshold)
        policy = InspectionPolicy(
            review_area_ratio=self.bundle.review_area_ratio,
            reject_area_ratio=self.bundle.reject_area_ratio,
            minimum_component_area_px=self.bundle.minimum_component_area_px,
        )
        outcome = evaluate_mask(prediction.binary_mask, policy)
        baseline_outcome = evaluate_mask(prediction.baseline_mask, policy)
        return {
            "request_id": str(uuid.uuid4()),
            "model_version": self.bundle.model_version,
            "pixel_threshold": threshold,
            "piece_threshold": self.bundle.review_area_ratio,
            **outcome.to_dict(),
            "latency_ms": prediction.latency_ms,
            "image_uri": image_data_uri(image),
            "mask_probability_uri": image_data_uri(probability_heatmap(prediction.probability)),
            "binary_mask_uri": image_data_uri(binary_mask_rgb(prediction.binary_mask)),
            "overlay_uri": image_data_uri(overlay_mask(image, prediction.binary_mask)),
            "baseline_mask_uri": image_data_uri(binary_mask_rgb(prediction.baseline_mask)),
            "baseline_overlay_uri": image_data_uri(
                overlay_mask(image, prediction.baseline_mask)
            ),
            "baseline_decision": baseline_outcome.decision,
            "warnings": [
                "Qualification-only checkpoint; not a KSDD2 production claim.",
                "Inspection output does not replace a validated industrial quality system.",
            ],
        }
