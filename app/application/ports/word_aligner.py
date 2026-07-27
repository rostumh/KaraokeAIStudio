from __future__ import annotations

from collections.abc import Callable
from threading import Event
from typing import Protocol

from app.domain.models.alignment import AlignedTranscript
from app.domain.models.transcription import Transcript

AlignmentProgress = Callable[[float, str], None]


class WordAligner(Protocol):
    def align(self, transcript: Transcript, progress: AlignmentProgress, cancel_event: Event) -> AlignedTranscript:
        """Align recognized words to audio and return monotonically ordered timings."""
