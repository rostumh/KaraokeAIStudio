from __future__ import annotations
from PySide6.QtCore import QObject,QRunnable,Signal,Slot
from ..automatic import AutomaticLyricsSearch
class AutomaticLyricsSignals(QObject):
    status=Signal(str);found=Signal(object);notFound=Signal(object);failed=Signal(str)
class AutomaticLyricsWorker(QRunnable):
    def __init__(self,search,asset):super().__init__();self.search=search;self.asset=asset;self.signals=AutomaticLyricsSignals()
    @Slot()
    def run(self):
        try:
            result,song=self.search.search(self.asset.source_path,self.asset.tags,self.asset.duration_seconds,self.signals.status.emit)
            (self.signals.found.emit(result) if result else self.signals.notFound.emit(self.asset))
        except Exception as exc:self.signals.failed.emit(str(exc));self.signals.notFound.emit(self.asset)
