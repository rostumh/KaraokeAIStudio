from __future__ import annotations
import re
from dataclasses import replace
from app.domain.models.transcription import Transcript,TranscriptSegment
class FilipinoLyricsPostProcessor:
 """Conservative Filipino/Taglish cleanup. Never inserts unsupported words."""
 _literal=((r'\bdi ba\b',"'di ba"),(r'\bdiba\b',"'di ba"),(r'\bwag\b',"'wag"),(r'\byun\b',"'yun"),(r'\byong\b',"'yong"),(r'\bkase\b','kasi'))
 def clean_text(self,text:str)->str:
  text=re.sub(r'\s+',' ',text).strip()
  for pattern,replacement in self._literal:text=re.sub(pattern,replacement,text,flags=re.I)
  text=re.sub(r'\s+([,.;:!?])',r'\1',text)
  if text:
   index=1 if text.startswith("'") and len(text)>1 else 0
   text=text[:index]+text[index].upper()+text[index+1:]
  return text
 def process(self,transcript:Transcript)->Transcript:
  segments=tuple(replace(s,text=self.clean_text(s.text)) for s in transcript.segments if self.clean_text(s.text))
  return replace(transcript,segments=segments)
