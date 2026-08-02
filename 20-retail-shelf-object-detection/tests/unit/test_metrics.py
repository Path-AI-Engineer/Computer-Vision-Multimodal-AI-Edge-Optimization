from ml.data.boxes import Box
from ml.evaluation.metrics import average_precision, detection_summary, match_image


def record(predicted_boxes: list[list[float]], scores: list[float]) -> dict[str, object]:
    return {
        "truth_boxes": [[0, 0, 10, 10]],
        "predicted_boxes": predicted_boxes,
        "scores": scores,
        "truth_count": 1,
        "predicted_count": len(predicted_boxes),
    }


def test_match_image_reports_tp_fp_and_fn() -> None:
    truth = [Box(0, 0, 10, 10), Box(20, 20, 30, 30)]
    predicted = [Box(0, 0, 10, 10), Box(50, 50, 60, 60)]
    assert match_image(truth, predicted, [0.9, 0.8], 0.5) == ([0], [1], 1)


def test_average_precision_is_perfect_for_exact_geometry() -> None:
    metrics = average_precision([record([[0, 0, 10, 10]], [0.9])], 0.5)
    assert metrics == {"ap": 1.0, "precision": 1.0, "recall": 1.0}


def test_summary_keeps_detection_and_count_metrics_separate() -> None:
    metrics = detection_summary([record([[0, 0, 10, 10], [20, 20, 30, 30]], [0.9, 0.8])])
    assert metrics["ap50"] == 1
    assert metrics["count_mae"] == 1
    assert metrics["test_status"] == "LOCKED_NOT_ACQUIRED"
