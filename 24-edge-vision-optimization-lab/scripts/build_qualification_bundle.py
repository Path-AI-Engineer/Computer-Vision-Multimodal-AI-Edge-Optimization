from __future__ import annotations

# ruff: noqa: E402, E501, I001

import csv
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from edge_ai.benchmark.environment import environment_manifest
from edge_ai.benchmark.harness import benchmark_callable
from edge_ai.benchmark.statistics import pareto_frontier, recommend_variant, summarize_latency
from edge_ai.core.contracts import VariantManifest, VariantStatus
from edge_ai.data.manifest import checksum_bytes, validate_manifest
from edge_ai.evaluation.metrics import confusion_rows, quality_metrics
from edge_ai.export.parity import parity_report
from edge_ai.optimization.contracts import validate_calibration_manifest, validate_pruning_report

CLASS_NAMES = ("abyssinian", "beagle", "ragdoll", "samoyed")
COLORS = ("#f3a34c", "#6fb7ff", "#af8cff", "#52d6b4")
MODEL_VERSION = "qualification-linear-vision-v1"
PREPROCESSING_VERSION = "generated-shape-features-v1"
ENVIRONMENT_ID = "host_cpu-qualification-v1"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sample_svg(index: int, label: str, color: str) -> str:
    shift = 8 * (index % 3)
    ears = (
        "M70 68 92 25l22 48M186 68l-22-43-22 48"
        if index % 2 == 0
        else "M80 62Q64 20 48 52M176 62q16-42 32-10"
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 192" role="img" aria-label="Generated {label} qualification sample">
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#0b1420"/><stop offset="1" stop-color="#172738"/></linearGradient></defs>
<rect width="256" height="192" rx="20" fill="url(#g)"/><circle cx="128" cy="98" r="62" fill="{color}" opacity=".16"/>
<path d="{ears}" fill="none" stroke="{color}" stroke-width="15" stroke-linecap="round"/>
<ellipse cx="128" cy="101" rx="66" ry="55" fill="#dce8ed"/><circle cx="103" cy="94" r="6" fill="#071019"/><circle cx="153" cy="94" r="6" fill="#071019"/>
<path d="M120 112q8 {10 + shift // 4} 16 0M128 111v16M110 132q18 12 36 0" fill="none" stroke="#071019" stroke-width="5" stroke-linecap="round"/>
<circle cx="30" cy="30" r="6" fill="{color}"/><text x="24" y="172" fill="#a8bbc6" font-family="monospace" font-size="11">EDGE-{index + 1:02d} / {label.upper()}</text></svg>"""


def build_samples() -> tuple[list[dict[str, Any]], list[int]]:
    records: list[dict[str, Any]] = []
    labels: list[int] = []
    sample_root = ROOT / "data" / "samples"
    sample_root.mkdir(parents=True, exist_ok=True)
    for index in range(12):
        class_id = index % len(CLASS_NAMES)
        label = CLASS_NAMES[class_id]
        sample_id = f"edge-{index + 1:03d}"
        svg = sample_svg(index, label, COLORS[class_id])
        path = sample_root / f"{sample_id}.svg"
        path.write_text(svg, encoding="utf-8")
        split = "train" if index < 6 else "validation" if index < 9 else "test"
        records.append(
            {
                "sample_id": sample_id,
                "label": label,
                "class_id": class_id,
                "split": split,
                "path": f"data/samples/{path.name}",
                "image_url": f"/assets/samples/{path.name}",
                "checksum": checksum_bytes(svg.encode("utf-8")),
                "source": "generated qualification fixture",
            }
        )
        labels.append(class_id)
    return records, labels


def logits_for_variant(labels: list[int], variant_id: str) -> np.ndarray:
    rng = np.random.default_rng(2401)
    logits = rng.normal(-0.8, 0.18, size=(len(labels), len(CLASS_NAMES)))
    for row, label in enumerate(labels):
        logits[row, label] = 2.4
    if variant_id == "pytorch-pruned-unstructured":
        logits[7, labels[7]] = 0.6
        logits[7, (labels[7] + 1) % 4] = 0.9
    if variant_id == "onnx-int8-ptq":
        logits[10, labels[10]] = 0.72
        logits[10, (labels[10] + 1) % 4] = 0.91
    if variant_id == "structured-channel-experimental":
        logits[5, labels[5]] = 0.5
        logits[5, (labels[5] + 2) % 4] = 0.85
    return logits.round(6)


def build_variant_artifact(
    variant_id: str, width: int, *, quantized: bool = False, sparsity: float = 0.0
) -> tuple[Path, np.ndarray]:
    rng = np.random.default_rng(2401 + width)
    weights = rng.normal(0, 0.12, size=(width, 4)).astype(np.float32)
    if sparsity:
        threshold = np.quantile(np.abs(weights), sparsity)
        weights[np.abs(weights) <= threshold] = 0
    payload_weights = np.rint(weights * 64).astype(np.int8) if quantized else weights
    folder = "int8" if quantized else "onnx" if variant_id.startswith("onnx") else "pytorch"
    artifact = ROOT / "artifacts" / folder / f"{variant_id}.npz"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(artifact, weights=payload_weights)
    return artifact, weights


def measure_variants() -> tuple[list[dict[str, Any]], dict[str, list[float]]]:
    rng = np.random.default_rng(672)
    payload = rng.normal(size=(1, 96)).astype(np.float32)
    definitions = [
        (
            "pytorch-fp32",
            "PyTorch FP32",
            "PyTorch",
            "FP32",
            "baseline",
            96,
            False,
            0.0,
            VariantStatus.APPROVED,
        ),
        (
            "pytorch-pruned-unstructured",
            "Pruned FP32",
            "PyTorch",
            "FP32",
            "50% unstructured",
            96,
            False,
            0.5,
            VariantStatus.APPROVED,
        ),
        (
            "structured-channel-experimental",
            "Structured channel proxy",
            "PyTorch",
            "FP32",
            "50% channels",
            48,
            False,
            0.0,
            VariantStatus.EXPERIMENTAL,
        ),
        (
            "onnx-fp32",
            "ONNX FP32",
            "ONNX Runtime",
            "FP32",
            "graph export",
            96,
            False,
            0.0,
            VariantStatus.APPROVED,
        ),
        (
            "onnx-int8-ptq",
            "ONNX INT8 PTQ",
            "ONNX Runtime",
            "INT8",
            "static PTQ",
            96,
            True,
            0.0,
            VariantStatus.APPROVED,
        ),
    ]
    manifests: list[dict[str, Any]] = []
    sample_map: dict[str, list[float]] = {}
    for (
        variant_id,
        name,
        runtime,
        precision,
        optimization,
        width,
        quantized,
        sparsity,
        status,
    ) in definitions:
        artifact, weights = build_variant_artifact(
            variant_id, width, quantized=quantized, sparsity=sparsity
        )
        if quantized:

            def operation(value: np.ndarray, matrix: np.ndarray = weights) -> np.ndarray:
                return np.rint(value * 32).astype(np.int8).astype(np.float32) @ matrix
        else:

            def operation(
                value: np.ndarray,
                matrix: np.ndarray = weights,
                active: int = width,
            ) -> np.ndarray:
                return value[:, :active] @ matrix

        samples = benchmark_callable(operation, payload, warmup=8, iterations=40)
        latency = summarize_latency(samples)
        sample_map[variant_id] = samples
        manifest = VariantManifest(
            variant_id=variant_id,
            display_name=name,
            runtime=runtime,
            precision=precision,
            optimization=optimization,
            status=status,
            artifact_path=artifact.relative_to(ROOT).as_posix(),
            artifact_size_mb=round(artifact.stat().st_size / (1024 * 1024), 5),
            parameters=int(weights.size),
            effective_sparsity=round(float(np.mean(weights == 0)), 4),
            quality=None,
            latency=latency,
            model_version=MODEL_VERSION,
            preprocessing_version=PREPROCESSING_VERSION,
            environment_id=ENVIRONMENT_ID,
            claim_boundary="Measured qualification adapter; not a MobileNet or ONNX Runtime result.",
        ).as_dict()
        manifests.append(manifest)
    manifests.append(
        VariantManifest(
            variant_id="qat-int8",
            display_name="QAT INT8",
            runtime="PyTorch / ONNX Runtime",
            precision="INT8",
            optimization="quantization-aware training",
            status=VariantStatus.NOT_RUN,
            artifact_path=None,
            artifact_size_mb=None,
            parameters=None,
            effective_sparsity=None,
            quality=None,
            latency=None,
            model_version=MODEL_VERSION,
            preprocessing_version=PREPROCESSING_VERSION,
            environment_id=ENVIRONMENT_ID,
            claim_boundary="Not run: the research MobileNet baseline is not yet qualified.",
        ).as_dict()
    )
    return manifests, sample_map


def main() -> None:
    records, labels = build_samples()
    dataset_manifest = validate_manifest(
        {
            "dataset_id": "sealed-edge-vision-qualification-v1",
            "official_dataset": "Oxford-IIIT Pet",
            "official_dataset_status": "LOCKED_NOT_ACQUIRED",
            "class_names": list(CLASS_NAMES),
            "records": records,
            "claim_boundary": "Generated fixtures validate contracts only.",
        }
    )
    write_json(ROOT / "data/manifests/qualification-dataset.json", dataset_manifest)

    manifests, latency_samples = measure_variants()
    logits = {
        item["variant_id"]: logits_for_variant(labels, item["variant_id"])
        for item in manifests
        if item["status"] != "NOT_RUN"
    }
    quality_reports: list[dict[str, Any]] = []
    for manifest in manifests:
        if manifest["status"] == "NOT_RUN":
            continue
        variant_id = manifest["variant_id"]
        quality = quality_metrics(labels, logits[variant_id])
        manifest["quality"] = quality.as_dict()
        report = {
            "variant_id": variant_id,
            "dataset": dataset_manifest["dataset_id"],
            "quality": quality.as_dict(),
            "confusion": confusion_rows(labels, logits[variant_id]),
            "status": "QUALIFICATION_ONLY",
        }
        quality_reports.append(report)
        write_json(ROOT / f"reports/quality/{variant_id}.json", report)
        write_json(ROOT / f"artifacts/bundles/{variant_id}-manifest.json", manifest)

    environment = environment_manifest(profile="host_cpu", threads=1)
    write_json(ROOT / "reports/environment/environment-manifest.json", environment)
    write_json(
        ROOT / "reports/runs/baseline-run.json",
        {
            "run_id": "p24-qualification-baseline-v1",
            "variant_id": "pytorch-fp32",
            "model_version": MODEL_VERSION,
            "selection_split": "validation",
            "test_policy": "LOCKED_UNTIL_CONFIGURATION_FREEZE",
            "seed": 2401,
            "status": "QUALIFICATION_ONLY",
        },
    )
    registry = {
        "registry_id": "edge-vision-qualification-registry-v1",
        "model_version": MODEL_VERSION,
        "preprocessing_version": PREPROCESSING_VERSION,
        "environment_id": ENVIRONMENT_ID,
        "variants": manifests,
        "claim_boundary": "Only qualification adapters are approved. Research MobileNet/ONNX artifacts are not bundled.",
    }
    write_json(ROOT / "artifacts/bundles/variant-registry.json", registry)

    reference = logits["pytorch-fp32"]
    parity = [
        parity_report(
            reference,
            logits[variant_id],
            atol=0.05 if variant_id == "onnx-fp32" else 0.75,
            reference_id="pytorch-fp32",
            candidate_id=variant_id,
        )
        for variant_id in ("onnx-fp32", "onnx-int8-ptq")
    ]
    write_json(
        ROOT / "reports/parity/onnx-parity-report.json",
        {"comparisons": parity, "status": "QUALIFICATION_ONLY"},
    )
    write_json(
        ROOT / "reports/memory/memory-summary.json",
        {
            "peak_rss": "NOT_MEASURED",
            "reason": "A stable isolated process RSS protocol is not available in the qualification adapter.",
            "status": "NOT_MEASURED",
        },
    )

    pruning = validate_pruning_report(
        {
            "variant_id": "pytorch-pruned-unstructured",
            "target_sparsity": 0.5,
            "effective_sparsity": next(
                item["effective_sparsity"]
                for item in manifests
                if item["variant_id"] == "pytorch-pruned-unstructured"
            ),
            "observed_speedup": round(
                next(
                    item["latency"]["p50_ms"]
                    for item in manifests
                    if item["variant_id"] == "pytorch-fp32"
                )
                / next(
                    item["latency"]["p50_ms"]
                    for item in manifests
                    if item["variant_id"] == "pytorch-pruned-unstructured"
                ),
                4,
            ),
            "interpretation": "Dense NumPy kernels do not guarantee acceleration from zero weights.",
            "status": "QUALIFICATION_ONLY",
        }
    )
    write_json(ROOT / "reports/pruning/pruning-report.json", pruning)
    calibration = validate_calibration_manifest(
        {
            "source_split": "train",
            "sample_ids": [item["sample_id"] for item in records if item["split"] == "train"],
            "status": "QUALIFICATION_ONLY",
        }
    )
    write_json(ROOT / "data/calibration/quantization-calibration-manifest.json", calibration)
    write_json(
        ROOT / "reports/quantization/ptq-report.json",
        {
            "variant_id": "onnx-int8-ptq",
            "calibration_manifest": "data/calibration/quantization-calibration-manifest.json",
            "research_execution": "NOT_RUN",
            "qualification_adapter": "MEASURED",
            "qat_decision": "NOT_RUN_UNTIL_MOBILENET_BASELINE_IS_QUALIFIED",
            "status": "QUALIFICATION_ONLY",
        },
    )

    measured = [
        {
            "variant_id": item["variant_id"],
            "display_name": item["display_name"],
            "runtime": item["runtime"],
            "precision": item["precision"],
            "status": item["status"],
            "macro_f1": item["quality"]["macro_f1"],
            "top1_accuracy": item["quality"]["top1_accuracy"],
            "top5_accuracy": item["quality"]["top5_accuracy"],
            "p50_ms": item["latency"]["p50_ms"],
            "p90_ms": item["latency"]["p90_ms"],
            "p95_ms": item["latency"]["p95_ms"],
            "throughput_per_second": item["latency"]["throughput_per_second"],
            "size_mb": item["artifact_size_mb"],
            "parameters": item["parameters"],
            "effective_sparsity": item["effective_sparsity"],
            "environment_id": item["environment_id"],
        }
        for item in manifests
        if item["status"] != "NOT_RUN"
    ]
    summary = {
        "benchmark_id": "p24-host-cpu-qualification-v1",
        "profile": "host_cpu",
        "batch_size": 1,
        "variants": measured,
        "status": "QUALIFICATION_ONLY",
        "claim_boundary": "Timings measure NumPy qualification adapters on this host, not MobileNetV3 or physical edge hardware.",
    }
    write_json(ROOT / "reports/latency/benchmark-summary.json", summary)
    latency_path = ROOT / "reports/latency/latency-samples.csv"
    latency_path.parent.mkdir(parents=True, exist_ok=True)
    with latency_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["variant_id", "profile", "batch_size", "iteration", "latency_ms"])
        for variant_id, samples in latency_samples.items():
            for index, sample in enumerate(samples, start=1):
                writer.writerow([variant_id, "host_cpu", 1, index, f"{sample:.6f}"])

    frontier = pareto_frontier(measured)
    pareto = {
        "frontier": frontier,
        "recommendations": {
            profile: recommend_variant(frontier, profile)
            for profile in ("cpu_low_latency", "small_size", "quality_first")
        },
        "policy": "No universal winner; select under explicit constraints.",
        "status": "QUALIFICATION_ONLY",
    }
    write_json(ROOT / "reports/pareto/pareto-frontier.json", pareto)
    sample_logits = {
        variant_id: {
            record["sample_id"]: matrix[index].tolist() for index, record in enumerate(records)
        }
        for variant_id, matrix in logits.items()
    }
    bundle = {
        "bundle_id": "edge-vision-qualification-v1",
        "class_names": list(CLASS_NAMES),
        "samples": records,
        "sample_logits": sample_logits,
        "registry": "artifacts/bundles/variant-registry.json",
        "benchmark": "reports/latency/benchmark-summary.json",
        "pareto": "reports/pareto/pareto-frontier.json",
        "status": "QUALIFICATION_ONLY",
    }
    write_json(ROOT / "artifacts/bundles/edge-qualification-v1.json", bundle)
    print(
        json.dumps(
            {"bundle": bundle["bundle_id"], "samples": len(records), "variants": len(manifests)}
        )
    )


if __name__ == "__main__":
    main()
