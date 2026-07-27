from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class CleanupPreset(StrEnum):
    GENTLE = "gentle"
    BALANCED = "balanced"
    STRONG = "strong"
    CUSTOM = "custom"


class CleanupOutputFormat(StrEnum):
    WAV_24 = "wav24"
    FLAC = "flac"


@dataclass(frozen=True, slots=True)
class CleanupSettings:
    preset: CleanupPreset
    noise_reduction_db: float
    noise_floor_db: float
    highpass_hz: int
    lowpass_hz: int
    target_lufs: float
    true_peak_db: float
    loudness_range: float
    limiter: bool
    output_format: CleanupOutputFormat


@dataclass(frozen=True, slots=True)
class InstrumentalCleanupRequest:
    source_path: Path
    output_path: Path
    stream_index: int
    duration_seconds: float
    settings: CleanupSettings
    overwrite: bool = False


@dataclass(frozen=True, slots=True)
class InstrumentalCleanupResult:
    output_path: Path
    size_bytes: int
    elapsed_seconds: float
    settings: CleanupSettings
