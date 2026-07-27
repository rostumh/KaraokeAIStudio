from __future__ import annotations

from collections.abc import Callable
from threading import Event
from typing import Protocol

from app.domain.models.transcription import Transcript, TranscriptionOptions
from pathlib import Path

TranscriptionProgress = Callable[[float, str], None]


class SpeechRecognizer(Protocol):
    def transcribe(self, source: Path, duration_seconds: float, options: TranscriptionOptions, progress: TranscriptionProgress, cancel_event: Event) -> Transcript:
        """Recognize speech and return timestamped transcript segments."""
