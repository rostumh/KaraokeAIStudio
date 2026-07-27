from __future__ import annotations

from pathlib import Path
from threading import Event
from PySide6.QtCore import QObject,QThread,Signal,Slot
from app.application.services.lyrics_translation_service import LyricsTranslationService
from app.domain.models.lyrics_document import LyricsDocument
from app.domain.models.translation import TranslationOptions
class _Worker(QObject):
 progress=Signal(float,str);succeeded=Signal(object);failed=Signal(str);finished=Signal()
 def __init__(self,s:LyricsTranslationService,d:LyricsDocument,o:TranslationOptions,p:Path,c:Event)->None:super().__init__();self.s=s;self.d=d;self.o=o;self.p=p;self.c=c
 @Slot()
 def run(self)->None:
  try:self.succeeded.emit(self.s.translate(self.d,self.o,self.p,self.progress.emit,self.c))
  except Exception as exc:self.failed.emit(str(exc))
  finally:self.finished.emit()
class TranslationController(QObject):
 progressChanged=Signal(int,str);succeeded=Signal(object);failed=Signal(str);busyChanged=Signal(bool)
 def __init__(self,s:LyricsTranslationService)->None:super().__init__();self.s=s;self.t:QThread|None=None;self.w:_Worker|None=None;self.c=Event()
 def start(self,d:LyricsDocument,o:TranslationOptions,p:Path)->None:
  if self.t:self.failed.emit("Lyrics translation is already running.");return
  self.c=Event();t=QThread(self);w=_Worker(self.s,d,o,p,self.c);w.moveToThread(t);t.started.connect(w.run);w.progress.connect(lambda v,x:self.progressChanged.emit(round(v*100),x));w.succeeded.connect(self.succeeded);w.failed.connect(self.failed);w.finished.connect(t.quit);w.finished.connect(w.deleteLater);t.finished.connect(t.deleteLater);t.finished.connect(self._release);self.t,self.w=t,w;self.busyChanged.emit(True);t.start()
 def cancel(self)->None:self.c.set()
 @Slot()
 def _release(self)->None:self.t=None;self.w=None;self.busyChanged.emit(False)
 def shutdown(self,timeout_milliseconds:int=8000)->bool:
  if self.t is None:return True
  self.cancel();return self.t.wait(timeout_milliseconds)
