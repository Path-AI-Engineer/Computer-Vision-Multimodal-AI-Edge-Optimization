from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")

from ml.models.small_cnn import SmallCNN  # noqa: E402
from ml.models.transfer import build_resnet18, trainable_parameters  # noqa: E402
from ml.training.engine import run_epoch  # noqa: E402


def test_small_cnn_forward_backward_contract() -> None:
    model = SmallCNN(classes=37)
    inputs = torch.rand(2, 3, 64, 64)
    labels = torch.tensor([1, 2])
    logits = model(inputs)
    assert tuple(logits.shape) == (2, 37)
    torch.nn.functional.cross_entropy(logits, labels).backward()
    assert any(parameter.grad is not None for parameter in model.parameters())


def test_frozen_resnet_exposes_trainable_head_without_downloading_weights() -> None:
    model = build_resnet18(classes=37, weights=None, frozen_backbone=True)
    assert model.fc.out_features == 37
    assert trainable_parameters(model) == model.fc.weight.numel() + model.fc.bias.numel()


def test_training_loop_records_examples() -> None:
    model = SmallCNN(classes=3)
    loader = [(torch.rand(2, 3, 32, 32), torch.tensor([0, 1]))]
    optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
    result = run_epoch(
        model,
        loader,
        torch.nn.CrossEntropyLoss(),
        device=torch.device("cpu"),
        optimizer=optimizer,
    )
    assert result.examples == 2
    assert result.loss > 0
