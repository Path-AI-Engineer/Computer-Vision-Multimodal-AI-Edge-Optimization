from __future__ import annotations

import numpy as np

from ml.evaluation.calibration import expected_calibration_error, softmax
from ml.evaluation.metrics import classification_report


def test_softmax_rows_sum_to_one() -> None:
    probabilities = softmax(np.asarray([[1.0, 2.0], [-1.0, 1.0]]))
    np.testing.assert_allclose(probabilities.sum(axis=1), [1.0, 1.0])


def test_classification_report_is_json_safe() -> None:
    probabilities = np.asarray([[0.9, 0.1], [0.2, 0.8]])
    summary, per_class, matrix = classification_report(
        np.asarray([0, 1]), probabilities, ("cat", "dog")
    )
    assert summary["accuracy_top_1"] == 1.0
    assert len(per_class) == 2
    assert matrix.tolist() == [[1, 0], [0, 1]]
    assert expected_calibration_error(probabilities, np.asarray([0, 1])) >= 0
