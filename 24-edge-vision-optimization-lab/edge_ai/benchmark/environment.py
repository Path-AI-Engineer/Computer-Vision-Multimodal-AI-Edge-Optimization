from __future__ import annotations

import os
import platform
from typing import Any

import numpy as np


def environment_manifest(*, profile: str = "host_cpu", threads: int = 1) -> dict[str, Any]:
    if profile not in {"host_cpu", "edge_proxy"}:
        raise ValueError("Only measured host_cpu and explicit edge_proxy profiles are supported.")
    return {
        "environment_id": f"{profile}-qualification-v1",
        "profile": profile,
        "hardware_model": platform.processor() or platform.machine() or "unknown-host-cpu",
        "architecture": platform.machine(),
        "os": platform.platform(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "execution_provider": "NumPy CPU qualification adapter",
        "threads": threads,
        "power_mode": os.getenv("EDGE_POWER_MODE", "NOT_OBSERVED"),
        "batch_size": 1,
        "input_size": [1, 3, 224, 224],
        "input_dtype": "float32",
        "warmup_iterations": 8,
        "measured_iterations": 40,
        "energy": "NOT_MEASURED",
        "claim_boundary": "This host measurement is not a physical edge-device benchmark.",
    }
