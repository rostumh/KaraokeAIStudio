from pathlib import Path
from threading import Event
import pytest
from app.application.errors import MediaImportError
from app.application.services.instrumental_cleanup_service import InstrumentalCleanupService
from app.domain.models.instrumental_cleanup import CleanupOutputFormat,CleanupPreset,CleanupSettings,InstrumentalCleanupResult
from app.domain.models.media import AudioStream,MediaAsset,MediaKind
class Stub:
 def clean(self,request,progress,cancel):return InstrumentalCleanupResult(request.output_path,1,.1,request.settings)
def asset(path):return MediaAsset("id",path,path.name,MediaKind.AUDIO,1,10,"wav",None,(AudioStream(0,"pcm",48000,2,None,None,None),),(),{})
def settings():return CleanupSettings(CleanupPreset.BALANCED,10,-50,30,19000,-16,-1.5,9,True,CleanupOutputFormat.WAV_24)
def test_valid_cleanup(tmp_path):
 source=tmp_path/"instrumental.wav";source.write_bytes(b"x");result=InstrumentalCleanupService(Stub()).clean(asset(source),tmp_path/"clean.wav",settings(),overwrite=False,progress=lambda x:None,cancel_event=Event());assert result.output_path.name=="clean.wav"
def test_rejects_invalid_filter_range(tmp_path):
 source=tmp_path/"instrumental.wav";source.write_bytes(b"x");bad=CleanupSettings(CleanupPreset.CUSTOM,10,-50,20000,19000,-16,-1.5,9,True,CleanupOutputFormat.WAV_24)
 with pytest.raises(MediaImportError,match="High-pass"):InstrumentalCleanupService(Stub()).clean(asset(source),tmp_path/"clean.wav",bad,overwrite=False,progress=lambda x:None,cancel_event=Event())
