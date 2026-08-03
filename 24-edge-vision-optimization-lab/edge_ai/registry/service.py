from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class RegistryError(RuntimeError):
    """Raised for incompatible or incomplete variant bundles."""


class VariantRegistry:
    def __init__(self, path: Path) -> None:
        payload = json.loads(path.read_text(encoding="utf-8"))
        variants = payload.get("variants", [])
        if not variants:
            raise RegistryError("Variant registry is empty.")
        ids = [item.get("variant_id") for item in variants]
        if len(ids) != len(set(ids)):
            raise RegistryError("Variant IDs must be unique.")
        expected_model = payload.get("model_version")
        expected_environment = payload.get("environment_id")
        for item in variants:
            if item.get("status") == "NOT_RUN":
                continue
            if item.get("model_version") != expected_model:
                raise RegistryError("Variant model versions are incompatible.")
            if item.get("environment_id") != expected_environment:
                raise RegistryError("Measured variants must share one environment.")
        self.payload = payload
        self._variants = {str(item["variant_id"]): item for item in variants}

    def list(self) -> list[dict[str, Any]]:
        return list(self._variants.values())

    def get(self, variant_id: str) -> dict[str, Any]:
        try:
            return self._variants[variant_id]
        except KeyError as error:
            raise RegistryError(f"Unknown variant: {variant_id}") from error

    def approved(self) -> list[dict[str, Any]]:
        return [item for item in self.list() if item["status"].startswith("APPROVED")]
