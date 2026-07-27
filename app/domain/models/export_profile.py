from __future__ import annotations

from dataclasses import dataclass

from app.domain.models.video_render import RenderEncoder, VideoCodec, VideoContainer


@dataclass(frozen=True, slots=True)
class ExportProfile:
    profile_id: str
    name: str
    description: str
    codec: VideoCodec
    container: VideoContainer
    encoder: RenderEncoder
    width: int
    height: int
    frame_rate: int
    quality: int
    audio_bitrate_kbps: int
    builtin: bool = False


BUILTIN_EXPORT_PROFILES: tuple[ExportProfile, ...] = (
    ExportProfile("builtin.web-720p", "Web Preview 720p", "Fast H.264 preview for review and sharing.", VideoCodec.H264, VideoContainer.MP4, RenderEncoder.SOFTWARE, 1280, 720, 30, 23, 192, True),
    ExportProfile("builtin.standard-1080p", "Standard 1080p", "Compatible H.264 delivery master.", VideoCodec.H264, VideoContainer.MP4, RenderEncoder.SOFTWARE, 1920, 1080, 30, 20, 320, True),
    ExportProfile("builtin.high-motion-1080p", "High Motion 1080p60", "Smooth H.264 export for animated backgrounds.", VideoCodec.H264, VideoContainer.MP4, RenderEncoder.SOFTWARE, 1920, 1080, 60, 19, 320, True),
    ExportProfile("builtin.archive-4k", "4K HEVC Master", "High-quality HEVC archival output.", VideoCodec.HEVC, VideoContainer.MKV, RenderEncoder.SOFTWARE, 3840, 2160, 30, 18, 320, True),
)
