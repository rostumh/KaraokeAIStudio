from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

class LyricsSource(StrEnum):
    CACHE='Local Cache'; LOCAL_FILE='Local File'; ONLINE='Online Provider'; WHISPER='Whisper AI'

@dataclass(frozen=True,slots=True)
class SongIdentity:
    title:str; artist:str=''; album:str=''; duration_seconds:float=0; media_path:Path|None=None; language:str=''

@dataclass(frozen=True,slots=True)
class LyricsResult:
    song:SongIdentity; lyrics:str; source:LyricsSource; provider:str; synchronized:bool=False; source_path:Path|None=None

@dataclass(frozen=True,slots=True)
class SearchOutcome:
    result:LyricsResult|None; whisper_required:bool; elapsed_seconds:float
