from pathlib import Path
from threading import Event
import pytest
from app.application.errors import MediaImportError
from app.application.services.transcription_service import TranscriptionService
from app.domain.models.media import AudioStream,MediaAsset,MediaKind
from app.domain.models.transcription import Transcript,TranscriptSegment,TranscriptionOptions,TranscriptionTask,WhisperDevice
class Recognizer:
 def transcribe(self,source,duration,options,progress,cancel):return Transcript(source,"en",.9,duration,options,(TranscriptSegment(0,0,1,"Hello",-.1,.01),))
class Repo:
 def save(self,t,d):return d/"a.json",d/"a.txt"
def asset(p):return MediaAsset("id",p,p.name,MediaKind.AUDIO,1,10,"wav",None,(AudioStream(0,"pcm",16000,1,None,None,None),),(),{})
def options():return TranscriptionOptions("small",WhisperDevice.CPU,"int8",None,TranscriptionTask.TRANSCRIBE,5,True,True,None)
def test_transcription_saves_result(tmp_path):
 source=tmp_path/"v.wav";source.write_bytes(b"x");result,paths=TranscriptionService(Recognizer(),Repo()).transcribe(asset(source),options(),tmp_path/"out",lambda a,b:None,Event());assert result.text=="Hello" and paths[0].name=="a.json"
def test_rejects_unknown_model(tmp_path):
 source=tmp_path/"v.wav";source.write_bytes(b"x");bad=TranscriptionOptions("unknown",WhisperDevice.CPU,"int8",None,TranscriptionTask.TRANSCRIBE,5,True,True,None)
 with pytest.raises(MediaImportError):TranscriptionService(Recognizer(),Repo()).transcribe(asset(source),bad,tmp_path,lambda a,b:None,Event())
