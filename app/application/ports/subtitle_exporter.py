from __future__ import annotations

from pathlib import Path
from typing import Protocol

from app.domain.models.subtitles import SubtitleDocument, SubtitleFormat


class SubtitleExporter(Protocol):
    format: SubtitleFormat

    def export(self, document: SubtitleDocument, destination: Path) -> Path:
        """Write one subtitle representation atomically and return its path."""
