from __future__ import annotations

import logging
from pathlib import Path
from threading import Event

from PySide6.QtCore import QObject, QThread, Signal, Slot

from app.application.services.vocal_separation_service import VocalSeparationService
from app.domain.models.media import MediaAsset
from app.domain.models.separation import ComputeDevice, SeparationMode, StemFormat

LOGGER = logging.getLogger(__name__)


class _Worker(QObject):
    status = Signal(str); succeeded = Signal(object); failed = Signal(str); finished = Signal()
    def __init__(self, service: VocalSeparationService, asset: MediaAsset, options: dict[str, object], cancel: Event) -> None:
        super().__init__(); self._service=service; self._asset=asset; self._options=options; self._cancel=cancel
    @Slot()
    def run(self) -> None:
        try:
            result=self._service.separate(self._asset, Path(str(self._options["output_root"])), model_name=str(self._options["model"]), mode=SeparationMode(str(self._options["mode"])), device=ComputeDevice(str(self._options["device"])), stem_format=StemFormat(str(self._options["format"])), shifts=int(self._options["shifts"]), overlap=float(self._options["overlap"]), segment_seconds=min(int(self._options["segment"]),7) if str(self._options.get("model","")).startswith("htdemucs") and self._options.get("segment") else int(self._options["segment"]) if self._options.get("segment") else None, status=self.status.emit, cancel_event=self._cancel)
            self.succeeded.emit(result)
        except Exception as exc: LOGGER.exception("Separation worker failed"); self.failed.emit(str(exc))
        finally: self.finished.emit()


class VocalSeparationController(QObject):
    started=Signal(); statusChanged=Signal(str); succeeded=Signal(object); failed=Signal(str); busyChanged=Signal(bool)
    def __init__(self, service: VocalSeparationService) -> None:
        super().__init__(); self._service=service; self._thread: QThread|None=None; self._worker: _Worker|None=None; self._cancel=Event()
    @property
    def busy(self) -> bool: return self._thread is not None
    def start(self, asset: MediaAsset, options: dict[str, object]) -> None:
        if self.busy: self.failed.emit("Vocal separation is already running."); return
        self._cancel=Event(); thread=QThread(self); worker=_Worker(self._service,asset,options,self._cancel); worker.moveToThread(thread); thread.started.connect(worker.run); worker.status.connect(self.statusChanged); worker.succeeded.connect(self.succeeded); worker.failed.connect(self.failed); worker.finished.connect(thread.quit); worker.finished.connect(worker.deleteLater); thread.finished.connect(thread.deleteLater); thread.finished.connect(self._release); self._thread,self._worker=thread,worker; self.started.emit(); self.busyChanged.emit(True); thread.start()
    def cancel(self) -> None: self._cancel.set()
    @Slot()
    def _release(self) -> None: self._thread=None; self._worker=None; self.busyChanged.emit(False)
    def shutdown(self, timeout_milliseconds: int=8000) -> bool:
        if self._thread is None: return True
        self.cancel(); return self._thread.wait(timeout_milliseconds)
