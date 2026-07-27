from __future__ import annotations

from pathlib import Path
from threading import Event
from PySide6.QtCore import QObject,QThread,Signal,Slot
from app.application.services.transcription_service import TranscriptionService
from app.domain.models.media import MediaAsset
from app.domain.models.transcription import TranscriptionOptions,TranscriptionTask,WhisperDevice

class _Worker(QObject):
    progress=Signal(float,str);succeeded=Signal(object);failed=Signal(str);finished=Signal()
    def __init__(self,service:TranscriptionService,asset:MediaAsset,options:dict[str,object],cancel:Event)->None:super().__init__();self.s=service;self.a=asset;self.o=options;self.c=cancel
    @Slot()
    def run(self)->None:
        try:
            options=TranscriptionOptions(str(self.o["model"]),WhisperDevice(str(self.o["device"])),str(self.o["compute"]),str(self.o["language"]) if self.o.get("language") else None,TranscriptionTask(str(self.o["task"])),int(self.o["beam"]),bool(self.o["vad"]),bool(self.o["context"]),str(self.o["prompt"]) if self.o.get("prompt") else None)
            self.succeeded.emit(self.s.transcribe(self.a,options,Path(str(self.o["destination"])),self.progress.emit,self.c))
        except Exception as exc:self.failed.emit(str(exc))
        finally:self.finished.emit()
class TranscriptionController(QObject):
    progressChanged=Signal(int,str);succeeded=Signal(object);failed=Signal(str);busyChanged=Signal(bool)
    def __init__(self,service:TranscriptionService)->None:super().__init__();self.s=service;self.t:QThread|None=None;self.w:_Worker|None=None;self.c=Event()
    def start(self,asset:MediaAsset,options:dict[str,object])->None:
        if self.t:self.failed.emit("Speech recognition is already running.");return
        self.c=Event();t=QThread(self);w=_Worker(self.s,asset,options,self.c);w.moveToThread(t);t.started.connect(w.run);w.progress.connect(lambda value,text:self.progressChanged.emit(round(value*100),text));w.succeeded.connect(self.succeeded);w.failed.connect(self.failed);w.finished.connect(t.quit);w.finished.connect(w.deleteLater);t.finished.connect(t.deleteLater);t.finished.connect(self._release);self.t,self.w=t,w;self.busyChanged.emit(True);t.start()
    def cancel(self)->None:self.c.set()
    @Slot()
    def _release(self)->None:self.t=None;self.w=None;self.busyChanged.emit(False)
    def shutdown(self,timeout_milliseconds:int=8000)->bool:
        if self.t is None:return True
        self.cancel();return self.t.wait(timeout_milliseconds)
