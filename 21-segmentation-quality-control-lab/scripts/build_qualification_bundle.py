from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from ml.data.fixture import build_qualification_dataset
from ml.evaluation.runner import create_bundle, evaluate_qualification
from ml.inference.bundle import QualityBundle
from ml.training.runner import TrainingResult, train_small_unet
from scripts.build_analysis_evidence import (
    build_contact_sheet,
    build_data_analysis,
    build_morphology_sensitivity,
)

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_model_card(
    training: object,
    summary: dict[str, object],
    bundle: QualityBundle,
) -> None:
    training_payload = training.__dict__
    pixel = summary["pixel_metrics"]
    piece = summary["piece_metrics"]
    latency = summary["latency"]
    content = f"""# Model card — Small U-Net qualification bundle

## Status

`QUALIFICATION_ONLY`. The served checkpoint is a real Small U-Net trained on deterministic
procedural surfaces. It is not a KSDD2 benchmark result and the official test remains
`{bundle.official_test_status}`.

## Architecture and training

- Model: Small U-Net with two encoder/decoder levels and skip connections.
- Trainable parameters: {training_payload["parameters"]}.
- Selected loss: {training_payload["loss_name"]}.
- Best epoch: {training_payload["best_epoch"]}.
- Best validation loss: {training_payload["best_validation_loss"]}.
- Threshold selection: qualification validation only.

## Qualification evidence

- Macro Dice: {pixel["macro_dice"]}.
- Macro IoU: {pixel["macro_iou"]}.
- Pixel recall: {pixel["macro_recall"]}.
- Pixel PR AUC: {pixel["pr_auc"]}.
- Defective-piece recall: {piece["defect_recall"]}.
- False accept rate: {piece["false_accept_rate"]}.
- Local p50/p95 latency: {latency["p50_ms"]} / {latency["p95_ms"]} ms.

## Intended use

Education, software qualification and controlled demonstration of how pixel masks become an
auditable ACCEPT, REVIEW or REJECT decision.

## Limitations

- KSDD2 was not acquired or opened.
- Transfer U-Net and DeepLabV3 are protocol-ready but not executed.
- Procedural textures do not represent industrial variability.
- This model must not control a production line or support a safety guarantee.
"""
    (ROOT / "model-card.md").write_text(content, encoding="utf-8")


def main() -> None:
    records = build_qualification_dataset(ROOT)
    build_data_analysis()
    build_contact_sheet()
    build_morphology_sensitivity()
    training_config = _load_json(ROOT / "configs" / "training" / "qualification.json")
    evaluation_protocol = _load_json(ROOT / "configs" / "evaluation" / "protocol.json")
    candidates: list[tuple[TrainingResult, dict[str, object]]] = []
    for loss_name in ("bce", "dice", "bce_dice"):
        training_candidate = train_small_unet(ROOT, training_config, loss_name=loss_name)
        candidate_summary = evaluate_qualification(
            ROOT,
            checkpoint_path=ROOT / training_candidate.checkpoint_path,
            protocol=evaluation_protocol,
        )
        candidates.append((training_candidate, candidate_summary))
    training, _ = max(
        candidates,
        key=lambda row: (
            row[1]["pixel_metrics"]["macro_dice"],
            row[1]["pixel_metrics"]["macro_recall"],
        ),
    )
    checkpoint_path = ROOT / training.checkpoint_path
    summary = evaluate_qualification(
        ROOT, checkpoint_path=checkpoint_path, protocol=evaluation_protocol
    )
    ablation = {
        "scope": "procedural_qualification_validation",
        "budget": "matched_seed_architecture_epochs_optimizer",
        "selected_loss": training.loss_name,
        "candidates": [
            {
                "loss_name": candidate_training.loss_name,
                "best_epoch": candidate_training.best_epoch,
                "best_validation_loss": candidate_training.best_validation_loss,
                "pixel_metrics": candidate_summary["pixel_metrics"],
                "piece_metrics": candidate_summary["piece_metrics"],
            }
            for candidate_training, candidate_summary in candidates
        ],
        "warning": "Qualification evidence is not KSDD2 benchmark evidence.",
    }
    (ROOT / "reports" / "metrics" / "loss_ablation.json").write_text(
        json.dumps(ablation, indent=2) + "\n", encoding="utf-8"
    )
    canonical_run = ROOT / "reports" / "runs" / "p21-qualification-v1"
    canonical_run.mkdir(parents=True, exist_ok=True)
    (canonical_run / "training_summary.json").write_text(
        json.dumps(asdict(training), indent=2) + "\n", encoding="utf-8"
    )
    (canonical_run / "history.json").write_text(
        json.dumps(training.history, indent=2) + "\n", encoding="utf-8"
    )
    bundle_path = create_bundle(
        ROOT,
        checkpoint_path=checkpoint_path,
        evaluation_summary=summary,
        protocol=evaluation_protocol,
    )
    bundle = QualityBundle.load(ROOT, bundle_path)
    _write_model_card(training, summary, bundle)
    print(
        json.dumps(
            {
                "status": "passed",
                "profile": bundle.evidence_profile,
                "model_version": bundle.model_version,
                "images": len(records),
                "pixel_threshold": bundle.pixel_threshold,
                "macro_dice": summary["pixel_metrics"]["macro_dice"],
                "official_test_status": bundle.official_test_status,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
