import json
from pathlib import Path
from app.domain.models.transcription import *
from app.infrastructure.repositories.json_transcript_repository import JsonTranscriptRepository
def test_repository_writes_unicode_json_and_text(tmp_path:Path):
 options=TranscriptionOptions("small",WhisperDevice.CPU,"int8","tl",TranscriptionTask.TRANSCRIBE,5,True,True,None);t=Transcript(tmp_path/"song.wav","tl",.9,1,options,(TranscriptSegment(0,0,1,"Kumusta",-.1,.01),));paths=JsonTranscriptRepository().save(t,tmp_path);assert json.loads(paths[0].read_text(encoding="utf-8"))["segments"][0]["text"]=="Kumusta";assert "Kumusta" in paths[1].read_text(encoding="utf-8")
