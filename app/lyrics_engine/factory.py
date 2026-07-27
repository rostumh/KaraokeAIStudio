from pathlib import Path
from .cache import SQLiteLyricsCache
from .engine import LyricsEngine,WhisperFallback
from .local_files import LocalLyricsFinder
from .logging_config import configure_lyrics_logger
from .providers.lrclib import LRCLibProvider
from .providers.lyrics_ovh import LyricsOvhProvider
from .providers.manager import LyricsProviderManager
def create_lyrics_engine(data_dir:Path,whisper:WhisperFallback|None=None)->LyricsEngine:
    logger=configure_lyrics_logger(data_dir/'lyrics.log')
    return LyricsEngine(SQLiteLyricsCache(data_dir/'lyrics.db'),LocalLyricsFinder(),LyricsProviderManager([LRCLibProvider(),LyricsOvhProvider()],logger),whisper=whisper,logger=logger)
