from __future__ import annotations

import logging
from pathlib import Path
from threading import Event
from PySide6.QtCore import QObject,QThread,Signal,Slot
from app.application.services.instrumental_cleanup_service import InstrumentalCleanupService
from app.domain.models.instrumental_cleanup import CleanupOutputFormat,CleanupPreset,CleanupSettings
from app.domain.models.media import MediaAsset
LOGGER=logging.getLogger(__name__)

class _Worker(QObject):
    progress=Signal(float); succeeded=Signal(object); failed=Signal(str); finished=Signal()
    def __init__(self,service: InstrumentalCleanupService,asset: MediaAsset,options: dict[str,object],cancel: Event)->None:
        super().__init__();self._service=service;self._asset=asset;self._options=options;self._cancel=cancel
    @Slot()
    def run(self)->None:
        try:
            settings=CleanupSettings(CleanupPreset(str(self._options["preset"])),float(self._options["noise_reduction"]),float(self._options["noise_floor"]),int(self._options["highpass"]),int(self._options["lowpass"]),float(self._options["target_lufs"]),float(self._options["true_peak"]),float(self._options["lra"]),bool(self._options["limiter"]),CleanupOutputFormat(str(self._options["format"])))
            result=self._service.clean(self._asset,Path(str(self._options["output_path"])),settings,overwrite=bool(self._options["overwrite"]),progress=self.progress.emit,cancel_event=self._cancel);self.succeeded.emit(result)
        except Exception as exc: LOGGER.exception("Cleanup worker failed");self.failed.emit(str(exc))
        finally:self.finished.emit()

class InstrumentalCleanupController(QObject):
    progressChanged=Signal(int);succeeded=Signal(object);failed=Signal(str);busyChanged=Signal(bool)
    def __init__(self,service: InstrumentalCleanupService)->None:
        super().__init__();self._service=service;self._thread:QThread|None=None;self._worker:_Worker|None=None;self._cancel=Event()
    @property
    def busy(self)->bool:return self._thread is not None
    def start(self,asset:MediaAsset,options:dict[str,object])->None:
        if self.busy:self.failed.emit("Instrumental cleanup is already running.");return
        self._cancel=Event();thread=QThread(self);worker=_Worker(self._service,asset,options,self._cancel);worker.moveToThread(thread);thread.started.connect(worker.run);worker.progress.connect(lambda value:self.progressChanged.emit(round(value*100)));worker.succeeded.connect(self.succeeded);worker.failed.connect(self.failed);worker.finished.connect(thread.quit);worker.finished.connect(worker.deleteLater);thread.finished.connect(thread.deleteLater);thread.finished.connect(self._release);self._thread,self._worker=thread,worker;self.busyChanged.emit(True);thread.start()
    def cancel(self)->None:self._cancel.set()
    @Slot()
    def _release(self)->None:self._thread=None;self._worker=None;self.busyChanged.emit(False)
    def shutdown(self,timeout_milliseconds:int=6000)->bool:
        if self._thread is None:return True
        self.cancel();return self._thread.wait(timeout_milliseconds)
