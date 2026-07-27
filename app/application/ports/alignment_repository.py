from __future__ import annotations

from pathlib import Path
from typing import Protocol
from app.domain.models.alignment import AlignedTranscript


class AlignmentRepository(Protocol):
    def save(self, alignment: AlignedTranscript, destination: Path) -> Path:
        """Persist canonical word-alignment data atomically."""
