from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Protocol

import numpy as np

from document_ai.core.contracts import OcrToken


class OcrUnavailableError(RuntimeError):
    """Raised when a real OCR runtime is required but not installed."""


class OcrAdapter(Protocol):
    name: str

    def recognize(self, image: np.ndarray) -> tuple[OcrToken, ...]: ...


class FixtureOcrAdapter:
    """Loads sealed predictions for generated qualification samples only."""

    name = "annotated-fixture-v1"

    def __init__(self, annotation_path: Path) -> None:
        self.annotation_path = annotation_path

    def recognize(self, image: np.ndarray) -> tuple[OcrToken, ...]:
        del image
        payload = json.loads(self.annotation_path.read_text(encoding="utf-8"))
        return tuple(
            OcrToken(
                token_id=item["token_id"],
                text=item["text"],
                confidence=float(item["confidence"]),
                box=tuple(item["box"]),
                line_index=int(item["line_index"]),
            )
            for item in payload["predicted_tokens"]
        )


class PaddleOcrAdapter:
    name = "paddleocr-v3"

    @staticmethod
    def available() -> bool:
        return importlib.util.find_spec("paddleocr") is not None

    def recognize(self, image: np.ndarray) -> tuple[OcrToken, ...]:
        if not self.available():
            raise OcrUnavailableError(
                "Arbitrary uploads require the optional PaddleOCR runtime. "
                "Install requirements-ocr.txt or use a sealed qualification sample."
            )
        from paddleocr import PaddleOCR  # type: ignore[import-not-found]

        engine = PaddleOCR(use_doc_orientation_classify=True, lang="en")
        pages = engine.predict(image)
        tokens: list[OcrToken] = []
        for page in pages:
            result = page.json.get("res", page.json)
            texts = result.get("rec_texts", [])
            scores = result.get("rec_scores", [])
            boxes = result.get("rec_boxes", [])
            for index, (text, score, box) in enumerate(zip(texts, scores, boxes, strict=False)):
                x1, y1, x2, y2 = (int(value) for value in box)
                tokens.append(
                    OcrToken(
                        f"ocr-{index:03}",
                        text,
                        float(score),
                        (x1, y1, x2, y2),
                        index,
                    )
                )
        return tuple(tokens)
