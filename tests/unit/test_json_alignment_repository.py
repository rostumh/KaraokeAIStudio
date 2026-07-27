import json
from pathlib import Path
from app.domain.models.alignment import *
from app.domain.models.transcription import *
from app.infrastructure.repositories.json_alignment_repository import JsonAlignmentRepository
def test_writes_unicode_alignment(tmp_path:Path):
 o=TranscriptionOptions("small",WhisperDevice.CPU,"int8","tl",TranscriptionTask.TRANSCRIBE,5,True,True,None);t=Transcript(tmp_path/"v.wav","tl",.9,2,o,(TranscriptSegment(0,0,2,"Kumusta",-.1,.1),));a=AlignedTranscript(t.source_path,t,(WordTiming(0,0,"Kumusta",0,1,.9),),"test");p=JsonAlignmentRepository().save(a,tmp_path);assert json.loads(p.read_text(encoding="utf-8"))["words"][0]["text"]=="Kumusta"
