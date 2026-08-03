from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from assistant.orchestration.service import AssistantOrchestrator
from backend.app.services.session_store import SessionStore
from multimodal.data.manifest import load_manifest
from multimodal.retrieval.service import RetrievalService


@dataclass(frozen=True)
class Runtime:
    root: Path
    retrieval: RetrievalService
    sessions: SessionStore
    assistant: AssistantOrchestrator

    @classmethod
    def load(cls, root: Path, ttl_seconds: int) -> Runtime:
        items = load_manifest(root / "data" / "manifests" / "qualification-corpus.json")
        retrieval = RetrievalService(items)
        return cls(root, retrieval, SessionStore(ttl_seconds), AssistantOrchestrator(retrieval))

    def json_artifact(self, *parts: str) -> dict | list:
        return json.loads(self.root.joinpath(*parts).read_text(encoding="utf-8"))
