from __future__ import annotations

from pathlib import Path
from threading import Event
from app.application.errors import MediaImportError
from app.application.ports.video_renderer import RenderProgress, VideoRenderer
from app.domain.models.video_render import RenderEncoder, VideoRenderRequest, VideoRenderResult


class VideoRenderService:
    """Validates render policy and delegates the FFmpeg implementation."""
    def __init__(self, renderer: VideoRenderer) -> None:
        self._renderer=renderer
    def render(self, request: VideoRenderRequest, progress: RenderProgress, cancel_event: Event) -> VideoRenderResult:
        generated = str(request.background_path) == "__generated_aurora__"
        for label,path in (("background",request.background_path),("audio",request.audio_path),("subtitle",request.subtitle_path)):
            if label == "background" and generated: continue
            if not path.is_file():raise MediaImportError(f"The {label} file does not exist: {path}")
        if request.subtitle_path.suffix.lower() != ".ass":raise MediaImportError("Video rendering requires an ASS subtitle file.")
        if request.output_path in {request.background_path,request.audio_path,request.subtitle_path}:raise MediaImportError("The output path must differ from every input path.")
        if request.output_path.exists() and not request.overwrite:raise MediaImportError(f"The output file already exists: {request.output_path}")
        if (request.width,request.height) not in {(1280,720),(1920,1080),(3840,2160)}:raise MediaImportError("Unsupported output resolution.")
        if request.frame_rate not in {24,25,30,50,60}:raise MediaImportError("Unsupported output frame rate.")
        if not 0<=request.quality<=51:raise MediaImportError("Video quality must be between 0 and 51.")
        request.output_path.parent.mkdir(parents=True,exist_ok=True)
        try:
            return self._renderer.render(request,progress,cancel_event)
        except Exception as exc:
            text=str(exc).casefold()
            hardware_failure=any(token in text for token in ("could not open encoder","no capable devices","function not implemented","nvenc api","device not found"))
            if request.encoder != RenderEncoder.SOFTWARE and hardware_failure and not cancel_event.is_set():
                from dataclasses import replace
                progress(0.0,"Hardware encoder unavailable; retrying with compatible CPU encoding")
                fallback=replace(request,encoder=RenderEncoder.SOFTWARE,overwrite=True)
                return self._renderer.render(fallback,progress,cancel_event)
            raise
