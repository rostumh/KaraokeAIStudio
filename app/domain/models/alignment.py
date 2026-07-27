from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.domain.models.transcription import Transcript


@dataclass(frozen=True, slots=True)
class WordTiming:
    word_id: int
    segment_id: int
    text: str
    start_seconds: float
    end_seconds: float
    probability: float


@dataclass(frozen=True, slots=True)
class AlignedTranscript:
    source_path: Path
    transcript: Transcript
    words: tuple[WordTiming, ...]
    alignment_model: str

    @property
    def duration_seconds(self) -> float:
        return self.transcript.duration_seconds
