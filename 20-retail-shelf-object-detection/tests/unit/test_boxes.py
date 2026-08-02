import pytest

from ml.data.boxes import Box, iou, nms


def test_xyxy_yolo_round_trip() -> None:
    original = Box(10, 20, 110, 220)
    restored = Box.from_yolo(original.to_yolo(200, 400), 200, 400)
    assert restored.as_list() == original.as_list()


def test_clip_keeps_box_inside_image() -> None:
    assert Box(-5, -10, 210, 410).clip(200, 400) == Box(0, 0, 200, 400)


def test_degenerate_box_is_rejected() -> None:
    with pytest.raises(ValueError, match="positive width"):
        Box(10, 10, 10, 30).validate()


def test_iou_and_nms_are_deterministic() -> None:
    boxes = [Box(0, 0, 20, 20), Box(2, 2, 22, 22), Box(40, 40, 60, 60)]
    assert iou(boxes[0], boxes[1]) == pytest.approx(324 / 476)
    assert nms(boxes, [0.95, 0.8, 0.7], 0.5) == [0, 2]


def test_nms_requires_aligned_scores() -> None:
    with pytest.raises(ValueError, match="same length"):
        nms([Box(0, 0, 1, 1)], [], 0.5)
