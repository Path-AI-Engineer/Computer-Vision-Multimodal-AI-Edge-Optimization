from __future__ import annotations

import json
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import numpy as np
from PIL import Image

from backend.app.core.errors import CapabilityUnavailableError
from backend.app.services.store import ExtractionStore
from document_ai.core.contracts import ExtractionRecord
from document_ai.extraction.layout import extract_fields
from document_ai.ingestion.validator import validate_upload
from document_ai.ocr.adapters import FixtureOcrAdapter, OcrUnavailableError, PaddleOcrAdapter
from document_ai.preprocessing.pipeline import apply_preprocessing


class ExtractionService:
    def __init__(self, root: Path, max_upload_bytes: int, ttl_seconds: int) -> None:
        self.root = root
        self.max_upload_bytes = max_upload_bytes
        self.store = ExtractionStore(ttl_seconds)

    def list_samples(self) -> list[dict[str, object]]:
        manifest_path = self.root / "data" / "manifests" / "qualification.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        samples = []
        for item in manifest["samples"]:
            annotation = json.loads((self.root / item["annotation"]).read_text(encoding="utf-8"))
            samples.append(
                {
                    "sample_id": item["sample_id"],
                    "image_url": f"/assets/samples/{item['sample_id']}.png",
                    "width": annotation["width"],
                    "height": annotation["height"],
                    "locale": annotation["locale"],
                }
            )
        return samples

    def extract_sample(self, sample_id: str, profile: str) -> ExtractionRecord:
        annotation_path = self.root / "data" / "samples" / f"{sample_id}.json"
        image_path = self.root / "data" / "samples" / f"{sample_id}.png"
        if not annotation_path.exists() or not image_path.exists():
            raise FileNotFoundError(f"Unknown sealed sample: {sample_id}")
        annotation = json.loads(annotation_path.read_text(encoding="utf-8"))
        image = np.asarray(Image.open(image_path).convert("RGB"))
        apply_preprocessing(image, profile)
        tokens = FixtureOcrAdapter(annotation_path).recognize(image)
        return self._record(
            sample_id=sample_id,
            source_name=image_path.name,
            source_kind="sealed-qualification-sample",
            profile=profile,
            adapter="annotated-fixture-v1",
            width=annotation["width"],
            height=annotation["height"],
            tokens=tokens,
            warnings=("Qualification fixture; not an official SROIE benchmark sample.",),
        )

    def extract_upload(
        self,
        payload: bytes,
        filename: str,
        content_type: str | None,
        profile: str,
    ) -> ExtractionRecord:
        safe_name, width, height = validate_upload(
            payload,
            filename,
            content_type,
            self.max_upload_bytes,
        )
        if content_type == "application/pdf":
            raise CapabilityUnavailableError(
                "PDF validation passed, but rasterization is not installed in this "
                "release candidate. "
                "Export the single page as PNG/JPEG or use a sealed sample."
            )
        assert width is not None and height is not None
        image = np.asarray(Image.open(BytesIO(payload)).convert("RGB"))
        processed = apply_preprocessing(image, profile)
        try:
            tokens = PaddleOcrAdapter().recognize(processed.image)
        except OcrUnavailableError as error:
            raise CapabilityUnavailableError(str(error)) from error
        return self._record(
            sample_id=None,
            source_name=safe_name,
            source_kind="operator-upload",
            profile=profile,
            adapter="paddleocr-v3",
            width=width,
            height=height,
            tokens=tokens,
            warnings=(),
        )

    def _record(
        self,
        *,
        sample_id: str | None,
        source_name: str,
        source_kind: str,
        profile: str,
        adapter: str,
        width: int,
        height: int,
        tokens: tuple,
        warnings: tuple[str, ...],
    ) -> ExtractionRecord:
        record = ExtractionRecord(
            request_id=str(uuid4()),
            sample_id=sample_id,
            source_name=source_name,
            source_kind=source_kind,
            created_at=datetime.now(UTC).isoformat(),
            pipeline_version="document-extractor-v1",
            preprocessing_profile=profile,
            ocr_adapter=adapter,
            width=width,
            height=height,
            tokens=tokens,
            fields=extract_fields(tokens, width, height),
            warnings=warnings,
        )
        self.store.put(record)
        return record
