from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class CheckSeverity(StrEnum):
    PASS = "pass"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class QualityCheck:
    code: str
    severity: CheckSeverity
    title: str
    detail: str


@dataclass(frozen=True, slots=True)
class MediaQualityReport:
    source_path: Path
    generated_utc: str
    duration_seconds: float
    size_bytes: int
    container: str
    video_codec: str | None
    audio_codec: str | None
    width: int | None
    height: int | None
    frame_rate: float | None
    sample_rate: int | None
    audio_channels: int | None
    checks: tuple[QualityCheck, ...]

    @property
    def passed(self) -> bool:
        return not any(check.severity == CheckSeverity.ERROR for check in self.checks)

    @property
    def warning_count(self) -> int:
        return sum(check.severity == CheckSeverity.WARNING for check in self.checks)
