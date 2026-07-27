from __future__ import annotations
from pathlib import Path
from .models import LyricsResult,LyricsSource,SongIdentity
from .normalization import TextNormalizer
class LocalLyricsFinder:
    EXTENSIONS=('.lrc','.txt','.srt','.ass')
    def find(self,song:SongIdentity)->LyricsResult|None:
        if not song.media_path:return None
        folder=song.media_path.parent; stems={TextNormalizer.key(song.media_path.stem),TextNormalizer.key(song.title)}
        candidates=sorted((p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in self.EXTENSIONS),key=lambda p:self.EXTENSIONS.index(p.suffix.lower()))
        for path in candidates:
            if TextNormalizer.key(path.stem) in stems:
                return LyricsResult(song,path.read_text(encoding='utf-8-sig',errors='replace'),LyricsSource.LOCAL_FILE,path.suffix.lower()[1:].upper(),path.suffix.lower()=='.lrc',path)
        return None
