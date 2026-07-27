from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class TranslationOptions:
    source_language: str
    target_language: str
    preserve_line_breaks: bool = True
    source_label: str = "Original"
    target_label: str = "Translation"


@dataclass(frozen=True, slots=True)
class TranslatedLine:
    line_id: int
    start_seconds: float
    end_seconds: float
    source_text: str
    translated_text: str


@dataclass(frozen=True, slots=True)
class TranslationDocument:
    source_path: Path
    source_language: str
    target_language: str
    engine: str
    lines: tuple[TranslatedLine, ...]

    @property
    def translated_text(self) -> str:
        return "\n".join(line.translated_text for line in self.lines)
