from __future__ import annotations
from collections.abc import Callable
from .engine import LyricsEngine
from .identity import ParsedSong,SongIdentityResolver
from .models import LyricsResult,SongIdentity
class AutomaticLyricsSearch:
    """Small automatic facade: resolve identity, try online/cache/local candidates, then request Whisper."""
    def __init__(self,engine:LyricsEngine,resolver:SongIdentityResolver|None=None):self.engine=engine;self.resolver=resolver or SongIdentityResolver()
    def search(self,path,tags,duration,progress:Callable[[str],None]=lambda _:None)->tuple[LyricsResult|None,SongIdentity]:
        progress('Reading filename...');parsed=self.resolver.resolve(path,tags,duration)
        candidates=(parsed.primary,*parsed.alternatives)
        progress('Searching online lyrics...')
        for song in candidates:
            outcome=self.engine.search(song,lambda _:None,allow_whisper=False)
            if outcome.result:
                progress('Lyrics found.');return outcome.result,song
        progress('Online search failed.');return None,parsed.primary
