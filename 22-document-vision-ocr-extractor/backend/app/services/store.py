from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from threading import RLock

from document_ai.core.contracts import ExtractionRecord


@dataclass(frozen=True)
class StoredRecord:
    record: ExtractionRecord
    expires_at: datetime


class ExtractionStore:
    def __init__(self, ttl_seconds: int) -> None:
        self._ttl = timedelta(seconds=ttl_seconds)
        self._records: dict[str, StoredRecord] = {}
        self._lock = RLock()

    def put(self, record: ExtractionRecord) -> None:
        with self._lock:
            self._records[record.request_id] = StoredRecord(record, datetime.now(UTC) + self._ttl)
            self._purge()

    def get(self, request_id: str) -> ExtractionRecord | None:
        with self._lock:
            self._purge()
            item = self._records.get(request_id)
            return item.record if item else None

    def _purge(self) -> None:
        now = datetime.now(UTC)
        expired = [key for key, value in self._records.items() if value.expires_at <= now]
        for key in expired:
            del self._records[key]
