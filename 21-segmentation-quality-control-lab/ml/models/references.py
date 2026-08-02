from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateState:
    model_id: str
    status: str
    reason: str


def protocol_ready_candidates() -> list[CandidateState]:
    return [
        CandidateState(
            model_id="pretrained-unet",
            status="NOT_RUN",
            reason=(
                "KSDD2 train/validation data and transfer-learning budget are not available."
            ),
        ),
        CandidateState(
            model_id="deeplabv3",
            status="NOT_RUN",
            reason="Optional reference remains excluded until the official split is acquired.",
        ),
    ]
