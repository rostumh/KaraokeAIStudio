from __future__ import annotations
from urllib.parse import quote
import requests
from .base import LyricsProvider
from ..models import LyricsResult,LyricsSource,SongIdentity

class LyricsOvhProvider(LyricsProvider):
    """Free no-key plain-lyrics fallback. LRCLIB remains first because it can return LRC."""
    BASE_URL='https://api.lyrics.ovh/v1'
    def __init__(self,timeout:tuple[float,float]=(3.05,15),session:requests.Session|None=None):
        self.timeout=timeout;self.session=session or requests.Session();self.session.headers.update({'User-Agent':'KaraokeAIStudio/0.28.3'})
    @property
    def name(self)->str:return 'Lyrics.ovh'
    def search(self,song:SongIdentity)->LyricsResult|None:
        if not song.artist or not song.title:return None
        url=f'{self.BASE_URL}/{quote(song.artist,safe="")}/{quote(song.title,safe="")}'
        response=self.session.get(url,timeout=self.timeout)
        if response.status_code==404:return None
        response.raise_for_status();lyrics=response.json().get('lyrics')
        return LyricsResult(song,lyrics,LyricsSource.ONLINE,self.name,False) if isinstance(lyrics,str) and lyrics.strip() else None
