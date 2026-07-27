from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.domain.models.alignment import AlignedTranscript


@dataclass(frozen=True, slots=True)
class EditableWord:
    word_id: int
    segment_id: int
    text: str
    start_seconds: float
    end_seconds: float
    probability: float


@dataclass(frozen=True, slots=True)
class LyricsDocument:
    source_path: Path
    language: str
    duration_seconds: float
    words: tuple[EditableWord, ...]
    revision: int

    @classmethod
    def from_alignment(cls, alignment: AlignedTranscript) -> "LyricsDocument":
        words = tuple(EditableWord(w.word_id, w.segment_id, w.text, w.start_seconds, w.end_seconds, w.probability) for w in alignment.words)
        return cls(alignment.source_path, alignment.transcript.language, alignment.duration_seconds, words, 0)
