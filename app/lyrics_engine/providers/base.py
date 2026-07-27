from __future__ import annotations
from abc import ABC,abstractmethod
from ..models import LyricsResult,SongIdentity
class LyricsProvider(ABC):
    @property
    @abstractmethod
    def name(self)->str:...
    @abstractmethod
    def search(self,song:SongIdentity)->LyricsResult|None:...
