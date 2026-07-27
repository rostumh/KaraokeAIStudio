from __future__ import annotations
import logging,time
from collections.abc import Callable
from .cache import SQLiteLyricsCache
from .local_files import LocalLyricsFinder
from .models import LyricsResult,LyricsSource,SearchOutcome,SongIdentity
from .normalization import LyricsCleaner
from .providers.manager import LyricsProviderManager
Progress=Callable[[str],None]
WhisperFallback=Callable[[SongIdentity,Progress],LyricsResult|None]
class LyricsEngine:
    """Independent orchestration service. No Qt or main-application dependencies."""
    def __init__(self,cache:SQLiteLyricsCache,local:LocalLyricsFinder,providers:LyricsProviderManager,cleaner:LyricsCleaner|None=None,whisper:WhisperFallback|None=None,logger:logging.Logger|None=None):
        self.cache=cache;self.local=local;self.providers=providers;self.cleaner=cleaner or LyricsCleaner();self.whisper=whisper;self.log=logger or logging.getLogger('lyrics')
    def search(self,song:SongIdentity,progress:Progress=lambda _:None,allow_whisper:bool=True)->SearchOutcome:
        started=time.monotonic()
        for message,finder in (('Searching Cache...',self.cache.find),('Searching Local Files...',self.local.find),('Searching Online...',self.providers.search)):
            progress(message);self.log.info(message+' title=%s artist=%s',song.title,song.artist);result=finder(song)
            if result:return self._finish(result,started,progress)
        if not allow_whisper or self.whisper is None:
            self.log.info('All non-AI sources exhausted; Whisper required');return SearchOutcome(None,True,time.monotonic()-started)
        progress('Running Whisper...');self.log.info('Running Whisper fallback title=%s',song.title)
        result=self.whisper(song,progress)
        return self._finish(result,started,progress) if result else SearchOutcome(None,False,time.monotonic()-started)
    def _finish(self,result:LyricsResult,started:float,progress:Progress)->SearchOutcome:
        cleaned=LyricsResult(result.song,self.cleaner.clean(result.lyrics),result.source,result.provider,result.synchronized,result.source_path)
        if cleaned.source is not LyricsSource.CACHE:self.cache.save(cleaned)
        elapsed=time.monotonic()-started;self.log.info('Finished source=%s provider=%s elapsed=%.3f',cleaned.source,cleaned.provider,elapsed);progress('Finished.')
        return SearchOutcome(cleaned,False,elapsed)
