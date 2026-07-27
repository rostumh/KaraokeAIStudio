from __future__ import annotations
import logging
from .base import LyricsProvider
from ..models import LyricsResult,SongIdentity
from ..validation import LyricsMatchValidator
class LyricsProviderManager:
    def __init__(self,providers:list[LyricsProvider],logger:logging.Logger|None=None,validator:LyricsMatchValidator|None=None):self._providers=list(providers);self._log=logger or logging.getLogger('lyrics');self._validator=validator or LyricsMatchValidator()
    def register(self,provider:LyricsProvider):self._providers.append(provider)
    def search(self,song:SongIdentity)->LyricsResult|None:
        accepted=[]
        for provider in tuple(self._providers):
            try:
                self._log.info('Trying provider=%s title=%s artist=%s',provider.name,song.title,song.artist)
                result=provider.search(song)
                if not result:continue
                score=self._validator.score(song,result)
                self._log.info('Candidate provider=%s accepted=%s confidence=%.3f %s',provider.name,score.accepted,score.confidence,score.reason)
                if score.accepted:accepted.append((result.synchronized,score.confidence,result))
            except Exception:self._log.exception('Provider failed provider=%s; continuing',provider.name)
        if not accepted:return None
        return max(accepted,key=lambda item:(item[0],item[1]))[2]
