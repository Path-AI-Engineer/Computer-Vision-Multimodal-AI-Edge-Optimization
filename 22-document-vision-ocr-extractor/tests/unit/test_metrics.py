from document_ai.evaluation.metrics import (
    character_error_rate,
    intersection_over_union,
    word_error_rate,
)


def test_error_rates_are_zero_for_exact_text() -> None:
    assert character_error_rate("TOTAL 10.00", "TOTAL 10.00") == 0
    assert word_error_rate("TOTAL 10.00", "TOTAL 10.00") == 0


def test_character_error_rate_counts_substitution() -> None:
    assert character_error_rate("road", "r0ad") == 0.25


def test_iou_handles_overlap_and_empty_union() -> None:
    assert intersection_over_union((0, 0, 10, 10), (0, 0, 10, 10)) == 1
    assert intersection_over_union((0, 0, 0, 0), (0, 0, 0, 0)) == 0
