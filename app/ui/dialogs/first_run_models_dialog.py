from __future__ import annotations

from pathlib import Path
from threading import Event, Thread

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QDialog, QLabel, QProgressBar, QPushButton, QVBoxLayout

from app.application.services.model_provisioning_service import ModelProvisioningService
from app.domain.models.model_package import ModelPackage


class _Bridge(QObject):
    progress = Signal(int, str)
    done = Signal()
    failed = Signal(str)


class FirstRunModelsDialog(QDialog):
    def __init__(self, service: ModelProvisioningService, models: tuple[ModelPackage, ...], root: Path, parent: object = None) -> None:
        super().__init__(parent)
        self.service = service
        self.models = models
        self.root = root
        self.cancel_event = Event()
        self.setWindowTitle("Preparing Karaoke AI Studio")
        self.setMinimumWidth(560)
        self.setModal(True)
        self.label = QLabel(
            "Karaoke AI Studio needs to download its essential speech-recognition model. "
            "This happens once and can resume if interrupted."
        )
        self.label.setWordWrap(True)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.button = QPushButton("Download Required Model")
        self.button.clicked.connect(self.start)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        layout.addWidget(self.button)
        self.bridge = _Bridge()
        self.bridge.progress.connect(self._progress)
        self.bridge.done.connect(self.accept)
        self.bridge.failed.connect(self._failed)

    def start(self) -> None:
        self.button.setEnabled(False)
        self.cancel_event.clear()

        def run() -> None:
            try:
                self.service.provision(
                    self.models,
                    self.root,
                    lambda received, total, name: self.bridge.progress.emit(
                        round(received * 100 / max(1, total)),
                        f"Downloading {name} - {received * 100 / max(1, total):.0f}%",
                    ),
                    self.cancel_event,
                )
                self.bridge.done.emit()
            except Exception as exc:
                self.bridge.failed.emit(str(exc))

        Thread(target=run, daemon=True).start()

    def _progress(self, value: int, text: str) -> None:
        self.progress.setValue(value)
        self.label.setText(text)

    def _failed(self, text: str) -> None:
        self.label.setText(
            text + "\n\nCheck your internet connection, then click Retry. Existing progress is preserved."
        )
        self.button.setText("Retry")
        self.button.setEnabled(True)

    def reject(self) -> None:
        self.cancel_event.set()
        super().reject()
