from __future__ import annotations

from collections.abc import Callable
from threading import Event
from typing import Protocol
from pathlib import Path

from app.domain.models.quality_validation import MediaQualityReport

ValidationProgress = Callable[[float, str], None]


class MediaQualityValidator(Protocol):
    def validate(self, source: Path, progress: ValidationProgress, cancel_event: Event) -> MediaQualityReport:
        """Inspect metadata, decode the artifact, and return structured validation results."""
