from __future__ import annotations

import hashlib
import json
from pathlib import Path

from multimodal.core.contracts import Caption, CorpusItem


class ManifestError(ValueError):
    """Raised when a corpus manifest violates the data contract."""


def load_manifest(path: Path, verify_assets: bool = True) -> tuple[CorpusItem, ...]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return parse_manifest(payload, path.parent.parent / "samples", verify_assets)


def parse_manifest(
    payload: dict, asset_directory: Path | None = None, verify_assets: bool = False
) -> tuple[CorpusItem, ...]:
    seen_images: set[str] = set()
    seen_captions: set[str] = set()
    items: list[CorpusItem] = []
    for raw in payload.get("items", []):
        image_id = str(raw["image_id"])
        if image_id in seen_images:
            raise ManifestError(f"Duplicate image_id: {image_id}")
        seen_images.add(image_id)
        captions: list[Caption] = []
        for caption in raw["captions"]:
            caption_id = str(caption["caption_id"])
            if caption_id in seen_captions:
                raise ManifestError(f"Duplicate caption_id: {caption_id}")
            seen_captions.add(caption_id)
            captions.append(Caption(caption_id, str(caption["text"])))
        vector = tuple(float(value) for value in raw["vector"])
        if not captions or not vector:
            raise ManifestError(f"Incomplete item: {image_id}")
        filename = str(raw["filename"])
        asset = asset_directory / filename if asset_directory else None
        if verify_assets and (asset is None or not asset.is_file()):
            raise ManifestError(f"Missing image asset: {filename}")
        checksum = (
            hashlib.sha256(asset.read_bytes()).hexdigest() if asset and asset.is_file() else ""
        )
        expected = str(raw.get("checksum", "AUTO"))
        if verify_assets and expected not in {"AUTO", checksum}:
            raise ManifestError(f"Checksum mismatch: {image_id}")
        items.append(
            CorpusItem(
                image_id=image_id,
                filename=filename,
                split=str(raw["split"]),
                category=str(raw["category"]),
                colors=tuple(str(value) for value in raw["colors"]),
                has_people=bool(raw["has_people"]),
                captions=tuple(captions),
                vector=vector,
                checksum=checksum,
            )
        )
    if not items:
        raise ManifestError("The corpus is empty.")
    return tuple(items)
