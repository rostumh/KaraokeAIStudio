from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class SeparationMode(StrEnum):
    VOCALS = "vocals"
    FOUR_STEMS = "four_stems"


class ComputeDevice(StrEnum):
    AUTO = "auto"
    CPU = "cpu"
    CUDA = "cuda"


class StemFormat(StrEnum):
    WAV_24 = "wav24"
    FLAC = "flac"


@dataclass(frozen=True, slots=True)
class SeparationRequest:
    source_path: Path
    output_root: Path
    model_name: str
    mode: SeparationMode
    device: ComputeDevice
    stem_format: StemFormat
    shifts: int
    overlap: float
    segment_seconds: int | None


@dataclass(frozen=True, slots=True)
class SeparationResult:
    source_path: Path
    output_directory: Path
    stems: tuple[Path, ...]
    model_name: str
    device: str
    elapsed_seconds: float
