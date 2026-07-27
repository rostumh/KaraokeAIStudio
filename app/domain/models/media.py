from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Mapping


class MediaKind(StrEnum):
    AUDIO = "audio"
    VIDEO = "video"


@dataclass(frozen=True, slots=True)
class AudioStream:
    index: int
    codec: str
    sample_rate: int | None
    channels: int | None
    channel_layout: str | None
    bit_rate: int | None
    language: str | None


@dataclass(frozen=True, slots=True)
class VideoStream:
    index: int
    codec: str
    width: int
    height: int
    frame_rate: float | None
    pixel_format: str | None
    bit_rate: int | None


@dataclass(frozen=True, slots=True)
class MediaAsset:
    asset_id: str
    source_path: Path
    display_name: str
    kind: MediaKind
    size_bytes: int
    duration_seconds: float
    container: str
    bit_rate: int | None
    audio_streams: tuple[AudioStream, ...]
    video_streams: tuple[VideoStream, ...]
    tags: Mapping[str, str]

    @property
    def primary_audio(self) -> AudioStream | None:
        return self.audio_streams[0] if self.audio_streams else None

    @property
    def primary_video(self) -> VideoStream | None:
        return self.video_streams[0] if self.video_streams else None
