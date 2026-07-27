from pathlib import Path
from threading import Event
import pytest
from app.application.errors import MediaImportError
from app.application.services.word_alignment_service import WordAlignmentService
from app.domain.models.alignment import AlignedTranscript, WordTiming
from app.domain.models.transcription import *


def transcript(tmp_path):
    options=TranscriptionOptions("small",WhisperDevice.CPU,"int8","en",TranscriptionTask.TRANSCRIBE,5,True,True,None)
    return Transcript(tmp_path/"voice.wav","en",.9,10,options,(TranscriptSegment(0,0,2,"hello world",-.1,.01),))
class Aligner:
    def align(self,t,p,c):return AlignedTranscript(t.source_path,t,(WordTiming(0,0," hello",-.2,1.0,1.2),WordTiming(1,0,"world",.8,1.5,-.2)),"test")
class Repo:
    def save(self,a,d):return d/"alignment.json"
def test_normalizes_order_bounds_and_probability(tmp_path):
    aligned,_=WordAlignmentService(Aligner(),Repo()).align(transcript(tmp_path),tmp_path,lambda a,b:None,Event());assert aligned.words[0].start_seconds==0;assert aligned.words[1].start_seconds>=aligned.words[0].end_seconds;assert aligned.words[0].probability==1;assert aligned.words[1].probability==0
def test_rejects_empty_words(tmp_path):
    t=transcript(tmp_path);empty=AlignedTranscript(t.source_path,t,(),"test")
    with pytest.raises(MediaImportError):WordAlignmentService._validate_and_normalize(empty)
