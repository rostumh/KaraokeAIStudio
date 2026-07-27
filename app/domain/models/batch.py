from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from uuid import uuid4


class BatchOperation(StrEnum):
    EXTRACT_WAV24 = "extract_wav24"
    VALIDATE_FINAL = "validate_final"


class BatchStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class BatchJob:
    job_id: str
    operation: BatchOperation
    source_path: Path
    output_path: Path
    status: BatchStatus
    progress: float
    message: str
    attempts: int
    created_utc: str
    started_utc: str | None = None
    finished_utc: str | None = None

    @classmethod
    def create(cls, operation: BatchOperation, source: Path, output: Path) -> "BatchJob":
        return cls(uuid4().hex, operation, source.resolve(strict=False), output.resolve(strict=False), BatchStatus.QUEUED, 0.0, "Queued", 0, datetime.now(timezone.utc).isoformat())

    def update(self, **changes: object) -> "BatchJob":
        return replace(self, **changes)
