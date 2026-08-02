from pathlib import Path
from unittest.mock import patch

import pytest

from ml.training.yolo import YoloTrainingRequest


def test_training_request_forbids_implicit_weight_download() -> None:
    request = YoloTrainingRequest(
        dataset_yaml=Path("dataset.yaml"),
        initial_weights=Path("missing.pt"),
        output_root=Path("runs"),
        run_name="yolo-nano-development",
    )
    with (
        patch.object(Path, "is_file", side_effect=[True, False]),
        pytest.raises(FileNotFoundError, match="implicit downloads are disabled"),
    ):
        request.validate()


def test_training_request_keeps_official_test_out_of_training() -> None:
    request = YoloTrainingRequest(
        dataset_yaml=Path("dataset.yaml"),
        initial_weights=Path("nano.pt"),
        output_root=Path("runs"),
        run_name="official-test-training",
        profile="full",
    )
    with (
        patch.object(Path, "is_file", return_value=True),
        pytest.raises(ValueError, match="locked official test"),
    ):
        request.validate()


def test_public_training_config_is_serializable() -> None:
    request = YoloTrainingRequest(Path("data.yaml"), Path("nano.pt"), Path("runs"), "run")
    assert request.public_config()["profile"] == "development"
    assert isinstance(request.public_config()["dataset_yaml"], str)
