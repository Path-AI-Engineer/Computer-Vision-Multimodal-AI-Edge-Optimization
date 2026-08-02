from __future__ import annotations

import numpy as np

from ml.evaluation.policy import InspectionDecision, InspectionPolicy, evaluate_mask


def test_policy_covers_accept_review_and_reject() -> None:
    policy = InspectionPolicy(
        review_area_ratio=0.01, reject_area_ratio=0.1, minimum_component_area_px=2
    )
    clean = evaluate_mask(np.zeros((10, 10), dtype=np.uint8), policy)
    review_mask = np.zeros((10, 10), dtype=np.uint8)
    review_mask[0:2, 0:2] = 1
    reject_mask = np.zeros((10, 10), dtype=np.uint8)
    reject_mask[0:4, 0:4] = 1
    assert clean.decision is InspectionDecision.ACCEPT
    assert evaluate_mask(review_mask, policy).decision is InspectionDecision.REVIEW
    assert evaluate_mask(reject_mask, policy).decision is InspectionDecision.REJECT


def test_policy_ignores_components_below_minimum_area() -> None:
    mask = np.zeros((10, 10), dtype=np.uint8)
    mask[1, 1] = 1
    outcome = evaluate_mask(mask, InspectionPolicy(minimum_component_area_px=2))
    assert outcome.decision is InspectionDecision.ACCEPT
    assert outcome.component_count == 0
