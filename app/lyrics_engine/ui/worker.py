from __future__ import annotations
from PySide6.QtCore import QObject,QRunnable,Signal,Slot
from ..engine import LyricsEngine
from ..models import SongIdentity
class LyricsWorkerSignals(QObject):
    progress=Signal(str);finished=Signal(object);failed=Signal(str)
class LyricsSearchWorker(QRunnable):
    def __init__(self,engine:LyricsEngine,song:SongIdentity,allow_whisper=True):super().__init__();self.engine=engine;self.song=song;self.allow_whisper=allow_whisper;self.signals=LyricsWorkerSignals()
    @Slot()
    def run(self):
        try:self.signals.finished.emit(self.engine.search(self.song,self.signals.progress.emit,self.allow_whisper))
        except Exception as exc:self.signals.failed.emit(str(exc))
