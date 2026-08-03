from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from threading import RLock
from uuid import uuid4

from multimodal.core.contracts import IndexMode, SearchMode, SearchState


@dataclass
class StoredSession:
    state: SearchState
    expires_at: datetime


class SessionStore:
    def __init__(self, ttl_seconds: int) -> None:
        self.ttl = timedelta(seconds=ttl_seconds)
        self.sessions: dict[str, StoredSession] = {}
        self.lock = RLock()

    def create(self, top_k: int, mode: SearchMode, index_mode: IndexMode) -> SearchState:
        with self.lock:
            self._purge()
            session_id = str(uuid4())
            state = SearchState(
                session_id=session_id, top_k=top_k, mode=mode, index_mode=index_mode
            )
            self.sessions[session_id] = StoredSession(state, datetime.now(UTC) + self.ttl)
            return state

    def get(self, session_id: str) -> SearchState | None:
        with self.lock:
            self._purge()
            stored = self.sessions.get(session_id)
            if stored:
                stored.expires_at = datetime.now(UTC) + self.ttl
                return stored.state
            return None

    def delete(self, session_id: str) -> bool:
        with self.lock:
            return self.sessions.pop(session_id, None) is not None

    def _purge(self) -> None:
        now = datetime.now(UTC)
        for key in [key for key, value in self.sessions.items() if value.expires_at <= now]:
            del self.sessions[key]
