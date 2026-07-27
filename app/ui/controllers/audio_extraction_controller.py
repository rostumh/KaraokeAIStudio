from __future__ import annotations

import logging
from pathlib import Path
from threading import Event

from PySide6.QtCore import QObject, QThread, Signal, Slot

from app.application.services.audio_extraction_service import AudioExtractionService
from app.domain.models.audio_extraction import AudioExtractionResult, AudioFormat
from app.domain.models.media import MediaAsset

LOGGER = logging.getLogger(__name__)


class _ExtractionWorker(QObject):
    progress = Signal(float)
    succeeded = Signal(object)
    failed = Signal(str)
    finished = Signal()

    def __init__(self, service: AudioExtractionService, asset: MediaAsset, options: dict[str, object], cancel_event: Event) -> None:
        super().__init__()
        self._service = service
        self._asset = asset
        self._options = options
        self._cancel_event = cancel_event

    @Slot()
    def run(self) -> None:
        try:
            result = self._service.extract(
                self._asset,
                Path(str(self._options["output_path"])),
                AudioFormat(str(self._options["output_format"])),
                stream_index=int(self._options["stream_index"]),
                sample_rate=int(self._options["sample_rate"]) if self._options.get("sample_rate") else None,
                channels=int(self._options["channels"]) if self._options.get("channels") else None,
                mp3_bitrate_kbps=int(self._options.get("mp3_bitrate_kbps", 320)),
                overwrite=bool(self._options.get("overwrite", False)),
                progress=self.progress.emit,
                cancel_event=self._cancel_event,
            )
            self.succeeded.emit(result)
        except Exception as exc:
            LOGGER.exception("Audio extraction worker failed")
            self.failed.emit(str(exc))
        finally:
            self.finished.emit()


class AudioExtractionController(QObject):
    started = Signal()
    progressChanged = Signal(int)
    succeeded = Signal(object)
    failed = Signal(str)
    busyChanged = Signal(bool)

    def __init__(self, service: AudioExtractionService) -> None:
        super().__init__()
        self._service = service
        self._thread: QThread | None = None
        self._worker: _ExtractionWorker | None = None
        self._cancel_event = Event()

    @property
    def busy(self) -> bool:
        return self._thread is not None

    def start(self, asset: MediaAsset, options: dict[str, object]) -> None:
        if self.busy:
            self.failed.emit("Audio extraction is already running.")
            return
        self._cancel_event = Event()
        thread = QThread(self)
        worker = _ExtractionWorker(self._service, asset, options, self._cancel_event)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(lambda value: self.progressChanged.emit(round(value * 100)))
        worker.succeeded.connect(self.succeeded)
        worker.failed.connect(self.failed)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._release)
        self._thread, self._worker = thread, worker
        self.started.emit()
        self.busyChanged.emit(True)
        thread.start()

    def cancel(self) -> None:
        self._cancel_event.set()

    @Slot()
    def _release(self) -> None:
        self._thread = None
        self._worker = None
        self.busyChanged.emit(False)

    def shutdown(self, timeout_milliseconds: int = 6000) -> bool:
        if self._thread is None:
            return True
        self.cancel()
        return self._thread.wait(timeout_milliseconds)
