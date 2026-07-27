from __future__ import annotations

from collections.abc import Callable
from threading import Event
from typing import Protocol

from app.domain.models.audio_extraction import AudioExtractionRequest, AudioExtractionResult

ProgressCallback = Callable[[float], None]


class AudioExtractor(Protocol):
    def extract(
        self,
        request: AudioExtractionRequest,
        progress: ProgressCallback,
        cancel_event: Event,
    ) -> AudioExtractionResult:
        """Extract one audio stream and report normalized progress from zero to one."""
