from __future__ import annotations

from collections.abc import Callable
from threading import Event
from typing import Protocol
from app.domain.models.batch import BatchJob

BatchProgress = Callable[[float, str], None]


class BatchJobExecutor(Protocol):
    def execute(self, job: BatchJob, progress: BatchProgress, cancel_event: Event) -> str:
        """Execute one queued job and return a completion message."""
