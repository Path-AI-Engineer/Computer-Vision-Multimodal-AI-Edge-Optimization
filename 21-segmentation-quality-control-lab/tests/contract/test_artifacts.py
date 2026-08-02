from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_release_evidence_has_locked_official_test() -> None:
    summary = json.loads(
        (ROOT / "reports/metrics/evaluation_summary.json").read_text(encoding="utf-8")
    )
    profile = json.loads(
        (ROOT / "data/manifests/dataset_profile.json").read_text(encoding="utf-8")
    )
    assert summary["profile"] == "procedural_qualification"
    assert summary["official_test_status"] == "LOCKED_NOT_ACQUIRED"
    assert profile["official_dataset"] == "NOT_ACQUIRED"
    assert summary["images"] == summary["defective_images"] + summary["clean_images"]


def test_candidate_registry_does_not_claim_unrun_models() -> None:
    candidates = json.loads(
        (ROOT / "configs/models/candidates.json").read_text(encoding="utf-8")
    )
    by_id = {row["id"]: row for row in candidates["candidates"]}
    assert by_id["small-unet"]["status"] == "executed"
    assert by_id["pretrained-unet"]["status"] == "not_run"
    assert by_id["deeplabv3"]["status"] == "not_run"


def test_loss_ablation_has_matched_executed_candidates() -> None:
    ablation = json.loads(
        (ROOT / "reports/metrics/loss_ablation.json").read_text(encoding="utf-8")
    )
    assert ablation["budget"] == "matched_seed_architecture_epochs_optimizer"
    assert {row["loss_name"] for row in ablation["candidates"]} == {
        "bce",
        "dice",
        "bce_dice",
    }
    assert ablation["selected_loss"] in {"bce", "dice", "bce_dice"}
