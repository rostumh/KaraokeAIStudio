from __future__ import annotations

from pathlib import Path
from typing import Protocol
from app.domain.models.transcription import Transcript


class TranscriptRepository(Protocol):
    def save(self, transcript: Transcript, destination: Path) -> tuple[Path, Path]:
        """Persist editable JSON and human-readable UTF-8 text representations."""
