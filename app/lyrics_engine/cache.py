from __future__ import annotations
import sqlite3
from pathlib import Path
from .models import LyricsResult,LyricsSource,SongIdentity
from .normalization import TextNormalizer
class SQLiteLyricsCache:
    def __init__(self,path:Path):self.path=path;path.parent.mkdir(parents=True,exist_ok=True);self._init()
    def _connect(self):return sqlite3.connect(self.path,timeout=10)
    def _init(self):
        with self._connect() as db:
            db.execute('''CREATE TABLE IF NOT EXISTS Lyrics(id INTEGER PRIMARY KEY,title TEXT NOT NULL,artist TEXT,album TEXT,language TEXT,lyrics TEXT NOT NULL,source TEXT NOT NULL,provider TEXT,synchronized INTEGER NOT NULL DEFAULT 0,title_key TEXT NOT NULL,artist_key TEXT NOT NULL,album_key TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)''')
            db.execute('CREATE INDEX IF NOT EXISTS ix_lyrics_match ON Lyrics(title_key,artist_key,album_key)')
    def find(self,song:SongIdentity)->LyricsResult|None:
        keys=(TextNormalizer.key(song.title),TextNormalizer.key(song.artist),TextNormalizer.key(song.album))
        with self._connect() as db:
            row=db.execute('''SELECT lyrics,provider,synchronized FROM Lyrics WHERE title_key=? AND (artist_key=? OR artist_key='' OR ?='') ORDER BY CASE WHEN album_key=? THEN 0 ELSE 1 END,id DESC LIMIT 1''',(keys[0],keys[1],keys[1],keys[2])).fetchone()
        return LyricsResult(song,row[0],LyricsSource.CACHE,row[1] or 'SQLite',bool(row[2])) if row else None
    def save(self,result:LyricsResult)->None:
        s=result.song
        with self._connect() as db:db.execute('''INSERT INTO Lyrics(title,artist,album,language,lyrics,source,provider,synchronized,title_key,artist_key,album_key) VALUES(?,?,?,?,?,?,?,?,?,?,?)''',(s.title,s.artist,s.album,s.language,result.lyrics,result.source.value,result.provider,int(result.synchronized),TextNormalizer.key(s.title),TextNormalizer.key(s.artist),TextNormalizer.key(s.album)))
