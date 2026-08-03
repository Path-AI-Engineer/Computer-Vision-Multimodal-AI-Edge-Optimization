from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from multimodal.data.manifest import load_manifest  # noqa: E402

REQUIRED = (
    "README.md",
    "model-card.md",
    "index-card.md",
    "docs/architecture.md",
    "docs/data-contract.md",
    "docs/embedding-contract.md",
    "docs/search-contract.md",
    "docs/assistant-contract.md",
    "artifacts/bundles/vision-language-qualification-v1.json",
    "artifacts/embeddings/embedding-manifest.json",
    "artifacts/indexes/index-manifest.json",
    "reports/metrics/retrieval-metrics.json",
    "reports/metrics/index-benchmark.json",
    "reports/metrics/conversational-eval.json",
    "reports/errors/error-gallery.json",
    "docker/production.Dockerfile",
    "infra/aws/release.ps1",
)


def main() -> None:
    missing = [item for item in REQUIRED if not ROOT.joinpath(item).is_file()]
    if missing:
        raise SystemExit(f"Missing required files: {missing}")
    items = load_manifest(ROOT / "data" / "manifests" / "qualification-corpus.json")
    if len(items) != 12 or sum(len(item.captions) for item in items) != 24:
        raise SystemExit("Qualification corpus cardinality changed unexpectedly.")
    embedding = json.loads(
        (ROOT / "artifacts" / "embeddings" / "embedding-manifest.json").read_text(encoding="utf-8")
    )
    index = json.loads(
        (ROOT / "artifacts" / "indexes" / "index-manifest.json").read_text(encoding="utf-8")
    )
    if embedding["model_version"] != index["model_version"]:
        raise SystemExit("Embedding and index model versions do not match.")
    if embedding["dimension"] != index["dimension"]:
        raise SystemExit("Embedding and index dimensions do not match.")
    metrics = json.loads(
        (ROOT / "reports" / "metrics" / "retrieval-metrics.json").read_text(encoding="utf-8")
    )
    if metrics["status"] != "QUALIFICATION_ONLY" or "Flickr8k" not in metrics["claim_boundary"]:
        raise SystemExit("The evidence boundary is missing from retrieval metrics.")
    print("Project 23 evidence validation passed.")


if __name__ == "__main__":
    main()
