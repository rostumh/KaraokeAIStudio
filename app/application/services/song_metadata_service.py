from __future__ import annotations
import json,re,urllib.parse,urllib.request
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
@dataclass(frozen=True,slots=True)
class SongMetadata:
 title:str='';artist:str='';songwriter:str='';release_year:str='';source:str='';confidence:int=0;message:str=''
class OnlineSongMetadataService:
 USER_AGENT='KaraokeAIStudio/0.28.4 (contact: app metadata lookup)'
 @staticmethod
 def _norm(value):return re.sub(r'[^a-z0-9]+',' ',value.casefold()).strip()
 @classmethod
 def _similar(cls,a,b):return SequenceMatcher(None,cls._norm(a),cls._norm(b)).ratio() if a and b else 0.0
 def lookup(self,source:Path|None,title:str='',artist:str='',duration_seconds:float|None=None)->SongMetadata:
  stem=source.stem if source else ''
  clean=re.sub(r'(?i)\b(no[ _-]?vocals|instrumental|karaoke|videoke|official|lyrics?|music video|hd|4k|side[ _-]?[ab])\b',' ',stem).replace('_',' ');clean=re.sub(r'\s+',' ',clean).strip(' -_')
  if not title:
   parts=[p.strip() for p in re.split(r'\s+-\s+',clean) if p.strip()]
   if len(parts)>=2:artist,title=artist or parts[0],parts[1]
   else:title=clean.strip()
  if not title:return SongMetadata(message='Enter a song title or import tagged media first.')
  query=f'recording:"{title}"'+(f' AND artist:"{artist}"' if artist else '')
  url='https://musicbrainz.org/ws/2/recording/?'+urllib.parse.urlencode({'query':query,'fmt':'json','limit':8})
  try:
   req=urllib.request.Request(url,headers={'User-Agent':self.USER_AGENT,'Accept':'application/json'});data=json.loads(urllib.request.urlopen(req,timeout=7).read());best=None;best_score=0.0
   for item in data.get('recordings',[]):
    candidate_title=str(item.get('title',''));credits=item.get('artist-credit') or [];candidate_artist=''.join(str(x.get('name','')) for x in credits if isinstance(x,dict));score=.65*self._similar(title,candidate_title)+.25*(self._similar(artist,candidate_artist) if artist else .7)
    length=item.get('length')
    if duration_seconds and isinstance(length,(int,float)):score+=.10*max(0,1-abs(length/1000-duration_seconds)/12)
    if score>best_score:best_score=score;best=(item,candidate_title,candidate_artist)
   if not best or best_score<.72:return SongMetadata(title=title,artist=artist,message='No verified online match was found. Existing fields were kept for manual review.')
   item,candidate_title,candidate_artist=best;year=''
   for release in item.get('releases') or []:
    date=str(release.get('date',''));m=re.match(r'(18|19|20)\d{2}',date)
    if m:year=m.group(0);break
   return SongMetadata(candidate_title,candidate_artist,'',year,'MusicBrainz',round(best_score*100),f'Verified MusicBrainz match ({round(best_score*100)}% confidence). Songwriter was left blank unless independently verified.')
  except Exception as exc:return SongMetadata(title=title,artist=artist,message=f'Online lookup unavailable. Existing fields were kept. ({type(exc).__name__})')
