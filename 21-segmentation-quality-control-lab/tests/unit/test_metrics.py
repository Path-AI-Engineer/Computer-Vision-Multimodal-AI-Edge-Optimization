from __future__ import annotations

import numpy as np

from ml.evaluation.metrics import piece_metrics, pixel_metrics, select_pixel_threshold


def test_empty_clean_pair_scores_as_correct() -> None:
    metrics = pixel_metrics(np.zeros((3, 3)), np.zeros((3, 3)), threshold=0.5)
    assert metrics.dice == metrics.iou == metrics.precision == metrics.recall == 1.0


def test_threshold_selection_uses_dice_then_recall() -> None:
    target = np.array([[0, 1]], dtype=np.uint8)
    probability = np.array([[0.4, 0.8]], dtype=np.float32)
    selected, rows = select_pixel_threshold([probability], [target], [0.3, 0.5, 0.9])
    assert selected == 0.5
    assert len(rows) == 3


def test_piece_metrics_name_false_accept_from_defect_escape() -> None:
    result = piece_metrics([False, True, True, False], [True, True, False, False])
    assert result["true_positive"] == 1
    assert result["true_negative"] == 1
    assert result["false_positive"] == 1
    assert result["false_negative"] == 1
    assert result["false_accept_rate"] == 0.5
    assert result["false_reject_rate"] == 0.5
