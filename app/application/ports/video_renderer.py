from __future__ import annotations

from collections.abc import Callable
from threading import Event
from typing import Protocol
from app.domain.models.video_render import VideoRenderRequest, VideoRenderResult

RenderProgress = Callable[[float, str], None]


class VideoRenderer(Protocol):
    def render(self, request: VideoRenderRequest, progress: RenderProgress, cancel_event: Event) -> VideoRenderResult:
        """Render a karaoke video and return a validated final artifact."""
