from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _json(relative: str) -> object:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    required = [
        "models/bundles/surface-quality-control-v1.json",
        "models/bundles/bundle_manifest.json",
        "reports/metrics/evaluation_summary.json",
        "reports/metrics/data_analysis.json",
        "reports/metrics/loss_ablation.json",
        "reports/metrics/morphology_sensitivity.json",
        "reports/metrics/threshold_sweep.json",
        "reports/metrics/model_comparison.json",
        "reports/metrics/inspection_policy.json",
        "reports/errors/error_gallery.json",
        "data/manifests/qualification_manifest.csv",
        "model-card.md",
        "reports/figures/validation-contact-sheet.png",
        "frontend/src/App.tsx",
        "backend/app/main.py",
        "infra/aws/apprunner.yaml",
        "docker/production.Dockerfile",
    ]
    missing = [relative for relative in required if not (ROOT / relative).is_file()]
    assert not missing, f"Missing required files: {missing}"

    manifest = _json("models/bundles/bundle_manifest.json")
    assert isinstance(manifest, dict)
    bundle = ROOT / str(manifest["bundle_path"])
    bundle_payload = json.loads(bundle.read_text(encoding="utf-8"))
    checkpoint = ROOT / str(bundle_payload["checkpoint_path"])
    assert _sha256(bundle) == manifest["bundle_sha256"], "Bundle hash mismatch."
    assert _sha256(checkpoint) == manifest["checkpoint_sha256"], "Checkpoint hash mismatch."

    summary = _json("reports/metrics/evaluation_summary.json")
    assert isinstance(summary, dict)
    assert summary["profile"] == "procedural_qualification"
    assert summary["official_test_status"] == "LOCKED_NOT_ACQUIRED"
    assert summary["selection_split"] == "qualification_validation"
    assert summary["images"] == 12
    assert summary["defective_images"] + summary["clean_images"] == summary["images"]
    assert 0.05 <= summary["pixel_threshold"] <= 0.95

    metrics = summary["pixel_metrics"]
    piece = summary["piece_metrics"]
    assert 0 <= metrics["macro_dice"] <= 1
    assert 0 <= metrics["macro_iou"] <= 1
    assert piece["true_positive"] + piece["false_negative"] == summary["defective_images"]
    assert piece["true_negative"] + piece["false_positive"] == summary["clean_images"]

    with (ROOT / "data/manifests/qualification_manifest.csv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 44
    for row in rows:
        image = ROOT / row["image_path"]
        mask = ROOT / row["mask_path"]
        assert image.is_file(), image
        assert mask.is_file(), mask

    source_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in [ROOT / "README.md", ROOT / "model-card.md"]
    )
    assert "LOCKED_NOT_ACQUIRED" in source_text
    print(
        json.dumps(
            {
                "status": "passed",
                "profile": summary["profile"],
                "images": summary["images"],
                "macro_dice": metrics["macro_dice"],
                "official_test": summary["official_test_status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
