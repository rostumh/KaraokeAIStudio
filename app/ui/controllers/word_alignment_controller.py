from __future__ import annotations

from pathlib import Path
from threading import Event

from PySide6.QtCore import QObject, QThread, Signal, Slot

from app.application.services.word_alignment_service import WordAlignmentService
from app.domain.models.transcription import Transcript


class _AlignmentWorker(QObject):
    progress = Signal(float, str)
    succeeded = Signal(object)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, service: WordAlignmentService, transcript: Transcript, destination: Path, cancel: Event) -> None:
        super().__init__()
        self._service = service
        self._transcript = transcript
        self._destination = destination
        self._cancel = cancel

    @Slot()
    def run(self) -> None:
        try:
            self.succeeded.emit(self._service.align(self._transcript, self._destination, self.progress.emit, self._cancel))
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            self.finished.emit()


class WordAlignmentController(QObject):
    progressChanged = Signal(int, str)
    succeeded = Signal(object)
    failed = Signal(str)
    busyChanged = Signal(bool)

    def __init__(self, service: WordAlignmentService) -> None:
        super().__init__()
        self._service = service
        self._thread: QThread | None = None
        self._worker: _AlignmentWorker | None = None
        self._cancel = Event()

    def start(self, transcript: Transcript, destination: Path) -> None:
        if self._thread is not None:
            self.failed.emit("Word alignment is already running.")
            return
        self._cancel = Event()
        thread = QThread(self)
        worker = _AlignmentWorker(self._service, transcript, destination, self._cancel)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(lambda value, text: self.progressChanged.emit(round(value * 100), text))
        worker.succeeded.connect(self.succeeded)
        worker.failed.connect(self.failed)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._release)
        self._thread, self._worker = thread, worker
        self.busyChanged.emit(True)
        thread.start()

    def cancel(self) -> None:
        self._cancel.set()

    @Slot()
    def _release(self) -> None:
        self._thread = None
        self._worker = None
        self.busyChanged.emit(False)

    def shutdown(self, timeout_milliseconds: int = 8000) -> bool:
        if self._thread is None:
            return True
        self.cancel()
        return self._thread.wait(timeout_milliseconds)
