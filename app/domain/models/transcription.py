from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class TranscriptionTask(StrEnum):
    TRANSCRIBE = "transcribe"
    TRANSLATE = "translate"


class WhisperDevice(StrEnum):
    AUTO = "auto"
    CPU = "cpu"
    CUDA = "cuda"


@dataclass(frozen=True, slots=True)
class TranscriptionOptions:
    model_name: str
    device: WhisperDevice
    compute_type: str
    language: str | None
    task: TranscriptionTask
    beam_size: int
    vad_filter: bool
    condition_on_previous_text: bool
    initial_prompt: str | None


@dataclass(frozen=True, slots=True)
class TranscriptSegment:
    segment_id: int
    start_seconds: float
    end_seconds: float
    text: str
    average_log_probability: float
    no_speech_probability: float


@dataclass(frozen=True, slots=True)
class Transcript:
    source_path: Path
    language: str
    language_probability: float
    duration_seconds: float
    options: TranscriptionOptions
    segments: tuple[TranscriptSegment, ...]

    @property
    def text(self) -> str:
        return " ".join(segment.text.strip() for segment in self.segments if segment.text.strip()).strip()
