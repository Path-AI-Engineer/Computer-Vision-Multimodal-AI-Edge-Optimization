from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum

import numpy as np
from scipy import ndimage


class InspectionDecision(StrEnum):
    ACCEPT = "ACCEPT"
    REVIEW = "REVIEW"
    REJECT = "REJECT"


@dataclass(frozen=True)
class InspectionPolicy:
    review_area_ratio: float = 0.001
    reject_area_ratio: float = 0.012
    minimum_component_area_px: int = 6

    def __post_init__(self) -> None:
        if not 0 <= self.review_area_ratio < self.reject_area_ratio <= 1:
            raise ValueError("Policy thresholds must satisfy 0 <= review < reject <= 1.")


@dataclass(frozen=True)
class InspectionOutcome:
    decision: InspectionDecision
    defect_detected: bool
    defect_area_px: int
    defect_area_ratio: float
    component_count: int
    largest_component_px: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def evaluate_mask(mask: np.ndarray, policy: InspectionPolicy) -> InspectionOutcome:
    binary = mask.astype(bool)
    labels, count = ndimage.label(binary)
    component_sizes = [int((labels == index).sum()) for index in range(1, count + 1)]
    retained = [size for size in component_sizes if size >= policy.minimum_component_area_px]
    retained_area = sum(retained)
    area_ratio = retained_area / binary.size
    if area_ratio < policy.review_area_ratio:
        decision = InspectionDecision.ACCEPT
    elif area_ratio < policy.reject_area_ratio:
        decision = InspectionDecision.REVIEW
    else:
        decision = InspectionDecision.REJECT
    return InspectionOutcome(
        decision=decision,
        defect_detected=bool(retained),
        defect_area_px=retained_area,
        defect_area_ratio=round(area_ratio, 8),
        component_count=len(retained),
        largest_component_px=max(retained, default=0),
    )
