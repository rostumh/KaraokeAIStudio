from __future__ import annotations

from collections.abc import Callable
from threading import Event
from typing import Protocol

from app.domain.models.instrumental_cleanup import InstrumentalCleanupRequest, InstrumentalCleanupResult

CleanupProgress = Callable[[float], None]


class InstrumentalCleaner(Protocol):
    def clean(self, request: InstrumentalCleanupRequest, progress: CleanupProgress, cancel_event: Event) -> InstrumentalCleanupResult:
        """Process an instrumental source and return a validated output."""
