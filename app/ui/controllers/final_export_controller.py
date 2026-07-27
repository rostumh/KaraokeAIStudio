from __future__ import annotations

from pathlib import Path
from threading import Event
from PySide6.QtCore import QObject,QThread,Signal,Slot
from app.application.services.final_export_service import FinalExportService
class _Worker(QObject):
 progress=Signal(float,str);succeeded=Signal(object);failed=Signal(str);finished=Signal()
 def __init__(self,s:FinalExportService,source:Path,dest:Path,c:Event)->None:super().__init__();self.s=s;self.source=source;self.dest=dest;self.c=c
 @Slot()
 def run(self)->None:
  try:self.succeeded.emit(self.s.validate(self.source,self.dest,self.progress.emit,self.c))
  except Exception as exc:self.failed.emit(str(exc))
  finally:self.finished.emit()
class FinalExportController(QObject):
 progressChanged=Signal(int,str);succeeded=Signal(object);failed=Signal(str);busyChanged=Signal(bool)
 def __init__(self,s:FinalExportService)->None:super().__init__();self.s=s;self.t:QThread|None=None;self.w:_Worker|None=None;self.c=Event()
 def start(self,source:Path,dest:Path)->None:
  if self.t:self.failed.emit("Quality validation is already running.");return
  self.c=Event();t=QThread(self);w=_Worker(self.s,source,dest,self.c);w.moveToThread(t);t.started.connect(w.run);w.progress.connect(lambda v,x:self.progressChanged.emit(round(v*100),x));w.succeeded.connect(self.succeeded);w.failed.connect(self.failed);w.finished.connect(t.quit);w.finished.connect(w.deleteLater);t.finished.connect(t.deleteLater);t.finished.connect(self._release);self.t,self.w=t,w;self.busyChanged.emit(True);t.start()
 def cancel(self)->None:self.c.set()
 @Slot()
 def _release(self)->None:self.t=None;self.w=None;self.busyChanged.emit(False)
 def shutdown(self,timeout_milliseconds:int=8000)->bool:
  if self.t is None:return True
  self.cancel();return self.t.wait(timeout_milliseconds)
