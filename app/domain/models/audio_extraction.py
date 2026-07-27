from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class AudioFormat(StrEnum):
    WAV_PCM_16 = "wav_pcm_16"
    WAV_PCM_24 = "wav_pcm_24"
    FLAC = "flac"
    MP3 = "mp3"


@dataclass(frozen=True, slots=True)
class AudioExtractionRequest:
    source_path: Path
    output_path: Path
    stream_index: int
    duration_seconds: float
    output_format: AudioFormat
    sample_rate: int | None = None
    channels: int | None = None
    mp3_bitrate_kbps: int = 320
    overwrite: bool = False


@dataclass(frozen=True, slots=True)
class AudioExtractionResult:
    output_path: Path
    size_bytes: int
    elapsed_seconds: float
    format: AudioFormat
