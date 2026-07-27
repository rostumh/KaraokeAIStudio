from __future__ import annotations

from datetime import datetime,timezone
from pathlib import Path
from threading import Event
from PySide6.QtCore import QObject,QThread,Signal,Slot
from app.application.ports.batch_job_executor import BatchJobExecutor
from app.application.services.batch_queue_service import BatchQueueService
from app.domain.models.batch import BatchJob,BatchOperation,BatchStatus
from app.infrastructure.repositories.batch_queue_repository import BatchQueueRepository

class _Worker(QObject):
 progress=Signal(float,str);succeeded=Signal(str);failed=Signal(str);finished=Signal()
 def __init__(self,e:BatchJobExecutor,j:BatchJob,c:Event)->None:super().__init__();self.e=e;self.j=j;self.c=c
 @Slot()
 def run(self)->None:
  try:self.succeeded.emit(self.e.execute(self.j,self.progress.emit,self.c))
  except Exception as exc:self.failed.emit(str(exc))
  finally:self.finished.emit()
class BatchQueueController(QObject):
 jobsChanged=Signal(object);busyChanged=Signal(bool)
 def __init__(self,e:BatchJobExecutor,r:BatchQueueRepository,path:Path)->None:
  super().__init__();self.e=e;self.r=r;self.path=path;self.jobs=r.load(path);self.t:QThread|None=None;self.w:_Worker|None=None;self.c=Event();self.active_id=None
 def add(self,sources:tuple[Path,...],operation:BatchOperation,root:Path)->None:self.jobs=BatchQueueService.add_jobs(self.jobs,sources,operation,root);self._publish()
 def start(self)->None:
  if self.t:return
  job=next((j for j in self.jobs if j.status==BatchStatus.QUEUED),None)
  if job is None:return
  now=datetime.now(timezone.utc).isoformat();self._replace(job.update(status=BatchStatus.RUNNING,progress=0,message="Starting",attempts=job.attempts+1,started_utc=now));self.active_id=job.job_id;self.c=Event();t=QThread(self);w=_Worker(self.e,job,self.c);w.moveToThread(t);t.started.connect(w.run);w.progress.connect(self._progress);w.succeeded.connect(self._success);w.failed.connect(self._failure);w.finished.connect(t.quit);w.finished.connect(w.deleteLater);t.finished.connect(t.deleteLater);t.finished.connect(self._release);self.t,self.w=t,w;self.busyChanged.emit(True);t.start()
 def cancel(self)->None:self.c.set()
 def retry(self,row:int)->None:
  if 0<=row<len(self.jobs):self._replace(BatchQueueService.retry(self.jobs[row]))
 def remove(self,row:int)->None:
  if self.t or not 0<=row<len(self.jobs):return
  self.jobs=self.jobs[:row]+self.jobs[row+1:];self._publish()
 @Slot(float,str)
 def _progress(self,value:float,message:str)->None:
  j=self._active();self._replace(j.update(progress=value,message=message)) if j else None
 @Slot(str)
 def _success(self,message:str)->None:
  j=self._active();self._replace(j.update(status=BatchStatus.SUCCEEDED,progress=1,message=message,finished_utc=datetime.now(timezone.utc).isoformat())) if j else None
 @Slot(str)
 def _failure(self,message:str)->None:
  j=self._active();status=BatchStatus.CANCELLED if self.c.is_set() else BatchStatus.FAILED;self._replace(j.update(status=status,message=message,finished_utc=datetime.now(timezone.utc).isoformat())) if j else None
 def _active(self)->BatchJob|None:return next((j for j in self.jobs if j.job_id==self.active_id),None)
 def _replace(self,job:BatchJob)->None:self.jobs=tuple(job if x.job_id==job.job_id else x for x in self.jobs);self._publish()
 def _publish(self)->None:self.r.save(self.jobs,self.path);self.jobsChanged.emit(self.jobs)
 @Slot()
 def _release(self)->None:self.t=None;self.w=None;self.active_id=None;self.busyChanged.emit(False);self.start()
 def shutdown(self,timeout_milliseconds:int=8000)->bool:
  if self.t is None:return True
  self.cancel();return self.t.wait(timeout_milliseconds)
