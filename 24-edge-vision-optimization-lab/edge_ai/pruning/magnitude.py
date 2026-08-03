from __future__ import annotations

from typing import Any


def apply_global_magnitude_pruning(model: Any, amount: float) -> dict[str, float | int]:
    if not 0 < amount < 1:
        raise ValueError("Pruning amount must be in (0, 1).")
    try:
        import torch
        import torch.nn as nn
        import torch.nn.utils.prune as prune
    except ImportError as error:
        raise RuntimeError("Install requirements-research.txt before pruning.") from error
    parameters = [
        (module, "weight")
        for module in model.modules()
        if isinstance(module, (nn.Conv2d, nn.Linear))
    ]
    prune.global_unstructured(parameters, pruning_method=prune.L1Unstructured, amount=amount)
    for module, name in parameters:
        prune.remove(module, name)
    total = sum(parameter.numel() for parameter in model.parameters())
    zeros = sum(int(torch.count_nonzero(parameter == 0)) for parameter in model.parameters())
    return {
        "parameters": total,
        "zeros": zeros,
        "effective_sparsity": zeros / total if total else 0.0,
    }
