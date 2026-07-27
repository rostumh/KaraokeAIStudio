from __future__ import annotations
import requests
from .base import LyricsProvider
from ..models import LyricsResult,LyricsSource,SongIdentity
class LRCLibProvider(LyricsProvider):
    BASE_URL='https://lrclib.net/api'
    def __init__(self,timeout:tuple[float,float]=(3.05,12),session:requests.Session|None=None):
        self.timeout=timeout;self.session=session or requests.Session();self.session.headers.update({'User-Agent':'KaraokeAIStudio/0.28.3 (lyrics-engine)'})
    @property
    def name(self):return 'LRCLIB'
    def search(self,song:SongIdentity)->LyricsResult|None:
        params={'track_name':song.title,'artist_name':song.artist,'album_name':song.album,'duration':round(song.duration_seconds)}
        response=self.session.get(f'{self.BASE_URL}/get',params=params,timeout=self.timeout)
        if response.status_code==404:return self._search_flexible(song)
        response.raise_for_status();return self._result(song,response.json())
    def _search_flexible(self,song):
        response=self.session.get(f'{self.BASE_URL}/search',params={'track_name':song.title,'artist_name':song.artist,'album_name':song.album},timeout=self.timeout)
        response.raise_for_status()
        for item in response.json():
            result=self._result(song,item)
            if result:return result
        return None
    def _result(self,song,data):
        lyrics=data.get('syncedLyrics') or data.get('plainLyrics')
        if not lyrics or data.get('instrumental'):return None
        return LyricsResult(song,lyrics,LyricsSource.ONLINE,self.name,bool(data.get('syncedLyrics')))
