from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.app.core.config import settings
from edge_ai.inference.predictor import QualificationPredictor
from edge_ai.registry.service import VariantRegistry


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


class Runtime:
    def __init__(self) -> None:
        root = settings.root
        self.registry = VariantRegistry(root / "artifacts/bundles/variant-registry.json")
        self.predictor = QualificationPredictor(root, self.registry)
        self.bundle = read_json(root / "artifacts/bundles/edge-qualification-v1.json")
        self.summary = read_json(root / "reports/latency/benchmark-summary.json")
        self.pareto = read_json(root / "reports/pareto/pareto-frontier.json")
        self.environment = read_json(root / "reports/environment/environment-manifest.json")
        self.parity = read_json(root / "reports/parity/onnx-parity-report.json")
        self.pruning = read_json(root / "reports/pruning/pruning-report.json")

    def readiness(self) -> dict[str, Any]:
        return {
            "status": "ready",
            "bundle_id": self.bundle["bundle_id"],
            "approved_variants": len(self.registry.approved()),
            "sample_count": len(self.predictor.samples),
            "claim_boundary": self.registry.payload["claim_boundary"],
        }


runtime = Runtime()
