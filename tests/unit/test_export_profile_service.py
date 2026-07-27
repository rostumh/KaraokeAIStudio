import pytest
from app.application.errors import MediaImportError
from app.application.services.export_profile_service import ExportProfileService
from app.domain.models.export_profile import ExportProfile
from app.domain.models.video_render import *
def profile():return ExportProfile("user.test","Test","",VideoCodec.H264,VideoContainer.MP4,RenderEncoder.SOFTWARE,1920,1080,30,20,320)
def test_merge_includes_builtins_user_and_plugin():
 values=ExportProfileService.merge((profile(),),{"plugin.web":("Web",{"codec":"h264","container":"mp4","width":1280,"height":720,"frame_rate":30,"quality":23,"audio_bitrate_kbps":192})});assert any(x.profile_id=="user.test" for x in values) and any(x.profile_id=="plugin.web" for x in values)
def test_rejects_invalid_resolution():
 p=profile();bad=ExportProfile(p.profile_id,p.name,p.description,p.codec,p.container,p.encoder,640,480,p.frame_rate,p.quality,p.audio_bitrate_kbps)
 with pytest.raises(MediaImportError):ExportProfileService.validate(bad)
