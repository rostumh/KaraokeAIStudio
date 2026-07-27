from pathlib import Path
from threading import Event
import pytest
from app.application.errors import MediaImportError
from app.application.services.video_render_service import VideoRenderService
from app.domain.models.video_render import *
class Renderer:
 def render(self,r,p,c):return VideoRenderResult(r.output_path,1,.1,"libx264")
def request(tmp):
 paths=[tmp/x for x in ("bg.mp4","audio.wav","sub.ass")];[p.write_bytes(b"x") for p in paths];return VideoRenderRequest(*paths,tmp/"out.mp4",10,1920,1080,30,VideoCodec.H264,VideoContainer.MP4,RenderEncoder.SOFTWARE,20,320,False)
def test_valid_render(tmp_path):assert VideoRenderService(Renderer()).render(request(tmp_path),lambda a,b:None,Event()).encoder_name=="libx264"
def test_rejects_non_ass(tmp_path):
 r=request(tmp_path);bad=VideoRenderRequest(r.background_path,r.audio_path,tmp_path/"x.srt",r.output_path,10,1920,1080,30,r.codec,r.container,r.encoder,20,320,False);bad.subtitle_path.write_bytes(b"x")
 with pytest.raises(MediaImportError):VideoRenderService(Renderer()).render(bad,lambda a,b:None,Event())
