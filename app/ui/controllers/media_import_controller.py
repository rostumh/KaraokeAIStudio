from __future__ import annotations

import logging
from collections import deque
from pathlib import Path

from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot

from app.application.services.media_import_service import MediaImportService
from app.domain.models.media import MediaAsset

LOGGER = logging.getLogger(__name__)


class _ImportWorker(QObject):
    succeeded = Signal(object)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, service: MediaImportService, source: Path) -> None:
        super().__init__()
        self._service = service
        self._source = source

    @Slot()
    def run(self) -> None:
        try:
            self.succeeded.emit(self._service.import_file(self._source))
        except Exception as exc:
            LOGGER.exception("Media import failed for %s", self._source)
            self.failed.emit(str(exc))
        finally:
            self.finished.emit()


class MediaImportController(QObject):
    """Runs blocking media inspection off the GUI thread and exposes Qt signals."""

    started = Signal(str)
    succeeded = Signal(object)
    failed = Signal(str)
    busyChanged = Signal(bool)

    def __init__(self, service: MediaImportService) -> None:
        super().__init__()
        self._service = service
        self._thread: QThread | None = None
        self._worker: _ImportWorker | None = None
        self._queue: deque[Path] = deque()

    @property
    def busy(self) -> bool:
        return self._thread is not None

    def import_file(self, source: Path) -> None:
        normalized = source.expanduser().resolve(strict=False)
        if self.busy:
            if normalized not in self._queue:
                self._queue.append(normalized)
            return
        thread = QThread(self)
        worker = _ImportWorker(self._service, normalized)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.succeeded.connect(self.succeeded)
        worker.failed.connect(self.failed)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._release_thread)
        self._thread = thread
        self._worker = worker
        self.started.emit(normalized.name)
        self.busyChanged.emit(True)
        thread.start()

    @Slot()
    def _release_thread(self) -> None:
        self._thread = None
        self._worker = None
        self.busyChanged.emit(False)
        if self._queue:
            next_source = self._queue.popleft()
            QTimer.singleShot(0, lambda: self.import_file(next_source))

    def shutdown(self, timeout_milliseconds: int = 5000) -> bool:
        self._queue.clear()
        thread = self._thread
        if thread is None:
            return True
        thread.requestInterruption()
        thread.quit()
        return thread.wait(timeout_milliseconds)
