from __future__ import annotations

from pathlib import Path
from threading import Event
from PySide6.QtCore import QObject,QThread,Signal,Slot
from app.application.services.update_service import UpdateService
class _Worker(QObject):
 progress=Signal(float,str);succeeded=Signal(object);failed=Signal(str);finished=Signal()
 def __init__(self,service:UpdateService,mode:str,args:tuple,cancel:Event)->None:super().__init__();self.s=service;self.mode=mode;self.args=args;self.c=cancel
 @Slot()
 def run(self)->None:
  try:
   value=self.s.check(*self.args) if self.mode=="check" else self.s.download(*self.args,self.progress.emit,self.c)
   self.succeeded.emit(value)
  except Exception as exc:self.failed.emit(str(exc))
  finally:self.finished.emit()
class UpdateController(QObject):
 progressChanged=Signal(int,str);checkSucceeded=Signal(object);downloadSucceeded=Signal(object);failed=Signal(str);busyChanged=Signal(bool)
 def __init__(self,service:UpdateService)->None:super().__init__();self.s=service;self.t:QThread|None=None;self.w:_Worker|None=None;self.c=Event();self.mode=""
 def check(self,current:str,url:str)->None:self._start("check",(current,url))
 def download(self,release:object,destination:Path)->None:self._start("download",(release,destination))
 def _start(self,mode:str,args:tuple)->None:
  if self.t:self.failed.emit("An update operation is already running.");return
  self.mode=mode;self.c=Event();t=QThread(self);w=_Worker(self.s,mode,args,self.c);w.moveToThread(t);t.started.connect(w.run);w.progress.connect(lambda v,x:self.progressChanged.emit(round(v*100),x));w.succeeded.connect(self._success);w.failed.connect(self.failed);w.finished.connect(t.quit);w.finished.connect(w.deleteLater);t.finished.connect(t.deleteLater);t.finished.connect(self._release);self.t,self.w=t,w;self.busyChanged.emit(True);t.start()
 @Slot(object)
 def _success(self,value:object)->None:(self.checkSucceeded if self.mode=="check" else self.downloadSucceeded).emit(value)
 def cancel(self)->None:self.c.set()
 @Slot()
 def _release(self)->None:self.t=None;self.w=None;self.mode="";self.busyChanged.emit(False)
 def shutdown(self,timeout_milliseconds:int=8000)->bool:
  if self.t is None:return True
  self.cancel();return self.t.wait(timeout_milliseconds)
