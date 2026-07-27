from __future__ import annotations
from dataclasses import dataclass
from app.domain.models.transcription import Transcript
@dataclass(frozen=True,slots=True)
class TranscriptQuality:
 accepted:bool;score:float;warning:str
class SingingTranscriptQualityGate:
 def evaluate(self,t:Transcript)->TranscriptQuality:
  if not t.segments:return TranscriptQuality(False,0,'No lyrics recognized.')
  spoken=sum(max(0,s.end_seconds-s.start_seconds) for s in t.segments);coverage=spoken/max(1,t.duration_seconds)
  mean_log=sum(s.average_log_probability for s in t.segments)/len(t.segments)
  no_speech=sum(s.no_speech_probability for s in t.segments)/len(t.segments)
  score=max(0,min(1,.45*min(1,coverage/.45)+.35*min(1,max(0,mean_log+1.5)/1.2)+.20*(1-no_speech)))
  warning='' if score>=.62 else 'Low-confidence singing transcription; review highlighted lyrics carefully.'
  return TranscriptQuality(score>=.42,score,warning)
