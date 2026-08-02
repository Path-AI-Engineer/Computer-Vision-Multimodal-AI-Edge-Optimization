from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TrainingBudget:
    profile: str
    seed: int
    epochs: int
    image_size: int
    batch_size: int
    device: str

    def validate(self) -> None:
        if self.profile not in {"smoke", "development", "full"}:
            raise ValueError("Unknown compute profile.")
        if min(self.epochs, self.image_size, self.batch_size) <= 0:
            raise ValueError("Training budget values must be positive.")
