from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter_ns
from typing import Any

import numpy as np

from edge_ai.core.contracts import PredictionResult
from edge_ai.registry.service import VariantRegistry


class QualificationPredictor:
    """Deterministic online adapter for the sealed qualification corpus."""

    def __init__(self, root: Path, registry: VariantRegistry) -> None:
        self.root = root
        self.registry = registry
        bundle = json.loads(
            (root / "artifacts/bundles/edge-qualification-v1.json").read_text(encoding="utf-8")
        )
        self.class_names = tuple(bundle["class_names"])
        self.sample_logits = bundle["sample_logits"]
        self.samples = {item["sample_id"]: item for item in bundle["samples"]}

    def predict(self, variant_id: str, sample_id: str, top_k: int = 3) -> PredictionResult:
        variant = self.registry.get(variant_id)
        if not variant["status"].startswith("APPROVED"):
            raise ValueError(f"Variant {variant_id} is not approved for online inference.")
        if sample_id not in self.samples:
            raise ValueError(f"Unknown qualification sample: {sample_id}")
        start = perf_counter_ns()
        logits = np.asarray(self.sample_logits[variant_id][sample_id], dtype=np.float64)
        probabilities = np.exp(logits - logits.max())
        probabilities /= probabilities.sum()
        ranking = np.argsort(probabilities)[::-1][: max(1, min(top_k, len(self.class_names)))]
        predictions = tuple(
            {
                "label": self.class_names[int(index)],
                "probability": round(float(probabilities[index]), 4),
            }
            for index in ranking
        )
        elapsed_ms = max((perf_counter_ns() - start) / 1_000_000, 0.0001)
        return PredictionResult(
            variant_id=variant_id,
            sample_id=sample_id,
            predictions=predictions,
            observed_latency_ms=round(elapsed_ms, 4),
            model_version=str(variant["model_version"]),
            status="QUALIFICATION_ONLY",
        )

    def sample_catalog(self) -> list[dict[str, Any]]:
        return list(self.samples.values())
