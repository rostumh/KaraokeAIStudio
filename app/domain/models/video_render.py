from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class VideoCodec(StrEnum):
    H264 = "h264"
    HEVC = "hevc"


class VideoContainer(StrEnum):
    MP4 = "mp4"
    MKV = "mkv"


class RenderEncoder(StrEnum):
    SOFTWARE = "software"
    NVIDIA = "nvidia"
    INTEL = "intel"
    AMD = "amd"


@dataclass(frozen=True, slots=True)
class VideoRenderRequest:
    background_path: Path
    audio_path: Path
    subtitle_path: Path
    output_path: Path
    duration_seconds: float
    width: int
    height: int
    frame_rate: int
    codec: VideoCodec
    container: VideoContainer
    encoder: RenderEncoder
    quality: int
    audio_bitrate_kbps: int
    overwrite: bool = False
    watermark_path: Path | None = None
    watermark_position: str = "bottom-right"
    watermark_opacity: int = 75
    watermark_text: str = ""
    presentation: "VideokePresentation | None" = None


@dataclass(frozen=True, slots=True)
class VideoRenderResult:
    output_path: Path
    size_bytes: int
    elapsed_seconds: float
    encoder_name: str

@dataclass(frozen=True, slots=True)
class VideokePresentation:
    title: str = ""
    artist: str = ""
    songwriter: str = ""
    release_year: str = ""
    title_duration: float = 0.0
    countdown_duration: float = 5.0
    countdown_start: int = 5
    countdown_enabled: bool = True
    countdown_style: str = "bounce"
    cta_text: str = "Please Subscribe to Our Channel"
    cta_delay: float = 3.0
    cta_duration: float = 6.0
    font_name: str = "Segoe UI Semibold"
    title_font_size: int = 116
    lyric_font_size: int = 78
    preview_font_size: int = 48
    primary_color: str = "#FFFFFF"
    highlight_color: str = "#FFD83D"
    accent_color: str = "#FFD54F"
    ambient_motion: bool = True
    audio_reactive: bool = True
