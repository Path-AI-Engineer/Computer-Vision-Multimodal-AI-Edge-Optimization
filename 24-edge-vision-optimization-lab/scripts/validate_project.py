from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> dict[str, object]:
    target = ROOT / path
    if not target.is_file():
        raise SystemExit(f"Missing required evidence: {path}")
    return json.loads(target.read_text(encoding="utf-8"))


def main() -> None:
    required = [
        "README.md",
        "model-card.md",
        "deployment-card.md",
        "data/manifests/qualification-dataset.json",
        "data/calibration/quantization-calibration-manifest.json",
        "artifacts/bundles/edge-qualification-v1.json",
        "artifacts/bundles/variant-registry.json",
        "reports/latency/latency-samples.csv",
        "reports/latency/benchmark-summary.json",
        "reports/runs/baseline-run.json",
        "reports/memory/memory-summary.json",
        "reports/quantization/ptq-report.json",
        "reports/pareto/pareto-frontier.json",
        "reports/parity/onnx-parity-report.json",
        "reports/pruning/pruning-report.json",
        "reports/environment/environment-manifest.json",
        "docker/production.Dockerfile",
        "infra/aws/apprunner.yaml",
    ]
    for path in required:
        if not (ROOT / path).is_file():
            raise SystemExit(f"Missing required project file: {path}")
    registry = read("artifacts/bundles/variant-registry.json")
    variants = registry["variants"]
    assert isinstance(variants, list)
    ids = {item["variant_id"] for item in variants}
    if len(ids) != len(variants) or "pytorch-fp32" not in ids or "onnx-int8-ptq" not in ids:
        raise SystemExit("Variant registry is incomplete or contains duplicate IDs.")
    for variant in variants:
        artifact = variant.get("artifact_path")
        if artifact and not (ROOT / artifact).is_file():
            raise SystemExit(f"Variant artifact does not exist: {artifact}")
    summary = read("reports/latency/benchmark-summary.json")
    measured = summary["variants"]
    assert isinstance(measured, list)
    environments = {item["environment_id"] for item in measured}
    if len(environments) != 1:
        raise SystemExit("Benchmark rows mix different environments.")
    calibration = read("data/calibration/quantization-calibration-manifest.json")
    if calibration["source_split"] != "train":
        raise SystemExit("Calibration data must come from train.")
    pareto = read("reports/pareto/pareto-frontier.json")
    frontier_ids = {item["variant_id"] for item in pareto["frontier"]}
    if not set(pareto["recommendations"].values()) <= frontier_ids:
        raise SystemExit("Deployment recommendations must reference Pareto variants.")
    if summary["status"] != "QUALIFICATION_ONLY":
        raise SystemExit("Qualification evidence boundary is missing.")
    print("Project 24 evidence validation passed.")


if __name__ == "__main__":
    main()
