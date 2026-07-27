from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
from .models import SongIdentity

@dataclass(frozen=True,slots=True)
class ParsedSong:
    primary:SongIdentity
    alternatives:tuple[SongIdentity,...]=()

class SongIdentityResolver:
    """Prefer embedded metadata; otherwise derive safe search candidates from the filename."""
    _spaces=re.compile(r'\s+')
    def resolve(self,path:Path,tags:Mapping[str,str],duration_seconds:float=0)->ParsedSong:
        lower={str(k).casefold():str(v).strip() for k,v in tags.items()}
        title=lower.get('title','').strip();artist=(lower.get('artist') or lower.get('album_artist') or '').strip();album=lower.get('album','').strip()
        if title:
            return ParsedSong(SongIdentity(title,artist,album,duration_seconds,path))
        raw_stem=path.stem
        stem=self._clean(raw_stem)
        parts=self._split(raw_stem)
        if len(parts)>=2:
            left,right=parts[0],self._clean(' - '.join(parts[1:]))
            primary=SongIdentity(right,left,'',duration_seconds,path)
            alternate=SongIdentity(left,right,'',duration_seconds,path)
            return ParsedSong(primary,(alternate,))
        return ParsedSong(SongIdentity(stem,'','',duration_seconds,path))
    def _split(self,stem:str)->list[str]:
        if re.search(r'\s[-–—]\s',stem):return [self._clean(x) for x in re.split(r'\s[-–—]\s',stem) if self._clean(x)]
        if '_' in stem:return [self._clean(x) for x in stem.split('_',1) if self._clean(x)]
        return [stem]
    def _clean(self,value:str)->str:
        value=re.sub(r'^\s*\d{1,3}[. _-]+','',value)
        value=re.sub(r'\s*[\[(](official\s+)?(audio|video|lyrics?|lyric video)[\]) ]\s*$','',value,flags=re.I)
        return self._spaces.sub(' ',value.replace('_',' ')).strip(' -_')
