from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from app.domain.models.karaoke_effects import KaraokeEffectSettings


class SubtitleFormat(StrEnum):
    ASS = "ass"
    SRT = "srt"
    LRC = "lrc"


@dataclass(frozen=True, slots=True)
class SubtitleStyle:
    font_name: str = "Arial"
    font_size: int = 54
    primary_color: str = "#FFFFFF"
    highlight_color: str = "#00D7FF"
    outline_color: str = "#000000"
    outline_width: float = 3.0
    shadow_depth: float = 1.5
    margin_vertical: int = 54
    bold: bool = True
    alignment: int = 2
    effect_settings: KaraokeEffectSettings = KaraokeEffectSettings()


@dataclass(frozen=True, slots=True)
class SubtitleOptions:
    formats: tuple[SubtitleFormat, ...]
    max_words_per_line: int
    max_line_duration: float
    gap_threshold: float
    lead_in_seconds: float
    lead_out_seconds: float
    resolution_width: int
    resolution_height: int
    style: SubtitleStyle


@dataclass(frozen=True, slots=True)
class SubtitleWord:
    text: str
    start_seconds: float
    end_seconds: float


@dataclass(frozen=True, slots=True)
class SubtitleCue:
    cue_id: int
    start_seconds: float
    end_seconds: float
    words: tuple[SubtitleWord, ...]

    @property
    def text(self) -> str:
        return " ".join(word.text for word in self.words)


@dataclass(frozen=True, slots=True)
class SubtitleDocument:
    source_path: Path
    language: str
    duration_seconds: float
    cues: tuple[SubtitleCue, ...]
    options: SubtitleOptions
