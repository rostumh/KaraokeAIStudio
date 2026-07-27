from __future__ import annotations
import re,unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from .models import LyricsResult,SongIdentity

def _key(value:str)->str:
 value=unicodedata.normalize('NFKD',value.casefold()).encode('ascii','ignore').decode();return re.sub(r'[^a-z0-9]+',' ',value).strip()
def _ratio(a:str,b:str)->float:return SequenceMatcher(None,_key(a),_key(b)).ratio() if a and b else 0.0
@dataclass(frozen=True,slots=True)
class MatchScore:
 accepted:bool;confidence:float;reason:str
class LyricsMatchValidator:
 """Deterministic, offline validator: rejects weak metadata and implausibly short/truncated text."""
 def score(self,requested:SongIdentity,candidate:LyricsResult)->MatchScore:
  title=_ratio(requested.title,candidate.song.title);artist=_ratio(requested.artist,candidate.song.artist) if requested.artist else .75
  chars=len(re.sub(r'\s+','',candidate.lyrics));duration=max(60.0,requested.duration_seconds or 210.0)
  expected=max(120.0,duration*2.2);length=min(1.0,chars/expected)
  confidence=.55*title+.30*artist+.15*length
  minimum_chars=80 if requested.duration_seconds else 4
  accepted=title>=.72 and artist>=.55 and chars>=minimum_chars and confidence>=.68
  return MatchScore(accepted,confidence,f'title={title:.2f}, artist={artist:.2f}, length={length:.2f}')
