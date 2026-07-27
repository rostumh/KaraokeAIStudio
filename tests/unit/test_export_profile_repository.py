from pathlib import Path
from app.domain.models.export_profile import ExportProfile
from app.domain.models.video_render import *
from app.infrastructure.repositories.export_profile_repository import ExportProfileRepository
def test_round_trip(tmp_path:Path):
 p=ExportProfile("user.x","X","d",VideoCodec.HEVC,VideoContainer.MKV,RenderEncoder.SOFTWARE,3840,2160,30,18,320);r=ExportProfileRepository(tmp_path/"profiles.json");r.save((p,));assert r.load()==(p,)
