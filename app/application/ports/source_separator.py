from __future__ import annotations

from collections.abc import Callable
from threading import Event
from typing import Protocol

from app.domain.models.separation import SeparationRequest, SeparationResult

StatusCallback = Callable[[str], None]


class SourceSeparator(Protocol):
    def separate(self, request: SeparationRequest, status: StatusCallback, cancel_event: Event) -> SeparationResult:
        """Separate source audio into validated stem files."""
