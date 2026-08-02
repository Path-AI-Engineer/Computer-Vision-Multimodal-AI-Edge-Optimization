from __future__ import annotations

from dataclasses import dataclass

import torch
from torch import nn


@dataclass(frozen=True, slots=True)
class EpochResult:
    loss: float
    accuracy: float
    examples: int


def run_epoch(
    model: nn.Module,
    loader,
    criterion: nn.Module,
    *,
    device: torch.device,
    optimizer=None,
) -> EpochResult:
    training = optimizer is not None
    model.train(training)
    total_loss = 0.0
    total_correct = 0
    total_examples = 0
    context = torch.enable_grad() if training else torch.inference_mode()
    with context:
        for inputs, labels in loader:
            inputs, labels = inputs.to(device), labels.to(device)
            if training:
                optimizer.zero_grad(set_to_none=True)
            logits = model(inputs)
            loss = criterion(logits, labels)
            if training:
                loss.backward()
                optimizer.step()
            total_examples += labels.shape[0]
            total_loss += float(loss.detach()) * labels.shape[0]
            total_correct += int((logits.argmax(dim=1) == labels).sum())
    if total_examples == 0:
        raise ValueError("The loader produced no examples.")
    return EpochResult(
        loss=total_loss / total_examples,
        accuracy=total_correct / total_examples,
        examples=total_examples,
    )
