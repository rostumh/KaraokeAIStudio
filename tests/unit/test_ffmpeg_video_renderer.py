from pathlib import Path
from app.domain.models.video_render import *
from app.infrastructure.media.ffmpeg_video_renderer import FFmpegVideoRenderer
def test_command_contains_ass_scale_maps_and_progress(tmp_path):
 renderer=object.__new__(FFmpegVideoRenderer);renderer._executable=Path("ffmpeg");renderer._encoders={"libx264"};r=VideoRenderRequest(tmp_path/"bg.mp4",tmp_path/"a.wav",tmp_path/"s.ass",tmp_path/"o.mp4",10,1920,1080,30,VideoCodec.H264,VideoContainer.MP4,RenderEncoder.SOFTWARE,20,320,False);c=renderer._command(r,tmp_path/"part.mp4","libx264");assert "libx264" in c and "pipe:1" in c and any("ass=" in x and "scale=1920:1080" in x for x in c)
def test_windows_filter_path_escapes_drive_colon():assert r"\:" in FFmpegVideoRenderer._escape_filter_path(Path("C:/video/lyrics.ass"))
